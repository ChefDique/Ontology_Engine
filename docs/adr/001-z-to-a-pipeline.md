# ADR-001: Z → A Reverse Extrapolation Pipeline

**Status:** Accepted
**Date:** 2026-03-07

## Context

We need a methodology for building the Ontology Engine that prevents the common failure mode of LLM pipelines: building forward from messy inputs and discovering late that the output is wrong.

## Decision

Adopt the **Z → A Reverse Extrapolation** approach:

1. Define the final output schema (Z) first — the exact format each CRM needs
2. Work backward to define every intermediate data structure
3. Enforce Design by Contract (DbC) at every node boundary
4. Write acceptance tests before implementation (Agentic V-Model)

## Consequences

- **Positive:** Output correctness is verifiable from day one. Agents can work in parallel because contracts are defined upfront.
- **Negative:** More upfront schema design work. Changes to output format cascade backward through all nodes.
- **Risk:** If CRM import formats change, contracts must be updated and re-validated.

## References

- DOC_002: Z → A Pipeline Research & Blueprint
- Hoare Logic, GOAP, Backward Chaining
