from pptx import Presentation

prs = Presentation('Presentation3.pptx')
for idx, slide in enumerate(prs.slides, 1):
    if idx > 8: break
    print(f'*** Slide {idx} ***')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs[:2]:
                f_name = para.font.name
                f_size = para.font.size.pt if para.font.size else None
                f_bold = para.font.bold
                print(f'   Text: "{para.text[:40]}" | Font: {f_name}, Size: {f_size}, Bold: {f_bold}')
