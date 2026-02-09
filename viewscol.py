from flet import *
from Views import home, signin, signup
from UI.widgets import themed_overlay
import firebaseConfig as fire 

def _build_theme_button(page):
    def toggle(e):
        if page.theme_mode == ThemeMode.LIGHT:
            page.theme_mode = ThemeMode.DARK
            page.bgcolor = colors.BLACK
        else:
            page.theme_mode = ThemeMode.LIGHT
            page.bgcolor = colors.WHITE
        e.control.icon = icons.LIGHT_MODE if page.theme_mode == ThemeMode.DARK else icons.DARK_MODE
        _apply_theme(page)
        page.update()

    return IconButton(
        icon=icons.DARK_MODE if page.theme_mode == ThemeMode.LIGHT else icons.LIGHT_MODE,
        tooltip="Toggle theme",
        on_click=toggle,
        hover_color= colors.BLUE_ACCENT,
    )




def _apply_theme(page):
    for attr in ("_home_view", "_signin_view", "_signup_view"):
        ctrl = getattr(page, attr, None)
        if ctrl and hasattr(ctrl, "apply_theme"):
            ctrl.apply_theme()
def _auth_appbar(page):
    return AppBar(
        actions=[_build_theme_button(page)],
        center_title=True,
    )


def views_handler(page):
    def out():
        fire.auth.current_user = None
        print("User Signed Out!")
        page.go('/signin')

    home_view = home.Home(page)
    page._home_view = home_view

    signin_view = signin.SignIn(page)
    signup_view = signup.SignUp(page)
    page._signin_view = signin_view
    page._signup_view = signup_view

    return{
        '/': View(
            appbar= AppBar(
            title= Text("نظام الاسئلة الالكترونية"),
            leading= Image(src= f"/Al-Mustansiriya_University_logo.png", fit= ImageFit.FILL),
            center_title= True,
            actions=[
                      _build_theme_button(page),
                      IconButton(icons.SETTINGS, on_click= lambda _: print("settings"),style= ButtonStyle(overlay_color= themed_overlay(page, colors.BLUE_900, colors.BLUE_300)), tooltip= "Settings"),
                      IconButton(icons.LOGOUT, on_click= lambda _: out(),style= ButtonStyle(overlay_color= themed_overlay(page, colors.RED_900, colors.RED_300)), tooltip= "Logout"),
                    ],
            bgcolor=colors.SURFACE_VARIANT,
            ),
            controls=[
                       home_view,
                     ],
            vertical_alignment= MainAxisAlignment.CENTER,
           ),
        '/signin': View(
            appbar=_auth_appbar(page),
            controls=[
                signin_view,
            ],
            vertical_alignment= MainAxisAlignment.CENTER,
            horizontal_alignment= CrossAxisAlignment.CENTER,
        ),
        '/signup': View(
            appbar=_auth_appbar(page),
            controls= [signup_view],
            vertical_alignment= MainAxisAlignment.CENTER,
            horizontal_alignment= CrossAxisAlignment.CENTER,
        )
    }
