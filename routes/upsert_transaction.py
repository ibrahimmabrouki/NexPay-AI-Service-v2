from fastapi import APIRouter
from db.queries import ingest_unembedded_transactions

router = APIRouter()


@router.post("/upsert-transaction")
async def ingest_transaction(event: dict):
    ingest_unembedded_transactions(event)
    return {"success": True}
