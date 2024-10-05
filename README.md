# Invoice Generator

This project is an Invoice Generator web application built with FastAPI and FastHX. It allows users to create, duplicate, and download customized invoices as PDF files.

## Features

- Generate invoices with custom fields
- Duplicate existing invoices for quick editing
- Download invoices as PDF files
- Responsive web interface

## Technologies Used

- Python 3.12
- FastAPI
- FastHX
- Jinja2
- ReportLab
- PyPDF2

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/zengjie/invoice-generator.git
   cd invoice-generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

2. Open your web browser and navigate to `http://localhost:8000`

3. Fill in the invoice details in the form and click "Generate Invoice" to create and download your PDF invoice.

4. To duplicate an existing invoice, click the "Duplicate" button next to the invoice you want to copy. This will create a new invoice with the same details, which you can then edit as needed.

## Project Structure

- `main.py`: Main application file containing FastAPI routes and logic
- `gen_invoice.py`: Module for generating PDF invoices using ReportLab
- `models.py`: Data models for the application
- `templates/`: Directory containing HTML templates
- `static/`: Directory for static files (CSS, JavaScript, images)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
