"""
Generate NOVANEST_RESEARCH_PAPER.pdf with IEEE-style academic formatting,
Times-Roman typography, running headers/footers, styled tables, and metadata.
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Times-Roman", 8)
        self.setFillColor(colors.HexColor("#4B5563"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            header_text = "IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING / ICDE RESEARCH DRAFT"
            self.drawString(54, 750, header_text)
            self.setStrokeColor(colors.HexColor("#D1D5DB"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Running Footer (all pages)
        footer_text = f"NovaNest: Grounded Multi-Agent Decision Intelligence  |  Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 36, footer_text)
        self.setStrokeColor(colors.HexColor("#D1D5DB"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)

        self.restoreState()


def clean_md_inline(text):
    """Convert Markdown formatting to ReportLab XML tags."""
    # Escape XML entities first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'(?<!\*)\*(.*?)\*(?!\*)', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`(.*?)`', r'<font face="Courier" size="8.5" color="#1E293B">\1</font>', text)
    return text


def build_pdf():
    md_path = r"c:\Users\madha\OneDrive\Documents\NovaNest-main\NEWCHAGES\RESEARCH_PAPER\NOVANEST_RESEARCH_PAPER.md"
    pdf_path = r"c:\Users\madha\OneDrive\Documents\NovaNest-main\NEWCHAGES\RESEARCH_PAPER\NOVANEST_RESEARCH_PAPER.pdf"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Define custom academic typography styles
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=17,
        leading=21,
        alignment=1,  # Center
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8
    )

    style_meta = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13,
        alignment=1,  # Center
        textColor=colors.HexColor("#334155"),
        spaceAfter=2
    )

    style_abstract_box = ParagraphStyle(
        'DocAbstract',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=9,
        leading=12.5,
        alignment=4,  # Justified
        textColor=colors.HexColor("#1E293B"),
        leftIndent=24,
        rightIndent=24,
        spaceBefore=6,
        spaceAfter=6
    )

    style_keywords = ParagraphStyle(
        'DocKeywords',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=12,
        alignment=0,
        textColor=colors.HexColor("#0F172A"),
        leftIndent=24,
        rightIndent=24,
        spaceAfter=14
    )

    style_h1 = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=5,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13,
        alignment=4,  # Justified
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=2,
        spaceAfter=5
    )

    style_bullet = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=12.5,
        alignment=4,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=16,
        firstLineIndent=-10,
        spaceBefore=1,
        spaceAfter=2
    )

    style_table_cell = ParagraphStyle(
        'DocTableCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B")
    )

    style_table_header = ParagraphStyle(
        'DocTableHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    style_code = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=15,
        rightIndent=15,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []
    lines = md_text.split('\n')
    i = 0
    in_code = False
    code_buf = []

    while i < len(lines):
        line = lines[i]

        # Code block
        if line.strip().startswith('```'):
            if in_code:
                in_code = False
                raw_code = "\n".join(code_buf)
                story.append(Preformatted(raw_code, style_code))
                story.append(Spacer(1, 4))
                code_buf = []
            else:
                in_code = True
                code_buf = []
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Tables
        if line.strip().startswith('|') and '|' in line.strip()[1:]:
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl_lines.append(lines[i].strip())
                i += 1
            
            # Filter separator
            content_rows = [r for r in tbl_lines if not re.match(r'^\|[\s\-:]+(\|[\s\-:]+)+\|$', r)]
            if content_rows:
                table_data = []
                for r_idx, r_str in enumerate(content_rows):
                    cells = [c.strip() for c in r_str.strip('|').split('|')]
                    row_cells = []
                    is_h = (r_idx == 0)
                    for c_str in cells:
                        clean_c = clean_md_inline(c_str)
                        st = style_table_header if is_h else style_table_cell
                        row_cells.append(Paragraph(clean_c, st))
                    table_data.append(row_cells)

                # Normalize column lengths
                max_c = max(len(r) for r in table_data)
                for r in table_data:
                    while len(r) < max_c:
                        r.append(Paragraph("", style_table_cell))

                # Available width is 504 pt (letter width 612 - 108 margin)
                col_w = 504.0 / max_c
                t = Table(table_data, colWidths=[col_w] * max_c)
                
                t_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F2937")),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ]
                # Alternating row colors
                for r_idx in range(1, len(table_data)):
                    if r_idx % 2 == 1:
                        t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor("#F9FAFB")))
                
                t.setStyle(TableStyle(t_style))
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 6))
            continue

        # Document Title
        if line.startswith('# '):
            story.append(Spacer(1, 6))
            story.append(Paragraph(clean_md_inline(line[2:].strip()), style_title))
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Authors / Metadata
        if line.startswith('**Author**:'):
            story.append(Paragraph(clean_md_inline(line.strip()), style_meta))
            i += 1
            continue
        if line.startswith('**Affiliation**:') or line.startswith('**Date**:') or line.startswith('**Target Venue**:'):
            story.append(Paragraph(clean_md_inline(line.strip()), style_meta))
            i += 1
            continue

        # Section Headings (## Section)
        if line.startswith('## '):
            story.append(Paragraph(clean_md_inline(line[3:].strip()), style_h1))
            i += 1
            continue

        # Subsection Headings (### Subsection)
        if line.startswith('### '):
            if 'Abstract' in line:
                i += 1
                continue
            story.append(Paragraph(clean_md_inline(line[4:].strip()), style_h2))
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            story.append(Spacer(1, 2))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceBefore=4, spaceAfter=6))
            i += 1
            continue

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Keywords line
        if line.startswith('**Keywords**:'):
            story.append(Paragraph(clean_md_inline(line.strip()), style_keywords))
            i += 1
            continue

        # Bullet list
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            txt = "&bull;  " + clean_md_inline(line.strip()[2:].strip())
            story.append(Paragraph(txt, style_bullet))
            i += 1
            continue

        # Numbered list
        m_num = re.match(r'^(\d+)[\.\)]\s+(.*)$', line.strip())
        if m_num:
            num_str, itm = m_num.groups()
            txt = f"<b>{num_str}.</b>  " + clean_md_inline(itm.strip())
            story.append(Paragraph(txt, style_bullet))
            i += 1
            continue

        # Abstract text
        if 'Modern on-demand food delivery platforms' in line:
            abs_text = "<b><i>Abstract</i>—" + clean_md_inline(line.strip()) + "</b>"
            story.append(Paragraph(abs_text, style_abstract_box))
            i += 1
            continue

        # Standard paragraph
        p_text = clean_md_inline(line.strip())
        story.append(Paragraph(p_text, style_body))
        i += 1

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")


if __name__ == "__main__":
    build_pdf()
