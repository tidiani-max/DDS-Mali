"""
Generate PDF e-certificates using ReportLab.
"""
import io
import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from django.conf import settings


def generate_certificate(registration):
    """
    Generate a PDF certificate for a webinar registration.
    Returns bytes of the PDF.
    """
    buffer = io.BytesIO()
    w, h = landscape(A4)

    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # ── Background gradient feel ──────────────────────────
    c.setFillColorRGB(0.04, 0.12, 0.28)   # dark navy
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Gold border outer
    c.setStrokeColorRGB(0.788, 0.635, 0.153)
    c.setLineWidth(6)
    c.rect(18, 18, w-36, h-36, fill=0, stroke=1)

    # Gold border inner
    c.setLineWidth(1.5)
    c.rect(26, 26, w-52, h-52, fill=0, stroke=1)

    # ── Header area ───────────────────────────────────────
    # DDS logo text
    c.setFillColorRGB(0.788, 0.635, 0.153)  # gold
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(w/2, h-58, 'DIAWARA DIGITAL & SOFTWARE')

    c.setFillColorRGB(0.220, 0.757, 0.957)  # cyan
    c.setFont('Helvetica', 10)
    c.drawCentredString(w/2, h-74, 'Empowering Africa & Southeast Asia')

    # Horizontal divider
    c.setStrokeColorRGB(0.788, 0.635, 0.153)
    c.setLineWidth(1)
    c.line(60, h-84, w-60, h-84)

    # Certificate of Completion
    c.setFillColorRGB(0.788, 0.635, 0.153)
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(w/2, h-140, 'CERTIFICATE OF COMPLETION')

    # This certifies that
    c.setFillColorRGB(1, 1, 1)
    c.setFont('Helvetica', 14)
    c.drawCentredString(w/2, h-176, 'This is to certify that')

    # Participant name
    c.setFillColorRGB(0.220, 0.757, 0.957)  # cyan
    c.setFont('Helvetica-Bold', 32)
    c.drawCentredString(w/2, h-218, registration.full_name.upper())

    # Name underline
    c.setStrokeColorRGB(0.220, 0.757, 0.957)
    c.setLineWidth(1.5)
    name_w = c.stringWidth(registration.full_name.upper(), 'Helvetica-Bold', 32)
    c.line(w/2 - name_w/2, h-224, w/2 + name_w/2, h-224)

    # Has successfully completed
    c.setFillColorRGB(1, 1, 1)
    c.setFont('Helvetica', 14)
    c.drawCentredString(w/2, h-252, 'has successfully completed the online webinar')

    # Webinar title
    c.setFillColorRGB(0.788, 0.635, 0.153)
    c.setFont('Helvetica-Bold', 20)
    title = registration.webinar.title
    # Wrap long titles
    if len(title) > 55:
        mid = title.rfind(' ', 0, 55)
        c.drawCentredString(w/2, h-282, f'"{title[:mid]}"')
        c.drawCentredString(w/2, h-306, f'"{title[mid+1:]}"')
        date_y = h-336
    else:
        c.drawCentredString(w/2, h-282, f'"{title}"')
        date_y = h-316

    # Date
    c.setFillColorRGB(1, 1, 1)
    c.setFont('Helvetica', 13)
    date_str = registration.webinar.date.strftime('%B %d, %Y')
    c.drawCentredString(w/2, date_y, f'Held on {date_str}')

    # Speaker
    c.setFont('Helvetica-Oblique', 12)
    c.setFillColorRGB(0.8, 0.8, 0.8)
    c.drawCentredString(w/2, date_y-24,
        f'Speaker: {registration.webinar.speaker_name} – {registration.webinar.speaker_role}'
        + (f' at {registration.webinar.speaker_company}' if registration.webinar.speaker_company else ''))

    # ── Bottom section ────────────────────────────────────
    bottom_y = 80

    # Signature line - left
    c.setStrokeColorRGB(0.788, 0.635, 0.153)
    c.setLineWidth(1)
    c.line(80, bottom_y + 30, 240, bottom_y + 30)
    c.setFillColorRGB(0.788, 0.635, 0.153)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(160, bottom_y + 16, 'Cheick Tidiani Diawara')
    c.setFillColorRGB(1, 1, 1)
    c.setFont('Helvetica', 10)
    c.drawCentredString(160, bottom_y + 4, 'Founder, DDS Mali')

    # Certificate code - center
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.setFont('Helvetica', 8)
    c.drawCentredString(w/2, bottom_y + 16, f'Certificate ID: {str(registration.certificate_code)[:18].upper()}')
    c.drawCentredString(w/2, bottom_y + 5, 'Verify at: dds-mali.com/verify')

    # QR code - right
    qr_data = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/webinars/certificate/{registration.certificate_code}/"
    qr_img = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    from reportlab.lib.utils import ImageReader
    qr_reader = ImageReader(qr_buffer)
    c.drawImage(qr_reader, w - 130, bottom_y - 10, width=80, height=80, mask='auto')
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.setFont('Helvetica', 8)
    c.drawCentredString(w - 90, bottom_y - 14, 'Scan to verify')

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
