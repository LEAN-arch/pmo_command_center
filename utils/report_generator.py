# pmo_command_center/utils/report_generator.py
"""
This utility module contains the function to generate a standardized
Microsoft PowerPoint (.pptx) project status report.

It leverages the python-pptx library to create a professional, one-page summary
that can be automatically generated, saving significant time for the PMO.
"""
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
import pandas as pd
from datetime import date

def set_cell_text(cell, text, bold=False, font_size=10):
    """Helper function to set text and formatting in a table cell."""
    p = cell.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = str(text)
    font = run.font
    font.name = 'Calibri'
    font.size = Pt(font_size)
    font.bold = bold
    font.color.rgb = RGBColor(0, 0, 0)
    cell.vertical_anchor = 'middle'

def generate_project_status_report(project_details: dict, financials_df: pd.DataFrame, milestones_df: pd.DataFrame, risks_df: pd.DataFrame) -> io.BytesIO:
    """
    Generates a one-page PowerPoint status report for a given project.

    Args:
        project_details: A dictionary containing the project's main attributes.
        financials_df: DataFrame of financial data for the project.
        milestones_df: DataFrame of milestones for the project.
        risks_df: DataFrame of risks for the project.

    Returns:
        A BytesIO buffer containing the generated .pptx file.
    """
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)

    # --- Slide Title ---
    title = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(15), Inches(0.75))
    p = title.text_frame.paragraphs[0]
    p.text = f"Project Status Report: {project_details.get('name', 'N/A')}"
    p.font.name = 'Calibri'
    p.font.size = Pt(32)
    p.font.bold = True

    # --- Subtitle / Date ---
    subtitle = slide.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(15), Inches(0.5))
    p_sub = subtitle.text_frame.paragraphs[0]
    p_sub.text = f"Report Date: {date.today().strftime('%Y-%m-%d')} | Project Manager: {project_details.get('pm', 'N/A')}"
    p_sub.font.name = 'Calibri'
    p_sub.font.size = Pt(14)

    # --- Overall Health Status Box ---
    health_status = project_details.get('health_status', 'N/A')
    status_colors = {
        "On Track": RGBColor(44, 160, 44),
        "Needs Monitoring": RGBColor(255, 127, 14),
        "At Risk": RGBColor(214, 39, 40),
        "Completed": RGBColor(127, 127, 127)
    }
    status_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(13.5), Inches(0.25), Inches(2), Inches(0.7))
    status_box.text = f"Status: {health_status}"
    status_box.text_frame.paragraphs[0].font.bold = True
    status_box.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    status_box.fill.solid()
    status_box.fill.fore_color.rgb = status_colors.get(health_status, RGBColor(127, 127, 127))
    status_box.line.fill.background()

    # --- Financial Summary Table ---
    shape = slide.shapes.add_table(4, 2, Inches(0.5), Inches(1.5), Inches(4.5), Inches(2))
    table = shape.table
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(2.0)

    budget = project_details.get('budget_usd', 0)
    actuals = project_details.get('actuals_usd', 0)
    eac = project_details.get('eac_usd', 0) # EAC from our new data model
    variance = actuals - budget

    set_cell_text(table.cell(0, 0), "Financial Summary", bold=True, font_size=14)
    set_cell_text(table.cell(1, 0), "Budget (BAC):", bold=True)
    set_cell_text(table.cell(1, 1), f"${budget:,.0f}")
    set_cell_text(table.cell(2, 0), "Actuals (AC):", bold=True)
    set_cell_text(table.cell(2, 1), f"${actuals:,.0f}")
    set_cell_text(table.cell(3, 0), "Estimate at Completion (EAC):", bold=True)
    set_cell_text(table.cell(3, 1), f"${eac:,.0f}")

    # --- EVM Summary Table ---
    shape = slide.shapes.add_table(4, 2, Inches(0.5), Inches(3.7), Inches(4.5), Inches(2))
    table = shape.table
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(2.0)

    cpi = project_details.get('cpi', 0)
    spi = project_details.get('spi', 0)

    set_cell_text(table.cell(0, 0), "Earned Value Metrics", bold=True, font_size=14)
    set_cell_text(table.cell(1, 0), "Planned Value (PV):", bold=True)
    set_cell_text(table.cell(1, 1), f"${project_details.get('pv_usd', 0):,.0f}")
    set_cell_text(table.cell(2, 0), "Cost Performance Index (CPI):", bold=True)
    set_cell_text(table.cell(2, 1), f"{cpi:.2f}")
    set_cell_text(table.cell(3, 0), "Schedule Performance Index (SPI):", bold=True)
    set_cell_text(table.cell(3, 1), f"{spi:.2f}")

    # --- Key Upcoming Milestones Table ---
    shape = slide.shapes.add_table(5, 3, Inches(5.5), Inches(1.5), Inches(10), Inches(3))
    table = shape.table
    table.columns[0].width = Inches(4.5)
    table.columns[1].width = Inches(2.5)
    table.columns[2].width = Inches(3.0)

    set_cell_text(table.cell(0, 0), "Key Upcoming Milestones", bold=True, font_size=14)
    set_cell_text(table.cell(0, 1), "Due Date", bold=True)
    set_cell_text(table.cell(0, 2), "Status", bold=True)

    upcoming_milestones = milestones_df[milestones_df['status'] != 'Completed'].head(4)
    for i, row in upcoming_milestones.iterrows():
        set_cell_text(table.cell(i + 1, 0), row['milestone'])
        set_cell_text(table.cell(i + 1, 1), row['due_date'])
        set_cell_text(table.cell(i + 1, 2), row['status'])

    # --- Top Risks Table ---
    shape = slide.shapes.add_table(4, 3, Inches(5.5), Inches(4.7), Inches(10), Inches(2.5))
    table = shape.table
    table.columns[0].width = Inches(4.5)
    table.columns[1].width = Inches(2.5)
    table.columns[2].width = Inches(3.0)

    set_cell_text(table.cell(0, 0), "Top Risks", bold=True, font_size=14)
    set_cell_text(table.cell(0, 1), "Owner", bold=True)
    set_cell_text(table.cell(0, 2), "Status", bold=True)

    top_risks = risks_df.sort_values(by='due_date').head(3) # Simple sort, could be by RPN
    for i, row in top_risks.iterrows():
        set_cell_text(table.cell(i + 1, 0), row['description'])
        set_cell_text(table.cell(i + 1, 1), row['owner'])
        set_cell_text(table.cell(i + 1, 2), row['status'])

    # Save presentation to a memory buffer
    ppt_buffer = io.BytesIO()
    prs.save(ppt_buffer)
    ppt_buffer.seek(0)
    return ppt_buffer
