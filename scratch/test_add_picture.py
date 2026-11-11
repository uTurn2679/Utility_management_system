from pptx import Presentation

prs = Presentation('Presentation3.pptx')
slide = prs.slides[0]

pic_shape = None
for s in slide.shapes:
    if s.shape_type == 13:
        pic_shape = s
        break

if pic_shape:
    left, top, width, height = pic_shape.left, pic_shape.top, pic_shape.width, pic_shape.height
    sp = pic_shape._element
    sp.getparent().remove(sp)
    slide.shapes.add_picture('scratch/existing_media/image7.png', left, top, width, height)

prs.save('scratch/test_add_pic.pptx')
print('Successfully saved test_add_pic.pptx!')
prs2 = Presentation('scratch/test_add_pic.pptx')
print('Successfully re-opened test_add_pic.pptx!')

