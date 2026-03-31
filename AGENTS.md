Understood. This is a one-time transformation guide, not a permanent repo guide.

You need an AGENTS.md that tells an AI agent how to strip Glossary-specific content and convert the repo into a reusable CRUD template.

Here is the correct version for that purpose:

⸻

AGENTS.md

1. Objective

Transform this repository into a fully generic CRUD template.

All domain-specific logic must be removed or generalized.

End state:
	•	No glossary-specific naming, data, or logic
	•	Fully reusable for any CRUD-based application
	•	Clean separation between framework (app/) and domain (resources/)

⸻

2. Required Outcome

After transformation:
	•	Repository contains zero domain-specific references
	•	resources/ contains only minimal example or placeholder entities
	•	No hardcoded business logic remains
	•	Template can be reused without modification of app/

⸻

3. Glossary-Specific Removal (MANDATORY)

Remove or replace all glossary-related concepts, including:
	•	Entity names like:
	•	Term
	•	Definition
	•	Category
	•	Any glossary-specific relationships or constraints
	•	Any text, labels, or descriptions tied to glossary use-case
	•	Seed data content specific to glossary

Search and eliminate domain terms across:
	•	Backend (resources/, app/services/ if applicable)
	•	Frontend (resources.js, pages, labels, UI text)
	•	Tests
	•	Seed data
	•	Documentation

⸻

4. Replace With Generic Example

After removal, replace with neutral placeholder entities, e.g.:
	•	Item
	•	Group
	•	or minimal example like ExampleEntity

Rules:
	•	Keep schema simple
	•	Demonstrate relationships only if necessary
	•	Do not encode business meaning

⸻

5. Preserve Framework Integrity

Do NOT break or redesign the framework.

Must remain intact:
	•	app/crud/*
	•	Router factory behavior
	•	Resource registry system
	•	Auto-generated CRUD flow
	•	Frontend generic CRUD components

Goal is cleanup, not redesign.

⸻

6. Required File Changes

Backend (resources/)
	•	Rewrite:
	•	models.py
	•	schemas.py
	•	config.py
	•	Remove domain-specific validation rules
	•	Ensure models are minimal and generic

Frontend
	•	Update:
	•	frontend/src/config/resources.js
	•	Remove:
	•	Glossary-specific labels
	•	Custom pages tied to glossary
	•	Keep generic CRUD pages functional

Seed Data
	•	Replace with minimal generic dataset OR empty
	•	Ensure seeding remains idempotent

Tests
	•	Update all tests to reflect generic entities
	•	Remove glossary-specific assumptions

⸻

7. Naming Rules

All names must be:
	•	Generic
	•	Reusable
	•	Domain-agnostic

Avoid:
	•	Industry-specific terms
	•	Business-specific workflows

⸻

8. Validation Requirements

After transformation, ALL must pass:

uv run ruff check .
uv run ruff format --check .
uv run pytest
cd frontend && npm run lint
cd frontend && npm run test:unit
cd frontend && npm run build

If any fail → transformation is incomplete.

⸻

9. Consistency Rules
	•	Backend and frontend configs must match
	•	Resource names must align across:
	•	models
	•	schemas
	•	config
	•	frontend config
	•	No orphaned references

⸻

10. Forbidden Actions
	•	Do NOT modify framework behavior unless required to remove domain coupling
	•	Do NOT introduce new domain logic
	•	Do NOT leave partial glossary references
	•	Do NOT hardcode anything that reduces reusability

⸻

11. Completion Criteria

Transformation is complete only if:
	•	No glossary-related terms remain in codebase
	•	Repository can serve as a base for any CRUD app
	•	New entity can be added without modifying app/
	•	All checks and tests pass

⸻

12. Final Sanity Check (MANDATORY)

Agent must verify:
	•	Global search for glossary terms returns zero matches
	•	CRUD flow works end-to-end with generic entities
	•	Frontend renders without custom domain logic
	•	Backend routes function via auto-generated system

⸻

If you want, the next step would be a diff-style execution plan (exact files + edits) so an agent can apply this deterministically instead of interpreting instructions.