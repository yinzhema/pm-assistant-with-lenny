"""
Export PM documents to Markdown, Excel, and Word (.docx).
"""
import io
import re

from markdownify import markdownify
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def export_to_markdown(document_html: str, title: str = "") -> str:
    """
    Convert Tiptap HTML to clean GitHub-Flavored Markdown.
    Tables are rendered as GFM pipe tables.
    """
    md = markdownify(document_html, heading_style="ATX", bullets="-")
    # Collapse excessive blank lines
    md = re.sub(r"\n{3,}", "\n\n", md)
    if title:
        md = f"# {title}\n\n{md.lstrip()}"
    return md.strip()


def export_to_excel(document_html: str, title: str = "Document") -> bytes:
    """
    Export all HTML tables from the document to an Excel workbook.
    Non-table content is exported to a 'Summary' sheet as plain text.

    Returns raw bytes suitable for sending as a file download.
    """
    soup = BeautifulSoup(document_html, "lxml")
    wb = openpyxl.Workbook()

    # ── Summary sheet (plain text) ────────────────────────────────────────────
    summary_ws = wb.active
    summary_ws.title = "Summary"
    summary_ws.column_dimensions["A"].width = 80

    plain_text = soup.get_text(separator="\n", strip=True)
    for i, line in enumerate(plain_text.splitlines(), start=1):
        if line.strip():
            summary_ws.cell(row=i, column=1, value=line.strip())

    # ── One sheet per table ───────────────────────────────────────────────────
    tables = soup.find_all("table")
    for t_idx, table in enumerate(tables, start=1):
        # Derive sheet name from preceding heading, or use generic name
        sheet_name = _preceding_heading(table) or f"Table {t_idx}"
        sheet_name = sheet_name[:31]  # Excel sheet name limit
        ws = wb.create_sheet(title=sheet_name)

        header_fill = PatternFill("solid", fgColor="1F2937")
        header_font = Font(color="FFFFFF", bold=True)
        alt_fill    = PatternFill("solid", fgColor="F9FAFB")

        rows = table.find_all("tr")
        for r_idx, row in enumerate(rows, start=1):
            cells = row.find_all(["th", "td"])
            is_header = row.find("th") is not None
            for c_idx, cell in enumerate(cells, start=1):
                value = cell.get_text(strip=True)
                xl_cell = ws.cell(row=r_idx, column=c_idx, value=value)
                xl_cell.alignment = Alignment(wrap_text=True, vertical="top")
                if is_header:
                    xl_cell.fill = header_fill
                    xl_cell.font = header_font
                elif r_idx % 2 == 0:
                    xl_cell.fill = alt_fill

            # Auto-width (approximate)
            for col in ws.columns:
                max_len = max((len(str(c.value or "")) for c in col), default=10)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _preceding_heading(tag) -> str:
    """Walk backwards in the DOM to find the nearest heading before a table."""
    for sibling in tag.find_previous_siblings():
        if sibling.name in ("h1", "h2", "h3", "h4"):
            return sibling.get_text(strip=True)
    return ""


def export_to_docx(document_html: str, title: str = "Document") -> bytes:
    """
    Convert Tiptap HTML to a formatted Word (.docx) document.
    Preserves headings, paragraphs, bullet lists, and tables.

    Returns raw bytes suitable for sending as a file download.
    """
    doc = DocxDocument()

    # ── Document title ────────────────────────────────────────────────────────
    if title:
        heading = doc.add_heading(title, level=0)
        heading.runs[0].font.color.rgb = RGBColor(0x11, 0x18, 0x27)

    soup = BeautifulSoup(document_html, "lxml")
    body = soup.find("body") or soup

    # ── Walk top-level elements ───────────────────────────────────────────────
    for el in body.children:
        if not hasattr(el, "name") or el.name is None:
            continue
        _render_element(doc, el)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _render_element(doc: DocxDocument, el) -> None:
    """Recursively render a BeautifulSoup element into the Word document."""
    tag = el.name

    # Headings
    if tag in ("h1", "h2", "h3", "h4"):
        level = int(tag[1])
        p = doc.add_heading(el.get_text(strip=True), level=level)
        p.runs[0].font.color.rgb = RGBColor(0x11, 0x18, 0x27)

    # Paragraphs
    elif tag == "p":
        text = el.get_text(strip=True)
        if text:
            doc.add_paragraph(text)

    # Unordered lists
    elif tag == "ul":
        for li in el.find_all("li", recursive=False):
            doc.add_paragraph(li.get_text(strip=True), style="List Bullet")

    # Ordered lists
    elif tag == "ol":
        for li in el.find_all("li", recursive=False):
            doc.add_paragraph(li.get_text(strip=True), style="List Number")

    # Tables
    elif tag == "table":
        rows = el.find_all("tr")
        if not rows:
            return
        # Determine column count from first row
        first_row_cells = rows[0].find_all(["th", "td"])
        col_count = len(first_row_cells)
        if col_count == 0:
            return

        tbl = doc.add_table(rows=0, cols=col_count)
        tbl.style = "Table Grid"

        for r_idx, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            row_cells = tbl.add_row().cells
            for c_idx, cell in enumerate(cells):
                if c_idx >= col_count:
                    break
                row_cells[c_idx].text = cell.get_text(strip=True)
                # Style header row
                if r_idx == 0:
                    run = row_cells[c_idx].paragraphs[0].runs
                    if run:
                        run[0].bold = True
                        run[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    # Dark background for header
                    from docx.oxml.ns import qn
                    from docx.oxml import OxmlElement
                    tc = row_cells[c_idx]._tc
                    tcPr = tc.get_or_add_tcPr()
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:color"), "auto")
                    shd.set(qn("w:fill"), "1F2937")
                    tcPr.append(shd)

    # Divs / sections — recurse into children
    elif tag in ("div", "section", "article"):
        for child in el.children:
            if hasattr(child, "name") and child.name:
                _render_element(doc, child)
