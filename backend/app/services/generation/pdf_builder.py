from pathlib import Path
from typing import List
from backend.app.schemas.slide import SlideContent
from backend.app.utils.file_utils import generate_temp_path

THEME_CSS = {
    "midnight_executive": {
        "primary": "#1E2761",
        "accent": "#CADCFC",
        "text": "#1E2761",
        "bg": "#FFFFFF",
    },
    "forest_moss": {
        "primary": "#2C5F2D",
        "accent": "#97BC62",
        "text": "#2C5F2D",
        "bg": "#F5F5F5",
    },
    "coral_energy": {
        "primary": "#F96167",
        "accent": "#2F3C7E",
        "text": "#2F3C7E",
        "bg": "#FFFFFF",
    },
    "charcoal_minimal": {
        "primary": "#36454F",
        "accent": "#212121",
        "text": "#36454F",
        "bg": "#F2F2F2",
    },
}


def _slide_html(slide: SlideContent, theme: dict, is_title: bool = False) -> str:
    bullets_html = "".join(f"<li>{b}</li>" for b in slide.bullets)

    if is_title:
        return f"""
<div class="slide title-slide">
  <h1>{slide.title}</h1>
  {'<p class="subtitle">' + slide.bullets[0] + '</p>' if slide.bullets else ''}
</div>"""

    return f"""
<div class="slide">
  <div class="slide-header">
    <h2>{slide.title}</h2>
    <span class="slide-num">{slide.slide_number}</span>
  </div>
  <ul>{bullets_html}</ul>
  {'<div class="notes"><strong>Notes:</strong> ' + slide.speaker_notes + '</div>' if slide.speaker_notes else ''}
</div>"""


def build_pdf(
    slides: List[SlideContent],
    presentation_title: str,
    theme_name: str = "midnight_executive",
) -> Path:
    """Build a PDF from slide content using ReportLab as fallback."""
    try:
        return _build_with_reportlab(slides, presentation_title, theme_name)
    except Exception:
        return _build_html_fallback(slides, presentation_title, theme_name)


def _build_with_reportlab(
    slides: List[SlideContent],
    presentation_title: str,
    theme_name: str,
) -> Path:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    theme = THEME_CSS.get(theme_name, THEME_CSS["midnight_executive"])
    primary = colors.HexColor(theme["primary"])
    accent = colors.HexColor(theme["accent"])
    text_color = colors.HexColor(theme["text"])

    out_path = generate_temp_path(suffix=".pdf")
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=landscape(A4),
        leftMargin=inch,
        rightMargin=inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SlideTitle", parent=styles["Heading1"],
        textColor=primary, fontSize=24, spaceAfter=12,
    )
    bullet_style = ParagraphStyle(
        "SlideBullet", parent=styles["Normal"],
        textColor=text_color, fontSize=13,
        leftIndent=20, spaceAfter=6,
    )
    notes_style = ParagraphStyle(
        "Notes", parent=styles["Normal"],
        textColor=colors.grey, fontSize=10,
        leftIndent=10, spaceBefore=10,
    )

    story = []
    for slide in slides:
        # Per-slide theme overrides the named theme when the LLM supplied one
        if slide.theme:
            slide_primary      = colors.HexColor(slide.theme.title_color)
            slide_text_color   = colors.HexColor(slide.theme.body_color)
            slide_accent       = colors.HexColor(slide.theme.accent_color)
        else:
            slide_primary    = primary
            slide_text_color = text_color
            slide_accent     = accent

        slide_title_style = ParagraphStyle(
            f"SlideTitle_{slide.slide_number}",
            parent=styles["Heading1"],
            textColor=slide_primary, fontSize=24, spaceAfter=12,
        )
        slide_bullet_style = ParagraphStyle(
            f"SlideBullet_{slide.slide_number}",
            parent=styles["Normal"],
            textColor=slide_text_color, fontSize=13,
            leftIndent=20, spaceAfter=6,
        )

        # Slide title
        story.append(Paragraph(slide.title, slide_title_style))
        story.append(Spacer(1, 0.1 * inch))

        # Fix 3: Prefer elements[] (what the LLM actually fills in),
        # fall back to bullets[] for backwards compat.
        if slide.elements:
            for element in slide.elements:
                if element.type == "text" and element.content.strip() != slide.title.strip():
                    story.append(Paragraph(element.content, slide_bullet_style))
                elif element.type == "image":
                    # Real image embedding not supported — show a placeholder note
                    story.append(
                        Paragraph(f"[Image: {element.content}]", notes_style)
                    )
        elif slide.bullets:
            for bullet in slide.bullets:
                story.append(Paragraph(f"\u2022 {bullet}", slide_bullet_style))

        if slide.speaker_notes:
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph(f"Notes: {slide.speaker_notes}", notes_style))
        story.append(PageBreak())

    doc.build(story)
    return out_path


def _build_html_fallback(
    slides: List[SlideContent],
    presentation_title: str,
    theme_name: str,
) -> Path:
    """If WeasyPrint/ReportLab fail, write a styled HTML file."""
    theme = THEME_CSS.get(theme_name, THEME_CSS["midnight_executive"])
    slides_html = "\n".join(
        _slide_html(s, theme, is_title=(s.slide_number == 1)) for s in slides
    )
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{presentation_title}</title>
<style>
  body {{ font-family: Calibri, Arial, sans-serif; margin: 0; background: #eee; }}
  .slide {{ background: {theme['bg']}; width: 900px; min-height: 500px; margin: 32px auto;
            padding: 40px 60px; box-shadow: 0 4px 24px #0002; page-break-after: always; }}
  .title-slide {{ background: {theme['primary']}; color: #fff; display: flex;
                  flex-direction: column; justify-content: center; }}
  .title-slide h1 {{ font-size: 42px; margin: 0 0 16px; }}
  .subtitle {{ font-size: 20px; opacity: .85; font-style: italic; }}
  .slide-header {{ display: flex; justify-content: space-between; align-items: center;
                   border-bottom: 3px solid {theme['primary']}; padding-bottom: 10px; margin-bottom: 20px; }}
  h2 {{ font-size: 28px; color: {theme['primary']}; margin: 0; }}
  .slide-num {{ color: {theme['accent']}; font-size: 14px; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ padding: 8px 0 8px 24px; position: relative; color: {theme['text']}; font-size: 16px; }}
  li::before {{ content: '●'; position: absolute; left: 0; color: {theme['primary']}; }}
  .notes {{ margin-top: 20px; font-size: 12px; color: #888; border-top: 1px solid #ddd; padding-top: 10px; }}
</style>
</head>
<body>
{slides_html}
</body>
</html>"""
    out_path = generate_temp_path(suffix=".html")
    out_path.write_text(html, encoding="utf-8")
    return out_path
