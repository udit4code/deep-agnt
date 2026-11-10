import uuid


def charge_order(gateway, ledger, order_id, cents, attempts=3):
    """Charge an order, retrying when the reply is lost."""
    # 1. Build a stable key from the order alone so every attempt/call uses the same one
    key = str(order_id)
    
    # 4 & 5. Check ledger first before contacting the gateway
    if order_id in ledger:
        stored_cents = ledger[order_id]["cents"]
        if stored_cents == cents:
            return {
                "status": "charged",
                "charge_id": ledger[order_id]["charge_id"],
                "repeat": True
            }
        else:
            return {
                "status": "conflict",
                "charged_cents": stored_cents
            }
            
    # 2. Retry a Timeout, up to `attempts` requests in all. Never retry Declined.
    for _ in range(attempts):
        try:
            charge = gateway.charge(cents, key)
        except Timeout:
            continue
        except Declined:
            # 6. Declined: return {"status": "declined"} and record nothing
            return {"status": "declined"}
            
        charged_cents = charge["cents"]
        charge_id = charge["charge_id"]
        
        # 5. If the gateway hands back a charge for another amount, record it and return conflict
        if charged_cents != cents:
            ledger[order_id] = {"cents": charged_cents, "charge_id": charge_id}
            return {
                "status": "conflict",
                "charged_cents": charged_cents
            }
            
        # 3. On success, record the order in ledger and return charged
        ledger[order_id] = {"cents": cents, "charge_id": charge_id}
        return {
            "status": "charged",
            "charge_id": charge_id,
            "repeat": False
        }
        
    # 7. Every attempt timed out: return {"status": "unknown"} and record nothing
    return {"status": "unknown"}
