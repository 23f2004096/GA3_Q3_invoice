import os
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()


# Configure Gemini
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


app = FastAPI()


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Input schema
class InvoiceRequest(BaseModel):
    invoice_text: str



# Output schema
class InvoiceResponse(BaseModel):
    invoice_no: str | None
    date: str | None
    vendor: str | None
    amount: float | None
    tax: float | None
    currency: str | None



@app.post("/extract", response_model=InvoiceResponse)
def extract_invoice(data: InvoiceRequest):

    prompt = f"""
You are an invoice extraction system.

Extract information from this invoice.

Return ONLY valid JSON.

Rules:
- Always include all six keys.
- Missing values should be null.
- Date must be YYYY-MM-DD.
- amount means subtotal before tax.
- tax means only tax amount.
- currency should be INR if rupees are used.

JSON format:

{{
 "invoice_no": null,
 "date": null,
 "vendor": null,
 "amount": null,
 "tax": null,
 "currency": null
}}


Invoice text:

{data.invoice_text}
"""


    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )


    result = json.loads(response.text)


    # Ensure all keys exist
    final_result = {
        "invoice_no": result.get("invoice_no"),
        "date": result.get("date"),
        "vendor": result.get("vendor"),
        "amount": result.get("amount"),
        "tax": result.get("tax"),
        "currency": result.get("currency") or "INR"
    }


    return final_result