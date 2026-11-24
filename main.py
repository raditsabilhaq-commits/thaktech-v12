from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp
import random

class Card(BoxLayout):
    def __init__(self, bg=(1,1,1,1), **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(12)
        self.spacing = dp(6)
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self.update, size=self.update)
    def update(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ThakApp(App):
    def build(self):
        try:
            root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
            scroll = ScrollView()
            main = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            main.bind(minimum_height=main.setter('height'))

            main.add_widget(Label(text='[b][color=FFD700]THAKTECH[/color] [color=333333]ULTIMATE[/color][/b]', markup=True, font_size=dp(28), size_hint_y=None, height=dp(35)))
            main.add_widget(Label(text='SMART DIAGNOSTIC SYSTEM', font_size=dp(11), bold=True, color=(0.3,0.3,0.3,1), size_hint_y=None, height=dp(16)))
            main.add_widget(Label(text='ARTIFICIAL PITSTOP', font_size=dp(10), bold=True, color=(0,0.6,0.8,1), size_hint_y=None, height=dp(18)))

            c = Card(bg=(1,1,1,1), orientation='vertical', size_hint_y=None, height=dp(115))
            c.add_widget(Label(text='[b]HASIL SCAN - HONDA[/b] [color=0099FF]OK[/color]', markup=True, font_size=dp(16), halign='left', size_hint_y=None, height=dp(22)))
            c.add_widget(Label(text='[b][color=FF8C00]8-1  P0122[/color][/b]  TP Sensor Low - Throttle Position Sensor Low', markup=True, font_size=dp(11), halign='left', size_hint_y=None, height=dp(32)))
            c.add_widget(Label(text='Level: [b][color=FFAA00]SEDANG[/color][/b]   Gejala: -', markup=True, font_size=dp(11), halign='left', size_hint_y=None, height=dp(20)))
            c.add_widget(Label(text='Motor: Honda Beat / Vario - ELM327 Ready', font_size=dp(10), color=(0.5,0.5,0.5,1), size_hint_y=None, height=dp(16)))
            main.add_widget(c)

            k = Card(bg=(1,1,1,1), orientation='vertical', size_hint_y=None, height=dp(110))
            k.add_widget(Label(text='[b]KESEHATAN MESIN[/b]', markup=True, font_size=dp(14), halign='left', size_hint_y=None, height=dp(22)))
            self.lbl_mesin = Label(text='Mesin: 92% - Optimal', font_size=dp(11), halign='left', size_hint_y=None, height=dp(20))
            self.lbl_baterai = Label(text='Baterai: 88% - Sehat', font_size=dp(11), halign='left', size_hint_y=None, height=dp(20))
            self.lbl_listrik = Label(text='Kelistrikan: 76% - Perlu Cek', font_size=dp(11), halign='left', size_hint_y=None, height=dp(20))
            k.add_widget(self.lbl_mesin); k.add_widget(self.lbl_baterai); k.add_widget(self.lbl_listrik)
            main.add_widget(k)

            grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(210))
            self.lbl_rpm = Label(text='[b]RPM[/b]\n[color=0099FF][b]1480[/b][/color]\nmin-1 - Idle Normal', markup=True, font_size=dp(15))
            self.lbl_suhu = Label(text='[b]SUHU[/b]\n[color=FF6600][b]86C[/b][/color]\nCOOLANT - Normal', markup=True, font_size=dp(15))
            self.lbl_aki = Label(text='[b]AKI[/b]\n[color=00AA00][b]13.8V[/b][/color]\nVOLTASE - Healthy', markup=True, font_size=dp(15))
            self.lbl_speed = Label(text='[b]SPEED[/b]\n[color=0000AA][b]0[/b][/color]\nkm/h - Static', markup=True, font_size=dp(15))
            for lbl, bg in [(self.lbl_rpm,(0.7,0.9,1,1)), (self.lbl_suhu,(1,0.85,0.6,1)), (self.lbl_aki,(0.7,1,0.7,1)), (self.lbl_speed,(0.7,0.8,1,1))]:
                box = Card(bg=bg, orientation='vertical', size_hint_y=None, height=dp(100))
                box.add_widget(lbl)
                grid.add_widget(box)
            main.add_widget(grid)

            r = Card(bg=(1,1,1,1), orientation='vertical', size_hint_y=None, height=dp(80))
            r.add_widget(Label(text='[b]RIWAYAT LIVE (30s)[/b]', markup=True, font_size=dp(12), halign='left', size_hint_y=None, height=dp(20)))
            self.lbl_grafik = Label(text='~~~~~~~~~~~~~~~~~~~~', font_size=dp(16), color=(0,0.6,0.8,1), size_hint_y=None, height=dp(30))
            r.add_widget(self.lbl_grafik)
            main.add_widget(r)

            btns = [('KONEK ELM327', self.konek), ('LIVE DATA', self.live), ('SCAN DTC', self.scan), ('HAPUS DTC', self.hapus), ('REMAP', self.remap), ('READ KEY', self.dummy), ('BATTERY', self.dummy), ('STRUK', self.dummy), ('HARGA', self.dummy), ('HISTORY', self.dummy)]
            g2 = GridLayout(cols=3, spacing=dp(6), size_hint_y=None, height=dp(160))
            for txt, fn in btns:
                b = Button(text=txt, font_size=dp(10), background_color=(0,0.7,0.9,1) if txt in ['KONEK ELM327','LIVE DATA','SCAN DTC'] else (1,0.6,0,1), size_hint_y=None, height=dp(38))
                b.bind(on_press=fn)
                g2.add_widget(b)
            main.add_widget(g2)

            self.lbl_status = Label(text='Status: Belum konek ELM327 - Pencet KONEK ELM327', font_size=dp(11), color=(0.3,0.3,0.3,1), size_hint_y=None, height=dp(20))
            main.add_widget(self.lbl_status)
            scroll.add_widget(main)
            root.add_widget(scroll)

            nav = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(4))
            for t in ['Home', 'Scan', 'Grafik', 'Remap', 'Profil']:
                b = Button(text=t, font_size=dp(11), background_color=(1,0.8,0.2,1) if t=='Home' else (0.9,0.9,0.9,1))
                b.bind(on_press=self.dummy)
                nav.add_widget(b)
            root.add_widget(nav)
            Clock.schedule_interval(self.update_live, 1.0)
            return root
        except Exception as e:
            return Label(text=f'Error load: {e}')

    def update_live(self, dt):
        try:
            rpm = random.randint(1450, 1520)
            suhu = random.randint(84, 88)
            volt = round(random.uniform(13.6, 14.0), 1)
            self.lbl_rpm.text = f'[b]RPM[/b]\n[color=0099FF][b]{rpm}[/b][/color]\nmin-1 - Idle Normal'
            self.lbl_suhu.text = f'[b]SUHU[/b]\n[color=FF6600][b]{suhu}C[/b][/color]\nCOOLANT - Normal'
            self.lbl_aki.text = f'[b]AKI[/b]\n[color=00AA00][b]{volt}V[/b][/color]\nVOLTASE - Healthy'
        except: pass

    def konek(self, x):
        try:
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            adapter = BluetoothAdapter.getDefaultAdapter()
            if adapter is None:
                self.lbl_status.text = 'Status: HP ini tidak ada Bluetooth'
                return
            if not adapter.isEnabled():
                adapter.enable()
            self.lbl_status.text = 'Status: Bluetooth NYALA, cari ELM327 di HP lu'
        except Exception as e:
            self.lbl_status.text = f'Status: BT Belum bisa - {e}'

    def live(self, x):
        self.lbl_status.text = 'Status: LIVE DATA Jalan - RPM gerak'
    def scan(self, x):
        self.lbl_status.text = 'Status: SCAN DTC - Ketemu P0122 TP Sensor Low'
    def hapus(self, x):
        self.lbl_status.text = 'Status: HAPUS DTC - DTC Dihapus'
    def remap(self, x):
        self.lbl_status.text = 'Status: REMAP - Fitur Remap Siap'
    def dummy(self, x):
        try: self.lbl_status.text = f'Status: {x.text} diklik'
        except: pass

ThakApp().run()
