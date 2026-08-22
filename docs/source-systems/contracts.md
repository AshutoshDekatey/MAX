# V0 source contracts

A source contract documents the normal shape of each Meridian operational interface. V0 deliberately violates some contracts in the `dirty/` extracts.

## Core banking PostgreSQL

The SQL DDL lives at `source-systems/core-banking/sql/001_v0_source_schemas.sql`.

| Table | Meaning | Important relationship |
|---|---|---|
| `core_banking.customers` | Customer identity, contact, KYC and status | Parent entity |
| `core_banking.accounts` | Deposit or credit relationship | References customer |
| `core_banking.cards` | Tokenised card; no PAN is generated | References account and customer |
| `core_banking.addresses` | Time-bounded customer address | References customer |
| `core_banking.customer_status_history` | Status over time | References customer |
| `fraud_ops.fraud_cases` | Structured fraud workflow and narrative notes | References customer; transaction is external |

The SQL constraints reject impossible normal-state relationships. Invalid foreign keys are demonstrated in a dirty device extract because real cross-system keys are not protected by one database constraint.

## Payment authorization JSON Lines

One JSON object per line. Important fields: `event_id`, `schema_version`, `transaction_id`, `card_token`, `customer_id`, `merchant_id`, `amount`, `currency`, `timestamp`, `emitted_at`, `country`, `channel`, `authentication_method`, `device_id`, and `authorization_result`.

`timestamp` is when the business event occurred. `emitted_at` is when the source emitted it. Their difference makes late data visible.

## Authentication JSON Lines

One event per simulated payment. Events include `OTP_SUCCESS`, `OTP_FAILED`, `BIOMETRIC_SUCCESS`, `3DS_CHALLENGE`, `PASSWORD_SUCCESS`, `PASSWORD_FAILURE`, `DEVICE_ENROLLED`, and `PASSIVE_AUTH`.

`transaction_id` links authentication evidence back to the authorization attempt.

## Device-intelligence JSON Lines

Contains `device_id`, `customer_id`, IP, browser, OS, `first_seen`, `last_seen`, and `device_risk_signal`. A device signal is evidence, not proof of fraud.

## Merchant-reference daily CSV

The filename is dated, for example `merchant_reference_2026_08_20.csv`. It includes name, merchant category code, country, risk tier, status and reference update time.

## Delayed fraud / chargeback CSV

Contains a confirmed label, reason, reporting time, delay in days, disputed amount/currency and reporting source. `reported_at` is always later than the original payment in the clean feed.

## Fraud case JSON Lines

Combines structured fields such as priority, status, queue and investigator with the unstructured `investigator_notes` narrative. Later AI work will use the text, but V0 only generates and preserves it.

## Banking documents

The repository covers fraud policy, disputes, escalation, merchant risk, authentication and investigations. `investigation_procedure_scanned_v1.pdf` is image-only: a later OCR pipeline will need to convert its pixels back into text.

## Defect catalogue

The injector creates: null values, duplicate rows, duplicate payment events, inconsistent country codes/currencies, malformed timestamps, wrong types, late records, delayed labels, stale reference data, unexpected categories, merchant-name variations, an in-stream schema change, invalid foreign keys and a duplicated file.

