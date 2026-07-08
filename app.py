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


# Request body format
class InvoiceRequest(BaseModel):
    invoice_text: str



def parse_date(date_string):

    formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                date_string.strip(),
                fmt
            ).strftime("%Y-%m-%d")
        except:
            pass

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


    # Invoice number
    invoice_match = re.search(
        r"(Invoice\s*No|Invoice Number|INV)\s*[:#]?\s*([A-Z0-9\-]+)",
        text,
        re.I
    )

    if invoice_match:
        result["invoice_no"] = invoice_match.group(2)



    # Date
    date_match = re.search(
        r"(Date)\s*[:\-]?\s*(\d{1,2}\s+\w+\s+\d{4})",
        text,
        re.I
    )

    if date_match:
        result["date"] = parse_date(
            date_match.group(2)
        )



    # Vendor
    vendor_match = re.search(
        r"Vendor\s*[:\-]?\s*(.+)",
        text,
        re.I
    )

    if vendor_match:
        result["vendor"] = vendor_match.group(1).strip()



    # Subtotal / Amount
    amount_match = re.search(
        r"(Subtotal|Sub Total|Amount)\s*[:\-]?\s*(?:Rs\.?|INR)?\s*([\d,]+\.\d{2})",
        text,
        re.I
    )


    if amount_match:
        amount = amount_match.group(2)
        result["amount"] = float(
            amount.replace(",", "")
        )



    # Tax
    tax_match = re.search(
        r"(GST|Tax|VAT).*?(?:Rs\.?|INR)?\s*([\d,]+\.\d{2})",
        text,
        re.I
    )


    if tax_match:
        tax = tax_match.group(2)

        result["tax"] = float(
            tax.replace(",", "")
        )


    return result



@app.post("/extract")
def extract_invoice_api(
    request: InvoiceRequest
):

    return extract_invoice(
        request.invoice_text
    )



@app.get("/")
def home():
    return {
        "message": "Invoice Extraction API running"
    }