# Residual Value Capability Specification

## Purpose

Calculates dual-track asset residual values combining statutory straight-line book depreciation with empirical market exponential depreciation and prediction intervals.

## Requirements

### Requirement: Statutory Book Value Computation
The system SHALL compute accounting book value using the straight-line depreciation formula based on statutory minimum useful life.

#### Scenario: Normal book depreciation
- **WHEN** evaluating an asset within its statutory useful life
- **THEN** system computes book value as original cost multiplied by remaining life fraction

#### Scenario: Fully depreciated asset
- **WHEN** evaluating an asset whose age equals or exceeds statutory useful life
- **THEN** system sets book value to zero or scrap residual value

### Requirement: Market Fair Value Estimation
The system SHALL compute market fair value using category exponential depreciation rates adjusted by physical condition ratings.

#### Scenario: Market valuation with confidence interval
- **WHEN** asset category and condition parameters are provided
- **THEN** system outputs estimated market price along with an 80% bootstrap confidence interval and advice
