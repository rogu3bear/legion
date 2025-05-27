from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PageBase(BaseModel):
    path: str
    title: str
    body: str
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    og_image_id: Optional[str] = Field(None, description="UUID of OG image asset")


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    og_image_id: Optional[str] = None


class Page(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class PageRevision(PageBase):
    id: int
    page_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class BlogPostBase(BaseModel):
    slug: str
    title: str
    content: str
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    og_image_id: Optional[str] = None


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    og_image_id: Optional[str] = None


class BlogPost(BlogPostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class BlogPostRevision(BlogPostBase):
    id: int
    post_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class RevisionDiff(BaseModel):
    base: int
    compare: int
    diff: str
