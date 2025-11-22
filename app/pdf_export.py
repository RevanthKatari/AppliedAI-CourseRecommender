"""
PDF Export functionality for MAC Course Pathfinder recommendations.
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas


def generate_recommendations_pdf(student, performance, recommendations, context, selected_interests=None):
    """
    Generate a PDF document with course recommendations.
    
    Args:
        student: Student data dictionary (can be None)
        performance: Performance data dictionary (can be None)
        recommendations: List of recommended courses
        context: Either "history" or "interests"
        selected_interests: List of selected interest tags
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        alignment=1,  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=10,
        spaceBefore=20,
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=8,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=6,
    )
    
    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['BodyText'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
    )
    
    # Title
    story.append(Paragraph("MAC Course Pathfinder", title_style))
    story.append(Paragraph("Personalized Course Recommendations", styles['Heading3']))
    story.append(Spacer(1, 0.2*inch))
    
    # Student Information
    if student:
        story.append(Paragraph("Student Profile", heading_style))
        
        profile_data = [
            ["Student ID:", student.get('student_id', 'N/A')],
            ["Program Stream:", student.get('program_stream', 'N/A')],
            ["Background:", student.get('undergrad_major', 'N/A')],
            ["Learning Style:", student.get('learning_style', 'N/A')],
        ]
        
        if performance:
            profile_data.extend([
                ["Cumulative GPA:", str(performance.get('cumulative_gpa', 'N/A'))],
                ["Last Term GPA:", str(performance.get('last_term_gpa', 'N/A'))],
                ["Academic Status:", performance.get('risk_flag', 'N/A').replace('-', ' ')],
            ])
        
        profile_table = Table(profile_data, colWidths=[2*inch, 4*inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(profile_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Recommendation Context
    story.append(Paragraph("Recommendation Method", heading_style))
    if context == "history":
        context_text = "These recommendations blend your completed coursework with insights from peers who share similar academic trajectories."
    else:
        if selected_interests:
            context_text = f"Curated from your selected interests: <b>{', '.join(selected_interests)}</b>"
        else:
            context_text = "Curated based on your interest profile."
    
    story.append(Paragraph(context_text, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph(f"Top {len(recommendations)} Recommended Courses", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    for idx, rec in enumerate(recommendations, 1):
        # Course header
        course_header = f"<b>{idx}. {rec['course_code']}: {rec['title']}</b>"
        story.append(Paragraph(course_header, subheading_style))
        
        # Course details table
        details_data = [
            ["Category:", rec['category'].title()],
            ["Delivery Mode:", rec['delivery_mode'].title()],
            ["Hybrid Score:", f"{rec['combined_score']:.3f}"],
            ["Content Match:", f"{rec['content_score']:.3f}"],
            ["Peer Alignment:", f"{rec['collab_score']:.3f}"],
        ]
        
        details_table = Table(details_data, colWidths=[1.5*inch, 4.5*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#475569')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 0.1*inch))
        
        # Description
        story.append(Paragraph(f"<b>Description:</b> {rec['description']}", body_style))
        
        # Skills
        if rec.get('skills'):
            skills_text = f"<b>Key Skills:</b> {', '.join(rec['skills'])}"
            story.append(Paragraph(skills_text, body_style))
        
        # Explanation
        story.append(Paragraph(f"<b>Why this course:</b> {rec['explanation']}", body_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Page break after every 2 courses (except the last one)
        if idx % 2 == 0 and idx < len(recommendations):
            story.append(PageBreak())
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | MAC Course Pathfinder"
    story.append(Paragraph(footer_text, small_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

