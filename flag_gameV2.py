from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

import cv2
import numpy as np
import os
import random

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text="GUESS THE FLAGS!", font_size=40, size_hint_y=None, height=100)
        layout.add_widget(title)
        
        mode_label = Label(text="Select Game Mode:", font_size=24, size_hint_y=None, height=50)
        layout.add_widget(mode_label)
        
        pixelated_button = Button(text="1. Pixelated", size_hint_y=None, height=60, background_color=(0.5, 0.7, 1, 1))
        normal_button = Button(text="2. Normal", size_hint_y=None, height=60, background_color=(0.5, 0.7, 1, 1))
        pixelated_button.bind(on_press=lambda x: self.set_game_mode(1))
        normal_button.bind(on_press=lambda x: self.set_game_mode(2))
        layout.add_widget(pixelated_button)
        layout.add_widget(normal_button)
        
        self.add_widget(layout)

    def set_game_mode(self, mode):
        app = App.get_running_app()
        app.GAME_MODE = mode
        self.manager.current = 'difficulty'

class DifficultyScreen(Screen):
    def __init__(self, **kwargs):
        super(DifficultyScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        difficulty_label = Label(text="Select Difficulty:", font_size=24, size_hint_y=None, height=50)
        layout.add_widget(difficulty_label)
        
        easy_button = Button(text="1. Easy Peasy Lemon Squeezy", size_hint_y=None, height=60, background_color=(0.5, 1, 0.5, 1))
        normal_button = Button(text="2. Normie", size_hint_y=None, height=60, background_color=(1, 1, 0.5, 1))
        hard_button = Button(text="3. Vexillologist", size_hint_y=None, height=60, background_color=(1, 0.5, 0.5, 1))
        
        easy_button.bind(on_press=lambda x: self.set_difficulty(1))
        normal_button.bind(on_press=lambda x: self.set_difficulty(2))
        hard_button.bind(on_press=lambda x: self.set_difficulty(3))
        
        layout.add_widget(easy_button)
        layout.add_widget(normal_button)
        layout.add_widget(hard_button)
        
        self.add_widget(layout)

    def set_difficulty(self, difficulty):
        app = App.get_running_app()
        app.SPEED = difficulty
        self.manager.current = 'game_length'

class GameLengthScreen(Screen):
    def __init__(self, **kwargs):
        super(GameLengthScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        length_label = Label(text="Enter number of flags (max 250):", font_size=24, size_hint_y=None, height=50)
        layout.add_widget(length_label)
        
        self.length_input = TextInput(text='10', input_filter='int', multiline=False, font_size=24, size_hint_y=None, height=50)
        layout.add_widget(self.length_input)
        
        start_button = Button(text="Start Game", size_hint_y=None, height=60, background_color=(0.5, 1, 0.5, 1))
        start_button.bind(on_press=self.start_game)
        layout.add_widget(start_button)
        
        self.add_widget(layout)

    def start_game(self, instance):
        app = App.get_running_app()
        try:
            app.GAME_LENGTH = min(250, max(1, int(self.length_input.text)))
        except ValueError:
            app.GAME_LENGTH = 10
        app.setup_game()
        self.manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        self.add_widget(self.layout)

    def setup_game_ui(self):
        self.layout.clear_widgets()
        
        top_layout = BoxLayout(size_hint_y=0.1)
        self.score_label = Label(text='Score: 0', font_size=20)
        self.timer_label = Label(text='Time: 10', font_size=20)
        top_layout.add_widget(self.score_label)
        top_layout.add_widget(self.timer_label)
        self.layout.add_widget(top_layout)
        
        self.img = Image(size_hint=(1, 0.7))
        self.layout.add_widget(self.img)
        
        bottom_layout = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=5)
        self.guess_input = TextInput(hint_text='Enter your guess', multiline=False, font_size=18, size_hint_y=None, height=40)
        self.submit_button = Button(text='Submit', size_hint_y=None, height=40, background_color=(0.5, 0.7, 1, 1))
        self.result_label = Label(text='', font_size=18)
        
        bottom_layout.add_widget(self.guess_input)
        bottom_layout.add_widget(self.submit_button)
        bottom_layout.add_widget(self.result_label)
        
        self.layout.add_widget(bottom_layout)

class GuessTheFlagsApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(DifficultyScreen(name='difficulty'))
        self.sm.add_widget(GameLengthScreen(name='game_length'))
        self.game_screen = GameScreen(name='game')
        self.sm.add_widget(self.game_screen)
        return self.sm

    def setup_game(self):
        current_directory = os.getcwd()
        folder = os.path.join(current_directory, "FLAGS")
        flag_list = []

        for i in os.scandir(folder):
            if i.is_file():
                temp = [i.name[:-4], os.path.join(folder, i.name)]
                flag_list.append(temp)

        self.game_list = random.sample(flag_list, self.GAME_LENGTH)
        self.iterations = 0
        self.pixel_size = 1
        self.score = 0

        if self.SPEED == 1:
            self.guess_time = 10
        elif self.SPEED == 2:
            self.guess_time = 7
        else:
            self.guess_time = 5

        self.game_screen.setup_game_ui()
        self.game_screen.submit_button.bind(on_press=self.check_answer)
        self.start_game()

    def start_game(self):
        self.update_flag()

    def update_flag(self):
        if self.iterations < self.GAME_LENGTH:
            if self.GAME_MODE == 1:
                self.pixel_size = max(1,(self.iterations // 2)*5)

            flag_image = self.pixelate(self.game_list[self.iterations][1], self.pixel_size)
            texture = Texture.create(size=(flag_image.shape[1], flag_image.shape[0]), colorfmt='rgb')
            texture.blit_buffer(flag_image.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            self.game_screen.img.texture = texture

            self.game_screen.guess_input.text = ''
            self.game_screen.result_label.text = ''
            self.game_screen.submit_button.disabled = False
            self.remaining_time = self.guess_time
            self.update_timer(None)
            Clock.schedule_interval(self.update_timer, 1)
        else:
            self.show_game_over()

    def update_timer(self, dt):
        self.game_screen.timer_label.text = f'Time: {self.remaining_time}'
        if self.remaining_time <= 0:
            self.time_up(None)
            return False
        self.remaining_time -= 1

    def check_answer(self, instance):
        Clock.unschedule(self.update_timer)
        user_guess = self.game_screen.guess_input.text.strip().lower()
        correct_answer = self.game_list[self.iterations][0].lower()
        
        if user_guess == correct_answer:
            self.score += 1
            self.game_screen.result_label.text = f"Correct! The answer is {correct_answer}"
        else:
            self.game_screen.result_label.text = f"Wrong. The correct answer is {correct_answer}"
        
        self.game_screen.score_label.text = f'Score: {self.score}'
        self.game_screen.submit_button.disabled = True
        Clock.schedule_once(lambda dt: self.next_flag(), 2)

    def time_up(self, dt):
        Clock.unschedule(self.update_timer)
        if not self.game_screen.submit_button.disabled:
            self.game_screen.result_label.text = f"Time's up! The correct answer is {self.game_list[self.iterations][0]}"
            self.game_screen.submit_button.disabled = True
            Clock.schedule_once(lambda dt: self.next_flag(), 2)

    def next_flag(self):
        self.iterations += 1
        self.update_flag()

    def pixelate(self, image_path, pixel_size):
        img = cv2.imread(image_path)
        img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)  # Increased size
        height, width, channels = img.shape

        if self.GAME_MODE == 1:
            pad_x = (pixel_size - width % pixel_size) % pixel_size
            pad_y = (pixel_size - height % pixel_size) % pixel_size
            img = np.pad(img, ((0, pad_y), (0, pad_x), (0, 0)), mode='constant', constant_values=0)

            h, w, c = img.shape
            blocks = np.mean(img.reshape(h // pixel_size, pixel_size, -1, pixel_size, c), axis=(1, 3))
            output = np.repeat(np.repeat(blocks, pixel_size, axis=1), pixel_size, axis=0)
            output = output[:height, :width].astype("uint8")
        else:
            output = img

        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output

    def show_game_over(self):
        self.game_screen.layout.clear_widgets()
        game_over_label = Label(text=f'Game Over!\nFinal Score: {self.score}/{self.GAME_LENGTH}', font_size=30, halign='center')
        self.game_screen.layout.add_widget(game_over_label)

if __name__ == '__main__':
    Window.size = (800, 500)  # Set window size for mobile-like appearance
    GuessTheFlagsApp().run()