from __future__ import annotations

from datetime import datetime

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine, func, select

from .models import ExpenseEntry, OwnerSettings, Party, PartyType, Product
from .settings import SETTINGS


connect_args = {"check_same_thread": False} if SETTINGS.database_url.startswith("sqlite") else {}
engine = create_engine(SETTINGS.database_url, connect_args=connect_args, pool_pre_ping=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    migrate_db()


def migrate_db() -> None:
    if not SETTINGS.database_url.startswith("sqlite"):
        return
    with engine.begin() as connection:
        invoice_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info('invoice')")).fetchall()
        }
        if "supply_type" not in invoice_columns:
            connection.execute(text("ALTER TABLE invoice ADD COLUMN supply_type VARCHAR NOT NULL DEFAULT 'INTRA_STATE'"))
        if "igst" not in invoice_columns:
            connection.execute(text("ALTER TABLE invoice ADD COLUMN igst FLOAT NOT NULL DEFAULT 0"))
        if "round_off" not in invoice_columns:
            connection.execute(text("ALTER TABLE invoice ADD COLUMN round_off FLOAT NOT NULL DEFAULT 0"))

        invoice_rows = connection.execute(
            text("SELECT id, taxable_total, cgst, sgst, igst, grand_total FROM invoice")
        ).fetchall()
        for row in invoice_rows:
            raw_total = round((row[1] or 0) + (row[2] or 0) + (row[3] or 0) + (row[4] or 0), 2)
            rounded_total = round(raw_total)
            round_off = round(rounded_total - raw_total, 2)
            if round(float(row[5] or 0), 2) != round(float(rounded_total), 2):
                connection.execute(
                    text("UPDATE invoice SET grand_total = :grand_total, round_off = :round_off WHERE id = :id"),
                    {"grand_total": float(rounded_total), "round_off": float(round_off), "id": row[0]},
                )


def get_session():
    with Session(engine) as session:
        yield session


def seed_data() -> None:
    with Session(engine) as session:
        product_count = session.exec(select(func.count(Product.id))).one()
        if product_count == 0:
            session.add_all(
                [
                    Product(
                        name="Tractor Emulsion",
                        brand="Asian Paints",
                        category="Paint",
                        size="20L",
                        shade="Ultra White",
                        hsn_code="3209",
                        gst_percent=18.0,
                        selling_price=4500.0,
                        stock_quantity=12,
                        low_stock_threshold=3,
                        barcode="AP-TRAC-20-UW",
                    ),
                    Product(
                        name="Apex Exterior",
                        brand="Asian Paints",
                        category="Paint",
                        size="10L",
                        shade="Snow Drift",
                        hsn_code="3209",
                        gst_percent=18.0,
                        selling_price=3650.0,
                        stock_quantity=8,
                        low_stock_threshold=2,
                        barcode="AP-APEX-10-SD",
                    ),
                    Product(
                        name="Wall Putty",
                        brand="Birla White",
                        category="Putty",
                        size="20KG",
                        shade="White",
                        hsn_code="3214",
                        gst_percent=18.0,
                        selling_price=720.0,
                        stock_quantity=15,
                        low_stock_threshold=5,
                        barcode="BW-PUTTY-20",
                    ),
                    Product(
                        name="Primer",
                        brand="Nerolac",
                        category="Primer",
                        size="4L",
                        shade="Grey",
                        hsn_code="3208",
                        gst_percent=18.0,
                        selling_price=980.0,
                        stock_quantity=10,
                        low_stock_threshold=4,
                        barcode="NER-PRI-4-GR",
                    ),
                    Product(
                        name="Ultra White",
                        brand="Rallison",
                        category="Paint",
                        size="1L",
                        shade="Ultra White",
                        hsn_code="3209",
                        gst_percent=18.0,
                        selling_price=280.0,
                        stock_quantity=20,
                        low_stock_threshold=6,
                        barcode="RAL-UW-1L-280",
                    ),
                ]
            )

        party_count = session.exec(select(func.count(Party.id))).one()
        if party_count == 0:
            session.add_all(
                [
                    Party(
                        name="Walk-in Customer",
                        phone="",
                        address="",
                        gstin="",
                        party_type=PartyType.customer,
                        running_balance=0.0,
                        created_at=datetime.utcnow(),
                    ),
                    Party(
                        name="Raju Painter",
                        phone="+91 98111 11111",
                        address="Railway Colony",
                        gstin="",
                        party_type=PartyType.painter,
                        running_balance=3500.0,
                        created_at=datetime.utcnow(),
                    ),
                ]
            )

        settings_count = session.exec(select(func.count(OwnerSettings.id))).one()
        if settings_count == 0:
            session.add(
                OwnerSettings(
                    owner_name="Anklikar Owner",
                    primary_phone="9918602602",
                    whatsapp_phone="9918602602",
                    report_start_hour=7,
                    report_end_hour=23,
                    enable_sms=False,
                    enable_whatsapp=False,
                )
            )

        expense_count = session.exec(select(func.count(ExpenseEntry.id))).one()
        if expense_count == 0:
            session.add_all(
                [
                    ExpenseEntry(
                        category="Shop Rent",
                        vendor_name="Landlord",
                        payment_mode="Bank Transfer",
                        amount=12000.0,
                        notes="Monthly rent sample entry",
                    ),
                    ExpenseEntry(
                        category="Electricity",
                        vendor_name="KESCO",
                        payment_mode="UPI",
                        amount=3250.0,
                        notes="Monthly electricity sample entry",
                    ),
                ]
            )

        session.commit()
