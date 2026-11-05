import random

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle, Triangle
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


class MonsterSprite(Widget):
    PALETTES = (
        ((0.20, 0.62, 0.37), (0.39, 0.82, 0.48), (0.12, 0.36, 0.25)),
        ((0.72, 0.30, 0.20), (0.96, 0.54, 0.28), (0.40, 0.16, 0.20)),
        ((0.31, 0.52, 0.78), (0.60, 0.77, 0.96), (0.16, 0.28, 0.52)),
        ((0.48, 0.32, 0.72), (0.73, 0.52, 0.91), (0.26, 0.18, 0.44)),
    )

    def __init__(self, variant=0, **kwargs):
        super().__init__(**kwargs)
        self.variant = variant
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def set_variant(self, variant):
        self.variant = variant % len(self.PALETTES)
        self.redraw()

    def redraw(self, *_):
        if self.width <= 0 or self.height <= 0:
            return
        x, y = self.pos
        w, h = self.size
        main, light, shade = self.PALETTES[self.variant]
        cx = x + w * 0.5
        self.canvas.clear()
        with self.canvas:
            Color(0.03, 0.05, 0.09, 0.42)
            Ellipse(pos=(x + w * 0.12, y + h * 0.03), size=(w * 0.76, h * 0.12))
            # Separate legs and feet
            Color(*shade, 1)
            RoundedRectangle(pos=(x + w * 0.32, y + h * 0.14), size=(w * 0.15, h * 0.25), radius=[w * 0.07])
            RoundedRectangle(pos=(x + w * 0.54, y + h * 0.14), size=(w * 0.15, h * 0.25), radius=[w * 0.07])
            Color(*main, 1)
            Ellipse(pos=(x + w * 0.24, y + h * 0.08), size=(w * 0.25, h * 0.12))
            Ellipse(pos=(x + w * 0.51, y + h * 0.08), size=(w * 0.25, h * 0.12))
            # Arms with visible hands
            Color(*shade, 1)
            RoundedRectangle(pos=(x + w * 0.12, y + h * 0.40), size=(w * 0.20, h * 0.13), radius=[w * 0.06])
            RoundedRectangle(pos=(x + w * 0.68, y + h * 0.40), size=(w * 0.20, h * 0.13), radius=[w * 0.06])
            Color(*light, 1)
            Ellipse(pos=(x + w * 0.06, y + h * 0.37), size=(w * 0.16, h * 0.18))
            Ellipse(pos=(x + w * 0.78, y + h * 0.37), size=(w * 0.16, h * 0.18))
            # Broad torso, head and horns
            Color(*main, 1)
            RoundedRectangle(pos=(x + w * 0.25, y + h * 0.30), size=(w * 0.50, h * 0.40), radius=[w * 0.17])
            Color(*light, 1)
            Ellipse(pos=(x + w * 0.34, y + h * 0.38), size=(w * 0.32, h * 0.18))
            Color(*shade, 1)
            Triangle(points=[x + w * 0.32, y + h * 0.64, x + w * 0.30, y + h * 0.91, x + w * 0.47, y + h * 0.70])
            Triangle(points=[x + w * 0.68, y + h * 0.64, x + w * 0.70, y + h * 0.91, x + w * 0.53, y + h * 0.70])
            Color(*main, 1)
            Ellipse(pos=(x + w * 0.29, y + h * 0.58), size=(w * 0.42, h * 0.32))
            Color(*light, 1)
            Ellipse(pos=(x + w * 0.33, y + h * 0.71), size=(w * 0.34, h * 0.14))
            Color(1.0, 0.88, 0.43, 1)
            Ellipse(pos=(x + w * 0.37, y + h * 0.70), size=(w * 0.09, h * 0.09))
            Ellipse(pos=(x + w * 0.54, y + h * 0.70), size=(w * 0.09, h * 0.09))
            Color(0.08, 0.10, 0.16, 1)
            Ellipse(pos=(x + w * 0.40, y + h * 0.72), size=(w * 0.035, h * 0.06))
            Ellipse(pos=(x + w * 0.57, y + h * 0.72), size=(w * 0.035, h * 0.06))
            Color(*light, 1)
            Line(points=[cx - w * 0.10, y + h * 0.63, cx, y + h * 0.60, cx + w * 0.10, y + h * 0.63], width=max(1, dp(2)))


