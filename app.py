from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import re
from datetime import datetime

app = FastAPI(title="Invoice Extraction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractRequest(BaseModel):
    invoice_text: str

class ExtractResponse(BaseModel):
    invoice_no: Optional[str] = None
    date: Optional[str] = None
    vendor: Optional[str] = None
    amount: Optional[float] = None
    tax: Optional[float] = None
    currency: Optional[str] = None

def extract_field(pattern, text, flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1).strip()
    return None

def parse_money(value):
    if value is None:
        return None

    value = value.strip()
    value = re.sub(r"(?i)\b(?:rs\.?|inr)\b", "", value)
    value = value.replace(",", "").replace("₹", "").strip()

    try:
        return float(value)
    except ValueError:
        return None

def parse_date_to_iso(value):
    if value is None:
        return None

    value = value.strip()

    possible_formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
    ]

    for fmt in possible_formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None

@app.get("/")
def home():
    return {"message": "Invoice Extraction API is running"}

@app.post("/extract", response_model=ExtractResponse)
def extract_invoice(data: ExtractRequest):
    text = data.invoice_text

    invoice_no = extract_field(r"Invoice\s*No[:\-]?\s*(.+)", text)
    date_raw = extract_field(r"Date[:\-]?\s*([A-Za-z0-9\/\-. ]+)", text)
    vendor = extract_field(r"Vendor[:\-]?\s*(.+)", text)

    subtotal_raw = extract_field(
        r"Subtotal[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{1,2})?)",
        text
    )

    tax_raw = extract_field(
        r"(?:GST(?:\s*\(\d+%?\))?|Tax)[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{1,2})?)",
        text
    )

    currency = None
    if re.search(r"(?i)\bINR\b|Rs\.?|₹", text):
        currency = "INR"

    result = {
        "invoice_no": invoice_no,
        "date": parse_date_to_iso(date_raw),
        "vendor": vendor,
        "amount": parse_money(subtotal_raw),
        "tax": parse_money(tax_raw),
        "currency": currency,
    }

    return result