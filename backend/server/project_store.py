"""Per-user research Projects (Perplexity-style folders with docs + instructions). :-)"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .auth_user import AuthUser, user_root


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^\w.\- ]+", "", name).strip()
    return cleaned[:120] or "document"


class ProjectStore:
    def __init__(self, data_root: Path):
        self._root = data_root
        self._lock = asyncio.Lock()

    def _user_dir(self, user: AuthUser) -> Path:
        path = Path(user_root(str(self._root), user))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _index_path(self, user: AuthUser) -> Path:
        return self._user_dir(user) / "projects.json"

    def _project_dir(self, user: AuthUser, project_id: str) -> Path:
        return self._user_dir(user) / "projects" / project_id

    def docs_dir(self, user: AuthUser, project_id: str) -> Path:
        path = self._project_dir(user, project_id) / "docs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def _read_index(self, user: AuthUser) -> Dict[str, Dict[str, Any]]:
        path = self._index_path(user)
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    async def _write_index(self, user: AuthUser, data: Dict[str, Dict[str, Any]]) -> None:
        path = self._index_path(user)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)

    def _public(self, project: Dict[str, Any], user: AuthUser) -> Dict[str, Any]:
        docs = []
        docs_path = self.docs_dir(user, project["id"])
        if docs_path.exists():
            docs = sorted(p.name for p in docs_path.iterdir() if p.is_file())
        return {
            **project,
            "documents": docs,
            "document_count": len(docs),
        }

    async def list_projects(self, user: AuthUser) -> List[Dict[str, Any]]:
        async with self._lock:
            data = await self._read_index(user)
            projects = [self._public(p, user) for p in data.values()]
            projects.sort(key=lambda p: p.get("updated_at", 0), reverse=True)
            return projects

    async def get_project(self, user: AuthUser, project_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            data = await self._read_index(user)
            project = data.get(project_id)
            return self._public(project, user) if project else None

    async def create_project(
        self,
        user: AuthUser,
        name: str,
        description: str = "",
        instructions: str = "",
    ) -> Dict[str, Any]:
        async with self._lock:
            data = await self._read_index(user)
            now = int(time.time() * 1000)
            project_id = f"proj_{uuid.uuid4().hex[:12]}"
            project = {
                "id": project_id,
                "name": (name or "Untitled project").strip()[:120],
                "description": (description or "").strip()[:2000],
                "instructions": (instructions or "").strip()[:8000],
                "owner_email": user.email,
                "created_at": now,
                "updated_at": now,
            }
            data[project_id] = project
            self.docs_dir(user, project_id)
            await self._write_index(user, data)
            return self._public(project, user)

    async def update_project(
        self,
        user: AuthUser,
        project_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        async with self._lock:
            data = await self._read_index(user)
            project = data.get(project_id)
            if not project:
                return None
            if name is not None:
                project["name"] = name.strip()[:120] or project["name"]
            if description is not None:
                project["description"] = description.strip()[:2000]
            if instructions is not None:
                project["instructions"] = instructions.strip()[:8000]
            project["updated_at"] = int(time.time() * 1000)
            data[project_id] = project
            await self._write_index(user, data)
            return self._public(project, user)

    async def delete_project(self, user: AuthUser, project_id: str) -> bool:
        async with self._lock:
            data = await self._read_index(user)
            if project_id not in data:
                return False
            del data[project_id]
            await self._write_index(user, data)
            shutil.rmtree(self._project_dir(user, project_id), ignore_errors=True)
            return True

    async def list_documents(self, user: AuthUser, project_id: str) -> Optional[List[str]]:
        project = await self.get_project(user, project_id)
        if not project:
            return None
        return project["documents"]

    async def save_document(self, user: AuthUser, project_id: str, filename: str, content: bytes) -> Optional[str]:
        project = await self.get_project(user, project_id)
        if not project:
            return None
        safe = _safe_name(filename)
        path = self.docs_dir(user, project_id) / safe
        path.write_bytes(content)
        async with self._lock:
            data = await self._read_index(user)
            if project_id in data:
                data[project_id]["updated_at"] = int(time.time() * 1000)
                await self._write_index(user, data)
        return safe

    async def delete_document(self, user: AuthUser, project_id: str, filename: str) -> bool:
        project = await self.get_project(user, project_id)
        if not project:
            return False
        path = self.docs_dir(user, project_id) / _safe_name(filename)
        if not path.exists() or not path.is_file():
            return False
        path.unlink()
        return True