class WordQuestApp(App):
    title = "Rune & Rimba"

    def build(self):
        self.level = 1
        self.hero_hp = 100
        self.enemy_hp = 100
        self.selected = []
        self.busy = False
        self.enemy_names = ["Lumut Rakus", "Gagak Bara", "Ratu Kabut", "Naga Akar"]
        self.root_box = BoxLayout(orientation="horizontal", padding=dp(12), spacing=dp(10))
        self.root_box.bind(size=self._resize)
        with self.root_box.canvas.before:
            from kivy.graphics import Color, Rectangle
            self.bg_color = Color(*INK)
            self.bg_rect = Rectangle(pos=self.root_box.pos, size=self.root_box.size)
        self.root_box.bind(pos=self._pos)

        self.battle_panel = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_x=0.48)
        self.game_panel = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_x=0.52)
        self.root_box.add_widget(self.battle_panel)
        self.root_box.add_widget(self.game_panel)

        header = BoxLayout(size_hint_y=None, height=dp(42))
        self.title_label = Label(text="[b]RUNE & RIMBA[/b]", markup=True, color=GOLD,
                                 font_size="22sp", halign="left")
        self.stage_label = Label(text="Bab 1 · Hutan Berbisik", color=CREAM,
                                 font_size="13sp", halign="right")
        header.add_widget(self.title_label)
        header.add_widget(self.stage_label)
        self.battle_panel.add_widget(header)

        self.enemy_card = FloatLayout(size_hint_y=0.30)
        from kivy.graphics import Color, RoundedRectangle
        with self.enemy_card.canvas.before:
            Color(*PANEL)
            self.card_rect = RoundedRectangle(pos=self.enemy_card.pos, size=self.enemy_card.size,
                                              radius=[dp(16)])
        self.enemy_card.bind(pos=lambda w, p: setattr(self.card_rect, 'pos', p),
                             size=lambda w, s: setattr(self.card_rect, 'size', s))

        self.enemy_sprite = MonsterSprite(size_hint=(None, None), size=(dp(112), dp(112)))
        self.enemy_label = Label(text="[b]Lumut Rakus[/b]", markup=True, color=CREAM,
                                 font_size="16sp", size_hint=(0.52, None), height=dp(30),
                                 pos_hint={"center_x": 0.30, "center_y": 0.80})
        self.enemy_bar = ProgressBar(max=100, value=100, size_hint=(0.90, None),
                                     height=dp(12), pos_hint={"center_x": 0.50, "y": 0.11})
        self.enemy_hp_label = Label(text="100 / 100", color=CREAM, font_size="12sp",
                                    size_hint=(0.90, None), height=dp(18),
                                    pos_hint={"center_x": 0.50, "y": 0.01})
        self.hero_sprite = Label(text="ARU", font_size="13sp", bold=True, color=GOLD,
                                 size_hint=(None, None), size=(dp(62), dp(62)))
        self.hit_effect = Label(text="HIT!", font_size="20sp", bold=True, color=GOLD,
                                size_hint=(None, None), size=(dp(76), dp(48)), opacity=0)
        for w in (self.enemy_sprite, self.enemy_label, self.enemy_bar, self.enemy_hp_label,
                  self.hero_sprite, self.hit_effect):
            self.enemy_card.add_widget(w)
        self.enemy_card.bind(size=self._layout_battle_sprites,
                             pos=self._layout_battle_sprites)
        self._layout_battle_sprites()
        self.battle_panel.add_widget(self.enemy_card)

        self.message = Label(text="Pilih huruf untuk merangkai mantra serangan.", color=CREAM,
                             font_size="13sp", halign="left", valign="middle",
                             size_hint_y=None, height=dp(56))
        self.message.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
        self.battle_panel.add_widget(self.message)
        self.word_label = Label(text="—", color=GOLD, font_size="26sp", bold=True,
                                size_hint_y=None, height=dp(42))
        self.game_panel.add_widget(self.word_label)

        self.tiles = GridLayout(cols=4, spacing=dp(8), padding=dp(2), size_hint_y=0.40)
        self.tile_buttons = []
        for i in range(16):
            b = Button(text="", font_size="24sp", bold=True, color=INK,
                       background_normal="", background_color=CREAM)
            b.bind(on_release=lambda btn, idx=i: self.pick(idx))
            self.tiles.add_widget(b)
            self.tile_buttons.append(b)
        self.game_panel.add_widget(self.tiles)

        controls = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.clear_button = Button(text="HAPUS", font_size="14sp", background_normal="",
                                   background_color=(0.36, 0.39, 0.48, 1))
        self.clear_button.bind(on_release=lambda *_: self.clear_word())
        self.attack_button = Button(text="SERANG", font_size="16sp", bold=True,
                                    background_normal="", background_color=GOLD, color=INK)
        self.attack_button.bind(on_release=lambda *_: self.attack())
        controls.add_widget(self.clear_button)
        controls.add_widget(self.attack_button)
        self.game_panel.add_widget(controls)

        self.hero_card = BoxLayout(orientation="vertical", padding=(dp(12), dp(5)), spacing=dp(3),
                                   size_hint_y=None, height=dp(66))
        self.hero_label = Label(text="[b]Aru · Penjelajah Rune[/b]     HP 100 / 100",
                                markup=True, color=CREAM, font_size="14sp", halign="left")
        self.hero_bar = ProgressBar(max=100, value=100, size_hint_y=None, height=dp(10))
        self.hero_card.add_widget(self.hero_label)
        self.hero_card.add_widget(self.hero_bar)
        self.battle_panel.add_widget(self.hero_card)
        self.new_tiles()
        return self.root_box

    def _layout_battle_sprites(self, *_):
        if not hasattr(self, "hero_sprite"):
            return
        self.hero_start_x = dp(14)
        self.hero_sprite.pos = (self.hero_start_x, self.enemy_card.height * 0.36)
        monster_size = min(dp(154), self.enemy_card.height * 0.76, self.enemy_card.width * 0.42)
        self.enemy_start_x = self.enemy_card.width - monster_size - dp(10)
        self.enemy_base_y = self.enemy_card.height * 0.19
        self.enemy_base_size = (monster_size, monster_size)
        self.enemy_sprite.size = self.enemy_base_size
        self.enemy_sprite.pos = (self.enemy_start_x, self.enemy_base_y)
        self.hit_effect.pos = (self.enemy_card.width * 0.51, self.enemy_card.height * 0.55)

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
        Clock.schedule_once(lambda _dt: shake.start(self.enemy_sprite), 0.22)

    def _play_monster_attack_animation(self):
        start_x = self.enemy_start_x
        start_y = self.enemy_base_y
        start_size = self.enemy_base_size
        target_x = self.hero_start_x + dp(34)
        enlarged = (start_size[0] * 1.42, start_size[1] * 1.42)
        lunge = (Animation(x=target_x, y=start_y + dp(9), size=enlarged,
                           duration=0.22, t="out_back") +
                 Animation(x=start_x, y=start_y, size=start_size,
                           duration=0.30, t="out_quad"))
        lunge.start(self.enemy_sprite)

        hit = (Animation(opacity=1, duration=0.08) +
               Animation(opacity=0, duration=0.28))

        def show_hit_effect(_dt):
            self.hit_effect.text = "POW!"
            hit.start(self.hit_effect)
            Clock.schedule_once(lambda _later: setattr(self.hit_effect, "text", "HIT!"), 0.45)

        Clock.schedule_once(show_hit_effect, 0.18)

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
        monster_counterattacked = False
        if self.enemy_hp <= 0:
            self.level += 1
            self.message.text = "Musuh tumbang! Perjalanan berlanjut…"
            if self.level > 4:
                self.level = 1
                self.message.text = "Hutan selamat! Petualangan baru dimulai."
            self.enemy_hp = 100
            name = self.enemy_names[(self.level - 1) % len(self.enemy_names)]
            self.enemy_label.text = f"[b]{name}[/b]"
            self.enemy_sprite.set_variant(self.level - 1)
            self.stage_label.text = f"Bab {self.level} · Hutan Berbisik"
            self.enemy_bar.value = 100
            self.enemy_hp_label.text = "100 / 100"
        else:
            monster_counterattacked = True
            self._play_monster_attack_animation()
            hit = min(25, 8 + self.level * 3)
            self.hero_hp = max(0, self.hero_hp - hit)
            self.hero_bar.value = self.hero_hp
            self.hero_label.text = f"[b]Aru · Penjelajah Rune[/b]     HP {self.hero_hp} / 100"
            if self.hero_hp <= 0:
                self.hero_hp = 100
                self.hero_bar.value = 100
                self.hero_label.text = "[b]Aru · Penjelajah Rune[/b]     HP 100 / 100"
                self.message.text = "Aru beristirahat dan pulih. Coba rangkai kata lebih panjang!"
            else:
                self.message.text += f"  {self.enemy_label.text.replace('[b]', '').replace('[/b]', '')} membalas {hit}!"
        self.new_tiles()
        if monster_counterattacked:
            Clock.schedule_once(self.finish_turn, 0.55)
        else:
            self.finish_turn()

    def finish_turn(self, _dt=0):
        self.busy = False
        self.attack_button.disabled = False
        self.clear_button.disabled = False


if __name__ == "__main__":
    WordQuestApp().run()
