from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

class CompanyInfo(BaseModel):
    name: str
    tagline: str
    address_line1: str
    address_line2: Optional[str] = ""
    city_country: str

class CustomerInfo(BaseModel):
    name: str
    address_line1: str
    address_line2: Optional[str] = ""
    city_country: str

class BankDetails(BaseModel):
    beneficiary_bank: str
    swift_code: str
    beneficiary_name: str
    account_number: str
    bank_address: str

class InvoiceForm(BaseModel):
    invoice_date: date
    due_date: date
    customer_info: CustomerInfo
    company_info: CompanyInfo
    bank_details: BankDetails
    currency: str
    second_currency: Optional[str] = None
    exchange_rate: Optional[float] = None
    additional_notes: Optional[str] = None  # Add this line

class InvoiceItem(BaseModel):
    item: str
    amount: float
    comments: Optional[str] = None
    second_currency_amount: Optional[float] = None

class Invoice(BaseModel):
    form_data: InvoiceForm
    items: List[InvoiceItem]
    invoice_number: str
    total: float
    currency: str
    second_currency: Optional[str] = None
    second_currency_total: Optional[float] = None