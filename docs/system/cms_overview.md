# CMS Overview

This document outlines the lightweight content management system used by Legion.

## Models
- **PageContent**: basic page entry with title, body, and SEO metadata.
- **BlogPost**: simple blog entry with slug and body.
- **Revision tables** track every update for audit purposes.

## Endpoints
- `GET /api/v1/cms/pages/{id}/revisions` – list revisions
- `GET /api/v1/cms/pages/{id}/revisions/{rev}/compare_with/{other}` – diff output
- `GET /api/v1/cms/pages/{id}/analyze` – compute word count and detect broken links
- Equivalent routes exist for blog posts.

Revisions are written automatically whenever a page or post is updated.
