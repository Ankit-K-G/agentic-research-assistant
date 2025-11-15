# backend/tools/pdf_tools.py
import io
import logging
logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(pdf_bytes) -> str:
    try:
        import pdfplumber
    except Exception as e:
        logger.warning("pdfplumber not installed: %s", e)
        return ""

    try:
        import io as _io
        with pdfplumber.open(_io.BytesIO(pdf_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n\n".join(pages)
    except Exception as e:
        logger.exception("Failed to parse PDF bytes: %s", e)
        return ""

def ocr_image_bytes(image_bytes) -> str:
    try:
        from PIL import Image
        import pytesseract, io as _io
    except Exception as e:
        logger.warning("OCR dependencies missing: %s", e)
        return ""

    try:
        img = Image.open(_io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logger.exception("OCR failed: %s", e)
        return ""

# ------------------------
# New helpers below:
# ------------------------
def markdown_from_paper(paper: dict) -> str:
    title = paper.get("title", "Untitled")
    abstract = paper.get("abstract", "")
    results = paper.get("results", {})
    critique = paper.get("critique", {})

    md_lines = []
    md_lines.append(f"# {title}\n")
    md_lines.append("## Abstract\n")
    md_lines.append(abstract + "\n")
    md_lines.append("## Results\n")
    import json
    md_lines.append("```json")
    md_lines.append(json.dumps(results, indent=2))
    md_lines.append("```\n")
    md_lines.append("## Critic\n")
    md_lines.append("```json")
    md_lines.append(json.dumps(critique, indent=2))
    md_lines.append("```\n")

    meta = paper.get("meta")
    if meta:
        md_lines.append("## Meta\n")
        md_lines.append("```json")
        md_lines.append(json.dumps(meta, indent=2))
        md_lines.append("```\n")

    return "\n".join(md_lines)

def generate_pdf_from_text(text: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
    except Exception as e:
        logger.exception("reportlab is required for PDF generation: %s", e)
        raise

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    left_margin = inch
    top = height - inch
    line_height = 12

    import textwrap
    max_chars_per_line = 95
    y = top
    for paragraph in text.split("\n\n"):
        wrapped = textwrap.wrap(paragraph, width=max_chars_per_line)
        if not wrapped:
            y -= line_height
        for ln in wrapped:
            if y < inch:
                c.showPage()
                y = top
            c.drawString(left_margin, y, ln)
            y -= line_height
        y -= line_height

    c.save()
    buffer.seek(0)
    return buffer.read()
