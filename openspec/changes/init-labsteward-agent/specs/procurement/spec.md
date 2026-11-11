# Spec Delta

## Purpose

Handles procurement requisition workflows by enforcing pre-purchase inventory checks, orchestrating multi-vendor price comparison, and ranking total cost of ownership.

## ADDED Requirements

### Requirement: Mandatory Inventory Pre-Check
The system SHALL query existing laboratory inventory for idle or matching equipment before initiating any external procurement search.

#### Scenario: Existing idle asset satisfies demand
- **WHEN** user submits a procurement request and inventory contains matching equipment with IDLE status
- **THEN** system halts external purchase flow and generates an internal borrowing recommendation

#### Scenario: No matching idle equipment exists
- **WHEN** user submits a procurement request and zero matching assets exist in inventory
- **THEN** system proceeds to multi-source market and contract search

### Requirement: Multi-Source Price Search and Entity Matching
The system SHALL search external vendor catalogues and joint supply contracts, verifying candidate products against requested technical specifications.

#### Scenario: Candidate specification alignment
- **WHEN** raw search results are retrieved from online vendor catalogues
- **THEN** system verifies core technical attributes and discards non-matching or refurbished listings

### Requirement: Total Cost of Ownership Ranking
The system SHALL rank matched candidate quotations by total cost of ownership incorporating price, warranty, shipping, and delivery time.

#### Scenario: Quotations TCO sorting
- **WHEN** three or more valid candidate quotations are validated
- **THEN** system ranks quotations by calculated TCO and recommends the optimal purchasing candidate
