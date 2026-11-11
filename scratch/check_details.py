import fitz

doc = fitz.open(r'C:\Users\Jasika\Downloads\Chapter 5 Software Design.pdf')

for p in range(70, 94):
    text = doc[p].get_text()
    if any(k in text.lower() for k in ['use case', 'actor', 'fig', 'diagram', 'library', 'system']):
        print(f"=== Page {p+1} ===")
        print(text)
