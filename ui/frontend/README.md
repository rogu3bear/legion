# Legion Frontend UI

<!-- reviewme: This was a generic Vite template README - updated to reflect Legion context -->

React + Vite frontend for the Legion agent orchestration system.

## Overview

This is the frontend component of Legion's web interface, providing:
- Agent management interface
- Real-time system monitoring
- Task management dashboard
- Configuration management

## Development Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Integration

The frontend integrates with Legion's FastAPI backend at `interface/main.py` and communicates via:
- REST API endpoints (`/api/v1/`)
- WebSocket connections for real-time updates
- Authentication system

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **ESLint** - Code linting
- **Tailwind CSS** - Styling (if configured)

For the complete Legion web interface documentation, see [docs/webui.md](../../docs/webui.md).
