import io
import csv
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ExportService:
    @staticmethod
    def generate_csv(headers, data_rows):
        """Generates a CSV string buffer."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in data_rows:
            writer.writerow(row)
        return output.getvalue().encode('utf-8')

    @staticmethod
    def generate_excel(title, headers, data_rows, summary_data=None):
        """Generates a styled Excel workbook."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title[:30]
        ws.views.sheetView[0].showGridLines = True

        # Styles
        title_font = Font(name='Segoe UI', size=16, bold=True, color='0D6EFD')
        header_font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
        sub_fill = PatternFill(start_color='F1F5F9', end_color='F1F5F9', fill_type='solid')
        data_font = Font(name='Segoe UI', size=10)
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        current_row = 1
        
        # Title
        ws.cell(row=current_row, column=1, value=f"COVID-19 HEALTHCARE DASHBOARD - {title.upper()}").font = title_font
        current_row += 1
        ws.cell(row=current_row, column=1, value=f"Generated On: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}").font = Font(name='Segoe UI', size=9, italic=True, color='64748B')
        current_row += 2

        # Summary Metrics if present
        if summary_data:
            ws.cell(row=current_row, column=1, value="SUMMARY OVERVIEW").font = Font(name='Segoe UI', size=11, bold=True, color='0F172A')
            current_row += 1
            for k, v in summary_data.items():
                c1 = ws.cell(row=current_row, column=1, value=k)
                c2 = ws.cell(row=current_row, column=2, value=str(v))
                c1.font = Font(name='Segoe UI', size=10, bold=True)
                c2.font = data_font
                c1.fill = sub_fill
                c2.fill = sub_fill
                current_row += 1
            current_row += 1

        # Table Header
        header_row_idx = current_row
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=header_row_idx, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = thin_border
        current_row += 1

        # Data Rows
        for row in data_rows:
            for col_idx, val in enumerate(row, 1):
                cell = ws.cell(row=current_row, column=col_idx, value=str(val) if val is not None else '-')
                cell.font = data_font
                cell.border = thin_border
                if isinstance(val, (int, float)):
                    cell.alignment = Alignment(horizontal='right')
                else:
                    cell.alignment = Alignment(horizontal='left')
            current_row += 1

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_pdf(title, headers, data_rows, summary_data=None):
        """Generates a professional healthcare-themed PDF report using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=4
        )
        sub_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=14
        )
        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor('#1E293B'),
            leading=10
        )
        header_cell_style = ParagraphStyle(
            'HeaderCellText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=colors.white,
            leading=10,
            alignment=1
        )

        # Header Section
        elements.append(Paragraph(f"COVID-19 Visualization Dashboard - {title}", title_style))
        elements.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')} | Official Public Health Report", sub_style))

        # Summary Grid if available
        if summary_data:
            summary_table_data = []
            row_chunk = []
            for k, v in summary_data.items():
                row_chunk.append(Paragraph(f"<b>{k}:</b> {v}", cell_style))
                if len(row_chunk) == 4:
                    summary_table_data.append(row_chunk)
                    row_chunk = []
            if row_chunk:
                while len(row_chunk) < 4:
                    row_chunk.append(Paragraph("", cell_style))
                summary_table_data.append(row_chunk)

            s_table = Table(summary_table_data, colWidths=[180, 180, 180, 180])
            s_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(s_table)
            elements.append(Spacer(1, 14))

        # Main Data Table
        table_content = []
        # Header row
        table_content.append([Paragraph(h, header_cell_style) for h in headers])
        
        # Limit rows to 150 for PDF stability if too huge, or show all
        for r in data_rows[:150]:
            row_items = []
            for item in r:
                text = str(item) if item is not None else '-'
                row_items.append(Paragraph(text, cell_style))
            table_content.append(row_items)

        # Calculate dynamic column widths
        col_count = len(headers)
        available_width = 730  # Landscape letter width minus margins
        col_width = available_width / col_count

        main_table = Table(table_content, colWidths=[col_width] * col_count, repeatRows=1)
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(main_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
