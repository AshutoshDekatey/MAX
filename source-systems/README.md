# Meridian Bank V0 source systems

This directory describes and demonstrates the independent operational systems simulated by Project MAX V0.

| Source | Prototype representation | Primary identity |
|---|---|---|
| Core customer system | PostgreSQL schema plus CSV snapshot | `customer_id`, `account_id`, `card_token` |
| Payment authorization | JSON Lines event stream | `transaction_id`, `event_id` |
| Authentication | JSON Lines event stream | `auth_event_id`, `transaction_id` |
| Device intelligence | JSON Lines snapshot | `device_id`, `customer_id` |
| Merchant reference | Dated daily CSV | `merchant_id` |
| Fraud / chargeback | Delayed CSV labels | `fraud_label_id`, `transaction_id` |
| Fraud cases | JSON Lines records with free-text notes | `case_id`, `transaction_id` |
| Banking documents | PDF, DOCX, TXT and HTML files | filename and policy version |

`sample-data/v0-demo/` is a small committed run for immediate inspection. `dirty/` contains controlled violations of the clean source contracts; `dirty/defect_ledger.json` explains every one.

The sample snapshots do not replace PostgreSQL. They make the generated records reviewable in Git and loadable into a database chosen by Max.

Full field contracts are in [`docs/source-systems/contracts.md`](../docs/source-systems/contracts.md).

