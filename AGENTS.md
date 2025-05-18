# AGENTS.md

## 0. Purpose & Reading Guide

This file defines and distinguishes Codex internal agents from Legion operational agents. It prevents confusion, enforces boundaries, and steers Codex's behaviour.

- [0. Purpose & Reading Guide](#0-purpose--reading-guide)
- [1. Codex Internal Agents](#1-codex-internal-agents)
- [2. Legion External Operational Agents](#2-legion-external-operational-agents)
- [3. Naming & Directory Conventions](#3-naming--directory-conventions)
- [4. Code Style & Lint Rules](#4-code-style--lint-rules)
- [5. Testing & Validation](#5-testing--validation)
- [6. Pull-Request (PR) Guidelines](#6-pull-request-pr-guidelines)
- [7. Multi-AGENTS.md Precedence](#7-multi-agentsmd-precedence)
- [8. Safety & Prohibited Actions](#8-safety--prohibited-actions)

## 1. Codex Internal Agents

Codex agents are internal automation scripts. They are not Legion operational agents and must never interact with Legion's runtime directly.

| Name                | Purpose                        | Permissions                | Hard Limits                       |
|---------------------|-------------------------------|----------------------------|-----------------------------------|
| CodexAgent-Scaffold | Generate stubs, boilerplate   | Read/write in repo         | - No direct writes outside repo   |
| CodexAgent-Refactor | Refactor code, enforce style  | Read/write in repo         | - Never call external APIs unless stubbed |
| CodexAgent-Test     | Run and validate tests        | Read, run tests            | - No network calls                |

- Hard limits:

  - No direct writes outside the repo
  - Never call external APIs unless stubbed
  - No network calls unless explicitly whitelisted (none by default)
  - No destructive operations (e.g., `rm -rf /`)

## 1.1 Roles

- Scaffold: Create new files, stubs, and structure
- Refactor: Enforce code style, rename, move, or clean code
- Test: Run, validate, and report on test suites

## 1.2 Permissions & Guard-rails

- Must respect .gitignore and .env
- May not alter Legion agent configs or runtime state
- All changes must be reviewable via PR

## 2. Legion External Operational Agents

Legion agents are runtime personas managed by the orchestrator. Codex must not manage, mutate, or impersonate these agents.

| Name           | Purpose                        | Permissions         | Boundaries                       |
|----------------|-------------------------------|---------------------|----------------------------------|
| Architect      | Code review, architecture      | Read logs, suggest  | No code writes, read-only logs   |
| Therapist      | Agent well-being, support      | Read logs           | No code writes, read-only logs   |
| Metrics        | Collect/analyze metrics        | Read logs           | No code writes, read-only logs   |
| UX Designer    | UX critique, suggestions       | Read logs           | No code writes, read-only logs   |
| Ping           | Health check, connectivity     | None                | No code writes                   |
| Echo           | Diagnostic echo                | None                | No code writes                   |
| Healthcheck    | System health, uptime          | Read logs           | No code writes, read-only logs   |
| Developer (Go) | Code tasks, review, debug      | Read logs           | No code writes, read-only logs   |

### 2.1 Roles

- Each agent has a single, well-defined persona and task domain.

### 2.2 Interaction Boundaries

- Legion agents may only interact via orchestrator APIs or Discord events.
- No agent may write to code or config files.
- All logs are read-only for agents.

## 3. Naming & Directory Conventions

- Prefix Codex internal scripts with `codex_`
- Prefix Legion helpers with `legion_`
- Directory layout:

  - `legion/agents/python/` for Python agents
  - `legion/agents/go/` for Go agents
  - `skills/`, `core/utils/`, `memory/` for helpers
  - `integration/`, `interface/`, `tests/` for integrations and UI

## 4. Code Style & Lint Rules

- Formatter: `black`-like, 88-char width, snake_case for functions/vars
- Use `.editorconfig` if present; otherwise, default to PEP8
- Codex must respect existing config before enforcing new rules

## 5. Testing & Validation

- Run tests with: `pytest -q` or `make test`
- Coverage threshold: 80% minimum
- Always dry-run before commit

## 6. Pull-Request (PR) Guidelines

- PR title: `[Component] <imperative>`
- PR must include:

  - Context
  - Changes
  - Risk
  - Checklist

- Auto-assign reviewers: architect, therapist

## 7. Multi-AGENTS.md Precedence

- Deeper path AGENTS.md overrides root for that subtree
- If conflict, root wins on safety clauses

## 8. Safety & Prohibited Actions

- No destructive ops (e.g., `rm -rf /`)
- No network calls except whitelisted domains (none by default)
- Fail fast on unknown commands
