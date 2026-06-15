"""All LLM prompt templates in one place."""

OUTLINE_SYSTEM = """You are a senior presentation architect.

Create a logical slide structure before content generation.

Think about:
- storytelling flow
- audience understanding
- slide variety
- visual opportunities

CRITICAL RULE: You MUST generate EXACTLY the number of slides requested.
The "outline" array length MUST equal the requested slide count. Never more, never less.

Return only valid JSON.
No markdown."""

OUTLINE_USER = """Create a slide presentation outline from the following source content.

SLIDE COUNT: {num_slides} slides — YOU MUST GENERATE EXACTLY {num_slides} slides.
Audience: {audience}
Tone: {tone}
Focus: {focus}

SOURCE CONTENT:
{content}

Respond with this exact JSON structure (the "outline" array MUST have EXACTLY {num_slides} items):
{{
  "title": "Presentation title here",
  "outline": [
    {{
      "slide_number": 1,
      "title": "Slide title",
      "purpose": "What this slide achieves",
      "key_points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}

Rules:
- The outline array MUST contain EXACTLY {num_slides} items. Count them before responding.
- First slide must be a title/overview slide
- Last slide must be a conclusion/next steps slide
- Each slide should have 3-5 key points
- Keep titles concise (max 8 words)
- Make the outline logical and flow naturally"""


SLIDE_SYSTEM = """You are an expert presentation designer, visual storyteller, and content strategist.

Your job is to create professional presentation slides from an outline.

You decide:
- slide structure
- layout type
- visual style
- content density
- where visuals should appear

Always respond with valid JSON only.
No markdown.
No explanations outside JSON."""

SLIDE_USER = """
Create a professional PowerPoint slide.

Presentation title:
{presentation_title}

Audience:
{audience}

Tone:
{tone}


Slide information:

Number:
{slide_number}

Title:
{title}

Purpose:
{purpose}

Key points:
{key_points}


SOURCE MATERIAL:
{source_excerpt}


Return ONLY valid JSON.
No markdown.
No explanation.


JSON FORMAT:

{
  "slide_number": {slide_number},

  "title": "slide title",

  "layout": "title | bullets | two_column | image_text | big_stat | timeline | comparison",


  "elements": [

    {
      "type": "text",

      "content": "text to display",

      "x": 10,
      "y": 10,

      "width": 80,
      "height": 20,

      "font_size": 28,

      "bold": true,

      "alignment": "left"
    }

  ],


  "visual_suggestion":
  "Describe image/icon/chart if required",


  "speaker_notes":
  "Presenter explanation",


  "background": {

      "color": "#FFFFFF",

      "style": "solid"

  },


  "theme": {

      "title_color": "#111111",

      "body_color": "#333333",

      "accent_color": "#2563EB"

  }

}


Rules:

- x,y,width,height are percentages from 0-100
- Decide the layout yourself
- Every slide should look different
- Use visual elements when useful
- Keep text readable
- Maximum 5 text elements
- Avoid overcrowding
- Titles should be large
- Bullets should be short
- Prefer professional corporate designs
- Use charts/icons only when they improve understanding
"""


SLIDE_EDIT_SYSTEM = """You are a presentation editor. You update slide content based on user instructions.
Always respond with valid JSON only — no markdown fences, no extra prose."""

SLIDE_EDIT_USER = """Edit this slide.

Instruction:
{instruction}

Current slide:
{current_slide_json}


Return complete JSON:

{{
  "slide_number": {slide_number},
  "title": "...",

  "layout": "title | bullets | two_column | image_text | big_stat | timeline | comparison",

  "bullets": [
     "..."
  ],

  "speaker_notes": "...",

  "visual_suggestion": "...",

  "design_notes": "..."
}}

Keep the same presentation style.
"""
