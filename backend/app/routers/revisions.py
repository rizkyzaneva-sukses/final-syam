"""User-submitted revision proposals with optional screenshots."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from sqlalchemy.orm import Session, defer

from ..auth import get_current_user
from ..audit import log_audit
from ..database import get_db
from ..models import RevisionProposal, User

router = APIRouter(prefix="/revisions", tags=["revisions"])
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def image_mime(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def proposal_out(proposal: RevisionProposal, reporter_name: str) -> dict:
    return {
        "id": proposal.id,
        "module_name": proposal.module_name,
        "bug_description": proposal.bug_description,
        "expected_behavior": proposal.expected_behavior,
        "has_image": proposal.image_mime is not None,
        "reported_by_id": proposal.reported_by_id,
        "reported_by_name": reporter_name,
        "created_at": proposal.created_at.isoformat() + "Z",
    }


@router.get("")
def list_revisions(limit: int = Query(100, ge=1, le=200), offset: int = Query(0, ge=0),
                   db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (db.query(RevisionProposal, User.name)
            .options(defer(RevisionProposal.image_data))
            .join(User, User.id == RevisionProposal.reported_by_id)
            .order_by(RevisionProposal.id.desc()).offset(offset).limit(limit).all())
    return [proposal_out(proposal, name) for proposal, name in rows]


@router.post("", status_code=201)
async def create_revision(module_name: str = Form(...), bug_description: str = Form(...),
                          expected_behavior: str = Form(...), image: UploadFile | None = File(None),
                          db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    module_name = module_name.strip()
    bug_description = bug_description.strip()
    expected_behavior = expected_behavior.strip()
    if not module_name or len(module_name) > 120:
        raise HTTPException(422, "Modul wajib diisi (maksimal 120 karakter).")
    if not bug_description or len(bug_description) > 5000:
        raise HTTPException(422, "Bug wajib diisi (maksimal 5000 karakter).")
    if not expected_behavior or len(expected_behavior) > 5000:
        raise HTTPException(422, "Perilaku yang diharapkan wajib diisi (maksimal 5000 karakter).")

    data = None
    mime = None
    if image is not None:
        data = await image.read(MAX_IMAGE_BYTES + 1)
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(413, "Gambar maksimal 5 MB.")
        mime = image_mime(data)
        if mime is None:
            raise HTTPException(415, "Gunakan gambar PNG, JPG, atau WebP.")

    proposal = RevisionProposal(module_name=module_name, bug_description=bug_description,
                                expected_behavior=expected_behavior, image_data=data, image_mime=mime,
                                reported_by_id=user.id)
    db.add(proposal)
    db.flush()
    log_audit(db, user, "CREATE", "RevisionProposal", proposal.id, module_name)
    db.commit()
    db.refresh(proposal)
    return proposal_out(proposal, user.name)


@router.get("/{proposal_id}/image")
def get_revision_image(proposal_id: int, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    proposal = db.get(RevisionProposal, proposal_id)
    if proposal is None or proposal.image_data is None:
        raise HTTPException(404, "Gambar tidak ditemukan.")
    return Response(content=proposal.image_data, media_type=proposal.image_mime,
                    headers={"Content-Disposition": "inline"})
