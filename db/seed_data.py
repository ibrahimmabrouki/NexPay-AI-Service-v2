"""
Seed helper for NexPay AI Backend.
Run from the ai-service/db directory:

    python seed_data.py

This script reads `seeds.sql` in the same directory and executes it using SQLAlchemy.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def main():
    load_dotenv()
    database_url = os.getenv("POSTGRES_URL")
    if not database_url:
        print("POSTGRES_URL not set. Set it in environment or .env file.")
        return

    engine = create_engine(database_url)

    sql_path = os.path.join(os.path.dirname(__file__), "seeds.sql")
    if not os.path.exists(sql_path):
        print(f"seeds.sql not found at {sql_path}")
        return

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    print("Executing seed SQL...")
    with engine.connect() as conn:
        conn.exec_driver_sql(sql)

    print("Seeding complete.")


if __name__ == "__main__":
    main()
