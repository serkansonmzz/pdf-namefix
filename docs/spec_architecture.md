# spec_architecture.md

## Goal

Refactor `pdf-namefix` into a lightweight clean architecture with feature-oriented module organization, without breaking CLI behavior, report formats, or current safety guarantees.

## Non-negotiable Rules

- Keep CLI command names and flags stable unless a phase explicitly states a compatibility migration.
- Keep JSON/Markdown report shapes stable.
- Keep safety model stable: no delete, no overwrite, confirmation defaults, undo logs.
- Every phase uses its own branch, commit(s), push, PR, and squash merge to `main`.
- No large-bang rewrite. Each phase must be shippable and test-green.

## Target Structure

```text
src/pdf_namefix/
  __init__.py
  cli.py

  app/
    preview.py
    apply.py
    organize.py
    undo.py
    ai_suggest.py
    use_cases/
      apply_rename.py
      organizer.py
      undo.py

  domain/
    models.py
    naming_profile.py
    ai_models.py

  services/
    scanner.py
    classifier.py
    name_suggester.py
    pdf_inspector.py
    preview_report.py
    ai_naming.py
    apply_ai_suggestions.py

  infrastructure/
    report_exporter.py
    ai_report_exporter.py
    safety.py
    type_resolver.py
    clients/
      openai_client.py
```

## Phase Plan

### Phase 1 - Foundation Layout

- Branch: `refactor/architecture-phase-01-foundation`
- Create architecture folders: `app`, `domain`, `services`, `infrastructure`
- Add package files and architecture notes.
- No behavior change.

Acceptance:

- Existing tests stay green.
- Imports still resolve from old module paths.

### Phase 2 - CLI Use-Case Extraction

- Branch: `refactor/architecture-phase-02-cli-extraction`
- Extract command bodies from `cli.py` into `app/{preview,apply,organize,undo,ai_suggest}.py`
- Keep Typer declarations in `cli.py`; delegate execution to app functions.
- Keep CLI output text and exit codes unchanged.

Acceptance:

- `tests/test_cli.py` unchanged or minimally adjusted only for import paths.
- Full suite green.

### Phase 3 - Domain Split

- Branch: `refactor/architecture-phase-03-domain-split`
- Move stable data contracts to `domain/models.py`
- Move AI-specific contracts to `domain/ai_models.py`
- Keep compatibility re-exports in old modules during transition.

Acceptance:

- No consumer-facing behavior change.
- Serialization and enum compatibility preserved.

### Phase 4 - Service and Infra Separation

- Branch: `refactor/architecture-phase-04-service-infra-separation`
- Move pure business processing to `services/`.
- Move side-effect adapters to `infrastructure/`.
- Introduce a tiny `infrastructure/filesystem.py` helper for common path/io operations.

Acceptance:

- No functional diff in CLI behavior.
- Existing report and log formats unchanged.

### Phase 5 - Compatibility Cleanup

- Branch: `refactor/architecture-phase-05-cleanup`
- Remove deprecated re-export shims after all callsites are migrated.
- Flatten circular imports if any remain.
- Final naming cleanup and docs update.

Acceptance:

- Full suite green.
- No dead compatibility modules.

### Phase 6 - Strict Clean Architecture Alignment

- Branch: `refactor/architecture-phase-06-strict-cleanup`
- Move remaining root modules to target layers:
  - `naming_profile.py` -> `domain/naming_profile.py`
  - `ai_naming.py` and `apply_ai_suggestions.py` -> `services/`
  - `apply_rename.py`, `organizer.py`, `undo.py` -> `app/use_cases/`
- Introduce `infrastructure/clients/openai_client.py` and wire AI client construction through infrastructure.
- Keep CLI behavior and report formats unchanged.

Acceptance:

- Full suite green.
- No business/use-case modules left at package root.

## Branch, PR, Merge Workflow (Mandatory)

For every phase:

1. Create branch from latest `main`.
2. Implement only that phase scope.
3. Run full tests.
4. Commit with phase-specific message.
5. Push branch.
6. Open PR targeting `main`.
7. Merge via squash.
8. Pull latest `main` locally before starting next phase.

## Release Strategy

- Architecture phases are refactor releases unless behavior changes are introduced.
- Patch release recommended after each completed phase if user-facing behavior is unchanged (for traceability).
- If a phase introduces user-visible behavior change, use minor release and dedicated release branch.

## Versioning Strategy

- Refactor-only phase: patch bump (example `0.2.3` -> `0.2.4`)
- Feature phase: minor bump (example `0.2.x` -> `0.3.0`)

When releasing:

- Update `pyproject.toml` version.
- Update `src/pdf_namefix/__init__.py` version.
- Open dedicated release branch and PR.
- Tag after merge and create GitHub release notes.

## Testing Gate for Every Phase

- Required: `uv run pytest -q`
- Required: `uv run pdf-namefix --help`
- Required: smoke check for one AI flow:
  - `ai-suggest` report generation
  - `preview --ai-suggestions`
  - `apply --ai-suggestions`

## Risks and Controls

- Risk: import breaks during move operations.
  - Control: compatibility re-exports per phase.
- Risk: accidental CLI behavior drift.
  - Control: lock existing `test_cli.py` expectations and keep text stable.
- Risk: oversized PRs.
  - Control: strict phase scope and squash merge per phase.

## Execution Status

- Phase 1: completed
- Phase 2: completed
- Phase 3: completed
- Phase 4: completed
- Phase 5: completed (compatibility shims removed after callsite migration)
- Phase 6: completed (strict layering applied for root leftovers)
