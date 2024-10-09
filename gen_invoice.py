import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch
from models import Invoice
from io import BytesIO
from currency_utils import format_currency

def invoice_to_json(invoice: Invoice):
    return json.dumps({
        "invoice_number": invoice.invoice_number,
        "total": invoice.total,
        "currency": invoice.currency,
        "second_currency": invoice.second_currency,
        "second_currency_total": invoice.second_currency_total,
        "invoice_date": invoice.form_data.invoice_date.isoformat(),
        "customer_info": invoice.form_data.customer_info.dict(),
        "company_info": invoice.form_data.company_info.dict(),
        "bank_details": invoice.form_data.bank_details.dict(),
        "items": [item.dict() for item in invoice.items],
        "exchange_rate": invoice.form_data.exchange_rate,
    })

class InvoiceCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self.invoice_data = kwargs.pop('invoice_data', {})
        super().__init__(*args, **kwargs)

    def showPage(self):
        self.setSubject(self.invoice_data)
        super().showPage()

    def save(self):
        self.setSubject(self.invoice_data)
        super().save()

def generate_invoice(output, invoice: Invoice):
    buffer = BytesIO()
    invoice_json = invoice_to_json(invoice)

    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

    # Header
    header_data = [
        [Paragraph("<font size=24><b>INVOICE</b></font>", styles['Left']), 
         Paragraph(f"""<font size=14><b>{invoice.form_data.company_info.name}</b></font>
                   <br/><font size=12>{invoice.form_data.company_info.tagline}</font>
                   <br/><br/><font size=10>{invoice.form_data.company_info.address_line1}</font>
                   <br/><font size=10>{invoice.form_data.company_info.address_line2}</font>
                   <br/><font size=10>{invoice.form_data.company_info.city_country}</font>""", styles['Right'])]
    ]
    header = Table(header_data, colWidths=[2*inch, 4.5*inch])
    header.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))

    # Divider line
    elements.append(Paragraph("<hr width='100%'/>", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))

    # Invoice details
    invoice_data = [
        [Paragraph("<b>BILL TO:</b>", styles['Normal']), "", Paragraph("<b>INVOICE DETAILS</b>", styles['Right'])],
        [Paragraph(f"<font size=12><b>{invoice.form_data.customer_info.name}</b></font>", styles['Normal']), "", Paragraph(f"<b>INVOICE NO: {invoice.invoice_number}</b>", styles['Right'])],
        [invoice.form_data.customer_info.address_line1, "", f"INVOICE DATE: {invoice.form_data.invoice_date}"],
        [invoice.form_data.customer_info.address_line2, "", f"DUE DATE: {invoice.form_data.due_date}"],
        [invoice.form_data.customer_info.city_country, "", ""]
    ]
    invoice_table = Table(invoice_data, colWidths=[2.8*inch, 1*inch, 2.6*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.5*inch))

    # Products table
    products_data = [["ITEM", f"AMOUNT ({invoice.currency})"]]
    if invoice.second_currency:
        products_data[0].append(f"AMOUNT ({invoice.second_currency})")
    products_data[0].append("COMMENTS")

    for item in invoice.items:
        row = [
            Paragraph(item.item, styles['BodyText']),
            Paragraph(f"{item.amount:,.2f}", styles['Right'])
        ]
        if invoice.second_currency:
            row.append(Paragraph(f"{item.second_currency_amount:,.2f}", styles['Right']))
        row.append(Paragraph(item.comments, styles['BodyText']))
        products_data.append(row)

    if invoice.second_currency:
        col_widths = [2.1*inch, 1.1*inch, 1.1*inch, 2.3*inch]
    else:
        col_widths = [2.5*inch, 1.3*inch, 2.8*inch]

    products_table = Table(products_data, colWidths=col_widths)
    products_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('FONTNAME', (1, 1), (1, -1), 'Courier'),
        ('FONTSIZE', (1, 1), (1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make header row bold
    ]))
    elements.append(products_table)

    # Totals
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"<font size=14><b>TOTAL DUE: <font face='Courier'>{format_currency(invoice.total, invoice.currency)}</font></b></font>", styles['Right']))
    elements.append(Spacer(1, 0.1*inch))  # Add a small spacer
    if invoice.second_currency and invoice.second_currency_total:
        elements.append(Paragraph(f"<font size=12><b><font face='Courier'>({format_currency(invoice.second_currency_total, invoice.second_currency)})</font></b></font>", styles['Right']))
        elements.append(Spacer(1, 0.1*inch))  # Add a small spacer
    elements.append(Paragraph(f"<font size=10 color='gray'>This invoice should be paid in {invoice.currency}.</font>", styles['Right']))
    elements.append(Spacer(1, 0.25*inch))

    # Exchange rate
    if invoice.form_data.exchange_rate:
        elements.append(Paragraph(f"Exchange rate: 1 {invoice.currency} = {invoice.form_data.exchange_rate} {invoice.second_currency}", styles['Right']))
    elements.append(Spacer(1, 0.5*inch))

    # Bank details
    bank_details = invoice.form_data.bank_details

    bank_details_data = [
        [Paragraph("<font size=12><b>BANK DETAILS</b></font>", styles['Normal']), ""],
        ["", ""],
        ["Beneficiary's Bank:", bank_details.beneficiary_bank],
        ["SWIFT Code:", bank_details.swift_code],
        ["Beneficiary's Name:", bank_details.beneficiary_name],
        ["Beneficiary's A/C No.:", bank_details.account_number],
        ["Bank Address:", bank_details.bank_address]
    ]
    
    bank_details_table = Table(bank_details_data, colWidths=[1.5*inch, 5*inch])
    bank_details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(bank_details_table)

    # Generate the PDF
    doc.build(elements, canvasmaker=lambda *args, **kwargs: InvoiceCanvas(*args, **kwargs, invoice_data=invoice_json))

    # If output is a file path, write to file; if it's BytesIO, write to it directly
    if isinstance(output, (str, bytes, os.PathLike)):
        with open(output, "wb") as f:
            f.write(buffer.getvalue())
    elif isinstance(output, BytesIO):
        output.write(buffer.getvalue())
    else:
        raise TypeError("output must be a file path or BytesIO object")

