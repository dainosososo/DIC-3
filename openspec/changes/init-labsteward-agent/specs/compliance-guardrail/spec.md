# Spec Delta

## Purpose

Enforces public procurement threshold constraints, detects split-order evasion, provides regulatory citations, and maintains immutable audit logs.

## ADDED Requirements

### Requirement: Procurement Threshold Route Determination
The system SHALL evaluate total procurement amounts against configurable YAML rule thresholds to classify statutory approval pathways.

#### Scenario: Small procurement classification
- **WHEN** total procurement amount is less than or equal to NT$ 150,000
- **THEN** system classifies route as small procurement with department head sign-off requirement

#### Scenario: Public tender classification
- **WHEN** total procurement amount is greater than or equal to NT$ 1,500,000
- **THEN** system classifies route as public tender requiring formal market analysis documentation

### Requirement: Anti-Split-Order Detection
The system SHALL scan historical procurement records within a 30-day window to identify suspected split-order transactions intended to bypass threshold rules.

#### Scenario: Split-order detected
- **WHEN** cumulative purchase amounts for similar equipment categories exceed NT$ 150,000 within 30 days
- **THEN** system raises a compliance violation warning and blocks independent order splitting

### Requirement: Human-in-the-Loop Review Gating
The system SHALL enforce human reviewer authorization before executing any ledger state mutation or dispatching external orders.

#### Scenario: Review sign-off required
- **WHEN** an action commits financial records or triggers compliance risk flags
- **THEN** system halts automated execution until authorized human reviewer approves or rejects
