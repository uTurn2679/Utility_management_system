import zipfile, os

os.makedirs('scratch/p3_media', exist_ok=True)
with zipfile.ZipFile('Presentation3.pptx', 'r') as z:
    for f in z.namelist():
        if f.startswith('ppt/media/'):
            basename = os.path.basename(f)
            outpath = os.path.join('scratch/p3_media', basename)
            with open(outpath, 'wb') as out_f:
                out_f.write(z.read(f))
            print(f'Extracted: {outpath} ({os.path.getsize(outpath)} bytes)')

