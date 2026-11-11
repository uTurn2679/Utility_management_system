from pptx import Presentation

prs = Presentation('Presentation3.pptx')
for idx, slide in enumerate(prs.slides, 1):
    print(f'=== SLIDE {idx} ===')
    for s_idx, shape in enumerate(slide.shapes):
        print(f'  Shape {s_idx}: type={shape.shape_type}, name="{shape.name}", left={shape.left.inches:.2f}, top={shape.top.inches:.2f}, w={shape.width.inches:.2f}, h={shape.height.inches:.2f}')
        if shape.has_text_frame:
            for p_idx, p in enumerate(shape.text_frame.paragraphs):
                if p.text.strip():
                    print(f'    P{p_idx}: "{p.text.strip()[:80]}"')

