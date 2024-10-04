from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from fasthx import Jinja
from datetime import datetime, timedelta
from io import BytesIO
from gen_invoice import generate_invoice
from models import BankDetails, InvoiceForm, Invoice, CompanyInfo, CustomerInfo, InvoiceItem
import json

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Create a FastHX Jinja instance
jinja = Jinja(templates)

async def get_invoice(
    customer_name: str = Form(...),
    invoice_date: str = Form(...),
    due_date: str = Form(...),  # Add this line
    address_line1: str = Form(...),
    address_line2: str = Form(None),
    city_country: str = Form(...),
    company_name: str = Form(...),
    company_tagline: str = Form(...),
    company_address: str = Form(...),
    bank_name: str = Form(...),
    swift_code: str = Form(...),
    account_number: str = Form(...),
    bank_address: str = Form(...),
    items: str = Form(...)
) -> Invoice:
    form_data = InvoiceForm(
        invoice_date=datetime.strptime(invoice_date, "%Y-%m-%d").date(),
        due_date=datetime.strptime(due_date, "%Y-%m-%d").date(),  # Add this line
        customer_info=CustomerInfo(
            name=customer_name,
            address_line1=address_line1,
            address_line2=address_line2 or "",
            city_country=city_country,
        ),
        company_info=CompanyInfo(
            name=company_name,
            tagline=company_tagline,
            address=company_address,
        ),
        bank_details=BankDetails(
            beneficiary_bank=bank_name,
            swift_code=swift_code,
            beneficiary_name=company_name,
            account_number=account_number,
            bank_address=bank_address
        )
    )
    
    invoice_items = [InvoiceItem(**item) for item in json.loads(items)]
    total = sum(item.amount for item in invoice_items)
    
    return Invoice(
        form_data=form_data,
        items=invoice_items,
        invoice_number=datetime.now().strftime("%Y%m%d%H%M%S"),
        total=total
    )

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
    })

@app.post("/generate-invoice")
@jinja.hx("invoice.html")
async def generate_invoice_html(
    request: Request,
    invoice: Invoice = Depends(get_invoice)
):
    context = {
        "request": request,
        "invoice": invoice
    }
    
    return templates.TemplateResponse("invoice.html", context)

@app.post("/download-invoice")
async def download_invoice(invoice: Invoice = Depends(get_invoice)):
    try:
        pdf_buffer = BytesIO()
        generate_invoice(pdf_buffer, invoice)
        pdf_buffer.seek(0)
        
        filename = f"invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/customer-form")
async def customer_form(request: Request):
    return templates.TemplateResponse("customer_form.html", {"request": request})

@app.get("/company-form")
async def company_form(request: Request):
    return templates.TemplateResponse("company_form.html", {"request": request})

@app.get("/bank-form")
async def bank_form(request: Request):
    return templates.TemplateResponse("bank_form.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)