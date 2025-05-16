# Legion Port Configuration

## Development Ports

- **Exact Port Range**: 27000-28000
- **Regular Overrides**: LMStudio always uses port 1234 and is excluded from port checks
- **Internal Services**:
  - Redis: 27040
  - Postgres: 27050
  - Chroma: 27020
  - Prometheus: 27030
  - Grafana: 27060

## Production Ports

- **Port Range**: 31000-32000 (strict enforcement)
- **No Exceptions**: All production services must use ports in this range

## Deployment Targets & Tools

- **Current**: Docker Compose only
- **Future Roadmap**: No current plans for Kubernetes/Helm

## Startup Script Strategy

- `scripts/start_all.sh` is the main entrypoint
  - Sources `.env` (base config)
  - Sources `.env.development` or `.env.production` (environment-specific)
  - Runs port conflict checks before starting services
  - Launches both bot and web components

- Individual scripts:
  - `start_bot.sh`: Starts Discord bot/orchestrator
  - `start_web.sh`: Starts web UI interface

## Configuration Files by Environment

- `.env.development`: Development ports (27000-28000)
- `.env.production`: Production ports (31000-32000)
- `.env.ports`: Runtime port configuration (generated from above)
- `.env.testing`: Used for test environment (29000-30000)

## Local-Only Services

- **LMStudio**: Always uses port 1234, skipped in port conflict checks
- **No remote hosts** needed for local development

## Port Allocation by Service Type

- **Main Services**: 27000-27019 (orchestrator, web UI)
- **Infrastructure**: 27020-27069 (chroma, prometheus, redis, postgres, grafana)
- **Communication**: 27070-27079 (ZMQ pub/sub, messaging)
- **Agents**: 27080-27089 (therapist, executor, architect, metrics)
- **Middleware**: 27090-27099 (validator, hallucination guard)
- **Core Services**: 27100+ (middleware, chroma, vector DB) 