import random

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget


INK = (0.10, 0.12, 0.19, 1)
PANEL = (0.17, 0.20, 0.29, 1)
GOLD = (0.96, 0.72, 0.30, 1)
CREAM = (0.97, 0.91, 0.75, 1)


class WordQuestApp(App):
    title = "Rune & Rimba"

    def build(self):
        self.level = 1
        self.hero_hp = 100
        self.enemy_hp = 100
        self.selected = []
        self.busy = False
        self.enemy_names = ["Lumut Rakus", "Gagak Bara", "Ratu Kabut", "Naga Akar"]
        self.root_box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(9))
        self.root_box.bind(size=self._resize)
        with self.root_box.canvas.before:
            from kivy.graphics import Color, Rectangle
            self.bg_color = Color(*INK)
            self.bg_rect = Rectangle(pos=self.root_box.pos, size=self.root_box.size)
        self.root_box.bind(pos=self._pos)

        header = BoxLayout(size_hint_y=None, height=dp(42))
        self.title_label = Label(text="[b]RUNE & RIMBA[/b]", markup=True, color=GOLD,
                                 font_size="22sp", halign="left")
        self.stage_label = Label(text="Bab 1 · Hutan Berbisik", color=CREAM,
                                 font_size="13sp", halign="right")
        header.add_widget(self.title_label)
        header.add_widget(self.stage_label)
        self.root_box.add_widget(header)

        self.enemy_card = FloatLayout(size_hint_y=0.30)
        from kivy.graphics import Color, RoundedRectangle
        with self.enemy_card.canvas.before:
            Color(*PANEL)
            self.card_rect = RoundedRectangle(pos=self.enemy_card.pos, size=self.enemy_card.size,
                                              radius=[dp(16)])
        self.enemy_card.bind(pos=lambda w, p: setattr(self.card_rect, 'pos', p),
                             size=lambda w, s: setattr(self.card_rect, 'size', s))

        self.enemy_emoji = Label(text="🍃", font_size="48sp", size_hint=(None, None),
                                 size=(dp(64), dp(62)))
        self.enemy_label = Label(text="[b]Lumut Rakus[/b]", markup=True, color=CREAM,
                                 font_size="18sp", size_hint=(0.55, None), height=dp(28),
                                 pos_hint={"center_x": 0.58, "center_y": 0.37})
        self.enemy_bar = ProgressBar(max=100, value=100, size_hint=(0.72, None),
                                     height=dp(12), pos_hint={"center_x": 0.58, "y": 0.10})
        self.enemy_hp_label = Label(text="100 / 100", color=CREAM, font_size="12sp",
                                    size_hint=(0.72, None), height=dp(18),
                                    pos_hint={"center_x": 0.58, "y": 0.01})
        self.hero_sprite = Label(text="🧙", font_size="42sp", size_hint=(None, None),
                                 size=(dp(62), dp(62)))
        self.hit_effect = Label(text="⚔️✨", font_size="30sp", size_hint=(None, None),
                                size=(dp(76), dp(48)), opacity=0)
        for w in (self.enemy_emoji, self.enemy_label, self.enemy_bar, self.enemy_hp_label,
                  self.hero_sprite, self.hit_effect):
            self.enemy_card.add_widget(w)
        self.enemy_card.bind(size=self._layout_battle_sprites,
                             pos=self._layout_battle_sprites)
        self._layout_battle_sprites()
        self.root_box.add_widget(self.enemy_card)

        self.message = Label(text="Pilih huruf untuk merangkai mantra serangan.", color=CREAM,
                             font_size="14sp", size_hint_y=None, height=dp(30))
        self.root_box.add_widget(self.message)
        self.word_label = Label(text="—", color=GOLD, font_size="26sp", bold=True,
                                size_hint_y=None, height=dp(42))
        self.root_box.add_widget(self.word_label)

        self.tiles = GridLayout(cols=4, spacing=dp(8), padding=dp(2), size_hint_y=0.40)
        self.tile_buttons = []
        for i in range(16):
            b = Button(text="", font_size="24sp", bold=True, color=INK,
                       background_normal="", background_color=CREAM)
            b.bind(on_release=lambda btn, idx=i: self.pick(idx))
            self.tiles.add_widget(b)
            self.tile_buttons.append(b)
        self.root_box.add_widget(self.tiles)

        controls = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.clear_button = Button(text="HAPUS", font_size="14sp", background_normal="",
                                   background_color=(0.36, 0.39, 0.48, 1))
        self.clear_button.bind(on_release=lambda *_: self.clear_word())
        self.attack_button = Button(text="SERANG ✦", font_size="16sp", bold=True,
                                    background_normal="", background_color=GOLD, color=INK)
        self.attack_button.bind(on_release=lambda *_: self.attack())
        controls.add_widget(self.clear_button)
        controls.add_widget(self.attack_button)
        self.root_box.add_widget(controls)

        self.hero_card = BoxLayout(orientation="vertical", padding=(dp(12), dp(5)), spacing=dp(3),
                                   size_hint_y=None, height=dp(66))
        self.hero_label = Label(text="[b]Aru · Penjelajah Rune[/b]     ❤️ 100 / 100",
                                markup=True, color=CREAM, font_size="14sp", halign="left")
        self.hero_bar = ProgressBar(max=100, value=100, size_hint_y=None, height=dp(10))
        self.hero_card.add_widget(self.hero_label)
        self.hero_card.add_widget(self.hero_bar)
        self.root_box.add_widget(self.hero_card)
        self.new_tiles()
        return self.root_box

    def _layout_battle_sprites(self, *_):
        if not hasattr(self, "hero_sprite"):
            return
        self.hero_start_x = dp(14)
        self.hero_sprite.pos = (self.hero_start_x, self.enemy_card.height * 0.36)
        self.enemy_start_x = self.enemy_card.width * 0.70
        self.enemy_emoji.pos = (self.enemy_start_x, self.enemy_card.height * 0.34)
        self.hit_effect.pos = (self.enemy_card.width * 0.49, self.enemy_card.height * 0.55)

    def _play_attack_animation(self):
        hero_target_x = max(self.hero_start_x + dp(55), self.enemy_start_x - dp(32))
        hero = (Animation(x=hero_target_x, duration=0.22, t="out_quad") +
                Animation(x=hero_target_x - dp(9), duration=0.07) +
                Animation(x=hero_target_x, duration=0.07) +
                Animation(x=self.hero_start_x, duration=0.24, t="out_quad"))
        hero.start(self.hero_sprite)

        hit = (Animation(opacity=1, duration=0.08) +
               Animation(opacity=0, duration=0.28))
        Clock.schedule_once(lambda _dt: hit.start(self.hit_effect), 0.20)

        shake = (Animation(x=self.enemy_start_x + dp(8), duration=0.05) +
                 Animation(x=self.enemy_start_x - dp(8), duration=0.06) +
                 Animation(x=self.enemy_start_x + dp(5), duration=0.05) +
                 Animation(x=self.enemy_start_x, duration=0.06))
        Clock.schedule_once(lambda _dt: shake.start(self.enemy_emoji), 0.22)

    def _resize(self, *_):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = self.root_box.size

    def _pos(self, *_):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.root_box.pos

    def new_tiles(self):
        bag = "AAAAEEEEIIINNNRRRRTTTSSSLOODGMUPK"
        for b in self.tile_buttons:
            b.text = random.choice(bag)
            b.disabled = False
            b.opacity = 1
            b.background_color = CREAM
        self.selected = []
        self.update_word()

    def pick(self, idx):
        if self.busy or self.tile_buttons[idx].disabled:
            return
        self.selected.append(idx)
        self.tile_buttons[idx].disabled = True
        self.tile_buttons[idx].background_color = GOLD
        self.update_word()

    def update_word(self):
        self.word_label.text = "".join(self.tile_buttons[i].text for i in self.selected) or "—"

    def clear_word(self):
        if self.busy:
            return
        for i in self.selected:
            self.tile_buttons[i].disabled = False
            self.tile_buttons[i].background_color = CREAM
        self.selected = []
        self.update_word()

    def attack(self):
        if self.busy:
            return
        word = "".join(self.tile_buttons[i].text for i in self.selected)
        if len(word) < 2:
            self.message.text = "Rangkai minimal dua huruf dulu."
            return
        damage = min(45, 5 + len(word) * 5 + sum(2 for c in word if c in "KZQX"))
        self.enemy_hp = max(0, self.enemy_hp - damage)
        self.enemy_bar.value = self.enemy_hp
        self.enemy_hp_label.text = f"{self.enemy_hp} / 100"
        self.message.text = f"Mantra {word.title()} memberi {damage} kerusakan!"
        self.busy = True
        self.attack_button.disabled = True
        self.clear_button.disabled = True
        self._play_attack_animation()
        Clock.schedule_once(self.after_attack, 0.68)

    def after_attack(self, _dt):
        if self.enemy_hp <= 0:
            self.level += 1
            self.message.text = "Musuh tumbang! Perjalanan berlanjut…"
            if self.level > 4:
                self.level = 1
                self.message.text = "Hutan selamat! Petualangan baru dimulai."
            self.enemy_hp = 100
            name = self.enemy_names[(self.level - 1) % len(self.enemy_names)]
            self.enemy_label.text = f"[b]{name}[/b]"
            self.enemy_emoji.text = ["🍃", "🐦‍⬛", "🌫️", "🐉"][(self.level - 1) % 4]
            self.stage_label.text = f"Bab {self.level} · Hutan Berbisik"
            self.enemy_bar.value = 100
            self.enemy_hp_label.text = "100 / 100"
        else:
            hit = min(25, 8 + self.level * 3)
            self.hero_hp = max(0, self.hero_hp - hit)
            self.hero_bar.value = self.hero_hp
            self.hero_label.text = f"[b]Aru · Penjelajah Rune[/b]     ❤️ {self.hero_hp} / 100"
            if self.hero_hp <= 0:
                self.hero_hp = 100
                self.hero_bar.value = 100
                self.hero_label.text = "[b]Aru · Penjelajah Rune[/b]     ❤️ 100 / 100"
                self.message.text = "Aru beristirahat dan pulih. Coba rangkai kata lebih panjang!"
            else:
                self.message.text += f"  {self.enemy_label.text.replace('[b]', '').replace('[/b]', '')} membalas {hit}!"
        self.new_tiles()
        self.busy = False
        self.attack_button.disabled = False
        self.clear_button.disabled = False


if __name__ == "__main__":
    WordQuestApp().run()
