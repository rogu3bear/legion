from scripts import migrate_redis_tags as migrate


def test_migrate_adds_fields():
    client = migrate.FakeRedis()
    client.set('task:1', '{"foo":"bar"}')
    migrate.migrate(client)
    data = client.get('task:1')
    assert 'tag_context' in data
    assert 'task_owner' in data
