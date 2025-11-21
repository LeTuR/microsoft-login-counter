<!--
SYNC IMPACT REPORT - Constitution v1.0.0
Generated: 2025-11-21

VERSION CHANGE: Initial → 1.0.0
BUMP RATIONALE: MAJOR - Initial constitution ratification for Microsoft Login Counter project

PRINCIPLES ESTABLISHED:
  1. Test-First Development (TDD) - NEW
  2. Integration & Contract Testing - NEW
  3. Pragmatic Simplicity - NEW

SECTIONS ADDED:
  - Core Principles (3 principles)
  - Development Workflow
  - Quality Standards
  - Governance

TEMPLATES REQUIRING UPDATES:
  ✅ plan-template.md - Constitution Check section aligned
  ✅ spec-template.md - User story and requirements structure aligned
  ✅ tasks-template.md - Test-first workflow and task organization aligned

FOLLOW-UP ITEMS:
  - None

NOTES:
  - Constitution structured for Microsoft OAuth integration project
  - Pragmatic governance allows justified exceptions with documentation
  - Test-first approach mandatory but with practical testing focus
  - Integration tests prioritized for external API contracts
-->

# Microsoft Login Counter Constitution

## Core Principles

### I. Test-First Development (TDD)

All features MUST follow the red-green-refactor cycle:
- Tests are written FIRST and must FAIL before implementation begins
- Implementation proceeds only after tests are approved and failing
- Tests define the contract and expected behavior
- Refactoring occurs only after tests pass

**Rationale**: Test-first development ensures clarity of requirements, prevents scope creep, and
provides immediate feedback on implementation correctness. For a project integrating with Microsoft
APIs, having tests define expected behaviors prevents integration issues and makes debugging faster.

### II. Integration & Contract Testing

The system MUST maintain robust integration and contract tests for:
- Microsoft authentication flows (OAuth, token refresh, session management)
- API contract changes (Microsoft Graph API or authentication endpoints)
- Login session tracking and time calculations
- Data persistence and retrieval operations

**Rationale**: Integration with external services like Microsoft is inherently fragile. Contract
tests catch breaking changes early. Login tracking requires accurate time calculations and state
management—integration tests verify the entire flow works correctly end-to-end, not just
individual units.

### III. Pragmatic Simplicity

Development MUST prioritize simplicity and practicality:
- Build only what is needed NOW (YAGNI - You Aren't Gonna Need It)
- Test what matters—avoid testing for test coverage metrics alone
- Choose straightforward solutions over clever abstractions
- Complexity requires explicit justification in code reviews
- Premature optimization is avoided unless performance issues are measured

**Rationale**: Small projects become unmaintainable when over-engineered. For a login counter,
simple data structures and clear logic are more valuable than elaborate architectures. Testing
pragmatically means focusing on critical paths (authentication, time tracking) rather than
achieving 100% coverage on trivial getters/setters.

## Development Workflow

### Feature Development Process

1. **Specification**: Feature requirements captured in `specs/[###-feature-name]/spec.md` with
   user stories and acceptance criteria
2. **Planning**: Technical design in `specs/[###-feature-name]/plan.md` with architecture
   decisions and structure
3. **Test Writing**: Tests written in appropriate directory (`tests/contract/`, `tests/integration/`,
   `tests/unit/`) and reviewed
4. **Test Validation**: Verify tests FAIL for the right reasons
5. **Implementation**: Code written to make tests pass
6. **Refactoring**: Clean up while keeping tests green
7. **Review**: Code review verifies constitution compliance

### Branching & Commits

- Feature branches: `[###-feature-name]` format
- Commit after each logical task or test-implementation pair
- Commit messages: concise, imperative mood (e.g., "Add OAuth token refresh logic")

### Code Review Requirements

All pull requests MUST verify:
- Tests were written first and failed before implementation
- Integration tests exist for Microsoft API interactions
- Complexity is justified or simplified
- Code follows project structure from plan.md

## Quality Standards

### Testing Hierarchy

Priority from highest to lowest:
1. **Contract Tests**: Microsoft API endpoints, authentication flows, data contracts
2. **Integration Tests**: Full user journeys (login → tracking → data retrieval)
3. **Unit Tests**: Critical business logic, time calculations, edge cases

### Coverage Philosophy

- Focus on **critical paths** rather than coverage percentages
- 100% coverage is NOT a goal—meaningful tests are
- Test failure cases and edge conditions for authentication and time tracking
- Skip testing trivial code (simple getters, config constants)

### Performance Expectations

- OAuth flows: reasonable response times (dependent on Microsoft servers)
- Local operations (time calculations, data queries): < 100ms for typical datasets
- Measure before optimizing—no premature optimization

## Governance

### Amendment Process

1. **Proposal**: Identify principle violation or improvement need
2. **Discussion**: Document rationale, alternatives considered, impact
3. **Approval**: Consensus required for constitution changes
4. **Migration**: Update affected code, templates, and documentation
5. **Version Bump**: Increment version per semantic versioning rules:
   - MAJOR: Backward-incompatible governance changes, principle removals/redefinitions
   - MINOR: New principles added, material expansions to guidance
   - PATCH: Clarifications, wording fixes, non-semantic refinements

### Compliance

- All features MUST pass constitution check in plan.md before implementation
- Violations require explicit justification in Complexity Tracking table
- Principle conflicts are resolved through pragmatic trade-off analysis
- Constitution supersedes all other project documentation

### Justified Exceptions

Given pragmatic governance:
- Exceptions are permitted when clearly justified (performance, external constraints, MVP scope)
- Justification MUST be documented in code comments or plan.md Complexity Tracking
- Exceptions are reviewed in code review process
- Pattern of exceptions triggers constitution review

### Living Document

- Constitution evolves with project needs
- Amendments tracked via version number and change log
- Templates (plan, spec, tasks) kept synchronized with constitution changes

**Version**: 1.0.0 | **Ratified**: 2025-11-21 | **Last Amended**: 2025-11-21
