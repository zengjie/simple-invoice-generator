from pydantic import BaseModel, Field
from datetime import date
from typing import List

class CompanyInfo(BaseModel):
    name: str
    tagline: str
    address: str

class CustomerInfo(BaseModel):
    name: str
    address_line1: str
    address_line2: str
    city_country: str

class BankDetails(BaseModel):
    beneficiary_bank: str
    swift_code: str
    beneficiary_name: str
    account_number: str
    bank_address: str

class InvoiceForm(BaseModel):
    invoice_date: date
    customer_info: CustomerInfo
    company_info: CompanyInfo
    bank_details: BankDetails

class InvoiceItem(BaseModel):
    item: str
    amount: float = Field(ge=0)
    comments: str = ""

class Invoice(BaseModel):
    form_data: InvoiceForm
    items: List[InvoiceItem]
    invoice_number: str
    total: float
