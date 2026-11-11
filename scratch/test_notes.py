from pptx import Presentation

prs = Presentation('Utility_Management_System_Presentation.pptx')
slide = prs.slides[0]
notes_slide = slide.notes_slide
text_frame = notes_slide.notes_text_frame
text_frame.text = "Hello, this is a test speaker note for Slide 1."
prs.save('scratch/test_notes.pptx')
print("Successfully added speaker note!")
