from flet import *
import firebaseConfig as fire
from twilio.rest import Client
import os
import uuid
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from UI.widgets import Drop, themed_overlay
from API import university as uni

# Download the helper library from https://www.twilio.com/docs/python/install
# Set environment variables for your credentials
# Read more at http://twil.io/secure


load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token) if account_sid and auth_token else None
verify_sid = os.getenv("TWILIO_VERIFY_SID")
uid = str(uuid.uuid4().hex).upper()
print(uid)


class SignUp(UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.selected_college = ""
        self.selected_department = ""

    def _theme_styles(self):
        if self.page.theme_mode == ThemeMode.DARK:
            return {
                "card_bg": "#1f2226",
                "shadow": [
                    BoxShadow(
                        offset=Offset(20, 20),
                        blur_radius=20,
                        color=colors.BLACK54,
                        blur_style=ShadowBlurStyle.NORMAL,
                    ),
                    BoxShadow(
                        offset=Offset(-20, -20),
                        blur_radius=20,
                        color=colors.WHITE10,
                        blur_style=ShadowBlurStyle.NORMAL,
                    ),
                ],
            }
        return {
            "card_bg": "white",
            "shadow": [
                BoxShadow(
                    offset=Offset(35, 35),
                    blur_radius=20,
                    color="#1f2226",
                    blur_style=ShadowBlurStyle.NORMAL,
                ),
                BoxShadow(
                    offset=Offset(-35, -35),
                    blur_radius=20,
                    color="#2a2f33",
                    blur_style=ShadowBlurStyle.NORMAL,
                ),
            ],
        }

    def apply_theme(self):
        if getattr(self, "card", None) is None:
            return
        styles = self._theme_styles()
        self.card.bgcolor = styles["card_bg"]
        self.card.shadow = styles["shadow"]
        self.update()

    def build(self):
        styles = self._theme_styles()
        global selected_college, selected_department
        def _input(label: str, hide: bool):
            return TextField(
                        height= 60,
                        width= 290,
                        label= label,
                        label_style= TextStyle(
                            size= 11,
                        ),
                        border_color= colors.INDIGO_ACCENT_700,
                        password= hide,
                    )

        # TextFields format
        _first = _input("First Name", False)
        _last = _input("Last Name", False)
        _email= _input("Email", False)
        _email.keyboard_type = KeyboardType.EMAIL
        _email.suffix_icon = icons.EMAIL
        _password= _input("Password", True)
        _password.can_reveal_password = True
        _phone = _input("Phone Number", False)
        _phone.input_filter = NumbersOnlyInputFilter()
        _phone.keyboard_type = KeyboardType.PHONE
        _phone.suffix_icon = icons.PHONE_ANDROID
        _code = TextField(label= "Enter the 6-digit code...",)
        _code.suffix_icon = icons.CODE

        colgs = Drop()
        colgs.label = "College"
        colgs.hint_text = "Select your college..."
        depts = Drop()
        depts.label = "Department"
        depts.hint_text = "Select your department..."
        depts.options=[]
        
        

        college_data = uni.get_college()
        colgs.options = [dropdown.Option(i["dept_name"]) for i in college_data]

        def on_department_change(e):
         self.selected_department = depts.value
         print(self.selected_department)
         

        def on_college_change(e):
          depts.options.clear()
          self.selected_college = colgs.value
          department_data = uni.get_depart(college_data, self.selected_college)
          depts.options = [dropdown.Option(i["dept_name"]) for i in department_data]

          print(self.selected_college)
          self.update()
          self.selected_department = ""
    
        colgs.on_change = on_college_change
        depts.on_change = on_department_change
        

        def email_check(email):
         try:
            emailinfo = validate_email(email, check_deliverability= False)
            email = emailinfo.normalized
            print('Valid')
         except EmailNotValidError as e:
           _email.error_text = str(e)
           self.update()
           print(str(e))
        
        def clearErrs():
            _first.error_text = ""
            _last.error_text = ""
            _email.error_text = ""
            _password.error_text = ""
            _phone.error_text = ""
        
        def validate_inputs():
            valid_inputs = True
            clearErrs()

            if not _first.value or len(_first.value.strip()) < 2:
               _first.error_text = "First name should be at least 2 characters."
               valid_inputs = False

            if not _last.value or len(_last.value.strip()) < 2:
               _last.error_text = "Last name should be at least 2 characters."
               valid_inputs = False

            if not _password.value or len(_password.value) < 6:
              _password.error_text = "Password should be 6 characters at least."
              valid_inputs = False

            if not _phone.value:
              _phone.error_text = "Please enter a valid phone number."
              valid_inputs = False
            
            if not colgs.value:
               colgs.error_text = "Please select a college."
               valid_inputs = False
            
            if not depts.value:
               depts.error_text = "Please select a department."
               valid_inputs = False

            email_check(_email.value)
            self.update()
            
            return valid_inputs

        def register(e):
            print(uid)
            try:
                if validate_inputs():
                  fire.adminAuth.create_user(
                      uid= uid,
                      email= _email.value,
                      password= _password.value,
                  )
                  addUser()
                  self.page.go('/')

            except Exception as e:
             open_dlg(err_dlg)
            self.page.update()
        
        def sendVcode(e):
         if not ensure_twilio():
            return
         if validate_inputs():
            verified_number = "+964" + _phone.value
            verification = client.verify.v2.services(verify_sid) \
               .verifications \
               .create(to=verified_number, channel="whatsapp",)
            print(verification.status)
            open_dlg(dlg)
         else:
            open_dlg(err_dlg)
         
         
        def sendVemail(e):
         if not ensure_twilio():
            return
         verification = client.verify \
            .v2 \
            .services(verify_sid) \
            .verifications \
            .create(to= _email.value, channel='email')
         print(verification.sid)

        def vCheck(e):
         if not ensure_twilio():
            return
         # Check via number
         verified_number = "+964" + _phone.value
         otp_code = _code.value
         verification_check = client.verify.v2.services(verify_sid) \
             .verification_checks \
             .create(to=verified_number, code=otp_code,)
         if verification_check.status == "approved":
            register(e)
            print(verification_check.status)
         else:
         # Check via email
            email_check = client.verify \
             .v2 \
             .services(verify_sid) \
             .verification_checks \
             .create(to= _email.value, code= otp_code)
            if email_check.status == "approved":
                register(e)
                addUser()
            print(email_check.status)
         

        dlg = AlertDialog(
                title= Text("Verify your information"),
                content= Text("We have sent you a 6-digit code via Phone Number"),
                modal= False,
                actions=[
                _code,
                Container(height= 10),
                Row(
                    [
                        
                        TextButton("Confirm", on_click= vCheck,),
                        TextButton("Send Code via Email", on_click= sendVemail,),
                        TextButton ("Cancel", on_click= lambda c: close_dlg(dlg))
                    ],
                    
                 ),
                ],
                adaptive= True,
                actions_alignment= MainAxisAlignment.END,
            )
        
        err_dlg = AlertDialog(
            title=  Text("Error!"),
            content=  Text("Something went wrong! Please try again."),
            modal= False,
            actions=[
                FilledButton(
                    text="OK",
                    on_click= lambda n: close_dlg(err_dlg),
                    adaptive= True,
                )
            ],
            actions_alignment= "center"
        )

        twilio_err_dlg = AlertDialog(
            title= Text("Twilio not configured"),
            content= Text("Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_VERIFY_SID in .env.", text_align= TextAlign.CENTER),
            modal= False,
            actions=[
                FilledButton(
                    text="OK",
                    on_click= lambda n: close_dlg(twilio_err_dlg),
                    adaptive= True,
                )
            ],
            actions_alignment= "center"
        )

        def ensure_twilio():
         if client is None or not verify_sid:
            open_dlg(twilio_err_dlg)
            return False
         return True

        def open_dlg(dialog: AlertDialog):
          self.page.dialog = dialog
          dialog.open = True
          self.page.update()
        
        def close_dlg(dialog: AlertDialog):
          dialog.open = False
          self.page.update()
        

        def addUser():
            doc_ref = fire.db.collection(u'Users').document(uid)
            doc_ref.set({
                'First name': _first.value,
                'Last name': _last.value,
                'Pass': _password.value,
                'Email': _email.value,
                'Phone': "+964" + _phone.value,
                'College': self.selected_college,
                'Department': self.selected_department,
                'Useruid': uid,
            })
            print("Done!")

        self.card = Container(
            border_radius= 70,
            bgcolor= styles["card_bg"],
            width = 800,
            height = 600,
            shadow = styles["shadow"],
            content= Column(
                spacing= 17,
                scroll= ScrollMode.ALWAYS,
                horizontal_alignment= "center",
                controls=[
                    Container(padding= 10),
                    Text("Registration", style= TextStyle(
                        weight= "bold",
                        size= 40,
                    )),
                    Text(
                        "ABQ - Question-Answer Generation Platform",
                        size=  17,
                        style= TextStyle(
                            weight= "bold",
                        ),
                    ),
                    Container(padding= 5),
                    Row(
                        controls=[
                         _first,
                         _last,
                        ],
                        alignment= "center"
                    ),
                    Row(
                        controls=[
                         _email,
                         _password,
                        ],
                        alignment= "center"
                    ),
                    Row(
                        controls=[
                         colgs,
                         depts,
                        ],
                        alignment= "center"
                    ),
                    _phone,
                    OutlinedButton(
                        text= "Sign Up",
                        style= ButtonStyle(
                            shape= {
                                "": RoundedRectangleBorder(radius= 8),
                            },
                            overlay_color= themed_overlay(self.page, colors.GREEN_900, colors.GREEN_300),
                        ),
                        height= 48,
                        width= 250,
                        icon= icons.LOGIN,
                        icon_color= colors.GREEN_ACCENT,
                        adaptive= True,
                        on_click= sendVcode, #register, 
                    ),
                    Row(
                        controls=[
                            Text(
                                "Already have an account?",
                                style= TextStyle(
                                size= 10,
                                ),
                            ),
                            GestureDetector(
                                content= Text(
                                    "Login",
                                    style= TextStyle(
                                        size= 10,
                                        color= "blue",
                                        decoration= TextDecoration.UNDERLINE,
                                        decoration_color= "blue",
                                    )
                                ),
                                on_tap= lambda a: (self.page.go('/signin'), print("Done\n")),
                                mouse_cursor= MouseCursor.CLICK,
                            ),
                        ],
                        alignment= "center",
                        spacing= 4,
                    ),
                ],
            )
        )
        return self.card