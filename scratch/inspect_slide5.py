from pptx import Presentation

prs = Presentation('Presentation3.pptx')
slide = prs.slides[4]
for s in slide.shapes:
    if s.has_text_frame:
        print(s.name)
        for i, p in enumerate(s.text_frame.paragraphs):
            print(f'P{i}: level={p.level}, text="{p.text[:60]}"')

