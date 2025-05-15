#!/usr/bin/env bash
# Generate .env.ports with PORT_ALLOCATOR_<SERVICE>=<port>
python3 - << 'PY' > .env.ports
from core.utils.ports import PortAllocator
pa = PortAllocator(base=5500, cluster_size=100)
services = ["orchestrator", "redis", "postgres", "prometheus", "grafana", "dev_frontend", "chroma"]
for svc in services:
    port = pa.get_free_port(svc)
    up = svc.upper()
    print(f"PORT_ALLOCATOR_{up}={port}")
PY
