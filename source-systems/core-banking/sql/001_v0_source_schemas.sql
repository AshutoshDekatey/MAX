-- Project MAX V0 - Meridian Bank operational source schemas
-- PostgreSQL 15+

CREATE SCHEMA IF NOT EXISTS core_banking;
CREATE SCHEMA IF NOT EXISTS fraud_ops;

CREATE TABLE IF NOT EXISTS core_banking.customers (
    customer_id            varchar(20) PRIMARY KEY,
    full_name              text NOT NULL,
    date_of_birth          date NOT NULL,
    email                  text,
    phone                  text,
    kyc_status             varchar(20) NOT NULL CHECK (kyc_status IN ('VERIFIED', 'PENDING', 'EXPIRED')),
    customer_status        varchar(20) NOT NULL CHECK (customer_status IN ('ACTIVE', 'DORMANT', 'REVIEW')),
    created_at             timestamptz NOT NULL,
    updated_at             timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS core_banking.accounts (
    account_id             varchar(20) PRIMARY KEY,
    customer_id            varchar(20) NOT NULL REFERENCES core_banking.customers(customer_id),
    account_type           varchar(20) NOT NULL CHECK (account_type IN ('SAVINGS', 'CURRENT', 'CREDIT')),
    currency               char(3) NOT NULL,
    status                 varchar(20) NOT NULL CHECK (status IN ('OPEN', 'RESTRICTED', 'CLOSED')),
    opened_at              timestamptz NOT NULL,
    closed_at              timestamptz,
    CHECK (closed_at IS NULL OR closed_at >= opened_at)
);

CREATE TABLE IF NOT EXISTS core_banking.cards (
    card_id                varchar(20) PRIMARY KEY,
    account_id             varchar(20) NOT NULL REFERENCES core_banking.accounts(account_id),
    customer_id            varchar(20) NOT NULL REFERENCES core_banking.customers(customer_id),
    card_token             varchar(64) NOT NULL UNIQUE,
    card_network           varchar(20) NOT NULL,
    card_type              varchar(20) NOT NULL CHECK (card_type IN ('DEBIT', 'CREDIT')),
    status                 varchar(20) NOT NULL CHECK (status IN ('ACTIVE', 'BLOCKED', 'EXPIRED')),
    issued_at              timestamptz NOT NULL,
    expires_on             date NOT NULL
);

CREATE TABLE IF NOT EXISTS core_banking.addresses (
    address_id             varchar(20) PRIMARY KEY,
    customer_id            varchar(20) NOT NULL REFERENCES core_banking.customers(customer_id),
    address_type           varchar(20) NOT NULL,
    line_1                 text NOT NULL,
    city                   text NOT NULL,
    state                  text NOT NULL,
    postal_code            varchar(20) NOT NULL,
    country_code           char(2) NOT NULL,
    valid_from             date NOT NULL,
    valid_to               date,
    CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

CREATE TABLE IF NOT EXISTS core_banking.customer_status_history (
    history_id             varchar(20) PRIMARY KEY,
    customer_id            varchar(20) NOT NULL REFERENCES core_banking.customers(customer_id),
    status                 varchar(20) NOT NULL,
    effective_from         timestamptz NOT NULL,
    effective_to           timestamptz,
    reason                 text NOT NULL,
    CHECK (effective_to IS NULL OR effective_to >= effective_from)
);

CREATE TABLE IF NOT EXISTS fraud_ops.fraud_cases (
    case_id                varchar(20) PRIMARY KEY,
    transaction_id        varchar(24) NOT NULL,
    customer_id            varchar(20) NOT NULL REFERENCES core_banking.customers(customer_id),
    priority               varchar(4) NOT NULL CHECK (priority IN ('P1', 'P2', 'P3', 'P4')),
    status                 varchar(24) NOT NULL,
    queue                  varchar(40) NOT NULL,
    assigned_investigator  varchar(20),
    opened_at              timestamptz NOT NULL,
    closed_at              timestamptz,
    investigator_notes     text NOT NULL,
    CHECK (closed_at IS NULL OR closed_at >= opened_at)
);

CREATE INDEX IF NOT EXISTS idx_accounts_customer ON core_banking.accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_cards_customer ON core_banking.cards(customer_id);
CREATE INDEX IF NOT EXISTS idx_addresses_customer ON core_banking.addresses(customer_id);
CREATE INDEX IF NOT EXISTS idx_status_history_customer ON core_banking.customer_status_history(customer_id);
CREATE INDEX IF NOT EXISTS idx_fraud_cases_transaction ON fraud_ops.fraud_cases(transaction_id);

