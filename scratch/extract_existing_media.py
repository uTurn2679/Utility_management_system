import zipfile, os

os.makedirs('scratch/existing_media', exist_ok=True)
with zipfile.ZipFile('existing_utility_presentation.pptx', 'r') as z:
    for f in z.namelist():
        if f.startswith('ppt/media/'):
            basename = os.path.basename(f)
            outpath = os.path.join('scratch/existing_media', basename)
            with open(outpath, 'wb') as out_f:
                out_f.write(z.read(f))
            print(f'Extracted: {outpath} ({os.path.getsize(outpath)} bytes)')

