from flet import *
from fpdf import *
from fpdf import encryption
from firebaseConfig import store
import re
import arabic_reshaper
from bidi.algorithm import get_display


bucket = store.bucket()
# Helper function to detect Arabic characters
def contains_arabic(text):
    # Arabic Unicode range is U+0600 to U+06FF
    arabic_re = re.compile(r'[\u0600-\u06FF]')
    return arabic_re.search(text) is not None

# Helper function to reverse and reshape Arabic text
def format_text(text):
    if contains_arabic(text):
        # Reshape the Arabic text and handle bidirectional display
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text  # Return reshaped and bidirectional text
    return text  # Return the original text if it's not Arabic

# Class to generate and upload PDF to Firebase Storage
class PDF(FPDF):
    def __init__(self, university: str, college: str, department: str, date: str, duration: str, exam_name: str, lecturer: str, folder: str, alignment: bool):
        self.university = university
        self.college = college
        self.department = department
        self.date = date
        self.duration = duration
        self.exam_name = exam_name
        self.lecturer = lecturer
        self.folder = folder
        self.alignment = alignment
        super().__init__()
        self.add_font('amiri', '', 'Fonts/Amiri-Regular.ttf',)
        self.add_font('amiri', 'B', 'Fonts/Amiri-Bold.ttf',)
        self.add_font('amiri', 'I', 'Fonts/Amiri-Italic.ttf',)
        self.add_font('amiri', 'BI', 'Fonts/Amiri-BoldItalic.ttf',)
        


    def header(self):
        logo_path = "Assets/Al-Mustansiriya_University_logo.png"  # Path to your logo image
        logo_width = 20  # Width of the logo in mm
        page_width = self.w

        # Left side: university, college, department
        self.set_font("amiri", "", 10)
        self.cell(0, 5, f"University: {format_text(self.university)}", new_x= XPos.LEFT, new_y= YPos.NEXT, align='L')
        #self.set_font("amiri", "", 10)
        self.cell(0, 5, f"College: {format_text(self.college)}", new_x= XPos.LEFT, new_y= YPos.NEXT, align='L')
        self.cell(0, 5, f"Department: {format_text(self.department)}", new_x= XPos.LEFT, new_y= YPos.NEXT, align='L')

        # Right side: duration, date, exam name
        self.set_xy(page_width - 70, 10)  # Adjust the position for the right side
        self.cell(0, 5, f"Duration: {format_text(self.duration)}", new_x= XPos.LEFT, new_y= YPos.NEXT, align='R')
        self.cell(0, 5, f"Date: {self.date}", new_x= XPos.LEFT, new_y= YPos.NEXT, align='R')
        self.cell(0, 5, f"Exam: {format_text(self.exam_name)}", new_x= XPos.LEFT, new_y= YPos.NEXT, align='R')

        # Centered logo
        center_x = (page_width - logo_width) / 2  # Center the logo
        self.image(logo_path, x=center_x, y=2, w=logo_width)

        # Draw a line under the header
        self.ln(5)
        self.set_draw_color(0, 0, 0)  # Line color
        self.set_line_width(0.5)  # Line thickness
        self.line(10, 28, page_width - 10, 28)  # Draw the line (x1, y1, x2, y2)
        self.ln(10)

    def footer(self):
        page_width = self.w
        # Draw a line above the footer
        self.set_y(-20)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), page_width - 10, self.get_y())

        # Left side: lecturer's name
        self.set_y(-15)
        self.set_font('amiri', 'I', 10)
        self.cell(0, 10, f"Lecturer: {format_text(self.lecturer)}", align='L')

        # Center: Page number
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", center= True)
        self.cell(0, 10, f"Chairman Signature:             ", align= 'R')

    def add_body(self, text):
        self.set_font('amiri',"", size=12)
        if(self.alignment):
         body = format_text(text)
         self.multi_cell(0, 10, body)
        else:
         body = format_text(text)
         self.multi_cell(0, 10, body, align= 'R')

# Function to generate and upload PDF to Firebase Storage
def generate_and_open_pdf(filename, password: str, university, college, department, date, duration, exam_name, lecturer, body_text, folder, alignment):
    # Generate PDF
    pdf = PDF(university=university, college=college, department=department, date=date, duration=duration, exam_name=exam_name, lecturer=lecturer, folder=folder, alignment= alignment)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set title (Center-aligned, removed "title" as per request)
    #pdf.set_font("amiri", "B", 16)
   # pdf.cell(200, 10, text=exam_name, align='C', new_x= XPos.LEFT, new_y= YPos.NEXT)"""

    # Add body text
    # pdf.ln(10)
    pdf.add_body(body_text)
    
    pdf.set_encryption(owner_password=password, user_password= password, encryption_method= encryption.EncryptionMethod.AES_128)
    
    
    # Save the PDF locally
    pdf_output = f"{filename}.pdf"
    pdf.output(pdf_output)
 
    # Upload PDF to Firebase Storage (with folder structure)
    folder_path = f"{folder}/"
    blob = bucket.blob(folder_path + pdf_output)
    blob.upload_from_filename(pdf_output)

    # Get the public URL of the uploaded file
    blob.make_public()

    return blob.public_url