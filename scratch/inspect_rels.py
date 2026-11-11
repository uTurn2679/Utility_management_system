import zipfile, xml.etree.ElementTree as ET

with zipfile.ZipFile('Presentation3.pptx', 'r') as z:
    for i in range(1, 17):
        rel_path = f'ppt/slides/_rels/slide{i}.xml.rels'
        if rel_path in z.namelist():
            rel_xml = z.read(rel_path)
            root = ET.fromstring(rel_xml)
            imgs = [elem.attrib.get('Target') for elem in root if 'image' in elem.attrib.get('Target', '')]
            print(f'Slide {i}: {imgs}')

