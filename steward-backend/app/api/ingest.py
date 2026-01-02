import os
import shutil
import zipfile
import uuid
import tempfile
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.ingest import ingest_codebase

router = APIRouter()


def _safe_extract_zip(zip_path: str, extract_to: str) -> None:
    """Prevent zip-slip attacks."""
    with zipfile.ZipFile(zip_path) as z:
        for member in z.namelist():
            target_path = os.path.abspath(os.path.join(extract_to, member))
            if not target_path.startswith(os.path.abspath(extract_to)):
                raise HTTPException(status_code=400, detail="Invalid zip file structure")
        z.extractall(extract_to)


@router.post("/")
async def ingest(
    zip_file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
):
    """
    Ingest endpoint.
    Exactly one of: zip_file OR files must be provided.
    """

    if (zip_file is None and not files) or (zip_file and files):
        raise HTTPException(
            status_code=400,
            detail="Provide either a zip_file or a list of files (not both).",
        )

    session_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory(prefix=f"steward_{session_id}_") as tmpdir:

        # -------- ZIP UPLOAD --------
        if zip_file:
            if not zip_file.filename.endswith(".zip"):
                raise HTTPException(status_code=400, detail="Only .zip files are allowed")

            zip_path = os.path.join(tmpdir, zip_file.filename)
            with open(zip_path, "wb") as f:
                f.write(await zip_file.read())

            try:
                _safe_extract_zip(zip_path, tmpdir)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        # -------- FILE PICKER --------
        else:
            for uploaded in files:
                dest = os.path.join(tmpdir, uploaded.filename)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as f:
                    f.write(await uploaded.read())

        # -------- INGEST --------
        try:
            summary = ingest_codebase(
                root_path=tmpdir,
                session_id=session_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return {
        "status": "ok",
        "session_id": session_id,
        "summary": summary,
    }
