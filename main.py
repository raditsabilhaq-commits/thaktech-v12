from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp
import threading, time

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sock = None
        self.stream_in = None
        self.stream_out = None
        self.connected = False
        self.running = True
        self.real_rpm = 0
        self.real_suhu = 0
        self.real_speed = 0
        self.real_volt = 0.0

    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.lbl_status = Label(text='Status: REAL MODE - Belum konek ELM327', font_size=dp(12), bold=True, color=(0.9,0.2,0.2,1), size_hint_y=None, height=dp(32))
        root.add_widget(self.lbl_status)

        scroll = ScrollView(scroll_timeout=150, scroll_distance=dp(10))
        main = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        main.bind(minimum_height=main.setter('height'))
        self.scroll = scroll

        main.add_widget(Label(text='[b][color=FFD700]THAKTECH[/color] [color=333333]ULTIMATE[/color][/b]', markup=True, font_size=dp(28), size_hint_y=None, height=dp(35)))
        main.add_widget(Label(text='SMART DIAGNOSTIC SYSTEM - REAL OBD', font_size=dp(11), bold=True, color=(0.3,0.3,0.3,1), size_hint_y=None, height=dp(16)))
        main.add_widget(Label(text='ARTIFICIAL PITSTOP - MODE REAL', font_size=dp(10), bold=True, color=(0,0.6,0.8,1), size_hint_y=None, height=dp(18)))

        c = Card(bg=(1,1,1,1), orientation='vertical', size_hint_y=None, height=dp(115))
        c.add_widget(Label(text='[b]HASIL SCAN - HONDA[/b]', markup=True, font_size=dp(16), size_hint_y=None, height=dp(22)))
        self.lbl_dtc = Label(text='Belum scan - Klik SCAN DTC setelah konek', font_size=dp(11), size_hint_y=None, height=dp(32))
        c.add_widget(self.lbl_dtc)
        c.add_widget(Label(text='Motor: Honda Beat / Vario - ELM327 Real', font_size=dp(10), color=(0.5,0.5,0.5,1), size_hint_y=None, height=dp(16)))
        main.add_widget(c)

        k = Card(bg=(1,1,1,1), orientation='vertical', size_hint_y=None, height=dp(110))
        k.add_widget(Label(text='[b]KESEHATAN MESIN (REAL)[/b]', markup=True, font_size=dp(14), size_hint_y=None, height=dp(22)))
        self.lbl_mesin = Label(text='Mesin: - % (Tunggu konek)', font_size=dp(11), size_hint_y=None, height=dp(20))
        self.lbl_baterai = Label(text='Baterai: - % (Tunggu konek)', font_size=dp(11), size_hint_y=None, height=dp(20))
        self.lbl_listrik = Label(text='Kelistrikan: - % (Tunggu konek)', font_size=dp(11), size_hint_y=None, height=dp(20))
        k.add_widget(self.lbl_mesin); k.add_widget(self.lbl_baterai); k.add_widget(self.lbl_listrik)
        main.add_widget(k)

        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(210))
        self.lbl_rpm = Label(text='[b]RPM[/b]\n[color=0099FF][b]-[/b][/color]\nmin-1 - Belum Konek', markup=True, font_size=dp(15))
        self.lbl_suhu = Label(text='[b]SUHU[/b]\n[color=FF6600][b]-[/b][/color]\nCOOLANT - Belum Konek', markup=True, font_size=dp(15))
        self.lbl_aki = Label(text='[b]AKI[/b]\n[color=00AA00][b]-[/b][/color]\nVOLTASE - Belum Konek', markup=True, font_size=dp(15))
        self.lbl_speed = Label(text='[b]SPEED[/b]\n[color=0000AA][b]-[/b][/color]\nkm/h - Belum Konek', markup=True, font_size=dp(15))
        for lbl, bg in [(self.lbl_rpm,(0.7,0.9,1,1)), (self.lbl_suhu,(1,0.85,0.6,1)), (self.lbl_aki,(0.7,1,0.7,1)), (self.lbl_speed,(0.7,0.8,1,1))]:
            box = Card(bg=bg, orientation='vertical', size_hint_y=None, height=dp(100))
            box.add_widget(lbl)
            grid.add_widget(box)
        main.add_widget(grid)

        r = Card(bg=(1,1,1,1), orientation='vertical', size_hint_y=None, height=dp(80))
        r.add_widget(Label(text='[b]RIWAYAT LIVE (REAL)[/b]', markup=True, font_size=dp(12), size_hint_y=None, height=dp(20)))
        self.lbl_grafik = Label(text='Belum ada data - Konek dulu', font_size=dp(12), color=(0,0.6,0.8,1), size_hint_y=None, height=dp(30))
        r.add_widget(self.lbl_grafik)
        main.add_widget(r)

        btns = [('KONEK ELM327', self.konek), ('LIVE DATA', self.live), ('SCAN DTC', self.scan), ('HAPUS DTC', self.hapus), ('REMAP', self.remap), ('PUTUS', self.putus)]
        g2 = GridLayout(cols=3, spacing=dp(6), size_hint_y=None, height=dp(110))
        for txt, fn in btns:
            b = Button(text=txt, font_size=dp(10), background_color=(0,0.7,0.9,1) if txt in ['KONEK ELM327','LIVE DATA','SCAN DTC'] else (1,0.6,0,1), size_hint_y=None, height=dp(44))
            b.bind(on_release=fn)
            g2.add_widget(b)
        main.add_widget(g2)

        scroll.add_widget(main)
        root.add_widget(scroll)

        nav = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(4))
        for t, fn in [('Home', self.nav_home), ('Scan', self.scan), ('Grafik', self.nav_grafik), ('Remap', self.remap), ('Profil', self.dummy)]:
            b = Button(text=t, font_size=dp(12), bold=True, background_color=(1,0.8,0.2,1) if t=='Home' else (0.9,0.9,0.9,1))
            b.bind(on_release=fn)
            nav.add_widget(b)
        root.add_widget(nav)
        Clock.schedule_interval(self.update_ui, 0.5)
        return root

    # --- OBD CORE ---
    def send_cmd(self, cmd):
        if not self.sock: return ""
        try:
            self.stream_out.write((cmd + "\r").encode())
            self.stream_out.flush()
            time.sleep(0.3)
            buf = b""
            # baca sampai ada '>'
            start = time.time()
            while time.time() - start < 2.0:
                if self.stream_in.available() > 0:
                    b = self.stream_in.read()
                    if b == -1: break
                    buf += bytes([b])
                    if b == ord('>'): break
                else:
                    time.sleep(0.05)
            return buf.decode(errors='ignore')
        except Exception as e:
            return f"ERR {e}"

    def parse_obd(self, resp, pid):
        # resp contoh: "41 0C 1A 2B >"
        try:
            resp = resp.replace("\r"," ").replace("\n"," ").replace(">"," ").strip()
            parts = [p for p in resp.split() if len(p)==2]
            # cari "41 PID ..."
            for i in range(len(parts)-1):
                if parts[i]=="41" and parts[i+1]==pid:
                    data = parts[i+2:]
                    if pid=="0C" and len(data)>=2:
                        return ((int(data[0],16)*256)+int(data[1],16))/4
                    if pid=="05" and len(data)>=1:
                        return int(data[0],16)-40
                    if pid=="0D" and len(data)>=1:
                        return int(data[0],16)
                    if pid=="0B" and len(data)>=1:
                        return int(data[0],16)
            return None
        except: return None

    def obd_loop(self):
        # jalan di thread, jangan di UI
        while self.running and self.connected:
            try:
                r = self.send_cmd("010C")
                v = self.parse_obd(r, "0C")
                if v is not None: self.real_rpm = int(v)
                r = self.send_cmd("0105")
                v = self.parse_obd(r, "05")
                if v is not None: self.real_suhu = int(v)
                r = self.send_cmd("010D")
                v = self.parse_obd(r, "0D")
                if v is not None: self.real_speed = int(v)
                r = self.send_cmd("ATRV")
                # ATRV jawab "13.7V"
                try:
                    import re
                    m = re.search(r"(\d+\.\d+)", r)
                    if m: self.real_volt = float(m.group(1))
                except: pass
            except Exception as e:
                print("OBD loop err", e)
            time.sleep(0.5)

    def update_ui(self, dt):
        if not self.connected:
            return
        self.lbl_rpm.text = f'[b]RPM[/b]\n[color=0099FF][b]{self.real_rpm}[/b][/color]\nmin-1 - REAL'
        self.lbl_suhu.text = f'[b]SUHU[/b]\n[color=FF6600][b]{self.real_suhu}C[/b][/color]\nCOOLANT - REAL'
        self.lbl_aki.text = f'[b]AKI[/b]\n[color=00AA00][b]{self.real_volt}V[/b][/color]\nVOLTASE - REAL'
        self.lbl_speed.text = f'[b]SPEED[/b]\n[color=0000AA][b]{self.real_speed}[/b][/color]\nkm/h - REAL'
        self.lbl_grafik.text = f'RPM {self.real_rpm} | Suhu {self.real_suhu}C | {self.real_speed} km/h'
        if self.real_rpm > 0:
            self.lbl_mesin.text = f'Mesin: REAL - RPM {self.real_rpm}'
        if self.real_volt > 0:
            self.lbl_baterai.text = f'Baterai: REAL - {self.real_volt}V'

    # --- BUTTONS ---
    def konek(self, x):
        self.lbl_status.text = 'Status: Mencari ELM327 yang sudah di-pairing...'
        threading.Thread(target=self._konek_thread, daemon=True).start()

    def _konek_thread(self):
        try:
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            UUID = autoclass('java.util.UUID')
            adapter = BluetoothAdapter.getDefaultAdapter()
            if adapter is None:
                Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', 'Status: HP ini tidak ada Bluetooth'))
                return
            if not adapter.isEnabled():
                adapter.enable()
                time.sleep(1.5)
            paired = adapter.getBondedDevices()
            target = None
            for d in paired.toArray():
                name = d.getName()
                if name and any(k in name.upper() for k in ['ELM', 'OBD', 'VLINK', 'OBDII']):
                    target = d
                    break
            if target is None:
                Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', 'Status: ELM327 belum di-pairing! Pairing dulu di Setting > Bluetooth, PIN 1234'))
                return
            Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', f'Status: Nyambung ke {target.getName()}...'))
            uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
            self.sock = target.createRfcommSocketToServiceRecord(uuid)
            adapter.cancelDiscovery()
            self.sock.connect()
            self.stream_in = self.sock.getInputStream()
            self.stream_out = self.sock.getOutputStream()
            # init ELM327
            self.send_cmd("ATZ")
            time.sleep(1)
            self.send_cmd("ATE0")
            self.send_cmd("ATL0")
            self.send_cmd("ATS0")
            self.send_cmd("ATH0")
            self.send_cmd("ATSP0")
            self.connected = True
            Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', f'Status: TERHUBUNG REAL ke {target.getName()} - Data dari motor!'))
            threading.Thread(target=self.obd_loop, daemon=True).start()
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', f'Status: Gagal konek - {e} - Coba pairing ulang / matiin-nyalain Bluetooth'))

    def putus(self, x):
        self.connected = False
        try:
            if self.sock: self.sock.close()
        except: pass
        self.lbl_status.text = 'Status: Diputus - Mode REAL, belum konek'
        self.lbl_rpm.text = '[b]RPM[/b]\n[color=0099FF][b]-[/b][/color]\nmin-1 - Belum Konek'

    def live(self, x):
        if not self.connected:
            self.lbl_status.text = 'Status: Belum konek! Klik KONEK ELM327 dulu'
        else:
            self.lbl_status.text = 'Status: LIVE DATA REAL Jalan - Data dari motor'

    def scan(self, x):
        if not self.connected:
            self.lbl_status.text = 'Status: Belum konek! Konek ELM327 dulu baru SCAN'
            return
        self.lbl_status.text = 'Status: SCAN DTC - Nanya ke ECU...'
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        r = self.send_cmd("03")
        # 03 = mode DTC. Jawaban "43 01 22 ..." -> P0122
        txt = r.strip()
        if "43" in txt:
            Clock.schedule_once(lambda dt: setattr(self.lbl_dtc, 'text', f'DTC REAL: {txt}'))
            Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', f'Status: SCAN Selesai - {txt}'))
        else:
            Clock.schedule_once(lambda dt: setattr(self.lbl_dtc, 'text', 'Tidak ada DTC / ECU tidak jawab (Mode 03)'))
            Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', 'Status: SCAN Selesai - Tidak ada DTC'))

    def hapus(self, x):
        if not self.connected:
            self.lbl_status.text = 'Status: Belum konek!'
            return
        threading.Thread(target=lambda: self.send_cmd("04"), daemon=True).start()
        self.lbl_status.text = 'Status: HAPUS DTC - Perintah 04 dikirim ke ECU'

    def remap(self, x):
        self.lbl_status.text = 'Status: REMAP - Belum aman di versi REAL, jangan dipake dulu'
    def nav_home(self, x):
        self.lbl_status.text = 'Status: HOME'
        self.scroll.scroll_y = 1
    def nav_grafik(self, x):
        self.lbl_status.text = 'Status: GRAFIK - Data REAL di bawah'
        self.scroll.scroll_y = 0.35
    def dummy(self, x):
        try: self.lbl_status.text = f'Status: {x.text} diklik - OK!'
        except: pass

ThakApp().run()
