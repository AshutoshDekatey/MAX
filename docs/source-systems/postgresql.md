# PostgreSQL setup: actions Max must perform

Project MAX does not create a database login, choose a password or alter machine-level PostgreSQL security. Those are human-controlled actions.

## 1. Install PostgreSQL 15 or newer

On Windows, use the official PostgreSQL installer and retain the password for the administrative `postgres` login. Ensure the command-line tools or pgAdmin are available.

## 2. Create a development login and database

Choose a unique local password. In pgAdmin Query Tool, connected as an administrator, run the following after replacing the placeholder yourself:

```sql
CREATE ROLE max_app LOGIN PASSWORD '<choose-a-local-password>';
CREATE DATABASE max_bank OWNER max_app;
```

Do not paste a real production or reused password into Git, chat, screenshots or `.env.example`.

## 3. Supply the connection at runtime

Create an untracked `.env` for your own reference or set the environment variable in PowerShell:

```powershell
$env:MAX_DATABASE_URL="postgresql://max_app:<your-password>@localhost:5432/max_bank"
```

The application reads the URL but never prints it into a run manifest.

## 4. Create the V0 schema and load clean records

```powershell
python -m project_max.cli bootstrap-db
python -m project_max.cli load-db source-systems/sample-data/v0-demo
```

The loader upserts clean operational records. Deliberately dirty extracts are not loaded into constrained tables.

## 5. Optional disposable integration-test database

Create a separate database owned by a separate local test login or the same local development login, then set `MAX_TEST_DATABASE_URL`. Tests never fall back from the test URL to `MAX_DATABASE_URL`.

No AWS, IAM or enterprise security configuration is part of V0.

