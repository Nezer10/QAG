from flet import *
import firebaseConfig as fire
from email_validator import  validate_email, EmailNotValidError
from UI.widgets import Drop, themed_overlay
from API import university as uni

class SignIn(UserControl):
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

        _email= _input("Email", False)
        _password= _input("Password", True)
        _password.can_reveal_password = True

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
            _email.error_text = ""
            _password.error_text = ""

        def validate_inputs():
            valid_inputs = True
            clearErrs()

            if not _password.value or len(_password.value) < 6:
              _password.error_text = "Password should be 6 characters at least."
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
        
        err_dlg = AlertDialog(
            title= Text("Error!",text_align= TextAlign.CENTER),
            content= Text("Something went wrong.! Please try again.", text_align= TextAlign.CENTER),
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

        def open_dlg(dialog: AlertDialog):
          self.page.dialog = dialog
          dialog.open = True
          self.page.update()
        
        def close_dlg(dialog: AlertDialog):
          dialog.open = False
          self.page.update()
        
        def _sign_in(e):
            try:
                if validate_inputs():
                   fire.auth.sign_in_with_email_and_password(
                   _email.value,
                   _password.value,
                  )
                   info = fire.auth.current_user["localId"]
                   print(info)
                   doc_ref = fire.db.collection('Users').document(info).get()
                   doc = doc_ref.to_dict()
                   if doc['College'] == self.selected_college and doc['Department'] == self.selected_department:
                     self.page.go('/')
                   else:
                     open_dlg(err_dlg)
            
            except Exception as e:
             open_dlg(err_dlg)
            self.page.update()

        
        self.card = Container(
            border_radius= 70,
            bgcolor= styles["card_bg"],
            width = 500,
            height = 620,
            shadow = styles["shadow"],
            content= Column(
                spacing= 15,
                horizontal_alignment= "center",
                controls=[
                    Container(padding= 10),
                    Text("Login", style= TextStyle(
                        weight= "bold",
                        size= 50,
                    )),
                    Text(
                        "Welcome Back",
                        size=  30,
                        style= TextStyle(
                            weight= "bold",
                        ),
                    ),
                    Text(
                        "ABQ - Question-Answer Generation Platform",
                        size=  17,
                        style= TextStyle(
                            weight= "bold",
                        ),
                    ),
                    _email,
                    colgs,
                    depts,
                    _password,
                    OutlinedButton(
                        text= "Sign In",
                        style= ButtonStyle(
                            shape= {
                                "": RoundedRectangleBorder(radius= 8),
                            },
                            overlay_color= themed_overlay(self.page, colors.GREEN_900, colors.GREEN_300),
                        ),
                        icon= icons.LOGIN,
                        icon_color= colors.GREEN_ACCENT,
                        adaptive= True,
                        on_click= _sign_in,
                        height= 48,
                        width= 250,
                    ),
                    Row(
                        controls=[
                            Text(
                                "Don't have an account? ",
                                style= TextStyle(
                                size= 10,
                                ),
                            ),
                            GestureDetector(
                                content= Text(
                                    "Register Now",
                                    style= TextStyle(
                                        size= 10,
                                        color= "blue",
                                        decoration= TextDecoration.UNDERLINE,
                                        decoration_color= "blue",
                                    )
                                ),
                                on_tap= lambda a: self.page.go('/signup'),
                                mouse_cursor= MouseCursor.CLICK,
                            )
                        ],
                        alignment= "center",
                        spacing= 4,
                    ),
                    Row(
                        controls=[
                             Text(
                                "Forgot your password? ",
                                style= TextStyle(
                                size= 10,
                                ),
                            ),
                            GestureDetector(
                                content= Text(
                                    "Reset",
                                    style= TextStyle(
                                        size= 10,
                                        color= "blue",
                                        decoration= TextDecoration.UNDERLINE,
                                        decoration_color= "blue",
                                    )
                                ),
                                on_tap= lambda a: fire.auth.send_password_reset_email(
                                    email= _email.value,  
                                ),
                                mouse_cursor= MouseCursor.CLICK,
                            )
                        ],
                        alignment= "center",
                        spacing= 4,
                    ),
                ]
            )
        )
        return Container(content=self.card)
