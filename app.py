from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import re
from datetime import datetime


app = FastAPI()


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request schema
class InvoiceRequest(BaseModel):
    invoice_text: str



def parse_date(date_string):

    formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%d %B, %Y",
        "%d %b, %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%d",
        "%d/%m/%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                date_string.strip(),
                fmt
            ).strftime("%Y-%m-%d")

        except ValueError:
            continue

    return None



def extract_invoice(text):

    result = {
        "invoice_no": None,
        "date": None,
        "vendor": None,
        "amount": None,
        "tax": None,
        "currency": "INR"
    }


    # -------------------------
    # Invoice Number
    # -------------------------
    invoice_match = re.search(
        r"(?:Invoice\s*(?:No|Number|ID)?|Inv)\s*[:#\-]?\s*([A-Z0-9\-]+)",
        text,
        re.I
    )

    if invoice_match:
        result["invoice_no"] = invoice_match.group(1)



    # -------------------------
    # Date
    # -------------------------
    date_match = re.search(
        r"(?:Invoice\s*Date|Date)\s*[:\-]?\s*"
        r"(\d{1,2}\s+\w+\s+\d{4}|"
        r"\d{1,2}\s+\w+,\s+\d{4}|"
        r"\w+\s+\d{1,2},\s+\d{4}|"
        r"\d{4}-\d{2}-\d{2}|"
        r"\d{1,2}/\d{1,2}/\d{4})",
        text,
        re.I
    )

    if date_match:
        result["date"] = parse_date(
            date_match.group(1)
        )



    # -------------------------
    # Vendor
    # -------------------------
    vendor_match = re.search(
        r"(?:Vendor|Supplier|Seller)\s*[:\-]?\s*"
        r"(.*?)(?=\s+(?:Subtotal|Sub Total|Amount|GST|Tax|VAT|TOTAL|Total|$))",
        text,
        re.I
    )

    if vendor_match:
        result["vendor"] = vendor_match.group(1).strip()



    # -------------------------
    # Subtotal / Amount
    # -------------------------
    amount_match = re.search(
        r"(?:Subtotal|Sub Total|Amount)\s*[:\-]?\s*"
        r"(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d+)?)",
        text,
        re.I
    )

    if amount_match:
        result["amount"] = float(
            amount_match.group(1).replace(",", "")
        )



    # -------------------------
    # Tax / GST
    # -------------------------
    tax_match = re.search(
        r"(?:GST|Tax|VAT)"
        r"(?:\s*\(\s*\d+%\s*\))?"
        r"\s*[:\-]?\s*"
        r"(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d+)?)",
        text,
        re.I
    )

    if tax_match:
        result["tax"] = float(
            tax_match.group(1).replace(",", "")
        )



    return result



@app.post("/extract")
def extract_invoice_api(request: InvoiceRequest):

    return extract_invoice(
        request.invoice_text
    )



@app.get("/")
def home():

    return {
        "message": "Invoice Extraction API running"
    }