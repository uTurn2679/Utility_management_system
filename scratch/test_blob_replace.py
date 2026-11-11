from pptx import Presentation

prs = Presentation('Presentation3.pptx')
slide = prs.slides[0]
for s in slide.shapes:
    if s.shape_type == 13:
        blip = s._element.xpath('.//a:blip')
        rId = blip[0].attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed']
        image_part = slide.part.related_part(rId)
        with open('scratch/existing_media/image7.png', 'rb') as f:
            new_data = f.read()
        image_part._blob = new_data
        print('Assigned new blob of length:', len(new_data))

prs.save('scratch/test_out.pptx')
print('Saved test_out.pptx successfully!')

prs2 = Presentation('scratch/test_out.pptx')
print('Reloaded test_out.pptx successfully! Slides count:', len(prs2.slides))

