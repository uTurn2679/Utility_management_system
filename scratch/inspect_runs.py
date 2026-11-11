from pptx import Presentation

prs = Presentation('Presentation3.pptx')
for idx, slide in enumerate(prs.slides, 1):
    print(f'=== SLIDE {idx} ===')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for r in p.runs:
                    print(f'  Text: "{r.text[:30]}" | font: {r.font.name}, size: {r.font.size.pt if r.font.size else None}, bold: {r.font.bold}, color: {r.font.color.rgb if r.font.color and r.font.color.type == 1 else "default"}')

