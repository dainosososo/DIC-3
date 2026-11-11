# Proposal

## Why

University research laboratories manage significant quantities of public-funded experimental instruments and computing equipment, yet face severe underutilization ("mosquito instruments"), tracking blindspots, and procurement compliance violations. Existing institutional ERPs only record static entries without dynamic availability or market valuation, while generic LLMs suffer a 32.1% hallucination tax in inventory decisions and lack adherence to public procurement thresholds. A domain-grounded, hybrid AI agent combining language planning with deterministic solvers is required now to eliminate waste and enforce compliance.

## What Changes

- Introduce LabSteward AI Agent combining ReAct planning with deterministic Python/SQLite tools and YAML guardrails.
- Implement pre-procurement mandatory inventory screening ("Utilize before Acquire") to prioritize borrowing and internal transfer over new purchases.
- Implement dual-track residual value estimation delivering both statutory straight-line book value and empirical market value with bootstrap intervals.
- Establish deterministic compliance guardrails to enforce Taiwan Government Procurement Act thresholds (NT$ 150k small procurement, NT$ 1.5M public tender) and prevent split-order evasion.
- Integrate Human-in-the-Loop (HITL) review gates for state mutations, high uncertainty, and legal violations, with complete audit log persistence.
- Provide automated official document draft generation (Word/Excel) for procurement requisitions and disposal applications.

## Capabilities

### New Capabilities
- `asset-management`: Core laboratory asset ledger, QR-code based physical inventory audit, lending/reservation tracking, and disposal lifecycle management.
- `procurement`: Requirement parameter extraction, mandatory inventory pre-check, multi-source price comparison, and TCO ranking.
- `residual-value`: Dual-track residual valuation computing statutory straight-line book value alongside market exponential depreciation with confidence intervals.
- `compliance-guardrail`: Deterministic YAML rule engine verifying procurement thresholds, anti-split-order detection, and audit logging.

### Modified Capabilities
<!-- None, this is a greenfield change creating initial specifications -->

## Impact

- Affects laboratory asset management workflows, procurement requisition drafting, and disposal review processes.
- Introduces SQLite database for asset records, YAML rule configurations, and Python tool adapters for web search and document generation.
- Zero breaking changes to existing institutional databases; operates as an intelligent overlay assistant generating standard review-ready documentation.
