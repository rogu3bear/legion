📄 agents.md — Authoritative Ledger (v M28.1)

Purpose – Single-source reference for every Legion agent, their scope, channel, and system touch-points.
Owner – Orchestrator & Echo; edited only through PRs tagged [M-agents].
ID	Agent	Discord Channel	Priority	Scope & Skills	Key Endpoints / Ports	Notes
00	Orchestrator	#operations 1372374906007720006	🔴 Critical	Task delegation, state repo, error routing, queue mgmt	REST /orchestrator/* → 7603	Reads Echo Nexus™ mirror
01	Echo	#agent-feed 1362902052279291904	🔴 Critical	Full log index, search/filter UI, feed to Therapist	Ingest /echo/ingest → 7605
Query /echo/logs → 7605	Echo Nexus™ = primary DB
02	Therapist	#therapist 1363185156759752865	🔴 Critical	Pre-exec validation, agent “health”, escalation checks	gRPC /therapist/validate → 7605	Absorbed Healthcheck
03	Middleware	N/A (internal)	🔴 Critical	Discord event listener, routing, tagging, LLM router	WS bridge → 7605	Writes to Echo & Orchestrator
04	Metrics	#metrics 1363185079173513358	🟠 High	Usage stats, cost & latency reporting	REST /metrics/* → 7606	Consumes Echo logs
05	UX Designer	#ui-ux <TBD>	🟡 Medium	UI component hints, CSS adjustments	—	Reads UI telemetry
06	Ping	#test 1362899585726418988	🟡 Medium	Simple heartbeat / keep-alive	REST /ping → 7604	
07	Researcher	#research 1372375150841954446	🟡 Medium	External data fetch, summarization	REST /research/* → 7607	
08	Architect (de-prioritized)	#architect 1363184898470445256	⚪ Low	Future infra planning	—	Dormant
09	Interface API	N/A (internal)	🔴 Critical	External SDK surface for agents	REST /interface/* → 7604	Consumes Orchestrator
10	ZMQ PUB	N/A	⚙ infra	Internal pub socket	7608	
11	ZMQ SUB	N/A	⚙ infra	Internal sub socket	7609	
12	Redis	N/A	⚙ infra	Global cache & queue	7600	Local-only
Tagging standard

[tag.project]  legion
[tag.intent]   orchestrate | log | validate | metric | ui | research
[tag.urgency]  p0..p3
[tag.origin]   user | agent | system
Message life-cycle

Discord ► Middleware ► Echo ingest
Middleware tags + routes ► Orchestrator
Orchestrator delegates ► Agent
Agent reply ► Discord + Echo ingest
Metrics pulls Echo logs for cost/latency