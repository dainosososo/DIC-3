# Asset Management Capability Specification

## Purpose

Enables laboratories to track asset lifecycle states, perform physical QR-code audits, record item borrowings, and process disposal eligibility.

## Requirements

### Requirement: Asset Ledger Ingestion
The system SHALL ingest asset metadata including category, cost, acquisition date, and custodian from purchase receipts or manual entry into a structured ledger.

#### Scenario: Successful asset registration
- **WHEN** user submits a new asset with purchase cost >= NT$ 10,000 and useful life >= 2 years
- **THEN** system assigns an asset ID, records state as IN_STOCK, and generates an audit log entry

### Requirement: Asset Borrowing and Reservation
The system SHALL manage asset lending with conflict detection, return schedules, and custodian state tracking.

#### Scenario: Loan conflict prevention
- **WHEN** user requests to borrow an asset currently in ON_LOAN or UNDER_MAINTENANCE status
- **THEN** system rejects the borrowing request and displays the expected return date

#### Scenario: Successful checkout
- **WHEN** user requests to borrow an available IN_STOCK asset with valid return date
- **THEN** system transitions asset state to ON_LOAN and dispatches return reminder schedule

### Requirement: Asset Disposal Screening
The system SHALL evaluate whether an asset has reached minimum useful life before allowing disposal draft generation.

#### Scenario: Premature disposal blocked
- **WHEN** user attempts to initiate disposal for a functioning asset whose used years is less than statutory minimum life
- **THEN** system rejects disposal request and recommends continued utilization or transfer
