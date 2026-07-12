from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def round_money(value: float) -> float:
    return round(value + 1e-9, 2)


@dataclass
class InvoiceLineInput:
    product_id: int
    name: str
    quantity: float
    unit_price: float
    gst_percent: float
    discount: float = 0.0


@dataclass
class CalculatedInvoiceLine:
    product_id: int
    name: str
    quantity: float
    unit_price: float
    gst_percent: float
    discount: float
    taxable_value: float
    gst_amount: float
    line_total: float


@dataclass
class InvoiceSummary:
    subtotal: float
    discount_total: float
    taxable_total: float
    cgst: float
    sgst: float
    igst: float
    round_off: float
    grand_total: float


def calculate_invoice(
    lines: Iterable[InvoiceLineInput], bill_type: str, supply_type: str = "INTRA_STATE"
) -> tuple[list[CalculatedInvoiceLine], InvoiceSummary]:
    calculated_lines: list[CalculatedInvoiceLine] = []
    subtotal = 0.0
    discount_total = 0.0
    taxable_total = 0.0
    total_gst = 0.0

    normalized_bill_type = bill_type.upper()
    for line in lines:
        raw_subtotal = round_money(line.quantity * line.unit_price)
        discount = round_money(line.discount)
        taxable_value = round_money(max(raw_subtotal - discount, 0.0))
        gst_percent = line.gst_percent if normalized_bill_type == "GST" else 0.0
        gst_amount = round_money(taxable_value * gst_percent / 100.0)
        line_total = round_money(taxable_value + gst_amount)

        subtotal = round_money(subtotal + raw_subtotal)
        discount_total = round_money(discount_total + discount)
        taxable_total = round_money(taxable_total + taxable_value)
        total_gst = round_money(total_gst + gst_amount)

        calculated_lines.append(
            CalculatedInvoiceLine(
                product_id=line.product_id,
                name=line.name,
                quantity=line.quantity,
                unit_price=line.unit_price,
                gst_percent=gst_percent,
                discount=discount,
                taxable_value=taxable_value,
                gst_amount=gst_amount,
                line_total=line_total,
            )
        )

    normalized_supply_type = supply_type.upper()
    if normalized_bill_type == "GST" and normalized_supply_type == "INTER_STATE":
        cgst = 0.0
        sgst = 0.0
        igst = total_gst
    elif normalized_bill_type == "GST":
        cgst = round_money(total_gst / 2.0)
        sgst = round_money(total_gst / 2.0)
        igst = 0.0
    else:
        cgst = 0.0
        sgst = 0.0
        igst = 0.0
    raw_total = round_money(taxable_total + total_gst)
    rounded_total = round_money(round(raw_total))
    round_off = round_money(rounded_total - raw_total)

    return calculated_lines, InvoiceSummary(
        subtotal=subtotal,
        discount_total=discount_total,
        taxable_total=taxable_total,
        cgst=cgst,
        sgst=sgst,
        igst=igst,
        round_off=round_off,
        grand_total=rounded_total,
    )


def normalize_search_text(text: str) -> list[str]:
    return [token.strip().lower() for token in text.split() if token.strip()]


def build_product_search_text(
    name: str, brand: str | None, size: str | None, shade: str | None, category: str | None
) -> str:
    parts = [name, brand or "", size or "", shade or "", category or ""]
    return " ".join(part for part in parts if part).strip().lower()


def matches_product_search(query: str, haystack: str) -> bool:
    query_tokens = normalize_search_text(query)
    if not query_tokens:
        return True
    return all(token in haystack for token in query_tokens)
