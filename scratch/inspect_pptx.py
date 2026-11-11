from pptx import Presentation

prs = Presentation('Presentation3.pptx')
print(f'Width: {prs.slide_width.inches} in, Height: {prs.slide_height.inches} in')

for i, slide in enumerate(prs.slides, 1):
    print(f'=== Slide {i} === (shapes: {len(slide.shapes)})')
    for shape in slide.shapes:
        info = f'  - Type: {shape.shape_type}'
        if shape.has_text_frame:
            txt = shape.text_frame.text.replace('\n', ' ')[:70]
            info += f' | Text: \"{txt}\"'
        if shape.shape_type == 13: # picture
            info += f' | Img: {shape.image.filename} ({shape.image.size}) pos: ({shape.left.inches:.2f}, {shape.top.inches:.2f}, {shape.width.inches:.2f}, {shape.height.inches:.2f})'
        print(info)

