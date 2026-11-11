import fitz

doc = fitz.open(r'C:\Users\Jasika\Downloads\Chapter 5 Software Design.pdf')

for p in range(83, 93):
    page = doc[p]
    blocks = page.get_text("blocks")
    print(f"=== Page {p+1} blocks count: {len(blocks)} ===")
    for b in blocks:
        print("  -", b[4].replace("\n", " "))
    
    # Also check drawing/vector shapes or drawings count
    drawings = page.get_drawings()
    images = page.get_images()
    print(f"  Drawings count: {len(drawings)}, Images count: {len(images)}")
