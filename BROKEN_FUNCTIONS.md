# Unimplemented or Placeholder Functions

The following functions currently contain placeholder implementations or TODO comments and require further work.

| File | Function | Notes |
| --- | --- | --- |
| legion/pipeline/BaseAgent.py | validate_payload | Abstract method raising `NotImplementedError`. |
| legion/pipeline/BaseAgent.py | perform_task | Abstract method raising `NotImplementedError`. |
| legion/pipeline/BaseAgent.py | build_response | Abstract method raising `NotImplementedError`. |
| legion/orchestrator.py | get_task_details | Returns dummy data; needs state manager integration. |
| legion/orchestrator.py | get_task_list | Returns dummy data; needs state manager integration. |
| legion/orchestrator.py | request_task_cancellation | Always returns `True`; should update state and signal workers. |
| legion/orchestrator.py | start_agent | Missing process creation and state update. |
| legion/orchestrator.py | stop_agent | Missing process shutdown and state update. |
| legion/orchestrator.py | restart_agent | Uses stub stop/start logic only. |
| legion/orchestrator.py | send_to_therapist | No routing implemented. |
| legion/orchestrator.py | receive_from_therapist | No dispatch pipeline integration. |
| legion/orchestrator.py | agent_comm_router | Dispatch rules not implemented. |
| legion/orchestrator.py | call_directive | Directive registry hookup pending. |
| legion/agents/python/metrics.py | collect_metrics | Stub; should gather runtime metrics. |
| legion/agents/python/metrics.py | analyze_metrics | Stub; should compute trends. |
| legion/agents/python/metrics.py | report_metrics | Stub; should publish metrics. |
| legion/pipeline/Middleware.py | authenticate | Placeholder auth rules. |
| legion/pipeline/Middleware.py | rate_limit | Rate limit store not integrated. |
| legion/pipeline/DiscordAdapter.py | send_message | Uses print statement instead of real Discord client. |
| legion/pipeline/TherapistAgent.py | validate | Needs full therapist validation logic. |
| middleware/src/middleware/context_manager.py | attach_core_directives | Context enrichment not implemented. |
| middleware/src/middleware/context_manager.py | log_interaction | Should persist interactions to state store. |
| middleware/src/main.py | orchestrate | Forwards to orchestrator; needs directive handling. |
| middleware/src/main.py | attach_context | Context extraction and logging TODO. |
