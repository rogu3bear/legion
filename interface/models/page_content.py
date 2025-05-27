from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from interface.db.base import Base


class PageContent(Base):
    """Web page content managed via the CMS."""

    __tablename__ = "page_contents"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    meta_title = Column(String(70), nullable=True)
    meta_description = Column(String(160), nullable=True)
    canonical_url = Column(String, nullable=True)
    og_image_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PageContentRevision(Base):
    """Historical revision for PageContent."""

    __tablename__ = "page_content_revisions"

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("page_contents.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    meta_title = Column(String(70), nullable=True)
    meta_description = Column(String(160), nullable=True)
    canonical_url = Column(String, nullable=True)
    og_image_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
