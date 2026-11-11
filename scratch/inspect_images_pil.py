from PIL import Image
import glob

for p in sorted(glob.glob('scratch/p3_media/*.*')):
    im = Image.open(p)
    print(f'{p}: size={im.size}, format={im.format}')

