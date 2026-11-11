# Design

## Context

University laboratories operate under Taiwan public procurement regulations and institutional asset rules. As established in `proposal.md`, asset management and procurement workflows currently suffer from information silos, high hallucination rates in generic LLMs, and non-compliance with statutory thresholds. This technical design establishes a hybrid agentic architecture coupling LLM reasoning with deterministic Python/SQLite tools and YAML guardrails.

## Goals / Non-Goals

**Goals:**
- Provide a robust ReAct planner coordinating two specialized sub-agents (`ManagementAgent` and `ProcurementAgent`).
- Ensure all statutory thresholds and mathematical calculations are executed by deterministic tools rather than LLM text generation.
- Enforce the "Utilize before Acquire" paradigm via mandatory pre-procurement inventory checks.
- Establish dual-track residual valuation delivering accounting book values and market price intervals.
- Maintain a tamper-evident audit log for every transaction and human review decision.

**Non-Goals:**
- Direct automatic bank account transfer or unreviewed purchase ordering without human signature.
- Replacement of institutional campus-wide ERP databases; the system acts as a smart laboratory-level interface and decision support overlay.
- High-frequency automated auction bidding on consumer platforms.

## Decisions

### 1. Hybrid Architecture: LLM Planner + Deterministic Tools
- **Decision**: Restrict LLM responsibility to natural language intent recognition, slot filling, and clarification. Delegate calculations, queries, and threshold evaluations to Python functions and SQLite.
- **Rationale**: Mitigates the 32.1% hallucination tax observed in end-to-end LLM inventory optimization (Duan et al., 2025).
- **Alternatives Considered**: Pure end-to-end LLM prompts (rejected due to calculation instability and low pass^k scores).

### 2. External Configurable Rules Engine (YAML Guardrail)
- **Decision**: Define legal thresholds (e.g., NT$ 150,000 for small purchases, NT$ 1,500,000 for tender requirements) in external `rules.yaml` files.
- **Rationale**: Enables zero-code policy updates when national procurement guidelines change without modifying model prompts or Python code.
- **Alternatives Considered**: In-prompt rule injection (rejected due to context window bloat and prompt sensitivity).

### 3. Dual-Track Residual Valuation (Straight-Line + Exponential Decay)
- **Decision**: Output both accounting book value $V_{book}(t)$ and market fair value $V_{mkt}(t)$ with condition factor $q(c)$ and 80% bootstrap intervals.
- **Rationale**: Resolves the discrepancy between statutory accounting life and real-world IT technology cycles (e.g., GPU depreciation debate).
- **Alternatives Considered**: Single linear depreciation (rejected as it distorts secondary market reality).

### 4. Human-in-the-Loop (HITL) State Mutation Barrier
- **Decision**: Require explicit reviewer authorization (PI or lab manager) whenever database records are modified or compliance violations are flagged.
- **Rationale**: Ensures legal accountability and guarantees no unverified purchase or disposal action takes effect autonomously.
- **Alternatives Considered**: Full autonomous execution (rejected due to public procurement legal liability).

## Risks / Trade-offs

- **[Risk] Web scraping rate limits or dynamic DOM changes during price comparison**  
  → *Mitigation*: Fall back to structured joint-contract tables and mock search APIs; flag `NEED_MANUAL_QUOTES` if fewer than 3 valid quotes are retrieved.
- **[Risk] Sparse secondary market transaction data for specialized laboratory equipment**  
  → *Mitigation*: Fall back to default category depreciation rates and explicitly flag `LOW_CONFIDENCE` with an expanded uncertainty interval.
- **[Risk] User friction during strict asset borrowing and checkouts**  
  → *Mitigation*: Provide tiered friction: instant QR-code scans for low-value accessories and streamlined one-click supervisor approvals for high-value GPUs.
