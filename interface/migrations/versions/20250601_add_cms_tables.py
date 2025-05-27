"""add cms tables"""

from alembic import op
import sqlalchemy as sa

revision = "20250601_cms_tables"
down_revision = "20250521_conversation_directive"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "page_contents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("meta_title", sa.String(length=70), nullable=True),
        sa.Column("meta_description", sa.String(length=160), nullable=True),
        sa.Column("canonical_url", sa.String(), nullable=True),
        sa.Column("og_image_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("path"),
    )
    op.create_table(
        "page_content_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page_id", sa.Integer(), sa.ForeignKey("page_contents.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("meta_title", sa.String(length=70), nullable=True),
        sa.Column("meta_description", sa.String(length=160), nullable=True),
        sa.Column("canonical_url", sa.String(), nullable=True),
        sa.Column("og_image_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_page_content_revisions_page_id", "page_content_revisions", ["page_id"])

    op.create_table(
        "blog_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("meta_title", sa.String(length=70), nullable=True),
        sa.Column("meta_description", sa.String(length=160), nullable=True),
        sa.Column("canonical_url", sa.String(), nullable=True),
        sa.Column("og_image_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "blog_post_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("blog_posts.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("meta_title", sa.String(length=70), nullable=True),
        sa.Column("meta_description", sa.String(length=160), nullable=True),
        sa.Column("canonical_url", sa.String(), nullable=True),
        sa.Column("og_image_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_blog_post_revisions_post_id", "blog_post_revisions", ["post_id"])


def downgrade() -> None:
    op.drop_index("ix_blog_post_revisions_post_id", table_name="blog_post_revisions")
    op.drop_table("blog_post_revisions")
    op.drop_table("blog_posts")
    op.drop_index("ix_page_content_revisions_page_id", table_name="page_content_revisions")
    op.drop_table("page_content_revisions")
    op.drop_table("page_contents")
