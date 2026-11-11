import fitz

doc = fitz.open(r'C:\Users\Jasika\Downloads\Chapter 5 Software Design.pdf')
for i, page in enumerate(doc):
    text = page.get_text()
    t_low = text.lower()
    if 'use case' in t_low or 'library' in t_low:
        print(f"Page {i+1}: use case={t_low.count('use case')}, library={t_low.count('library')}")
