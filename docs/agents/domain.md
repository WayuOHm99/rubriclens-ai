# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, if it exists.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in, if they exist.

If these files do not exist, proceed without creating them. The `/domain-modeling` skill creates them when the project resolves a domain term or decision.

## File structure

This is a single-context repository:

```
/
├── CONTEXT.md
├── docs/adr/
└── src/
```

## Use the glossary's vocabulary

When output names a domain concept, use the term as defined in `CONTEXT.md`. If a needed concept is absent, note it for `/domain-modeling` rather than inventing a conflicting synonym.

## Flag ADR conflicts

If an output contradicts an existing ADR, state the conflict explicitly rather than silently overriding it.
