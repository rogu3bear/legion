#!/usr/bin/env python3
"""
Unit tests for PortAllocator: idempotency, collision avoidance, cluster overflow.
"""

import pytest

from core.utils.ports import PortAllocator, PortRangeExhausted


def test_idempotency() -> None:
    pa1 = PortAllocator(base=5500, cluster_size=100)
    keys = ["a", "b", "c"]
    first = {k: pa1.get_free_port(k) for k in keys}
    pa2 = PortAllocator(base=5500, cluster_size=100)
    second = {k: pa2.get_free_port(k) for k in keys}
    assert first == second


def test_collision_avoidance_and_range() -> None:
    pa = PortAllocator(base=5500, cluster_size=100)
    keys = [f"svc{i}" for i in range(100)]
    ports = [pa.get_free_port(k) for k in keys]
    assert len(set(ports)) == 100
    for port in ports:
        assert 5500 <= port < 5600


def test_cluster_overflow() -> None:
    pa = PortAllocator(base=5500, cluster_size=100)
    for i in range(100):
        pa.get_free_port(f"key{i}")
    with pytest.raises(PortRangeExhausted):
        pa.get_free_port("overflow")
