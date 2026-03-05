from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from core.security import get_current_user
from models.user import User
from models.autoreply import AutoReply
from schemas.autoreply import AutoReplyCreate, AutoReplyUpdate, AutoReplyResponse

router = APIRouter()


@router.post("/autoreplies", response_model=AutoReplyResponse, status_code=201)
async def create_autoreply(
    data: AutoReplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check for duplicate keyword
    existing = db.query(AutoReply).filter(
        AutoReply.user_id == current_user.id,
        AutoReply.keyword == data.keyword.lower()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Keyword already exists")

    reply = AutoReply(
        user_id=current_user.id,
        keyword=data.keyword.lower(),
        response=data.response
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


@router.get("/autoreplies", response_model=List[AutoReplyResponse])
async def list_autoreplies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(AutoReply).filter(AutoReply.user_id == current_user.id).all()


@router.put("/autoreplies/{reply_id}", response_model=AutoReplyResponse)
async def update_autoreply(
    reply_id: int,
    updates: AutoReplyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reply = db.query(AutoReply).filter(
        AutoReply.id == reply_id, AutoReply.user_id == current_user.id
    ).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Auto-reply not found")

    if updates.keyword:
        reply.keyword = updates.keyword.lower()
    if updates.response:
        reply.response = updates.response

    db.commit()
    db.refresh(reply)
    return reply


@router.delete("/autoreplies/{reply_id}", status_code=204)
async def delete_autoreply(
    reply_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reply = db.query(AutoReply).filter(
        AutoReply.id == reply_id, AutoReply.user_id == current_user.id
    ).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Auto-reply not found")
    db.delete(reply)
    db.commit()
