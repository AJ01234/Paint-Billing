from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class PartyType(str, Enum):
    customer = "customer"
    painter = "painter"


class BillType(str, Enum):
    gst = "GST"
    non_gst = "NON_GST"


class InvoiceStatus(str, Enum):
    finalized = "FINALIZED"
    cancelled = "CANCELLED"


class LedgerEntryType(str, Enum):
    debit = "DEBIT"
    credit = "CREDIT"


class ReminderStatus(str, Enum):
    pending = "PENDING"
    sent = "SENT"
    completed = "COMPLETED"


class NotificationChannel(str, Enum):
    sms = "SMS"
    whatsapp = "WHATSAPP"
    internal = "INTERNAL"


class NotificationStatus(str, Enum):
    pending = "PENDING"
    sent = "SENT"
    failed = "FAILED"


class ExpenseType(str, Enum):
    business = "BUSINESS"
    personal = "PERSONAL"


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    brand: str = ""
    category: str = ""
    size: str = ""
    shade: str = ""
    hsn_code: str = ""
    gst_percent: float = 18.0
    selling_price: float
    stock_quantity: float = 0.0
    low_stock_threshold: float = 5.0
    barcode: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Party(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str = ""
    address: str = ""
    gstin: str = ""
    party_type: PartyType = Field(default=PartyType.customer)
    running_balance: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str = Field(index=True)
    invoice_date: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    bill_type: BillType = Field(default=BillType.gst)
    payment_mode: str = "Cash"
    party_id: Optional[int] = Field(default=None, foreign_key="party.id")
    notes: str = ""
    supply_type: str = "INTRA_STATE"
    subtotal: float = 0.0
    discount_total: float = 0.0
    taxable_total: float = 0.0
    cgst: float = 0.0
    sgst: float = 0.0
    igst: float = 0.0
    round_off: float = 0.0
    grand_total: float = 0.0
    status: InvoiceStatus = Field(default=InvoiceStatus.finalized)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class InvoiceItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoice.id", index=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product_name: str
    brand: str = ""
    size: str = ""
    shade: str = ""
    hsn_code: str = ""
    quantity: float
    unit_price: float
    gst_percent: float
    discount: float = 0.0
    taxable_value: float
    gst_amount: float
    line_total: float


class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="party.id", index=True)
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoice.id", index=True)
    entry_date: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    entry_type: LedgerEntryType
    amount: float
    description: str = ""


class OwnerSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_name: str = "Owner"
    primary_phone: str = ""
    whatsapp_phone: str = ""
    report_start_hour: int = 7
    report_end_hour: int = 23
    enable_sms: bool = False
    enable_whatsapp: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DailyReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    report_date: str = Field(index=True, unique=True)
    period_start: datetime = Field(nullable=False)
    period_end: datetime = Field(nullable=False)
    invoice_count: int = 0
    total_sales: float = 0.0
    outstanding_ledger: float = 0.0
    low_stock_count: int = 0
    report_summary: str = ""
    report_path: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class NotificationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel: NotificationChannel = Field(default=NotificationChannel.internal)
    status: NotificationStatus = Field(default=NotificationStatus.pending)
    recipient_name: str = ""
    recipient_phone: str = ""
    message_type: str = ""
    message_body: str = ""
    file_url: str = ""
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoice.id", index=True)
    report_id: Optional[int] = Field(default=None, foreign_key="dailyreport.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)


class PaymentReminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    party_id: int = Field(foreign_key="party.id", index=True)
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoice.id", index=True)
    due_date: datetime = Field(nullable=False, index=True)
    amount_due: float = 0.0
    notes: str = ""
    status: ReminderStatus = Field(default=ReminderStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_sent_at: Optional[datetime] = None


class ExpenseEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entry_date: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    expense_type: ExpenseType = Field(default=ExpenseType.business)
    category: str = "Misc"
    vendor_name: str = ""
    payment_mode: str = "Cash"
    amount: float = 0.0
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
