# Legacy Docker Artifacts

**Date Archived**: 2025-05-27 (M27.6 Sync)  
**Reason**: Docker removal mandate - "NO DOCKER ALLOWED - GET RID OF IT ALL"

## Archived Files

- `Dockerfile` - Multi-stage Python build with Legion dependencies
- `docker-compose.yml` - Main service orchestration
- `docker-compose.override.dev.yml` - Development overrides

## Migration Path

Docker functionality has been replaced with:

- **Development**: `scripts/dev_start.sh` (native Redis + FastAPI + React)
- **CI**: Native GitHub Actions with `redis-server` installation
- **Port Management**: Unified through `.env.ports` with legacy shims

## Restoration

If Docker support needs to be restored:

1. Move files back to project root
2. Update port references to use `.env.ports` variables
3. Re-enable `.github/workflows/base-image.yml`
4. Update `scripts/dev_start.sh` to support Docker mode

**Note**: These files are preserved for reference but should not be used in current development. 