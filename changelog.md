# Changelog

All notable changes to Legion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Robust process locking mechanism using `fcntl` in orchestrator
- Graceful shutdown handling for both orchestrator and Discord bot
- Proper signal handling (SIGINT, SIGTERM) in Discord bot
- Comprehensive error handling and logging improvements
- Automatic maintenance tasks with graceful cancellation
- Message deduplication with periodic cleanup
- Better channel-to-agent mapping and message routing

### Changed
- Improved orchestrator initialization with proper error handling
- Enhanced Discord bot startup sequence
- More resilient agent message dispatch system
- Better resource cleanup on shutdown
- Standardized logging format and levels
- More efficient maintenance task scheduling

### Fixed
- Race conditions in orchestrator process management
- Resource leaks in file descriptor handling
- Stale PID file handling
- Message processing duplicates
- Channel mapping edge cases
- Unhandled exceptions in message processing

## [0.1.0] - 2024-04-20

### Added
- Initial release
- Basic Discord bot integration
- Simple agent system
- Basic orchestrator
- Channel-based message routing

## 2024-06-11
- Completed comprehensive architectural review of Legion system
- Identified need for improved modularity and dependency management
- Proposed reorganization of project structure:
  * Moving core utilities to legion/core
  * Consolidating agent configurations
  * Standardizing API endpoints
- Added new tasks for dependency injection implementation
- Enhanced error handling and logging requirements
- Updated test coverage requirements
- Added documentation improvements to roadmap
- Created comprehensive system diagrams in docs/diagram.md:
  * System component diagram
  * Message flow diagram
  * Agent initialization flow
  * Memory management flow
  * Error handling flow
  * Deployment architecture
  * Data flow and state management diagram
  * Configuration management diagram
  * Testing architecture diagram
  * Security architecture diagram
  * Detailed deployment pipeline diagram
  * Function relationships diagram
  * Layer-specific details diagram
  * Agent message processing logic
  * Memory management logic
  * Error recovery logic
  * Agent collaboration logic
  * System health check logic
- Reorganized diagram.md with improved structure:
  * Added table of contents
  * Grouped diagrams by logical sections
  * Improved visual hierarchy
  * Enhanced readability with clear section headers
- Added new integration-focused diagrams:
  * Component Integration Map
  * Service Integration Flow
  * State Management Integration
  * Data Flow Integration
  * System Integration Points
- Added composite system integration diagram for end-to-end flow
- Added composite swimlane integration diagram with error paths and fallbacks
- Added a new section in docs/diagram.md explaining how to test Mermaid diagrams in Live Editor and quick syntax links

## 2024-06-10
- Ensured LLM API calls route to the correct `/v1/chat/completions` path by normalizing `OPENAI_API_BASE`
- Updated orchestrator to load agent configs from `legion/configs`
- Patched `scripts/test_lm_studio.py` to dynamically select endpoint
- Implemented ArchitectAgent log/metrics test support
- Added GitHub Actions CI for ArchitectAgent tests
- Implemented cross-agent collaboration tests

## 2024-06-09
- Fixed shebang and permissions for scripts
- Implemented DoctorAgent with health check logic
- Added PingAgent, EchoAgent, HealthcheckAgent stubs
- Completed Discord integration
- Implemented local LLM Studio integration
- Added MetricsAgent and TherapistAgent
- Implemented cross-agent collaboration tests

## 2024-06-13
- [18:00] Fixed YAML syntax in `legion/configs/doctor.yaml`, resolving orchestrator agent loading errors. Test suite: 64 passed, 1 skipped (LLM endpoint), 4 warnings. [diff:legion/configs/doctor.yaml lines 1–3]
- [2025-04-21 00:19] Fixed Go Developer agent tests: aligned struct fields, method signatures, and message struct with implementation. All tests pass. [diff:legion/agents/go/developer_test.go lines 1–158]

## 2024-06-14
- Discord bot now correctly returns agent responses to channels via orchestrator.dispatch_message. [diff:integration/discord/bot.py lines 166–200]
- Discord integration and command handling are covered by 10 async tests (integration/discord/test_discord_integration.py, test_commands.py).
- 5/10 Discord tests fail if orchestrator is running due to PID file lock (ProcessRunningError/SystemExit). This blocks CI for concurrent orchestrator/test runs. [diff:tests/discord/test_discord_integration.py lines 1–264]
- Test coverage includes: slash command parsing, config update, state query, feedback, alert subscribe, message event flow, and error handling. [diff:tests/discord/test_commands.py lines 1–123]
- To pass all tests, ensure no orchestrator process is running before test execution. 