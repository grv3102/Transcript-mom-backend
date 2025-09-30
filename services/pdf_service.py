from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, Any, List
from datetime import datetime

def generate_pdf(data: Dict[str, Any]) -> BytesIO:
    """Generate PDF document from structured meeting data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Build document content
    story = []
    
    # Title
    story.append(Paragraph("Meeting Minutes", title_style))
    story.append(Spacer(1, 20))
    
    # Metadata
    processed_at = data.get('processed_at', datetime.utcnow().isoformat())
    model_used = data.get('model_used', 'AI Assistant')
    
    story.append(Paragraph(f"<b>Generated on:</b> {processed_at}", styles['Normal']))
    story.append(Paragraph(f"<b>Processed by:</b> {model_used}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Participants
    participants = data.get('participants', [])
    if participants:
        story.append(Paragraph("Participants", heading_style))
        for participant in participants:
            story.append(Paragraph(f"• {participant}", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Summary
    summary = data.get('summary', [])
    if summary:
        story.append(Paragraph("Summary", heading_style))
        if isinstance(summary, list):
            for point in summary:
                story.append(Paragraph(f"• {point}", styles['Normal']))
        else:
            story.append(Paragraph(str(summary), styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Agenda Items
    agenda = data.get('agenda', [])
    if agenda:
        story.append(Paragraph("Agenda Items", heading_style))
        for item in agenda:
            story.append(Paragraph(f"• {item}", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Topics Discussed
    topics = data.get('topics', [])
    if topics:
        story.append(Paragraph("Topics Discussed", heading_style))
        for topic in topics:
            if isinstance(topic, dict):
                topic_name = topic.get('topic', '')
                confidence = topic.get('confidence', 0)
                story.append(Paragraph(f"• {topic_name} (Confidence: {confidence:.1%})", styles['Normal']))
            else:
                story.append(Paragraph(f"• {topic}", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Decisions Made
    decisions = data.get('decisions', [])
    if decisions:
        story.append(Paragraph("Decisions Made", heading_style))
        for decision in decisions:
            story.append(Paragraph(f"• {decision}", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Action Items
    action_items = data.get('actionItems', [])
    if action_items:
        story.append(Paragraph("Action Items", heading_style))
        
        # Create table data
        table_data = [['Task', 'Owner', 'Deadline', 'Status']]
        
        for item in action_items:
            table_data.append([
                str(item.get('task', '')),
                str(item.get('owner', '')),
                str(item.get('deadline', 'Not specified')),
                str(item.get('status', 'Pending'))
            ])
        
        # Create table
        table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
