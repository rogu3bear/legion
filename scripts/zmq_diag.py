#!/usr/bin/env python3
"""Simple subscriber to verify orchestrator ZMQ PUB broadcasts."""

import time

import zmq


def run_zmq_diag(pub_port: str = "7808", duration: int = 15) -> None:
    """Listen to PUB socket on given port and print messages for duration."""
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.setsockopt_string(zmq.SUBSCRIBE, "")
    connect_addr = f"tcp://127.0.0.1:{pub_port}"
    sub.connect(connect_addr)

    print(f"Connected to {connect_addr}. Listening for {duration} seconds...")
    start = time.monotonic()
    try:
        while time.monotonic() - start < duration:
            if sub.poll(500):  # wait up to 0.5 sec for message
                try:
                    msg = sub.recv_string(flags=zmq.NOBLOCK)
                    ts = time.strftime("%H:%M:%S")
                    print(f"[{ts}] {msg}")
                except zmq.Again:
                    pass
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        sub.close()
        context.term()
        print("ZMQ diagnostic finished.")


if __name__ == "__main__":
    run_zmq_diag()
