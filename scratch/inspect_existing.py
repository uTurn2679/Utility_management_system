import zipfile, xml.etree.ElementTree as ET

pptx_path = 'existing_utility_presentation.pptx'
with zipfile.ZipFile(pptx_path, 'r') as z:
    media = [f for f in z.namelist() if f.startswith('ppt/media/')]
    print(f'Media in existing presentation: {len(media)}')
    slides = [f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
    slides.sort(key=lambda x: int(''.join(filter(str.isdigit, x.split('/')[-1]))))
    print(f'Total Slides: {len(slides)}')
    for i, sf in enumerate(slides, 1):
        content = z.read(sf)
        tree = ET.fromstring(content)
        texts = [node.text.strip() for node in tree.iter() if node.tag.endswith('}t') and node.text and node.text.strip()]
        print(f'=== Slide {i} ===')
        print(' | '.join(texts[:5]))

