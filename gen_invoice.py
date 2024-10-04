from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch
from models import Invoice

def generate_invoice(output_file, invoice: Invoice):
    doc = SimpleDocTemplate(output_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
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
                   <br/><br/><font size=10>{invoice.form_data.company_info.address}</font>""", styles['Right'])]
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
        [invoice.form_data.customer_info.address_line2, "", f"DUE DATE: {invoice.form_data.invoice_date}"],
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
    products_data = [["ITEM", "AMOUNT", "COMMENTS"]]
    for item in invoice.items:
        products_data.append([item.item, f"${item.amount:,.2f}", item.comments])

    products_table = Table(products_data, colWidths=[2.5*inch, 1*inch, 2.8*inch])
    products_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(products_table)

    # Totals
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"<font size=14><b>TOTAL DUE: US${invoice.total:,.2f}</b></font>", styles['Right']))
    elements.append(Spacer(1, 1*inch))

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
    doc.build(elements)

# Update the test function
if __name__ == "__main__":
    from datetime import date
    from models import InvoiceForm, CustomerInfo, CompanyInfo, BankDetails, Invoice, InvoiceItem

    test_form = InvoiceForm(
        invoice_date=date(2024, 5, 10),
        customer_info=CustomerInfo(
            name="Test Customer",
            address_line1="123 Test Street",
            address_line2="Apt 4B",
            city_country="Test City, Test Country"
        ),
        company_info=CompanyInfo(
            name="Lebao Interactive Technology Co., Ltd.",
            tagline="Your Global Game Dev Partner",
            address="Office E1003, Sanlitun SOHO, Chaoyang, Beijing, China"
        ),
        bank_details=BankDetails(
            beneficiary_bank="CHINA MERCHANTS BANK H.O. SHENZHEN",
            swift_code="CMBCCNBS",
            beneficiary_name="Lebao Interactive Technology Co., Ltd.",
            account_number="110959177110001",
            bank_address="China Merchants Bank Tower NO.7088, Shennan Boulevard, Shenzhen, China"
        )
    )

    test_invoice = Invoice(
        form_data=test_form,
        items=[
            InvoiceItem(item="Game Development Services", amount=5000.00, comments="Project milestone 1"),
            InvoiceItem(item="Art Assets", amount=2000.00, comments="Character designs"),
        ],
        invoice_number="INV-20240510-001",
        total=7000.00
    )

    generate_invoice('test_invoice.pdf', test_invoice)
    print("test_invoice.pdf has been created successfully.")