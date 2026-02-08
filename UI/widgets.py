from flet import *
import openai
import os
import time
import threading
from dotenv import load_dotenv

load_dotenv()


def themed_overlay(page, light_color, dark_color):
    if page is not None and page.theme_mode == ThemeMode.DARK:
        return dark_color
    return light_color

def main_style():
    return{
      "width": 620,
      "height": 400,
      "bgcolor": colors.BLACK45,
      "border_radius": 10,
    }


class MainContentArea(Container):
  def __init__(self):
    super().__init__(**main_style())
    self.chat = ListView(
      expand= True,
        height= 200,
        spacing= 15,
        auto_scroll= True,
    )
    self.content = self.chat
    self.padding = 7

"""class CreateMessage(Column):
  def __init__(self, name: str, message: str):
    self.name = name
    self.message = message
    self.text = Text(self.message, selectable= True)
    super().__init__(spacing= 4)
    self.controls = [Text(self.name, opacity= 0.6), self.text]

def animate_text(txt: str, chat: ListView, message: CreateMessage):
    words = []
    for word in list(txt):
        words.append(word)
        message.text.value = "".join(words)
        chat.update()
        time.sleep(0.008)

def user_output(prompt: str): #chat: ListView,
    message = CreateMessage(message=prompt)
    #chat.controls.append(message)
    #animate_text(prompt, chat, message)"""



_openai_client = None

def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _openai_client = openai.OpenAI(api_key=api_key)
    return _openai_client

def gpt_output(prompt: str, model: str, temperature: float): #chat: ListView,
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature= temperature,
    )
    answer = response.choices[0].message.content.strip()
    #message = CreateMessage(message=answer)
    #chat.controls.append(message)
    #animate_text(answer, chat, message)
    return answer

def run_prompt(event, text: str, model: str, temperature: float): #chat: ListView,
    #user_output(prompt=text) #chat,
    #print(text)
    gpt_answer = gpt_output(prompt=text, model= model, temperature= temperature) #chat,  # Capture the GPT output
    return gpt_answer 


class TextPrompt(TextField):
  def __init__(self):
        super().__init__()
        self.hint_text = "Enter your message..."
        self.width = 420
        self.content_padding = 10
        self.multiline = True
        self.max_lines = 2
        self.min_lines = 1
        self.shift_enter = True
        self.autofocus = True

  def run_prompt(self, event):
    text = self.value
    run_prompt(event)
    self.value = ""
    self.update()

class Drop(Dropdown):
  def __init__(self):
    super().__init__()
    self.width = 290
    self.border_color= colors.INDIGO_ACCENT_700
    self.alignment = alignment.center_left
    self.options_fill_horizontally = True

class PDF_Value(TextField):
  def __init__(self, label: str):
    super().__init__()
    self.label = label
    self.height = 60
    self.width = 290
    self.label_style = TextStyle(size= 12)
    self.border_color = colors.INDIGO

class GPTManager:
    def __init__(self):
        self.gpt_answer = ""  # Initialize an empty string

    def update_answer(self, new_answer):
        self.gpt_answer = new_answer  # Update with new GPT answer

    def get_answer(self):
        return self.gpt_answer  # Return the stored GPT answer

class ProgressRingManager:
    def __init__(self, progress_ring, page, changer):
        self.progress_ring = progress_ring
        self.page = page
        self.changer = changer
        self.stop_event = threading.Event()
        self.thread = None

    # Start the color changer in a thread
    def start(self):
        self.thread = threading.Thread(target=self.color_changer)
        self.thread.start()

    # Method to change ProgressRing colors in a separate thread
    def color_changer(self):
        while not self.stop_event.is_set():
            self.progress_ring.color = self.changer # Set random color
            self.page.update()  # Update page to reflect the color change
            time.sleep(0.5)  # Change color every 0.5 seconds

    # Stop the color-changing thread
    def stop(self):
        if self.thread:
            self.stop_event.set()  # Signal the thread to stop
            self.thread.join()  # Wait for the thread to finish