<!-- File: docs/architecture/ports.md -->

# Legion Port Map

The following ports are reserved for Legion services. Values are fixed and
should remain within **7601-7810**. See `legion/ports.py` for the source of
truth.

| Service            | Port |
|--------------------|------|
| UI Backend         | 7801 |
| UI Frontend        | 7802 |
| Orchestrator REST  | 7803 |
| Interface API      | 7804 |
| Middleware         | 7805 |
| Metrics            | 7606 |
| Researcher API     | 7807 |
| ZMQ PUB            | 7808 |
| ZMQ SUB            | 7809 |
| Redis              | 7810 |
