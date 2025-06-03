from agents.metrics.handler import MetricsAgent


def test_metrics_stub():
    agent = MetricsAgent()
    assert isinstance(agent.collect(), dict)
