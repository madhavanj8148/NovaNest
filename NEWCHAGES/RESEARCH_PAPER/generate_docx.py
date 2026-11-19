"""
Generate NOVANEST_RESEARCH_PAPER.docx from NOVANEST_RESEARCH_PAPER.md
with academic IEEE-style formatting, clean typography, styled tables, and metadata.
"""

import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def create_research_docx():
    md_path = r"c:\Users\madha\OneDrive\Documents\NovaNest-main\NEWCHAGES\RESEARCH_PAPER\NOVANEST_RESEARCH_PAPER.md"
    docx_path = r"c:\Users\madha\OneDrive\Documents\NovaNest-main\NEWCHAGES\RESEARCH_PAPER\NOVANEST_RESEARCH_PAPER.docx"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = docx.Document()

    # Set 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Set base font to Times New Roman
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(10.5)
    font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    lines = md_text.split('\n')
    i = 0
    in_abstract = False
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                in_code_block = False
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run('\n'.join(code_lines))
                run.font.name = 'Courier New'
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(0x33, 0x33, 0x55)
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Markdown Table Parsing
        if line.strip().startswith('|') and '|' in line.strip()[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            
            # Filter out separator line (e.g. |---|---|)
            content_rows = [r for r in table_lines if not re.match(r'^\|[\s\-:]+(\|[\s\-:]+)+\|$', r)]
            if content_rows:
                parsed_rows = []
                for row_str in content_rows:
                    cells = [c.strip() for c in row_str.strip('|').split('|')]
                    # Clean bold/italic markdown
                    cells_clean = [re.sub(r'\*\*(.*?)\*\*', r'\1', c) for c in cells]
                    parsed_rows.append(cells_clean)

                num_cols = max(len(r) for r in parsed_rows)
                # Normalize row lengths
                for r in parsed_rows:
                    while len(r) < num_cols:
                        r.append('')

                # Add table to doc
                tbl = doc.add_table(rows=len(parsed_rows), cols=num_cols)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                tbl.autofit = False

                for r_idx, row_data in enumerate(parsed_rows):
                    row = tbl.rows[r_idx]
                    is_header = (r_idx == 0)
                    for c_idx, cell_value in enumerate(row_data):
                        cell = row.cells[c_idx]
                        cell.text = cell_value
                        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
                        
                        # Style text
                        p = cell.paragraphs[0]
                        p.paragraph_format.space_before = Pt(2)
                        p.paragraph_format.space_after = Pt(2)
                        if p.runs:
                            run = p.runs[0]
                            run.font.name = 'Times New Roman'
                            if is_header:
                                run.font.size = Pt(9.5)
                                run.font.bold = True
                                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                                set_cell_background(cell, "1F2937")  # Dark slate
                            else:
                                run.font.size = Pt(8.5)
                                run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
                                if r_idx % 2 == 1:
                                    set_cell_background(cell, "F9FAFB")  # Light gray zebra
                                else:
                                    set_cell_background(cell, "FFFFFF")

                # Add spacing after table
                sp_p = doc.add_paragraph()
                sp_p.paragraph_format.space_before = Pt(0)
                sp_p.paragraph_format.space_after = Pt(6)
            continue

        # Document Title (# Title)
        if line.startswith('# '):
            title_text = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(title_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
            i += 1
            continue

        # Authors / Metadata
        if line.startswith('**Author**:'):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(line.strip())
            run.font.size = Pt(10.5)
            run.font.bold = True
            i += 1
            continue

        if line.startswith('**Affiliation**:') or line.startswith('**Date**:') or line.startswith('**Target Venue**:'):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(line.strip())
            run.font.size = Pt(9.5)
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)
            i += 1
            continue

        # Section Headings (## Section)
        if line.startswith('## '):
            sec_text = line[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(sec_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
            i += 1
            continue

        # Subsection Headings (### Subsection)
        if line.startswith('### '):
            subsec_text = line[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(subsec_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x37, 0x41, 0x51)
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            i += 1
            continue

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Abstract block handling
        if line.startswith('**Keywords**:'):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run(line.strip())
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            run.font.bold = True
            i += 1
            continue

        # Bullet lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            bullet_text = line.strip()[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            # Simple bold parsing
            parts = re.split(r'(\*\*.*?\*\*)', bullet_text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    p.add_run(part)
            i += 1
            continue

        # Numbered lists (e.g. 1. Item)
        m_num = re.match(r'^(\d+)[\.\)]\s+(.*)$', line.strip())
        if m_num:
            num_str, item_text = m_num.groups()
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            parts = re.split(r'(\*\*.*?\*\*)', item_text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    p.add_run(part)
            i += 1
            continue

        # Normal Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        # Check if this is Abstract body
        if 'Modern on-demand food delivery platforms' in line:
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            run_lbl = p.add_run("Abstract—")
            run_lbl.bold = True
            run_lbl.font.size = Pt(9.5)
            run_body = p.add_run(line.strip())
            run_body.font.size = Pt(9.5)
            run_body.italic = True
            i += 1
            continue

        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', line.strip())
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                run = p.add_run(part[2:-2])
                run.bold = True
            elif part.startswith('*') and part.endswith('*') and len(part) > 2:
                run = p.add_run(part[1:-1])
                run.italic = True
            elif part.startswith('`') and part.endswith('`'):
                run = p.add_run(part[1:-1])
                run.font.name = 'Courier New'
                run.font.size = Pt(9.5)
            else:
                p.add_run(part)

        i += 1

    doc.save(docx_path)
    print(f"Successfully generated DOCX at: {docx_path} ({os.path.getsize(docx_path)} bytes)")

if __name__ == "__main__":
    create_research_docx()
