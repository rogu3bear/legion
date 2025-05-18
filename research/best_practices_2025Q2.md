# Best Practices 2025 Q2

## Redis Streams vs PostgreSQL LISTEN/NOTIFY
- Redis Streams offer scalable fan-out and persistence [[1](https://redis.io/docs/latest/develop/data-types/streams/)].
- PostgreSQL LISTEN/NOTIFY is simple but lacks durability [[2](https://www.postgresql.org/docs/current/sql-notify.html)].

## Async Worker Pools
- Celery 6 adds async `TaskPool` for Python 3.11 [[3](https://docs.celeryq.dev/en/stable/whatsnew-6.0.html)].
- Dramatiq provides minimalistic async workers [[4](https://dramatiq.io/guide/)].
- Native `asyncio.create_task` best for lightweight jobs [[5](https://docs.python.org/3/library/asyncio-task.html)].

## Vite 5 Bundling
- Code-splitting with import maps reduces bundle size [[6](https://vitejs.dev/guide/features.html)].

## OpenTelemetry
- Standardized tracing across services [[7](https://opentelemetry.io/docs/instrumentation/python/)].
