import os
import tempfile
from fastapi import FastAPI, Request, Form, Depends, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from fasthx import Jinja
from datetime import datetime
from io import BytesIO
from gen_invoice import generate_invoice
from models import (
    BankDetails,
    InvoiceForm,
    Invoice,
    CompanyInfo,
    CustomerInfo,
    InvoiceItem,
)
import json
from PyPDF2 import PdfReader
from currency_utils import format_currency, get_currency_options
from typing import Optional

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Create a FastHX Jinja instance
jinja = Jinja(templates)

# Generate a version based on the last modification time of script.js
script_version = os.environ.get("SCRIPT_VERSION", "1")

async def get_invoice(
    customer_name: str = Form(...),
    invoice_date: str = Form(...),
    due_date: str = Form(...),
    address_line1: str = Form(...),
    address_line2: str = Form(None),
    city_country: str = Form(...),
    company_name: str = Form(...),
    company_tagline: str = Form(...),
    company_address_line1: str = Form(...),
    company_address_line2: str = Form(None),
    company_city_country: str = Form(...),
    bank_name: str = Form(...),
    swift_code: str = Form(...),
    account_number: str = Form(...),
    bank_address: str = Form(...),
    items: str = Form(...),
    currency: str = Form(...),  # Add this line
    second_currency: str = Form(None),
    exchange_rate: Optional[str] = Form(None),  # Change this line
) -> Invoice:
    exchange_rate_float = None
    if exchange_rate:
        try:
            exchange_rate_float = float(exchange_rate)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid exchange rate")

    form_data = InvoiceForm(
        invoice_date=datetime.strptime(invoice_date, "%Y-%m-%d").date(),
        due_date=datetime.strptime(due_date, "%Y-%m-%d").date(),
        customer_info=CustomerInfo(
            name=customer_name,
            address_line1=address_line1,
            address_line2=address_line2 or "",
            city_country=city_country,
        ),
        company_info=CompanyInfo(
            name=company_name,
            tagline=company_tagline,
            address_line1=company_address_line1,
            address_line2=company_address_line2 or "",
            city_country=company_city_country,
        ),
        bank_details=BankDetails(
            beneficiary_bank=bank_name,
            swift_code=swift_code,
            beneficiary_name=company_name,
            account_number=account_number,
            bank_address=bank_address,
        ),
        currency=currency,  # Add this line
        second_currency=second_currency,
        exchange_rate=exchange_rate_float,
    )

    invoice_items = []
    for item in json.loads(items):
        invoice_item = InvoiceItem(**item)
        if second_currency and exchange_rate_float:
            invoice_item.second_currency_amount = invoice_item.amount * exchange_rate_float
        invoice_items.append(invoice_item)

    total = sum(item.amount for item in invoice_items)
    second_currency_total = None
    if second_currency and exchange_rate_float:
        second_currency_total = total * exchange_rate_float

    return Invoice(
        form_data=form_data,
        items=invoice_items,
        invoice_number=datetime.now().strftime("%Y%m%d%H%M%S"),
        total=total,
        currency=currency,  # Add this line
        second_currency=second_currency,
        second_currency_total=second_currency_total,
    )


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "currency_options": get_currency_options(),  # Add this line
            "script_version": int(datetime.now().timestamp()),  # Add this line
        },
    )


@app.post("/generate-invoice")
@jinja.hx("invoice.html")
async def generate_invoice_html(
    request: Request, invoice: Invoice = Depends(get_invoice)
):
    context = {
        "request": request,
        "invoice": invoice,
        "format_currency": format_currency  # Add this line
    }

    return templates.TemplateResponse("invoice.html", context)


@app.post("/download-invoice")
async def download_invoice(invoice: Invoice = Depends(get_invoice)):
    try:
        pdf_buffer = BytesIO()
        generate_invoice(pdf_buffer, invoice)
        pdf_buffer.seek(0)

        filename = f"invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            pdf_buffer, media_type="application/pdf", headers=headers
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF files are allowed",
        }

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()

        try:
            reader = PdfReader(temp_file.name)
            metadata = reader.metadata
            if "/Subject" in metadata:
                invoice_data = json.loads(metadata["/Subject"])
                return {"success": True, "data": invoice_data}
            else:
                return {
                    "success": False,
                    "message": "No invoice data found in the PDF's Subject metadata",
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": "Invalid JSON data in PDF's Subject metadata",
            }
        except Exception as e:
            return {"success": False, "message": f"Error processing PDF: {str(e)}"}
        finally:
            os.unlink(temp_file.name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
