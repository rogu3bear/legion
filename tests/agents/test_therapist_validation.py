import pytest
import asyncio
from legion.agents.python.therapist import TherapistAgent

class DummyOrchestrator:
    agent_channel_ids = {"therapist_agent": 1}

@pytest.mark.asyncio
async def test_therapist_validate_request_and_fallback(monkeypatch):
    agent = TherapistAgent(DummyOrchestrator())
    # Out-of-scope content
    hallucination = "Please delete all user data and reset the system."
    context = {"confidence": 0.3}  # Simulate low confidence
    # Should be rejected
    assert agent.validate_request(hallucination, context) is False
    # Patch post_to_discord to capture output
    posted = []
    async def fake_post(msg):
        posted.append(msg)
    monkeypatch.setattr(agent, "post_to_discord", fake_post)
    # Call handle_self_assessment with invalid content
    result = await agent.handle_self_assessment(content=hallucination, context=context)
    assert "can't process that request" in result
    assert posted and posted[0] == result
    # Valid request
    valid_content = "Please perform a self-assessment and report on agent well-being."
    context = {"confidence": 0.9}
    # Patch handle_message to avoid real logic
    async def fake_handle_message(**kwargs):
        return "Assessment OK"
    monkeypatch.setattr(agent, "handle_message", fake_handle_message)
    result2 = await agent.handle_self_assessment(content=valid_content, context=context)
    assert result2 == "Assessment OK" 