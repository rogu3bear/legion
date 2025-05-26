# Legion Port Map

<!-- reviewme: Previous port documentation was completely outdated (fixed 7801-7810 range no longer used) -->

Legion uses dynamic port allocation based on deployment environment. The port allocation follows these patterns:

## Environment-Based Port Ranges

### Development Profile (`.env.development`)
- **Port Range**: 27000-27999
- **Pattern**: `PORT_ALLOCATOR_<SERVICE>=<port>`

### Production Profile (`.env.production`)
- **Port Range**: 31000-31999
- **Pattern**: `PORT_ALLOCATOR_<SERVICE>=<port>`

### Staging Profile (`.env`)
- **Port Range**: Dynamic allocation
- **Pattern**: `PORT_ALLOCATOR_<SERVICE>=<port>`

## Key Services Port Allocation

| Service | Environment Variable | Dev Default | Production Default |
|---------|---------------------|-------------|-------------------|
| Orchestrator | PORT_ALLOCATOR_ORCHESTRATOR | 27000 | 31000 |
| Web UI | PORT_ALLOCATOR_WEB_UI | 27001 | 31001 |
| ChromaDB | PORT_ALLOCATOR_CHROMA | 27020 | 31020 |
| Prometheus | PORT_ALLOCATOR_PROMETHEUS | 27030 | 31030 |
| Redis | PORT_ALLOCATOR_REDIS | 27040 | 31040 |
| PostgreSQL | PORT_ALLOCATOR_POSTGRES | 27050 | 31050 |
| Grafana | PORT_ALLOCATOR_GRAFANA | 27060 | 31060 |

## ZeroMQ Services

| Service | Environment Variable | Dev Default | Production Default |
|---------|---------------------|-------------|-------------------|
| ZMQ PUB | PORT_ALLOCATOR_ORCHESTRATOR_ZMQ_PUB | 27070 | 31070 |
| ZMQ REP | PORT_ALLOCATOR_ORCHESTRATOR_ZMQ_REP | 27071 | 31071 |

## Agent Services

| Service | Environment Variable | Dev Default | Production Default |
|---------|---------------------|-------------|-------------------|
| Therapist | PORT_ALLOCATOR_AGENTS_THERAPIST | 27080 | 31080 |
| Executor | PORT_ALLOCATOR_AGENTS_EXECUTOR | 27081 | 31081 |
| Architect | PORT_ALLOCATOR_AGENTS_ARCHITECT | 27082 | 31082 |
| Metrics | PORT_ALLOCATOR_AGENTS_METRICS | 27083 | 31083 |

## Middleware Services

| Service | Environment Variable | Dev Default | Production Default |
|---------|---------------------|-------------|-------------------|
| Validator | PORT_ALLOCATOR_MIDDLEWARE_VALIDATOR | 27090 | 31090 |
| Hallucination Guard | PORT_ALLOCATOR_MIDDLEWARE_HALLUCINATION_GUARD | 27091 | 31091 |

## Configuration Files

- **Development**: `.env.development`
- **Production**: `.env.production`
- **Staging**: `.env` (main environment file)

See the individual environment files for the complete port allocation configuration.
