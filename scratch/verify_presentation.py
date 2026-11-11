from pptx import Presentation

prs = Presentation('Utility_Management_System_Presentation.pptx')
print(f'Total Slides: {len(prs.slides)}')

for idx, slide in enumerate(prs.slides, 1):
    print(f'=== SLIDE {idx} ===')
    for s in slide.shapes:
        if s.has_text_frame:
            for p in s.text_frame.paragraphs:
                txt = p.text.strip()
                if txt:
                    print(f'  [Text]: {txt[:70]}')
        if s.shape_type == 13:
            print(f'  [Picture]: {s.name} pos=({s.left.inches:.2f}, {s.top.inches:.2f}, {s.width.inches:.2f}, {s.height.inches:.2f})')

