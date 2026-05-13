from db.postgres import SessionLocal
from db.models import LedgerTransaction
from ingestion.embed_transactions import upsert_transaction


# -------------------------
# BUILDERS
# -------------------------
def build_transfer_out_dict(event):
    return {
        "id": str(event["id"]),
        "user_id": event["user_id"],
        "user_name": event.get("user_name"),
        "phone_number": event.get("phone_number"),
        "type": "TRANSFER_OUT",
        "amount": event["amount"],
        "currency": event["currency"],
        "receiver_name": event.get("receiver_name", "unknown"),
        "receiver_phone": event.get("receiver_phone", "unknown"),
        "created_at": str(event["created_at"]),
    }


def build_transfer_in_dict(event):
    return {
        "id": str(event["id"]),
        "user_id": event["user_id"],
        "user_name": event.get("user_name"),
        "phone_number": event.get("phone_number"),
        "type": "TRANSFER_IN",
        "amount": event["amount"],
        "currency": event["currency"],
        "sender_name": event.get("sender_name"),
        "sender_phone": event.get("sender_phone"),
        "created_at": str(event["created_at"]),
    }


def build_conversion_dict(event):
    return {
        "id": str(event["id"]),
        "user_id": event["user_id"],
        "user_name": event.get("user_name"),
        "phone_number": event.get("phone_number"),
        "type": "CONVERSION",
        "from_currency": event["from_currency"],
        "to_currency": event["to_currency"],
        "amount_from": float(event["amount_from"]),
        "amount_to": float(event["amount_to"]),
        "created_at": str(event["created_at"]),
    }


def build_topup_dict(event):
    return {
        "id": str(event["id"]),
        "user_id": event["user_id"],
        "user_name": event.get("user_name"),
        "phone_number": event.get("phone_number"),
        "type": "TOPUP",
        "amount": float(event["amount"]),
        "currency": event["currency"],
        "created_at": str(event["created_at"]),
    }


# -------------------------
# MAIN INGESTION
# -------------------------
def ingest_unembedded_transactions(event: dict):
    db = SessionLocal()
    eventt = None

    try:
        # SAFE event handling
        if event.get("type") == "TRANSFER_OUT":
            eventt = build_transfer_out_dict(event)

        elif event.get("type") == "TRANSFER_IN":
            eventt = build_transfer_in_dict(event)

        elif event.get("reference_type") == "CONVERSION":
            eventt = build_conversion_dict(event)

        elif event.get("reference_type") == "STRIPE":
            eventt = build_topup_dict(event)

        if not eventt:
            return  # ignore unknown events safely

        # send to vector store / embedding service
        upsert_transaction(eventt)

        # mark ledger rows as embedded (ONLY if reference_id exists)
        # ref_id = event.get("id")  # assuming the event has an "id" field that corresponds to reference_id in the DB

        # if ref_id:
        #     db.query(LedgerTransaction).filter(
        #         LedgerTransaction.id == ref_id
        #     ).update({"embedded": True})

        # 
        #    db.commit()
    
    except Exception as e:
        print(f"Error ingesting transaction: {e}")

    finally:

        db.close()
