Database helpers and seeds

This directory contains database models, connection helpers, queries, and seed data for local development.

Files
- `models.py`: SQLAlchemy ORM models for `users`, `ledger_transactions`, `transfers`, `currency_conversions`, and `stripe_topups`.
- `postgres.py`: SQLAlchemy engine and `SessionLocal` configuration (reads `POSTGRES_URL` from environment).
- `seeds.sql`: SQL file with sample inserts for development.
- `seed_data.py`: small Python helper to execute `seeds.sql` via SQLAlchemy.
- `queries.py`: project-specific database query helpers used by the service.

Quick commands
- Run the seed SQL with psql (recommended):

```powershell
psql "$env:POSTGRES_URL" -f seeds.sql
```

- Or run the Python helper from this directory:

```powershell
python seed_data.py
```

Environment
- Ensure `POSTGRES_URL` is set in your environment or in a `.env` file at the project root.

Notes
- These scripts are intended for development and testing only. The `TRUNCATE` in `seeds.sql` will remove existing rows.
