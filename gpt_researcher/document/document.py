import asyncio
import base64
import logging
import mimetypes
import os
from typing import List, Union

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredCSVLoader,
    UnstructuredEPubLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_community.document_loaders import BSHTMLLoader

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = frozenset(
    {"png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff", "heic", "heif"}
)

_IMAGE_MIME = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "heic": "image/heic",
    "heif": "image/heif",
}


def detect_utf8(file_path: str) -> str | None:
    """Return "utf-8-sig" if the file decodes as UTF-8, else None.

    TextLoader and BSHTMLLoader otherwise open files with the locale encoding,
    which on Windows is a code page such as cp1252 that rejects or garbles
    UTF-8. Non-UTF-8 files keep that default; "utf-8-sig" also drops a BOM.
    """
    with open(file_path, "rb") as f:
        try:
            f.read().decode("utf-8")
        except UnicodeDecodeError:
            return None
    return "utf-8-sig"


def _image_mime_type(file_path: str, file_extension: str) -> str:
    """Pick a MIME type for an image file. :-)"""
    return (
        _IMAGE_MIME.get(file_extension)
        or mimetypes.guess_type(file_path)[0]
        or "application/octet-stream"
    )


def _vision_image_payload(file_path: str, file_extension: str) -> tuple[str, str]:
    """Return (mime, base64) for vision APIs; convert HEIC/HEIF to JPEG when possible. :-)"""
    if file_extension in {"heic", "heif"}:
        try:
            from io import BytesIO

            from PIL import Image
            from pillow_heif import register_heif_opener

            register_heif_opener()
            with Image.open(file_path) as img:
                rgb = img.convert("RGB")
                buf = BytesIO()
                rgb.save(buf, format="JPEG", quality=90)
            return "image/jpeg", base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception as exc:
            logger.info(
                "HEIC/HEIF convert unavailable for %s (%s); sending original bytes.",
                file_path,
                exc,
            )

    mime = _image_mime_type(file_path, file_extension)
    with open(file_path, "rb") as f:
        return mime, base64.b64encode(f.read()).decode("ascii")


async def describe_image_with_vision(file_path: str) -> str:
    """Describe an image via the configured Smart LLM (multimodal). :-)

    Smart is preferred over Fast: image indexing needs a vision-capable model,
    and Smart is the research-quality slot operators usually keep healthy.
    """
    from gpt_researcher.config.config import Config
    from gpt_researcher.utils.llm import create_chat_completion

    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    mime, encoded = _vision_image_payload(file_path, ext)
    data_url = f"data:{mime};base64,{encoded}"
    filename = os.path.basename(file_path)

    cfg = Config()
    prompt = (
        f"You are indexing the uploaded project document named `{filename}` "
        "for later research. Describe everything useful for answering "
        "questions about this image: visible text (transcribe it), layout, "
        "objects, people, charts, logos, and any context. Be concrete and "
        "complete. Reply in plain text only."
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]
    # Prefer Smart (vision-capable). If Smart fails, fall back to Fast. :-)
    try:
        return await create_chat_completion(
            messages=messages,
            model=cfg.smart_llm_model,
            temperature=0.2,
            max_tokens=min(getattr(cfg, "smart_token_limit", 4000) or 4000, 4000),
            llm_provider=cfg.smart_llm_provider,
            llm_kwargs=cfg.llm_kwargs,
            fallback_llm="",
        )
    except Exception as smart_exc:
        logger.warning(
            "Smart vision describe failed for %s (%s); trying Fast LLM.",
            filename,
            smart_exc,
        )
        return await create_chat_completion(
            messages=messages,
            model=cfg.fast_llm_model,
            temperature=0.2,
            max_tokens=min(getattr(cfg, "fast_token_limit", 4000) or 4000, 4000),
            llm_provider=cfg.fast_llm_provider,
            llm_kwargs=cfg.llm_kwargs,
        )


