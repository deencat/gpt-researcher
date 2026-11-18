"""Image uploads must load via vision when OCR deps are unavailable. :-)"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.documents import Document

from gpt_researcher.document.document import (
    DocumentLoader,
    IMAGE_EXTENSIONS,
    load_image_as_documents,
)
from gpt_researcher.document.online_document import OnlineDocumentLoader


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
    b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
    b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.mark.parametrize("ext", sorted(IMAGE_EXTENSIONS))
def test_image_extensions_include_common_formats(ext):
    assert ext in IMAGE_EXTENSIONS


def test_png_loads_via_vision_fallback(tmp_path, monkeypatch):
    path = tmp_path / "IMG_3601.png"
    path.write_bytes(PNG_BYTES)

    async def fake_describe(file_path: str) -> str:
        assert Path(file_path).name == "IMG_3601.png"
        return "A research whiteboard with two uploaded project photos."

    monkeypatch.setattr(
        "gpt_researcher.document.document.describe_image_with_vision",
        fake_describe,
    )

    # Force the Unstructured path to fail so vision is used.
    class Boom:
        def __init__(self, *_a, **_k):
            raise RuntimeError("pdfminer missing")

    with patch(
        "langchain_community.document_loaders.UnstructuredImageLoader",
        Boom,
        create=True,
    ):
        docs = asyncio.run(DocumentLoader(str(tmp_path)).load())

    assert len(docs) == 1
    assert docs[0]["url"] == "IMG_3601.png"
    assert "whiteboard" in docs[0]["raw_content"]


def test_load_image_as_documents_returns_document(tmp_path, monkeypatch):
    path = tmp_path / "shot.jpg"
    path.write_bytes(PNG_BYTES)

    monkeypatch.setattr(
        "gpt_researcher.document.document.describe_image_with_vision",
        AsyncMock(return_value="Visible text: Hello"),
    )

    with patch(
        "langchain_community.document_loaders.UnstructuredImageLoader",
        side_effect=ImportError("no unstructured"),
        create=True,
    ):
        pages = asyncio.run(load_image_as_documents(str(path)))

    assert len(pages) == 1
    assert isinstance(pages[0], Document)
    assert pages[0].page_content == "Visible text: Hello"
    assert pages[0].metadata["source"] == str(path)


def test_online_loader_handles_image_extension(tmp_path, monkeypatch):
    path = tmp_path / "remote.webp"
    path.write_bytes(PNG_BYTES)

    monkeypatch.setattr(
        "gpt_researcher.document.document.describe_image_with_vision",
        AsyncMock(return_value="Remote poster"),
    )

    loader = OnlineDocumentLoader([])
    with patch(
        "langchain_community.document_loaders.UnstructuredImageLoader",
        side_effect=RuntimeError("skip ocr"),
        create=True,
    ):
        pages = asyncio.run(loader._load_document(str(path), "webp"))

    # Online loader deletes the temp file in finally.
    assert not path.exists()
    assert [p.page_content for p in pages] == ["Remote poster"]
