from pptx import Presentation

prs = Presentation('Presentation3.pptx')
slide = prs.slides[0]
for s in slide.shapes:
    if s.shape_type == 13: # picture
        print('Picture found:', s.name)
        # can we inspect s._element?
        blip = s._element.xpath('.//a:blip')
        if blip:
            rId = blip[0].attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed']
            print('rId:', rId)
            image_part = slide.part.related_part(rId)
            print('Image part:', image_part, 'blob len:', len(image_part.blob))

