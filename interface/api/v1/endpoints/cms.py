from __future__ import annotations

import difflib
import logging
import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from interface import dependencies
from interface.models.blog_post import BlogPost, BlogPostRevision
from interface.models.page_content import PageContent, PageContentRevision
from interface.models.user import User
from interface.schemas.cms import (
    BlogPost as BlogPostSchema,
    BlogPostCreate,
    BlogPostRevision as BlogPostRevisionSchema,
    BlogPostUpdate,
    Page as PageSchema,
    PageCreate,
    PageRevision as PageRevisionSchema,
    PageUpdate,
    RevisionDiff,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Helper to store revision

def _create_page_revision(db: Session, page: PageContent) -> None:
    rev = PageContentRevision(
        page_id=page.id,
        title=page.title,
        body=page.body,
        meta_title=page.meta_title,
        meta_description=page.meta_description,
        canonical_url=page.canonical_url,
        og_image_id=page.og_image_id,
    )
    db.add(rev)


def _create_post_revision(db: Session, post: BlogPost) -> None:
    rev = BlogPostRevision(
        post_id=post.id,
        title=post.title,
        content=post.content,
        meta_title=post.meta_title,
        meta_description=post.meta_description,
        canonical_url=post.canonical_url,
        og_image_id=post.og_image_id,
    )
    db.add(rev)


@router.post("/pages", response_model=PageSchema, status_code=status.HTTP_201_CREATED)
def create_page(
    payload: PageCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> PageSchema:
    page = PageContent(**payload.dict())
    db.add(page)
    db.commit()
    db.refresh(page)
    return PageSchema.from_orm(page)


@router.get("/pages/{page_id}", response_model=PageSchema)
def get_page(
    page_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> PageSchema:
    page = db.get(PageContent, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageSchema.from_orm(page)


@router.put("/pages/{page_id}", response_model=PageSchema)
def update_page(
    page_id: int,
    payload: PageUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> PageSchema:
    page = db.get(PageContent, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    _create_page_revision(db, page)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(page, field, value)
    db.add(page)
    db.commit()
    db.refresh(page)
    return PageSchema.from_orm(page)


@router.get("/pages/{page_id}/revisions", response_model=List[PageRevisionSchema])
def list_page_revisions(
    page_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> List[PageRevisionSchema]:
    revisions = (
        db.query(PageContentRevision)
        .filter(PageContentRevision.page_id == page_id)
        .order_by(PageContentRevision.created_at.desc())
        .all()
    )
    return [PageRevisionSchema.from_orm(r) for r in revisions]


@router.get(
    "/pages/{page_id}/revisions/{rev_id}/compare_with/{other_id}",
    response_model=RevisionDiff,
)
def compare_page_revisions(
    page_id: int,
    rev_id: int,
    other_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> RevisionDiff:
    rev_a = db.get(PageContentRevision, rev_id)
    rev_b = db.get(PageContentRevision, other_id)
    if not rev_a or not rev_b or rev_a.page_id != page_id or rev_b.page_id != page_id:
        raise HTTPException(status_code=404, detail="Revision not found")
    diff = "\n".join(
        difflib.unified_diff(
            rev_a.body.splitlines(), rev_b.body.splitlines(), lineterm=""
        )
    )
    return RevisionDiff(base=rev_id, compare=other_id, diff=diff)


@router.get("/pages/{page_id}/analyze")
def analyze_page(
    page_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    page = db.get(PageContent, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    word_count = len(page.body.split())
    sections = [h.strip() for h in re.findall(r"^#+\\s+.*$", page.body, re.MULTILINE)]
    # TODO: implement real link validation
    broken_links = [
        url
        for url in re.findall(r"\[[^\]]*\]\(([^)]+)\)", page.body)
        if not url.startswith("http")
    ]
    return {
        "word_count": word_count,
        "sections": sections,
        "broken_links": broken_links,
        "tag_quality": "todo",
    }


@router.post("/posts", response_model=BlogPostSchema, status_code=status.HTTP_201_CREATED)
def create_blog_post(
    payload: BlogPostCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> BlogPostSchema:
    post = BlogPost(**payload.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return BlogPostSchema.from_orm(post)


@router.get("/posts/{post_id}", response_model=BlogPostSchema)
def get_blog_post(
    post_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> BlogPostSchema:
    post = db.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return BlogPostSchema.from_orm(post)


@router.put("/posts/{post_id}", response_model=BlogPostSchema)
def update_blog_post(
    post_id: int,
    payload: BlogPostUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> BlogPostSchema:
    post = db.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    _create_post_revision(db, post)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(post, field, value)
    db.add(post)
    db.commit()
    db.refresh(post)
    return BlogPostSchema.from_orm(post)


@router.get("/posts/{post_id}/revisions", response_model=List[BlogPostRevisionSchema])
def list_post_revisions(
    post_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> List[BlogPostRevisionSchema]:
    revisions = (
        db.query(BlogPostRevision)
        .filter(BlogPostRevision.post_id == post_id)
        .order_by(BlogPostRevision.created_at.desc())
        .all()
    )
    return [BlogPostRevisionSchema.from_orm(r) for r in revisions]


@router.get(
    "/posts/{post_id}/revisions/{rev_id}/compare_with/{other_id}",
    response_model=RevisionDiff,
)
def compare_post_revisions(
    post_id: int,
    rev_id: int,
    other_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> RevisionDiff:
    rev_a = db.get(BlogPostRevision, rev_id)
    rev_b = db.get(BlogPostRevision, other_id)
    if not rev_a or not rev_b or rev_a.post_id != post_id or rev_b.post_id != post_id:
        raise HTTPException(status_code=404, detail="Revision not found")
    diff = "\n".join(
        difflib.unified_diff(
            rev_a.content.splitlines(), rev_b.content.splitlines(), lineterm=""
        )
    )
    return RevisionDiff(base=rev_id, compare=other_id, diff=diff)


@router.get("/posts/{post_id}/analyze")
def analyze_post(
    post_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    post = db.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    word_count = len(post.content.split())
    sections = [h.strip() for h in re.findall(r"^#+\s+.*$", post.content, re.MULTILINE)]
    # TODO: implement real link validation
    broken_links = [
        url
        for url in re.findall(r"\[[^\]]*\]\(([^)]+)\)", post.content)
        if not url.startswith("http")
    ]
    return {
        "word_count": word_count,
        "sections": sections,
        "broken_links": broken_links,
        "tag_quality": "todo",
    }
