from flet import *
import datetime
import os
import io
import random
import firebaseConfig as fire
import uuid
from Views.signup import uid as user
from UI.widgets import *
from Generator.pdfgen import *
from Generator.docgen import *
import fitz
import threading
import time
    
class Home(UserControl):
   def __init__(self, page):
      super().__init__()
      self.page = page
      self.page.title = "Home"
      self.listV = None
    
   def _theme_styles(self):
    if self.page.theme_mode == ThemeMode.DARK:
      return {
        "tile_bg": "#1f2226",
        "snack_text": colors.WHITE,
      }
    return {
      "tile_bg": colors.SECONDARY_CONTAINER,
      "snack_text": colors.BLACK,
    }

   def apply_theme(self):
    styles = self._theme_styles()
    if self.listV:
      for ctrl in self.listV.controls:
        if isinstance(ctrl, Dismissible) and isinstance(ctrl.content, ListTile):
          ctrl.content.bgcolor = styles["tile_bg"]
      self.listV.update()

   def build(self):
    info = None
    doc_ref = fire.db.collection('Users').document(user).get()
    if(not doc_ref.exists): # == False
      info = fire.auth.current_user['localId']
      doc_ref = fire.db.collection('Users').document(info).get()
      print(info)

    doc = doc_ref.to_dict()
    def _styles():
     return self._theme_styles()
    gptMan = GPTManager()
    txt_prompt = TextPrompt()
    model_dropdown = Dropdown(
            width=255,
            options=[
                dropdown.Option("ft:gpt-3.5-turbo-0125:personal:qagmodel:9d9ba593", "QAG-1"),
                dropdown.Option("ft:gpt-3.5-turbo-0125:personal:finalqagmodel:9dr0Wvmp", "QAG-2"),
                dropdown.Option("ft:gpt-4o-mini-2024-07-18:personal:finalqag-4o-mini:9zwqb37L", "QAG-3o-mini (يفضل اختياره)"),
                dropdown.Option("gpt-4o", "GPT-4o"),
            ],
            value="gpt-4",  # Default value
            hint_text= "اختر نموذج الذكاء الاصطناعي",
            on_change=lambda e: print(f"Selected model: {e.control.value}"),
            alignment= alignment.center_left,
            border_color= colors.INDIGO,
            options_fill_horizontally= True
        )
    
    def err_message(message: str):
        err_log = AlertDialog(
        title=Text("Error ❌"),
        content=Text(message, text_align=TextAlign.CENTER),
        actions=[
            OutlinedButton(
                text="Ok",
                style=ButtonStyle(
                    shape={
                        "": RoundedRectangleBorder(radius=8),
                    },
                    overlay_color= themed_overlay(self.page, colors.GREEN_900, colors.GREEN_300)
                ),
                adaptive=True,
                on_click=lambda e: close_dlg(err_log)
            )
        ],
        actions_alignment= MainAxisAlignment.CENTER
      )
        return err_log

    def get_random_color():
     return random.choice([
        colors.RED_400,
        colors.RED,
        colors.BLUE,
        colors.BLUE_400,
        colors.GREEN,
        colors.GREEN_400,
        colors.PURPLE_400,
        colors.DEEP_ORANGE,
        colors.ORANGE_400,
        colors.PINK_400,
        colors.TEAL_400,
        colors.TEAL,
        colors.CYAN_400,
        colors.AMBER,
        colors.INDIGO_400,
        colors.PURPLE,
        colors.PINK,
        colors.INDIGO,
        colors.INDIGO_500,
    ])

    def temp_label(slider):
     slider.label = f"عشوائية النموذج: {slider.value:.1f}"  # Format the value to one decimal place
     slider.update()  # Update the slider to reflect the new label
    
    temp_slider = Slider(
            min=0.0,
            max=2.0,
            value=0.7,  # Default value
            divisions=20,
            label= f"عشوائية النموذج: {0.7:.1f}",  # Display the current value
            width=300,
            inactive_color= get_random_color(),
            active_color= get_random_color(),
            overlay_color= get_random_color(),
            secondary_active_color= get_random_color(),
            on_change=lambda e: temp_label(e.control),
        )

    head = Text(
            spans=[
                TextSpan(
                    "مرحباً بك، " + doc['First name'] + "!",
                    TextStyle(
                        size=50,
                        weight= FontWeight.BOLD,
                        foreground= Paint(
                            gradient= PaintLinearGradient(
                                (100, 150), (900, 1000), [get_random_color(), get_random_color()]
                            )
                        ),
                    ),
                ),
            ],
        )

    def handle_delete(e: ControlEvent):
     try:
        # Attempt to remove the control from listV's controls
        listV.controls.remove(e.control.data)
        self.update()  # Update listV to reflect changes in the UI
     except ValueError:
        print("Error: The item was not found in the list and could not be removed.")
        open_dlg(err_message("Error: The item was not found in the list and could not be removed."))

    
    self.listV = ListView(
     controls=[Text("ملفاتي - My Files", style= TextStyle(size= 14, weight= FontWeight.BOLD), 
     expand= True,)],
     expand_loose= True, 
     spacing=10, 
     auto_scroll=True,
     divider_thickness= 2,
     width=200)
    listV = self.listV

    def delete_pdf(e: ControlEvent):
     try:
        blob_name = e.control.data  # The name of the PDF file (including the path)
        
        # Delete the file from Firebase Storage
        blob = bucket.blob(blob_name)
        blob.delete()
        print(f"{blob_name} deleted successfully.")
        
        # Remove the corresponding ListTile from the ListView
        listV.controls = [control for control in listV.controls if control.data != blob_name]
        
        # Update the UI after deletion
        self.update()

        self.page.snack_bar = SnackBar(
            Text(f"{blob_name.split('/')[-1].replace('.pdf', '')} has been deleted successfully.", text_align= TextAlign.CENTER,style= TextStyle(weight= FontWeight.BOLD),color= _styles()["snack_text"]),    
            bgcolor= colors.RED_300,
            duration= 5000,
            open=True,
        )
        self.page.update()

     except Exception as ex:
        print(f"Error deleting {blob_name}: {ex}")
        open_dlg(err_message(f"Error deleting {blob_name}: {ex}"))

    def download_pdf(e: ControlEvent):
     try:
        blob_name = e.control.data
        blob = bucket.blob(blob_name)
        # Get the URL
        download_url = blob.public_url
        # Open the URL in the browser for the user to download the file
        self.page.launch_url(download_url)
        print(f"Download URL generated: {download_url}")
     except Exception as ex:
        self.update()
        print(f"Error generating download URL for {blob_name}: {ex}")
        open_dlg(err_message(f"Error generating download URL for {blob_name}: {ex}"))
    
    def dimiss(e: DismissibleDismissEvent):
        if e.direction == DismissDirection.START_TO_END:
            delete_pdf(e)
        else:
            delete_pdf(e)

    def fetch_pdfs():
     styles = _styles()
     blobs = list(bucket.list_blobs(prefix= doc['Useruid']))
     found = False # Variable to track if any PDFs are found
     if blobs:
        blobs.sort(key= lambda blob: blob.updated, reverse = True) # Sort blobs by their 'updated' or 'time_created' metadata in descending order (newest first)
        for blob in blobs:
         found = True # If there's at least one blob, set this to True
         # Determine file extension
         file_name = blob.name.split('/')[-1]
         file_extension = file_name.split('.')[-1].lower()

         # Set logo image based on file type
         if file_extension == 'pdf':
             logo_image = '/pdf.png'
             subtitle_text = "PDF"
         elif file_extension == 'docx':
             logo_image = '/docx.png'
             subtitle_text = "DOCX"
         else:
             print("What???")

         list_tile = ListTile(
            title= Text(file_name.replace(f".{file_extension}", ""), style= TextStyle(size= 14), text_align= TextAlign.CENTER, no_wrap= True),
            subtitle= Text(f"{subtitle_text}", style= TextStyle(size= 14), text_align= TextAlign.CENTER),
            bgcolor= styles["tile_bg"],
            on_click= download_pdf,
            data= blob.name,
            )

         file_image = Image(logo_image, width=30, height=30)
         delete_button = IconButton(icons.DELETE, on_click= delete_pdf, icon_color= colors.RED,data= blob.name)
         list_tile.trailing = file_image
         list_tile.leading = delete_button

         dismissible_tile = Dismissible(
            content=list_tile,  # The actual ListTile content
            on_dismiss= lambda e: dimiss(e),
            data=blob.name,  # Pass the file name as data for identification
            background=Container(
                alignment= alignment.center_left,
                padding=padding.symmetric(horizontal=20),
                bgcolor=colors.RED,  # Background color for right swipe
                content=Row([
                    Icon(icons.DELETE, color=colors.WHITE),
                    Text("Delete", color=colors.WHITE)
                ])
            ),
            secondary_background= Container(
                alignment= alignment.center_right,
                padding=padding.symmetric(horizontal=20),
                bgcolor=colors.RED,  # Background color for left swipe
                content=Row([
                    Icon(icons.DELETE, color=colors.WHITE),
                    Text("Delete", color=colors.WHITE)
                ])
            ),
        )

         listV.controls.append(dismissible_tile)

     if not found:
        listV.controls.append(Text("No PDF files found", text_align= TextAlign.CENTER,style=TextStyle(size=14, italic= True)))

    
    fetch_pdfs()
    
    lec_name = PDF_Value("Lectruer's Name")
    lec_name.value = doc['First name'] + " " + doc['Last name']
    file_txt = PDF_Value("Filename")
    uni_txt = PDF_Value("University")
    uni_txt.value = "Mustansiriyah University"
    depa_txt = PDF_Value("Department")
    depa_txt.value = doc['Department']
    colg_txt = PDF_Value("College")
    colg_txt.value = doc['College']
    date_txt = PDF_Value("Date")
    date_txt.text_align = TextAlign.CENTER
    date_txt.width = 180
    dur_txt = PDF_Value("Duration")
    exam_txt = PDF_Value("Exam")

    def handle_change(e):
     selected_date = e.control.value.strftime(r'%d-%m-%Y')  # Format the selected date
     date_txt.value = selected_date  # Update date_txt with the selected date
     #self.page.overlay.clear()
     date_txt.update()

    date_picker =  DatePicker(
        first_date= datetime.datetime(year=1900, month=1, day=1),
        last_date= datetime.datetime(year=2090, month=1, day=1),
        on_change=handle_change,
        open= False,
    )
    
    pick_date_button = OutlinedButton(
            "حدد التاريخ",
            icon=icons.CALENDAR_MONTH,
            icon_color= colors.TEAL_ACCENT,
            style= ButtonStyle(
                shape= {
                "": RoundedRectangleBorder(radius= 8),
                },        
                color= colors.LIGHT_BLUE_600
            ),
            on_click=lambda e: self.page.open(date_picker)
        )
    
    
    def generate_pdf(e):
     filename = file_txt.value
     university = uni_txt.value
     college = colg_txt.value
     department = depa_txt.value
     date = date_txt.value
     duration = dur_txt.value
     exam = exam_txt.value
     alignment = align_switch.value
     lecturer = lec_name.value
     folder = doc['Useruid']
     password = doc['Pass'][:4] + "IRQ"
     # Capture the GPT output
     body_text = gptMan.get_answer()
     public_url = generate_and_open_pdf(filename, password, university, college, department, date, duration, exam, lecturer, body_text, folder, alignment)
     public_url2 = docx_generate(filename, university, college, department, date, duration, exam, lecturer, body_text, folder)
     print(f"PDF {filename} generated and uploaded successfully!\nDownload URL: {public_url}")
     print(f"DOCX {filename} generated and uploaded successfully!\nDownload URL: {public_url2}")
     listV.controls.clear()
     listV.controls.append(Text("My PDF", style= TextStyle(size= 14, weight= FontWeight.BOLD), 
     expand= True))
     self.page.snack_bar = SnackBar(
         Text(f"{filename} has been created successfully.", text_align= TextAlign.CENTER,style= TextStyle(weight= FontWeight.BOLD),color= _styles()["snack_text"]),
         bgcolor= colors.GREEN_300,
         duration= 5000,
         open=True,
        )
     fetch_pdfs()
     self.update()
       

    def open_dlg(dialog: AlertDialog):
     self.page.dialog = dialog
     dialog.open = True
     self.page.update()
        
    def close_dlg(dialog: AlertDialog):
     dialog.open = False
     self.page.update()

    pdf_pages = []

    def extract_text(file_path):
      try:
        # Open the PDF from the file path (for desktop)
        pdf_document = fitz.open(file_path)

        # Extract text from each page
        pdf_pages.clear()
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
            pdf_pages.append(text)

        display_pdf(pdf_pages)
      except Exception as e:
        print(f"Error processing PDF via path: {e}")
        open(err_message(f"Error processing PDF via path: {e}"))

    def open_pdf(e) :
     # Opens a file picker for uploading a PDF file and extracting text.
     try:
      file_picker.pick_files(allowed_extensions=['pdf'], dialog_title= 'Select File') # Open the file picker dialog
     except Exception as e:
      open_dlg(err_message(str(e)))
     
    pdf_name = Text(expand= True, text_align= TextAlign.CENTER)
   
    def process_pdf(files):
        if files:
         file = files[0]
         file_name = file.name
         pdf_name.value = file_name
         file_extension = os.path.splitext(file_name)[1].lower()

        # Only process PDF files
         if file_extension == ".pdf":
            # Check if file path is available (desktop environment)
            if hasattr(file, 'path') and file.path:
                extract_text(file.path)
            else:
                print("No file path available. Cannot process the file.")
         else:
            print("Unsupported file format.")
            return


    def display_pdf(pdf_pages):
    # Clear previous content
     content_area.controls.clear()

     for page_num, page_text in enumerate(pdf_pages):
        page_label = Text(f"Page {page_num + 1}", weight="bold", size=16)
        page_text_field = TextField(
            value=format_text(page_text),
            multiline=True,
            expand=True,
            min_lines=10,
            max_lines=20,
        )

        # Add a button for selecting the current page's text
        select_button = IconButton(
            icon=icons.CHECK,
            tooltip="Select this text",
            icon_color=colors.GREEN,
            on_click=lambda b, txt=page_text_field.value: select_text(txt),
        )

        content_area.controls.append(
            ListTile(title=page_label, subtitle=page_text_field, trailing=select_button)
        )

     # Open the BottomSheet to display the PDF pages
     open_bottomsheet(pdf_bottomsheet)

    def select_text(selected_text):
      # Handle the text selection and store it in txt_context.
      txt_prompt.value += selected_text
      self.page.snack_bar = SnackBar(
        Text("Text has been selected successfully!", text_align=TextAlign.CENTER,style= TextStyle(weight= FontWeight.BOLD)),
        bgcolor=colors.GREEN_300,
        duration=5000,
        open=True
       )  
      close_bottomsheet(pdf_bottomsheet) # Close dialog after selection
      self.update()
    
    def select_all(pdf_pages):
      # Concatenate all the pages' text into one string
     full_text = "\n\n".join(pdf_pages)

     # Set the full text in the desired field (e.g., txt_context)
     txt_prompt.value = full_text
     self.page.snack_bar = SnackBar(
        Text("All Text has been selected successfully!", text_align=TextAlign.CENTER,style= TextStyle(weight= FontWeight.BOLD)),
        bgcolor=colors.GREEN_300,
        duration=5000,
        open=True
       )  
     
     close_bottomsheet(pdf_bottomsheet)
     self.update()

    # Create the dialog and content area
    content_area = ListView(expand=True, spacing= 10, divider_thickness= 2)

    def open_bottomsheet(sheet):
     self.page.open(sheet)
     self.page.update()


    def close_bottomsheet(sheet):
     sheet.open = False
     self.page.update()

    pdf_bottomsheet = BottomSheet(
    content=Container(
        content=Column([
            Text("PDF Context Selection", style= TextStyle(size= 18, weight= FontWeight.BOLD)),
            content_area,
            Row([
             OutlinedButton(text="Select All", 
             on_click=lambda e: select_all(pdf_pages),
             style= ButtonStyle(
                            shape= {
                                "": RoundedRectangleBorder(radius= 8),
                            },
                            overlay_color= themed_overlay(self.page, colors.GREEN_900, colors.GREEN_300)
                        ),
             ),
             OutlinedButton(text="Close", 
             on_click=lambda e: close_bottomsheet(pdf_bottomsheet),
             style= ButtonStyle(
                            shape= {
                                "": RoundedRectangleBorder(radius= 8),
                            },
                            overlay_color= themed_overlay(self.page, colors.RED_900, colors.RED_300)
                        ),
             ),
             
             ],alignment= MainAxisAlignment.SPACE_BETWEEN),
            ],),
        width=700,  # Adjust width as needed
        height=1000, padding= padding.all(10)), # Adjust height as needed
   )

    # Initialize the file picker and add it to the page
    file_picker = FilePicker(on_result=lambda file_picker_event: process_pdf(file_picker_event.files))
    self.page.overlay.append(file_picker)  # Add file picker to the page
   
    mcq_select = Checkbox("اختيارات", value= True)
    mcq_number = Dropdown(
         options=[
                dropdown.Option("5", "5"),
                dropdown.Option("10", "10"),
                dropdown.Option("15", "15"),
                dropdown.Option("20", "20"),
                dropdown.Option("25", "25"),
            ],
            value="5",  # Default value
            label= "عدد الاسئلة",
            on_change=lambda e: print(f"Selected number: {e.control.value}"),
            width= 200,
            border_color= colors.INDIGO,
            options_fill_horizontally= True
    )

    tf_select = Checkbox("صح / خطأ",)
    tf_number = PDF_Value("عدد الاسئلة")
    tf_number.width = 200
    short_select = Checkbox("اسئلة مقالية")
    short_number = PDF_Value("عدد الاسئلة")
    short_number.width = 200
    align_switch = Switch("يسار", value= True, inactive_track_color=colors.GREEN, track_outline_color=colors.INDIGO, inactive_thumb_color= colors.ORANGE)

    def designQ():
        final_prompt = ""
        if mcq_select.value & tf_select.value & short_select.value:
         final_prompt = f"Generate {mcq_number.value} MCQs with correct answers, {tf_number.value} true/false questions with correct answers and {short_number.value} short answer questions with correct answers:\n"
        
        elif mcq_select.value & tf_select.value:
         final_prompt = f"Generate {mcq_number.value} MCQs with correct answers and {tf_number.value} true/false with correct answers:\n"
        
        elif mcq_select.value & short_select.value:
         final_prompt = f"Generate {mcq_number.value} MCQs with correct answers and {short_number.value} short answer questions with correct answers:\n"
        
        elif tf_select.value & short_select.value:
         final_prompt = f"Generate {tf_number.value} true/false questions with correct answers and {short_number.value} short answer questions with correct answers:\n"
        
        elif mcq_select.value:
         final_prompt = f"Generate {mcq_number.value} MCQs with correct answers:\n"
        
        elif tf_select.value:
         final_prompt = f"Generate {tf_number.value} true/false questions with correct answers:\n"

        elif short_select.value:
         final_prompt = f"Generate {short_number.value} short answer questions with correct answers:\n"
        
        return final_prompt
    

    dial = AlertDialog(
        title= Text("Responding... 🤖"),
        content=Container(
            content= Column(
                [
                 Text("Generating response, please wait... ⌛"),
                 ProgressRing(width=50, height=50, color=get_random_color())
                ],
                horizontal_alignment= CrossAxisAlignment.CENTER,
            ),
            height= 100,
        ),
        actions=[],  # No action buttons needed for this dialog
    )

    # Method to change ProgressRing colors in a separate thread
    def color_changer(progress_ring, stop_event, page):
     while not stop_event.is_set():  # Run loop until stop_event is set
        progress_ring.color = get_random_color()  # Set random color
        self.page.update()  # Update page to show the color change
        time.sleep(0.5)  # Change color every 0.5 seconds

    def submit(e):
     open_dlg(dial)
     pp = designQ() + txt_prompt.value
     selected_model = model_dropdown.value  # Get the selected model
     selected_temp = temp_slider.value # Get the selected temperature
     stop_event = threading.Event()  # Initialize stop_event to control the color-changing thread
     progress_ring = dial.content.content.controls[1] # Get ProgressRing reference and start the color changer thread
     threading.Thread(target=color_changer, args=(progress_ring, stop_event, self.page)).start()

     def get_response():
      gpt_answer = run_prompt(None, pp, selected_model, selected_temp) #txt_prompt.chat,   # Get GPT response
      gptMan.update_answer(gpt_answer)  # Store the GPT answer in GPTManager
      print(gpt_answer)
      txt_prompt.value = gptMan.get_answer()  # Update txt_context with the stored answer
      txt_prompt.value = ""
      txt_prompt.update()
      generate_pdf(e)
      stop_event.set()
      close_dlg(dial)
     threading.Thread(target= get_response).start()
    

    btn_send = OutlinedButton(
        text= "توليد الاسئلة", 
        style= ButtonStyle(
        shape= {
            "": RoundedRectangleBorder(radius= 8),
        },
        color= colors.LIGHT_BLUE_600
        ),
        adaptive= True,
        on_click = submit,
        icon= icons.DRIVE_FILE_RENAME_OUTLINE_OUTLINED,
        icon_color= colors.TEAL_ACCENT,
    )

    txt_prompt.on_submit = submit

    btn_upload = OutlinedButton(
            "اختر المادة العلمية",
            icon=icons.FILE_UPLOAD_OUTLINED,
            icon_color= colors.TEAL_ACCENT,
            style= ButtonStyle(
                shape= {
                "": RoundedRectangleBorder(radius= 8),
                },        
                color= colors.LIGHT_BLUE_600
            ),
            on_click= open_pdf,
        )

    return Container (
        content= Row(
        controls= [
            listV,
            VerticalDivider(width=1, color= colors.TEAL, thickness=2),
            Column(
              controls=[
                head,
                Text("ادخل تفاصيل الاسئلة:-", rtl= True, style= TextStyle(weight= 'bold', size= 15)),
                Divider(height= 16, thickness= 2, color= colors.TEAL),
                Row([Text("الاسم"), lec_name, Text("المادة"), exam_txt, pick_date_button, date_txt],),
                Row([Text("الجامعة"), uni_txt, Text("الكلية"),colg_txt, Text("القسم"), depa_txt]),
                Row([Text("مدة الامتحان"), dur_txt, Text("اسم الملف"), file_txt]),
                Divider(height= 16, thickness= 2, color= colors.TEAL),
                Text("حدد طبيعة الاسئلة :-", rtl= True, style= TextStyle(weight= 'bold', size= 15)),
                Divider(height= 16, thickness= 2, color= colors.TEAL),
                Row([Text("محاذاة النص:"), Text("يمين"), align_switch, pdf_name,]),
                Row([mcq_select, mcq_number, tf_select, tf_number, short_select, short_number], spacing= 15),
                Row([Image(f'/robot.png', width= 40, tooltip= 'اختر نموذجاً'), model_dropdown, Text("عشوائية النموذج: "), Text("0"), temp_slider, Text("2"),]),
                Row(
                 controls=[
                  btn_upload,
                  Text("او انسخ المادة هنا:"),
                  txt_prompt,
                  btn_send,
                ],
          ),
         
        ],
          rtl= True,
          expand= True,
         ),
        ],
        alignment= MainAxisAlignment.START,
        rtl= True,
       ),
        height= self.page.height,
    )
