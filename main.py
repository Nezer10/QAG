from flet import *
from viewscol import views_handler


def main(page: Page):
  page.adaptive = True
  page.horizontal_alignment = "center"
  page.vertical_alignment = "center"
  page.theme = Theme(color_scheme_seed=colors.INDIGO, use_material3=True)
  page.dark_theme = Theme(color_scheme_seed=colors.INDIGO, use_material3=True)
  page.theme_mode = ThemeMode.LIGHT
  page.bgcolor = colors.WHITE
  page.update()

  def route_change(route):
    print(page.route)
    page.views.append(
      views_handler(page)[page.route],
    )
    page.update()
  
  def view_pop(view):
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)
  

  page.on_route_change = route_change
  page.on_view_pop = view_pop
  page.go('/signin')

app(target= main, assets_dir= "Assets", use_color_emoji= True,) #view= AppView.WEB_BROWSER,)
