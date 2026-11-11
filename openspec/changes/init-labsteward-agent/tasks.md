# Tasks

## 1. Domain Knowledge and Rules Setup

- [ ] 1.1 Create `knowledge/rules.yaml` specifying Taiwan procurement thresholds (NT$ 150k small purchase, NT$ 1.5M announcement threshold) and verify schema validation
- [ ] 1.2 Create `knowledge/std_class_table.csv` defining statutory minimum useful life for lab assets and verify CSV query lookups
- [ ] 1.3 Create regulation markdown documents in `knowledge/regulations/` and verify text retrieval

## 2. Deterministic Tools Implementation

- [ ] 2.1 Implement `tools/inventory.py` with SQLite asset database and status machine transitions, verifying unit tests for state constraints
- [ ] 2.2 Implement `tools/valuation.py` for dual-track residual calculation (straight-line + log-linear/GBDT) and verify output against synthetic test cases
- [ ] 2.3 Implement `tools/guardrail.py` for threshold classification and anti-split-order detection, verifying detection on historical test records
- [ ] 2.4 Implement `tools/web_search.py` and entity matching for multi-vendor quotes, verifying price normalization and TCO ranking
- [ ] 2.5 Implement `tools/docgen.py` for requisition and disposal draft generation, verifying output file generation

## 3. Agent Coordination Architecture

- [ ] 3.1 Implement `agent/planner.py` ReAct loop with slot clarification and RBAC enforcement, verifying parse accuracy
- [ ] 3.2 Implement `agent/management_agent.py` covering M1 to M4 modules and verify asset lending/disposal workflows
- [ ] 3.3 Implement `agent/procurement_agent.py` covering P1 to P4 modules enforcing mandatory pre-check and verify execution trace

## 4. Evaluation and Web Interface

- [ ] 4.1 Create `eval/tasks.jsonl` containing 50 laboratory benchmark tasks and verify schema integrity
- [ ] 4.2 Implement `eval/run_eval.py` and `eval/metrics.py` measuring pass^k, MAPE, and violation rates, verifying benchmark run completion
- [ ] 4.3 Implement `app/streamlit_app.py` interactive interface and verify local web serving
- [ ] 4.4 Verify full project integration and commit to GitHub repository `DIC-3`
