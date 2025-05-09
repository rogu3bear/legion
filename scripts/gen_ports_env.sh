#!/usr/bin/env bash
# Generate PORT_ALLOCATOR_<SERVICE> env variables for docker-compose
python3 - <<'PY'
from core.utils.ports import PortAllocator
pa = PortAllocator(base=5500, cluster_size=100)
services = ["orchestrator", "redis", "postgres", "prometheus", "grafana"]
for svc in services:
    port = pa.get_free_port(svc)
    up = svc.upper()
    print(f"export PORT_ALLOCATOR_{up}={port}")
PY
