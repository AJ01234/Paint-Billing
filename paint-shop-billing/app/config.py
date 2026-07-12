from dataclasses import dataclass


@dataclass(frozen=True)
class ShopDetails:
    app_name: str = "Local First Billing Anklikar Hardware and Paints"
    business_name: str = "ANKLIKAR HARDWARE & PAINT STORE"
    name: str = "ANKLIKAR HARDWARE & PAINT STORE"
    address: str = "SAKET NAGAR KANPUR"
    phone: str = "9918602602"
    gstin: str = "09AGSPJ3870D1Z4"
    state: str = "Uttar Pradesh"
    state_code: str = "09"
    email: str = "billing@anklikarpaints.local"


SHOP_DETAILS = ShopDetails()
