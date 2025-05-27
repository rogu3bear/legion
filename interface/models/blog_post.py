from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from interface.db.base import Base


class BlogPost(Base):
    """Blog post entry."""

    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    meta_title = Column(String(70), nullable=True)
    meta_description = Column(String(160), nullable=True)
    canonical_url = Column(String, nullable=True)
    og_image_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BlogPostRevision(Base):
    """Historical revision for BlogPost."""

    __tablename__ = "blog_post_revisions"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("blog_posts.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    meta_title = Column(String(70), nullable=True)
    meta_description = Column(String(160), nullable=True)
    canonical_url = Column(String, nullable=True)
    og_image_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
