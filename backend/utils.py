from datetime import datetime

from fastapi import HTTPException
from fpdf import FPDF
from starlette import status


def throw_server_error(message: str):
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, message)


def throw_bad_request(message: str):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, message)


def throw_not_found(message: str):
    raise HTTPException(status.HTTP_404_NOT_FOUND, message)


def throw_failed_dependency(message: str):
    raise HTTPException(status.HTTP_424_FAILED_DEPENDENCY, message)


def throw_credential_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_invoice(order_id: int, product: str, quantity: int) -> bytes:
    # ✅ Создаём PDF
    pdf = FPDF()
    pdf.add_page()

    # Заголовок
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 10, "INVOICE", ln=True, align="C")
    pdf.ln(10)

    # Детали
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Order ID: #{order_id}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    # Линия
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Товары
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Order Details:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Product: {product}", ln=True)
    pdf.cell(0, 10, f"Quantity: {quantity}", ln=True)
    pdf.ln(5)

    # ✅ Получаем bytes
    pdf_bytes = pdf.output()
    return pdf_bytes