async def load_image_as_documents(file_path: str) -> list:
    """Load an image as LangChain Documents (OCR first, then vision). :-)"""
    # Prefer local OCR when Unstructured + deps are installed.
    try:
        from langchain_community.document_loaders import UnstructuredImageLoader

        pages = await asyncio.to_thread(UnstructuredImageLoader(file_path).load)
        if pages and any((p.page_content or "").strip() for p in pages):
            for page in pages:
                meta = getattr(page, "metadata", None) or {}
                if not meta.get("source"):
                    page.metadata = {**meta, "source": file_path}
            return pages
    except Exception as exc:
        logger.info(
            "Unstructured image OCR unavailable for %s (%s); using vision.",
            file_path,
            exc,
        )

    try:
        description = (await describe_image_with_vision(file_path) or "").strip()
    except Exception as exc:
        print(f"Failed to describe image document: {file_path}")
        print(exc)
        return []

    if not description:
        return []

    return [
        Document(
            page_content=description,
            metadata={"source": file_path, "loader": "vision"},
        )
    ]


class DocumentLoader:

    def __init__(self, path: Union[str, List[str]]):
        self.path = path

    async def load(self) -> list:
        tasks = []
        if isinstance(self.path, list):
            for file_path in self.path:
                if os.path.isfile(file_path):  # Ensure it's a valid file
                    filename = os.path.basename(file_path)
                    file_name, file_extension_with_dot = os.path.splitext(filename)
                    file_extension = file_extension_with_dot.strip(".").lower()
                    tasks.append(self._load_document(file_path, file_extension))

        elif isinstance(self.path, (str, bytes, os.PathLike)):
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_name, file_extension_with_dot = os.path.splitext(file)
                    file_extension = file_extension_with_dot.strip(".").lower()
                    tasks.append(self._load_document(file_path, file_extension))

        else:
            raise ValueError("Invalid type for path. Expected str, bytes, os.PathLike, or list thereof.")

        docs = []
        for pages in await asyncio.gather(*tasks):
            for page in pages:
                if page.page_content:
                    # Loaders occasionally omit metadata["source"] (custom loaders,
                    # some HTML partitions). Prefer source, then fall back to path.
                    meta = getattr(page, "metadata", None) or {}
                    source = meta.get("source") or meta.get("file_path") or ""
                    url = os.path.basename(source) if source else ""
                    docs.append({
                        "raw_content": page.page_content,
                        "url": url,
                    })

        if not docs:
            raise ValueError("🤷 Failed to load any documents!")

        return docs

    async def _load_document(self, file_path: str, file_extension: str) -> list:
        ret_data = []
        try:
            if file_extension in IMAGE_EXTENSIONS:
                return await load_image_as_documents(file_path)

            encoding = detect_utf8(file_path) if file_extension in ("txt", "html", "htm") else None
            loader_dict = {
                "pdf": PyMuPDFLoader(file_path),
                "epub": UnstructuredEPubLoader(file_path),
                "txt": TextLoader(file_path, encoding=encoding),
                "doc": UnstructuredWordDocumentLoader(file_path),
                "docx": UnstructuredWordDocumentLoader(file_path),
                "pptx": UnstructuredPowerPointLoader(file_path),
                "csv": UnstructuredCSVLoader(file_path, mode="elements"),
                "xls": UnstructuredExcelLoader(file_path, mode="elements"),
                "xlsx": UnstructuredExcelLoader(file_path, mode="elements"),
                "md": UnstructuredMarkdownLoader(file_path),
                "html": BSHTMLLoader(file_path, open_encoding=encoding),
                "htm": BSHTMLLoader(file_path, open_encoding=encoding),
            }

            loader = loader_dict.get(file_extension, None)
            if loader:
                try:
                    ret_data = loader.load()
                except Exception as e:
                    print(
                        f"Failed to load {file_extension or 'unknown'} document: {file_path}"
                    )
                    print(e)

        except Exception as e:
            print(f"Failed to load document : {file_path}")
            print(e)

        return ret_data