def verify_pdf_metadata(pdf_file):
    from PyPDF2 import PdfReader
    reader = PdfReader(pdf_file)
    if "/Subject" in reader.metadata:
        print("Invoice data found in PDF metadata:")
        print(reader.metadata["/Subject"])
    else:
        print("Invoice data not found in PDF metadata")

# Update the test function
if __name__ == "__main__":
    from datetime import date
    from models import InvoiceForm, CustomerInfo, CompanyInfo, BankDetails, Invoice, InvoiceItem
    test_form = InvoiceForm(
        invoice_date=date(2023, 7, 15),
        due_date=date(2023, 8, 15),
        customer_info=CustomerInfo(
            name="Acme Corporation",
            address_line1="789 Fictional Avenue",
            address_line2="Suite 101",
            city_country="Imaginary City, Wonderland"
        ),
        company_info=CompanyInfo(
            name="TechnoVision Solutions Inc.",
            tagline="Innovating for Tomorrow",
            address_line1="456 Digital Boulevard",
            address_line2="Tech Park",
            city_country="Silicon Valley, USA"
        ),
        bank_details=BankDetails(
            beneficiary_bank="Global Trust Bank",
            swift_code="GTBKUS33",
            beneficiary_name="TechnoVision Solutions Inc.",
            account_number="987654321000",
            bank_address="1 Financial Plaza, New York, NY 10005, USA"
        ),
        currency="USD",
        second_currency="EUR",
        exchange_rate=0.85
    )

    test_invoice = Invoice(
        form_data=test_form,
        items=[
            InvoiceItem(item="Game Development Services", amount=5000.00, comments="Project milestone 1", second_currency_amount=4250.00),
            InvoiceItem(item="Art Assets", amount=2000.00, comments="Character designs", second_currency_amount=1700.00),
        ],
        invoice_number="INV-20240510-001",
        total=7000.00,
        currency="USD",
        second_currency="EUR",
        second_currency_total=5950.00
    )

    generate_invoice('test_invoice.pdf', test_invoice)
    print("test_invoice.pdf has been created successfully.")

    verify_pdf_metadata('test_invoice.pdf')