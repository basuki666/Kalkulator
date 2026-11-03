from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class KalkulatorApp(App):
    def build(self):
        self.operators = ["/", "*", "+", "-"]
        self.last_was_operator = None
        self.last_button = None
        
        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        
        # Layar Tampilan Angka
        self.solution = TextInput(
            multiline=False, readonly=True, halign="right", font_size=55
        )
        main_layout.add_widget(self.solution)
        
        # Tombol-tombol Kalkulator
        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            [".", "0", "C", "+"]
        ]
        
        grid_layout = GridLayout(cols=4, spacing=10)
        for row in buttons:
            for label in row:
                button = Button(
                    text=label, font_size=30,
                    background_color=[0.2, 0.6, 0.8, 1]
                )
                button.bind(on_press=self.on_button_press)
                grid_layout.add_widget(button)
                
        # Tombol Sama Dengan (=)
        equals_button = Button(
            text="=", font_size=30, background_color=[0.9, 0.4, 0.4, 1]
        )
        equals_button.bind(on_press=self.on_solution)
        
        main_layout.add_widget(grid_layout)
        main_layout.add_widget(equals_button)
        
        return main_layout

    def on_button_press(self, instance):
        current = self.solution.text
        button_text = instance.text
        
        if button_text == "C":
            self.solution.text = ""
        else:
            if current and (self.last_was_operator and button_text in self.operators):
                return
            elif current == "" and button_text in self.operators:
                return
            else:
                new_text = current + button_text
                self.solution.text = new_text
        self.last_button = button_text
        self.last_was_operator = button_text in self.operators

    def on_solution(self, instance):
        text = self.solution.text
        if text:
            try:
                self.solution.text = str(eval(text))
            except Exception:
                self.solution.text = "Error"

if __name__ == "__main__":
    KalkulatorApp().run()

