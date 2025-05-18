# Security Policy

All secrets must be stored in environment variables or secret managers. `.env` files are excluded from version control via `.gitignore`.

Developers should:
- Never commit real credentials.
- Use `.env.ports` for local port settings.
- Rotate credentials regularly.
- Report security issues to the maintainers.
