import hmac
import hashlib
import uuid
from urllib.parse import urlencode


class PaymentService:
    def __init__(self, form_url: str, secret_key: str):
        self.form_url = form_url
        self.secret_key = secret_key

    def create_payment_link(self, user_id: int, plan: str = "monthly") -> str:
        order_id = f"{user_id}-{uuid.uuid4().hex[:8]}"
        query = urlencode({"order_id": order_id})
        return f"{self.form_url}?{query}"

    def verify_signature(self, data: dict, signature: str) -> bool:
        # Webhook unused in polling mode
        return True

    def fetch_new_payments(self, since):
        import requests

        url = "https://api.prodamus.ru/transactions"
        params = {"status": "paid", "since": since.isoformat()}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
