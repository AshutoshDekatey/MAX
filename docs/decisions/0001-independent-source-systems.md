# ADR-0001: Preserve independent V0 source representations

**Status:** Accepted for V0

## Decision

Use PostgreSQL for the core customer and fraud-case systems; JSON Lines for payment/authentication/device events; daily CSV for merchant and label feeds; native document formats for policies.

## Why

A single clean database or DataFrame would erase the heterogeneity that makes later ingestion and quality engineering necessary. Separate formats also make event time, file duplication, schema drift and delayed labels observable.

## Consequence

V0 is less convenient to query globally. That inconvenience is the point. V1 must preserve these sources before V2 creates trustworthy curated data.

