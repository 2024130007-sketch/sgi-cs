from io import BytesIO
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


def excel(titulo, columnas, filas):
    wb = Workbook()
    ws = wb.active
    ws.title = titulo[:30]
    ws.append(columnas)
    for f in filas:
        ws.append(list(f))
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def pdf(titulo, columnas, filas):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
    tabla = Table([columnas] + [list(map(str, f)) for f in filas], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    doc.build([Paragraph(titulo, getSampleStyleSheet()["Title"]), tabla])
    return buf.getvalue()