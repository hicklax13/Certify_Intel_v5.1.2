"""
Generate PDF with all outstanding todos for Certify Intel
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

def generate_todo_pdf():
    # Output path
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Outstanding_Tasks_Report.pdf")

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d')
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=20,
        textColor=colors.HexColor('#2563eb')
    )

    subsection_style = ParagraphStyle(
        'SubsectionTitle',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#4b5563')
    )

    normal_style = styles['Normal']

    story = []

    # Title
    story.append(Paragraph("Certify Intel - Outstanding Tasks Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                          ParagraphStyle('Date', parent=normal_style, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3*inch))

    # Executive Summary
    story.append(Paragraph("Executive Summary", section_style))
    summary_data = [
        ['Category', 'Total', 'Completed', 'Pending', 'Blocked'],
        ['Development Tasks', '83', '80', '2', '1'],
        ['API Configuration', '8', '1', '7', '0'],
        ['Personal Tasks', '15', '2', '13', '0'],
        ['GRAND TOTAL', '106', '83', '22', '1'],
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 25),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))

    # Section 1: Development Tasks (Blocked/Pending)
    story.append(Paragraph("1. Development Tasks - Pending/Blocked", section_style))

    story.append(Paragraph("Desktop App (v5.0.3) - BLOCKED", subsection_style))
    dev_data = [
        ['ID', 'Task', 'Status', 'Priority'],
        ['5.0.3-001', 'Fix .env path in PyInstaller desktop app', 'BLOCKED', 'HIGH'],
        ['5.0.3-002', 'Test installed desktop app end-to-end', 'PENDING', 'HIGH'],
        ['5.0.3-003', 'Auto-updater implementation testing', 'PENDING', 'LOW'],
    ]
    dev_table = Table(dev_data, colWidths=[1*inch, 3.5*inch, 1*inch, 1*inch])
    dev_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 22),
        ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#fef2f2')),  # BLOCKED row
    ]))
    story.append(dev_table)
    story.append(Spacer(1, 0.2*inch))

    # Section 2: API Configuration Tasks
    story.append(Paragraph("2. API Configuration Tasks", section_style))

    story.append(Paragraph("Critical APIs (Required for Full Functionality)", subsection_style))
    critical_data = [
        ['ID', 'Task', 'Status', 'Instructions'],
        ['API-001', 'Google Gemini API Key', 'COMPLETED', 'Added to .env - Hybrid AI active'],
    ]
    critical_table = Table(critical_data, colWidths=[0.8*inch, 2*inch, 1*inch, 2.7*inch])
    critical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 22),
        ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#dcfce7')),
    ]))
    story.append(critical_table)
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("Optional News APIs (Free Tiers Available)", subsection_style))
    news_data = [
        ['ID', 'Task', 'Status', 'Free Tier', 'URL'],
        ['API-002', 'GNews API', 'PENDING', '100 req/day', 'gnews.io'],
        ['API-003', 'MediaStack API', 'PENDING', '500 req/month', 'mediastack.com'],
        ['API-004', 'NewsData.io API', 'PENDING', '200 req/day', 'newsdata.io'],
        ['API-005', 'Firecrawl API', 'PENDING', '500 credits/mo', 'firecrawl.dev'],
    ]
    news_table = Table(news_data, colWidths=[0.8*inch, 1.5*inch, 0.9*inch, 1.2*inch, 2.1*inch])
    news_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 22),
    ]))
    story.append(news_table)
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("Notification Configuration", subsection_style))
    notif_data = [
        ['ID', 'Task', 'Status', 'Priority', 'Required Config'],
        ['NOTIF-001', 'Email (SMTP)', 'PENDING', 'MEDIUM', 'SMTP_HOST, PORT, USER, PASSWORD'],
        ['NOTIF-002', 'Slack Webhook', 'PENDING', 'LOW', 'SLACK_WEBHOOK_URL'],
        ['NOTIF-003', 'Teams Webhook', 'PENDING', 'LOW', 'TEAMS_WEBHOOK_URL'],
    ]
    notif_table = Table(notif_data, colWidths=[0.9*inch, 1.3*inch, 0.9*inch, 0.9*inch, 2.5*inch])
    notif_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 22),
    ]))
    story.append(notif_table)

    # Page break for personal tasks
    story.append(PageBreak())

    # Section 3: Personal To-Do List
    story.append(Paragraph("3. Personal To-Do List (Connor Hickey)", section_style))

    story.append(Paragraph("News API Registration", subsection_style))
    personal_news = [
        ['#', 'Task', 'Status', 'URL'],
        ['1', 'Register for GNews API', 'PENDING', 'https://gnews.io'],
        ['2', 'Register for MediaStack API', 'PENDING', 'https://mediastack.com'],
        ['3', 'Register for NewsData.io API', 'PENDING', 'https://newsdata.io'],
        ['4', 'Register for Firecrawl API', 'PENDING', 'https://firecrawl.dev'],
        ['5', 'Register for NewsAPI.org', 'PENDING', 'https://newsapi.org'],
    ]
    personal_news_table = Table(personal_news, colWidths=[0.4*inch, 2.5*inch, 1*inch, 2.6*inch])
    personal_news_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 20),
    ]))
    story.append(personal_news_table)
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("Data API Registration", subsection_style))
    data_api = [
        ['#', 'Task', 'Status', 'Notes'],
        ['1', 'SEC EDGAR access', 'DONE', 'Free, no registration needed'],
        ['2', 'USPTO Patent API', 'DONE', 'Free, no registration needed'],
        ['3', 'KLAS API (if available)', 'PENDING', 'May require subscription'],
        ['4', 'G2/Capterra API', 'PENDING', 'May require partnership'],
    ]
    data_api_table = Table(data_api, colWidths=[0.4*inch, 2*inch, 1*inch, 3.1*inch])
    data_api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 20),
        ('BACKGROUND', (2, 1), (2, 2), colors.HexColor('#dcfce7')),  # DONE rows
    ]))
    story.append(data_api_table)
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("Notification & Alert Setup", subsection_style))
    notif_setup = [
        ['#', 'Task', 'Status', 'Priority', 'Required Info'],
        ['1', 'Configure SMTP Email', 'PENDING', 'HIGH', 'SMTP server, credentials'],
        ['2', 'Set up Slack Webhook', 'PENDING', 'MEDIUM', 'Slack workspace admin'],
        ['3', 'Set up Teams Webhook', 'PENDING', 'MEDIUM', 'Teams channel access'],
        ['4', 'Configure Twilio SMS', 'PENDING', 'LOW', 'Twilio account, phone #s'],
        ['5', 'PagerDuty Integration', 'PENDING', 'LOW', 'PagerDuty subscription'],
    ]
    notif_setup_table = Table(notif_setup, colWidths=[0.4*inch, 1.8*inch, 0.9*inch, 0.9*inch, 2.5*inch])
    notif_setup_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#db2777')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 20),
    ]))
    story.append(notif_setup_table)
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("Infrastructure & Security", subsection_style))
    infra = [
        ['#', 'Task', 'Status', 'Priority'],
        ['1', 'Set up production database (PostgreSQL)', 'PENDING', 'HIGH'],
        ['2', 'Configure SSL/TLS certificates', 'PENDING', 'HIGH'],
        ['3', 'Set up backup automation', 'PENDING', 'MEDIUM'],
        ['4', 'Configure rate limiting', 'PENDING', 'MEDIUM'],
        ['5', 'Set up monitoring (Datadog/New Relic)', 'PENDING', 'LOW'],
    ]
    infra_table = Table(infra, colWidths=[0.4*inch, 3.5*inch, 1*inch, 1.6*inch])
    infra_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea580c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 20),
    ]))
    story.append(infra_table)

    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("---", ParagraphStyle('Divider', parent=normal_style, alignment=TA_CENTER)))
    story.append(Paragraph("Certify Intel v5.0.7 | Generated by Claude Opus 4.5",
                          ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER,
                                        fontSize=9, textColor=colors.HexColor('#6b7280'))))

    # Build PDF
    doc.build(story)
    print(f"PDF generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_todo_pdf()
