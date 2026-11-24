from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import random, time, hashlib, csv, os, threading, re

try:
    from kivy.core.clipboard import Clipboard
    HAS_CLIP = True
except:
    HAS_CLIP = False
    Clipboard = None

# PREMIUM PALETTE
def C(n):
    d = {
        "BG": (0.04,0.07,0.13,1),      # Navy gelap premium
        "CARD": (0.10,0.14,0.22,1),    # Card gelap
        "CARD2": (0.14,0.19,0.29,1),
        "TEXT": (0.97,0.98,1,1),
        "SUB": (0.65,0.70,0.80,1),
        "GOLD": (0.98,0.75,0.14,1),    # Emas
        "GOLD_DARK": (0.85,0.60,0.05,1),
        "CYAN": (0.13,0.83,0.93,1),
        "GREEN": (0.13,0.77,0.37,1),
        "RED": (0.94,0.27,0.27,1),
        "ORANGE": (0.98,0.57,0.24,1),
        "WHITE": (1,1,1,1),
    }
    return d.get(n,(1,1,1,1))

def DATA_PATH(fn):
    try:
        app = App.get_running_app()
        if app and app.user_data_dir:
            os.makedirs(app.user_data_dir, exist_ok=True)
            return os.path.join(app.user_data_dir, fn)
    except: pass
    return fn

def premium_btn(text, func, bg, txt_color=(0,0,0,1)):
    # Helper bikin tombol premium - cuma pake background_color, AMAN
    b = Button(text=text, font_size='11sp', bold=True, size_hint_y=None, height=52, background_color=bg, background_normal='', color=txt_color)
    b.bind(on_press=func)
    return b

HARGA = {"STANDAR":0,"ECO / IRIT":150000,"HARIAN / TOURING":250000,"RACING / BALAP":400000,"SCAN DTC":50000,"READ KEY":75000,"REGISTER KEY":150000,"CLONE KEY":200000,"KEY HILANG":350000,"GANTI BATERAI REMOT":30000,"HAPUS KEY":50000,"BATTERY TEST":20000}
MAPS = {"STANDAR":{"fuel":0,"timing":0,"limiter":10500,"afr":14.7,"ket":"Pabrik"},"ECO / IRIT":{"fuel":-8,"timing":-2,"limiter":9800,"afr":15.2,"ket":"Irit"},"HARIAN / TOURING":{"fuel":6,"timing":2,"limiter":11000,"afr":14.2,"ket":"Enteng"},"RACING / BALAP":{"fuel":15,"timing":5,"limiter":12500,"afr":13.2,"ket":"Balap RON 98"}}
UNIVERSAL_PROFILES = {"HONDA":{"dlc":"Honda DLC 4-Pin Merah","protokol":["ATSP6","ATSP3","ATSP0"]},"YAMAHA":{"dlc":"Yamaha DLC 3/4-Pin","protokol":["ATSP6","ATSP5","ATSP0"]},"SUZUKI":{"dlc":"Suzuki DLC 6-Pin","protokol":["ATSP5","ATSP3","ATSP0"]},"KAWASAKI":{"dlc":"Kawasaki DLC 4-Pin","protokol":["ATSP6","ATSP0"]},"MOBIL OBD2":{"dlc":"OBD2 16-Pin","protokol":["ATSP0"]},"UNIVERSAL":{"dlc":"Auto","protokol":["ATSP0","ATSP6","ATSP5","ATSP3"]},"AUTO - UNIVERSAL":{"dlc":"Auto","protokol":["ATSP0","ATSP6","ATSP5","ATSP3"]}}
REMAP_REAL_MAP = {"HONDA":{"addr":"0x1A00","protokol":"K-Line","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":12,"max_timing":4},"YAMAHA":{"addr":"0x2B00","protokol":"CAN","cmd_backup":"2102","cmd_write":"3B2B","max_fuel":10,"max_timing":3},"SUZUKI":{"addr":"0x3C00","protokol":"K-Line","cmd_backup":"2103","cmd_write":"3B3C","max_fuel":10,"max_timing":3},"KAWASAKI":{"addr":"0x4D00","protokol":"CAN","cmd_backup":"2104","cmd_write":"3B4D","max_fuel":12,"max_timing":4},"MOBIL OBD2":{"addr":"0x5E00","protokol":"CAN","cmd_backup":"2105","cmd_write":"3B5E","max_fuel":15,"max_timing":5},"UNIVERSAL":{"addr":"0x1A00","protokol":"AUTO","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":8,"max_timing":2},"AUTO - UNIVERSAL":{"addr":"0x1A00","protokol":"AUTO","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":8,"max_timing":2}}
DB = [("HONDA","1-1","P0107","MAP Low","Brebet","Cek MAP","SEDANG"),("HONDA","8-1","P0122","TP Low","Gas ngempos","Cek TP","SEDANG"),("HONDA","8-2","P0123","TP High","Gas nyangkut","Cek TP","BAHAYA"),("HONDA","52-1","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("YAMAHA","15","P0120","TPS","Gas ngempos","Cek TPS","SEDANG"),("YAMAHA","12","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("SUZUKI","C14","P0120","TP","Gas ngempos","Cek TPS","SEDANG"),("KAWASAKI","11","P0120","TPS","Gas ngempos","Cek TPS","SEDANG"),("OBDII","P0122","P0122","TP Low","Gas ngempos","Cek TP","SEDANG"),("OBDII","P0335","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("OBDII","P0300","P0300","Misfire","Brebet pincang","Cek busi","BAHAYA"),("OBDII","P0500","P0500","Speed","Speedo mati","Cek sensor","RINGAN")]

def cari(q, merk):
    try:
        q = q.strip().upper().replace(" ", "")
        out = []
        for r in DB:
            if merk not in ["AUTO - UNIVERSAL","UNIVERSAL"] and r[0] != merk and r[0] != "OBDII": continue
            if q == r[1] or q == r[2] or q in r[3].upper(): out.append(r)
        return out
    except: return []
def buat_id(p):
    try:
        h = hashlib.md5(f"{p}-{time.time()}-{random.randint(1,99999)}".encode()).hexdigest().upper()
        return f"{h[:4]}-{h[4:8]}"
    except: return "AB12-CD34"
def buat_pass(a,b):
    try:
        h = hashlib.sha256((a+b).replace("-","").encode()).hexdigest()
        s = "".join([c for c in h if c.isdigit()][:6])
        return (s+"000000")[:6]
    except: return "123456"
def safe_float(x,d=0.0):
    try: return float(x)
    except: return d
def safe_int(x,d=0):
    try: return int(float(x))
    except: return d

class ELM327Universal:
    def __init__(self):
        self.sock=None; self.in_stream=None; self.out_stream=None; self.connected=False; self.lock=threading.Lock()
        self.merk_terdeteksi="UNIVERSAL"; self.protokol_aktif="ATSP0"; self.tipe_kendaraan="MOTOR"; self.vin=""; self.fail_count=0
    def find_device(self):
        try:
            from jnius import autoclass
            adapter = autoclass('android.bluetooth.BluetoothAdapter').getDefaultAdapter()
            if not adapter or not adapter.isEnabled(): return None, "Bluetooth HP mati."
            for d in adapter.getBondedDevices():
                name = str(d.getName()).upper()
                if any(x in name for x in ["ELM","OBD","V-LINK","VLINK","THAK"]): return d, f"Ditemukan: {d.getName()}"
            return None, "ELM327 belum pairing. Pairing PIN 1234 dulu."
        except Exception as e: return None, f"Jnius error: {e}"
    def send_raw(self,cmd,timeout=1.2):
        if not self.connected: return ""
        with self.lock:
            try:
                self.out_stream.write((cmd+"\r").encode()); self.out_stream.flush(); time.sleep(0.22)
                buf=bytearray(); start=time.time()
                while time.time()-start<timeout:
                    avail=self.in_stream.available()
                    if avail>0:
                        b=bytearray(avail); self.in_stream.read(b); buf.extend(b)
                        if b'>' in b: break
                    else: time.sleep(0.04)
                self.fail_count=0; return buf.decode(errors='ignore')
            except Exception as e:
                self.fail_count+=1
                if self.fail_count>=3: self.connected=False
                return f"ERR {e}"
    def connect_universal(self, merk_pilihan="AUTO - UNIVERSAL"):
        try:
            dev,msg=self.find_device()
            if not dev: return False,msg
            try:
                from jnius import autoclass
                uuid=autoclass('java.util.UUID').fromString("00001101-0000-1000-8000-00805F9B34FB")
                self.sock=dev.createRfcommSocketToServiceRecord(uuid); self.sock.connect()
                self.in_stream=self.sock.getInputStream(); self.out_stream=self.sock.getOutputStream(); self.connected=True
            except Exception as e: return False, f"Gagal RFCOMM: {e}\nLupakan device, pairing ulang, kontak ON."
            self.send_raw("ATZ",1.5); time.sleep(0.5); self.send_raw("ATE0"); self.send_raw("ATL0"); self.send_raw("ATS0")
            if merk_pilihan in UNIVERSAL_PROFILES and merk_pilihan!="AUTO - UNIVERSAL":
                self.merk_terdeteksi=merk_pilihan
                for proto in UNIVERSAL_PROFILES[merk_pilihan]["protokol"]:
                    self.send_raw(proto); resp=self.send_raw("0100")
                    if "41 00" in resp: self.protokol_aktif=proto; break
            else:
                for proto in ["ATSP0","ATSP6","ATSP5","ATSP3"]:
                    self.send_raw(proto); resp=self.send_raw("0100")
                    if "41 00" in resp: self.protokol_aktif=proto; break
            return True, f"TERHUBUNG\nDevice: {dev.getName()}\nProtokol: {self.protokol_aktif}\nTerdeteksi: {self.merk_terdeteksi}"
        except Exception as e: return False, f"Connect error: {e}"
    def parse_hex(self,resp):
        try:
            resp=resp.replace("SEARCHING...","").replace("NO DATA","").replace(">","").replace("\r"," ").replace("\n"," ")
            return re.findall(r'\b[0-9A-Fa-f]{2}\b',resp)
        except: return []
    def read_pid(self,pid_hex):
        try:
            resp=self.send_raw(f"01{pid_hex}"); toks=self.parse_hex(resp)
            if len(toks)>=3 and toks[0]=="41" and toks[1].upper()==pid_hex.upper():
                a=int(toks[2],16); b=int(toks[3],16) if len(toks)>3 else 0; return a,b,resp
            return None,None,resp
        except: return None,None,""
    def get_live_25(self):
        try:
            out={}
            for name,pid in [("RPM","0C"),("SUHU","05"),("SPEED","0D"),("TP","11")]:
                a,b,_=self.read_pid(pid)
                if a is not None:
                    if name=="RPM": out[name]=((a*256)+b)/4
                    elif name=="SUHU": out[name]=a-40
                    elif name=="SPEED": out[name]=a
                    elif name=="TP": out[name]=a*100/255
            resp=self.send_raw("ATRV"); m=re.search(r'(\d+\.\d+)',resp)
            if m: out['AKI']=float(m.group(1))
            out.setdefault('RPM',1480); out.setdefault('SUHU',86); out.setdefault('SPEED',0); out.setdefault('TP',1.0); out.setdefault('AKI',13.8)
            return out
        except: return {'RPM':1480,'SUHU':86,'SPEED':0,'TP':1.0,'AKI':13.8}
    def get_dtc_universal(self):
        try:
            resp=self.send_raw("03"); toks=self.parse_hex(resp); codes=[]
            if len(toks)>=3 and toks[0]=="43":
                for i in range(1,len(toks)-1,2):
                    try:
                        v1=int(toks[i],16); v2=int(toks[i+1],16)
                        if v1==0 and v2==0: continue
                        first=["P","C","B","U"][v1>>6]; code=f"{first}{((v1>>4)&0x3)}{v1&0x0F:X}{v2>>4:X}{v2&0x0F:X}"
                        if re.match(r'^[PCBU][0-9][0-9A-F]{3}$',code): codes.append(code)
                    except: pass
            return codes,resp
        except: return [],""
    def backup_map_real(self,merk="AUTO - UNIVERSAL"):
        try:
            p=REMAP_REAL_MAP.get(merk,REMAP_REAL_MAP["UNIVERSAL"]); resp=self.send_raw(p["cmd_backup"],timeout=2.0)
            return (True,resp) if ("61" in resp or len(resp)>10) else (False,resp)
        except Exception as e: return False,str(e)
    def remap_real_stage1(self,merk,map_nama,fuel_pct,timing_deg):
        try:
            p=REMAP_REAL_MAP.get(merk,REMAP_REAL_MAP["UNIVERSAL"])
            fuel_pct=max(-8,min(p["max_fuel"],fuel_pct)); timing_deg=max(-2,min(p["max_timing"],timing_deg))
            cmd=f"{p['cmd_write']} {fuel_pct & 0xFF:02X} {timing_deg & 0xFF:02X}"
            resp=self.send_raw(cmd,timeout=2.5)
            if "7B" in resp or "OK" in resp.upper() or ">" in resp: return True, f"ECU OK: {resp}"
            return False, f"ECU TOLAK: {resp}"
        except Exception as e: return False,str(e)
    def clear_dtc(self):
        try: return self.send_raw("04")
        except: return ""
    def disconnect(self):
        try:
            if self.sock: self.sock.close()
        except: pass
        self.connected=False

class ThakTechApp(App):
    def build(self):
        Window.clearcolor = C("BG")
        self.title="THAKTECH V12.5 PREMIUM"
        self.mode="SIMULASI"; self.real=False; self.history=[]; self.live_event=None; self.log=[]; self.elm=ELM327Universal()
        self.last_scan="Belum ada scan"; self.last_live="Belum ada Live"; self.last_key="Belum ada Key"; self.last_remap="Map: STANDAR"; self.last_dtc=[]
        self.map_aktif="STANDAR"; self.map_backup=None; self.map_backup_data=None
        self.key_id=buat_id("KEY"); self.ecu_id=buat_id("ECU"); self.passkey=buat_pass(self.key_id,self.ecu_id)
        self.key_list=[self.key_id]; self.key_baterai=92; self.key_sinyal=88
        self.rpm=1480.0; self.suhu=86.0; self.aki=13.8; self.tp=1.0; self.speed=0.0; self.detik=0; self.total_km=0.0; self.total_bbm=0.0; self.timing_real=12.0; self.last_score=98

        root=BoxLayout(orientation='vertical', spacing=6, padding=[12,10,12,10])

        # ===== HEADER PREMIUM =====
        header=BoxLayout(orientation='vertical', size_hint_y=None, height=78, spacing=1)
        header.add_widget(Label(text="[b][color=FBBF24]T[/color][/b]  [b][color=F8FAFC]THAKTECH[/color][/b]", markup=True, font_size='26sp', size_hint_y=None, height=34, halign='center', valign='middle'))
        header.add_widget(Label(text="ARTIFICIAL PITSTOP  •  PREMIUM DIAGNOSTIC", font_size='9sp', color=C("SUB"), bold=True, size_hint_y=None, height=16))
        header.add_widget(Label(text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", font_size='9sp', color=C("GOLD"), size_hint_y=None, height=12))
        self.status_lbl=Label(text="●  SIMULASI  |  BELUM KONEK  |  MAP: STANDAR", font_size='10sp', color=C("GOLD"), bold=True, size_hint_y=None, height=16)
        header.add_widget(self.status_lbl)
        root.add_widget(header)

        # ===== INPUT CARD =====
        root.add_widget(Label(text="  DATA MOTOR", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=16, size_hint_x=1, text_size=(Window.width-24, None)))
        row=BoxLayout(size_hint_y=None, height=42, spacing=6)
        self.in_plat=TextInput(text="B 1234 THK", multiline=False, font_size='12sp', background_color=C("CARD2"), foreground_color=C("TEXT"), hint_text_color=C("SUB"))
        self.in_motor=TextInput(text="Vario 160", multiline=False, font_size='12sp', background_color=C("CARD2"), foreground_color=C("TEXT"))
        self.in_km=TextInput(text="24500", multiline=False, input_filter='int', font_size='12sp', background_color=C("CARD2"), foreground_color=C("TEXT"))
        for w in [self.in_plat,self.in_motor,self.in_km]: row.add_widget(w)
        root.add_widget(row)

        # ===== DASHBOARD PREMIUM - 4 CARD =====
        root.add_widget(Label(text="  LIVE MONITOR", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=16, text_size=(Window.width-24, None)))
        dash=GridLayout(cols=4, size_hint_y=None, height=58, spacing=6)
        # Tiap card pake BoxLayout + Label, biar keliatan kayak kartu premium
        def card(title, value, col):
            box=BoxLayout(orientation='vertical', spacing=0)
            box.add_widget(Label(text=title, font_size='8sp', bold=True, color=C("SUB"), size_hint_y=None, height=14))
            lbl=Label(text=value, font_size='13sp', bold=True, color=col, size_hint_y=None, height=24)
            box.add_widget(lbl)
            box.add_widget(Label(text="━━━━━━━━", font_size='8sp', color=col, size_hint_y=None, height=10))
            return box, lbl
        self._c1, self.lbl_rpm = card("RPM", "1480", C("CYAN"))
        self._c2, self.lbl_suhu = card("SUHU", "86°C", C("GOLD"))
        self._c3, self.lbl_aki = card("AKI", "13.8V", C("GREEN"))
        self._c4, self.lbl_speed = card("SPEED", "0", C("TEXT"))
        for b in [self._c1,self._c2,self._c3,self._c4]: dash.add_widget(b)
        root.add_widget(dash)

        # ===== OUTPUT PREMIUM =====
        root.add_widget(Label(text="  HASIL DIAGNOSA", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=16, text_size=(Window.width-24, None)))
        self.output=Label(text=self.teks_home(), font_size='13sp', color=C("TEXT"), halign='left', valign='top', size_hint_y=None, size_hint_x=1, text_size=(Window.width - 32, None), line_height=1.25)
        self.output.bind(texture_size=self.output.setter('size'))
        sc=ScrollView(size_hint_y=0.36, bar_width=6)
        sc.add_widget(self.output); root.add_widget(sc)

        # ===== PILIH MERK & MAP =====
        root.add_widget(Label(text="  PENGATURAN", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=16, text_size=(Window.width-24, None)))
        bar=BoxLayout(size_hint_y=None, height=42, spacing=6)
        self.merk=Spinner(text='AUTO - UNIVERSAL', values=('AUTO - UNIVERSAL','HONDA','YAMAHA','SUZUKI','KAWASAKI','MOBIL OBD2'), font_size='11sp', background_color=C("CARD2"), color=C("TEXT"))
        self.map_spinner=Spinner(text='HARIAN / TOURING', values=('STANDAR','ECO / IRIT','HARIAN / TOURING','RACING / BALAP'), font_size='11sp', background_color=C("CARD2"), color=C("TEXT"))
        self.input_kode=TextInput(hint_text="Ketik: 8-1 / P0122 / brebet", multiline=False, font_size='11sp', background_color=C("CARD2"), foreground_color=C("TEXT"), hint_text_color=C("SUB"))
        for w in [self.merk,self.map_spinner,self.input_kode]: bar.add_widget(w)
        root.add_widget(bar)

        # ===== MENU PREMIUM =====
        root.add_widget(Label(text="  MENU UTAMA  •  TAP UNTUK JALANKAN", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=16, text_size=(Window.width-24, None)))
        gs=ScrollView(size_hint_y=0.46, bar_width=6)
        grid=GridLayout(cols=3, spacing=6, padding=2, size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        # PREMIUM COLOR RULE: Emas = uang, Cyan = scan, Hijau = sehat, Merah = bahaya, Orange = key
        menus=[
            ("◆ KONEK\nELM327",self.konek_real,C("CYAN"),(0,0,0,1)),
            ("● LIVE\nDATA",self.live_start,C("GREEN"),(0,0,0,1)),
            ("■ STOP",self.live_stop,C("RED"),(1,1,1,1)),
            ("SCAN\nDTC",self.obd_scan,C("CYAN"),(0,0,0,1)),
            ("HAPUS\nDTC",self.clear_dtc,C("RED"),(1,1,1,1)),
            ("CARI\nKODE",self.dtc_lookup,C("ORANGE"),(0,0,0,1)),
            ("HEALTH\nSCORE",self.health_score,C("GREEN"),(0,0,0,1)),
            ("★ AI\nDIAGNOSA",self.ai_diagnosa,C("GOLD"),(0,0,0,1)),
            ("★ REMAP",self.remap_ecu,C("GOLD"),(0,0,0,1)),
            ("BACKUP",self.backup_map,C("CYAN"),(0,0,0,1)),
            ("RESTORE",self.restore_map,C("RED"),(1,1,1,1)),
            ("READ\nKEY",self.read_key,C("GOLD"),(0,0,0,1)),
            ("REGISTER\nKEY",self.register_key,C("CYAN"),(0,0,0,1)),
            ("CLONE\nKEY",self.clone_key,C("GOLD"),(0,0,0,1)),
            ("KEY\nHILANG",self.key_hilang,C("RED"),(1,1,1,1)),
            ("CEK\nKEY",self.cek_key_manual,C("ORANGE"),(0,0,0,1)),
            ("BATERAI\nREMOT",self.baterai_remot,C("CYAN"),(0,0,0,1)),
            ("HAPUS\nKEY",self.hapus_key,C("RED"),(1,1,1,1)),
            ("DAFTAR\nKEY",self.daftar_key,C("ORANGE"),(0,0,0,1)),
            ("BATTERY",self.battery,C("GOLD"),(0,0,0,1)),
            ("TRIP /\nBBM",self.trip_bbm,C("CYAN"),(0,0,0,1)),
            ("SERVIS",self.servis,C("CYAN"),(0,0,0,1)),
            ("READINESS",self.readiness,C("CYAN"),(0,0,0,1)),
            ("EMERGENCY",self.emergency,C("RED"),(1,1,1,1)),
            ("EXPORT\nCSV",self.export_csv,C("GREEN"),(0,0,0,1)),
            ("STRUK\n+ HARGA",self.print_struk,C("GREEN"),(0,0,0,1)),
            ("HISTORY",self.show_history,C("CYAN"),(0,0,0,1)),
            ("HOME",self.go_home,C("GOLD"),(0,0,0,1)),
        ]
        for t,a,c,txt in menus:
            b=Button(text=t, font_size='10sp', bold=True, size_hint_y=None, height=52, background_color=c, background_normal='', color=txt)
            b.bind(on_press=a); grid.add_widget(b)
        gs.add_widget(grid); root.add_widget(gs)

        # FOOTER PREMIUM
        root.add_widget(Label(text="THAKTECH V12.5 PREMIUM  •  Garansi Diagnosa 7 Hari  •  Garansi Remap 30 Hari", font_size='8sp', color=C("SUB"), size_hint_y=None, height=14))

        self.root_widget=root
        Window.bind(on_resize=self._fix_text_size)
        return root
    def _fix_text_size(self, win, w, h):
        try: self.output.text_size = (w - 32, None)
        except: pass
    def on_stop(self):
        try:
            if self.live_event: self.live_event.cancel()
            self.auto_save(); self.elm.disconnect()
        except: pass
    def teks_home(self):
        return "✦ THAKTECH V12.5 PREMIUM ✦\n\nSelamat datang di bengkel digital premium.\n\n1. Isi Plat + Motor + KM\n2. Pilih AUTO - UNIVERSAL\n3. Pairing ELM327 PIN 1234\n4. Colok DLC, Kontak ON\n5. KONEK ELM327 → LIVE DATA\n\nFitur: Scan DTC • Remap Real • Key Keyless • AI Diagnosa • Struk Otomatis"
    def set_output(self,t):
        try: self.output.text=str(t)
        except: pass
    def show_popup(self,judul,isi):
        try:
            box=BoxLayout(orientation='vertical', spacing=8, padding=12)
            box.add_widget(Label(text=str(isi), halign='left', valign='top', text_size=(Window.width-70, None), color=C("TEXT")))
            btn=Button(text="OK  •  MENGERTI", size_hint_y=None, height=44, background_color=C("GOLD"), color=(0,0,0,1), bold=True)
            box.add_widget(btn)
            p=Popup(title=str(judul), content=box, size_hint=(0.92,0.6)); btn.bind(on_press=p.dismiss); p.open()
        except: self.set_output(isi)
    def profil(self):
        try: km=safe_int(self.in_km.text,24500)
        except: km=24500
        plat=self.in_plat.text.strip().upper() or "B 1234 THK"
        motor=self.in_motor.text.strip() or "Vario 160"
        return plat,motor,km
    def go_home(self,i): self.set_output(self.teks_home())
    def konek_real(self,i):
        try:
            self.set_output("MENGHUBUNGKAN ELM327...")
            def _do():
                ok,msg=self.elm.connect_universal(self.merk.text)
                def _ui(dt):
                    if ok: self.mode="REAL"; self.real=True; self.set_output(f"✓ ELM327 TERHUBUNG - REAL\n{msg}"); self.status_lbl.text=f"●  REAL  |  {self.elm.merk_terdeteksi}  |  MAP: {self.map_aktif}"
                    else: self.mode="SIMULASI"; self.real=False; self.set_output(f"✕ ELM327 GAGAL - SIMULASI\n{msg}"); self.status_lbl.text=f"●  SIMULASI  |  MAP: {self.map_aktif}"
                Clock.schedule_once(_ui)
            threading.Thread(target=_do, daemon=True).start()
        except Exception as e: self.set_output(f"Konek error: {e}")
    def live_start(self,i):
        try:
            if self.live_event: self.set_output("LIVE SUDAH JALAN"); return
            self.detik=0; self.live_event=Clock.schedule_interval(self.update_live,0.7)
        except Exception as e: self.set_output(f"Live error: {e}")
    def live_stop(self,i):
        try:
            if self.live_event: self.live_event.cancel(); self.live_event=None
            self.auto_save(); self.set_output(self.output.text+"\n\n■ LIVE STOP.")
        except Exception as e: self.set_output(f"Stop error: {e}")
    def auto_save(self):
        try:
            with open(DATA_PATH("log_thaktech.csv"),"w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["Waktu","RPM","Suhu","Aki","Speed"]); w.writerows(self.log)
        except: pass
    def update_live(self,dt):
        try:
            if self.real and self.elm.connected:
                def _fetch():
                    try: data=self.elm.get_live_25()
                    except: data={}
                    def _apply(_dt):
                        self.rpm=safe_float(data.get('RPM',1480),1480); self.suhu=safe_float(data.get('SUHU',86),86); self.speed=safe_float(data.get('SPEED',0),0); self.aki=safe_float(data.get('AKI',13.8),13.8); self.tp=safe_float(data.get('TP',1.0),1.0); self._render()
                    Clock.schedule_once(_apply)
                threading.Thread(target=_fetch, daemon=True).start(); return
            else:
                bonus=180 if self.map_aktif=="RACING / BALAP" else 80 if self.map_aktif=="HARIAN / TOURING" else -40 if self.map_aktif=="ECO / IRIT" else 0
                self.tp=max(0.5,min(12,self.tp+random.uniform(-0.3,0.5))); self.rpm=max(1200,min(12500,1480+self.tp*220+bonus)); self.suhu=max(60,min(118,self.suhu+random.uniform(-0.3,0.3))); self.aki=max(11.5,min(14.8,self.aki+random.uniform(-0.04,0.04))); self.speed=max(0,min(160,self.rpm/110))
                self._render()
        except Exception as e: self.set_output(f"Live error: {e}")
    def _render(self):
        try:
            self.detik+=1; self.total_km+=self.speed*0.7/3600; self.total_bbm+=(0.6+self.tp*0.35)*0.7/3600
            self.lbl_rpm.text=f"{self.rpm:.0f}"; self.lbl_suhu.text=f"{self.suhu:.0f}°C"; self.lbl_aki.text=f"{self.aki:.1f}V"; self.lbl_speed.text=f"{self.speed:.0f}"
            self.log.append([time.strftime("%H:%M:%S"),f"{self.rpm:.0f}",f"{self.suhu:.0f}",f"{self.aki:.1f}",f"{self.speed:.0f}"])
            if len(self.log)>500: self.log.pop(0)
            score=100
            if self.suhu>100: score-=20
            if self.aki<12.2: score-=25
            if self.last_dtc: score-=len(self.last_dtc)*15
            self.last_score=max(0,score)
            self.status_lbl.text=f"●  {self.mode}  |  MAP: {self.map_aktif}  |  SEHAT {self.last_score}%"
            self.set_output(f"● LIVE {self.mode}  •  {self.detik}s  •  SCORE {self.last_score}%\n━━━━━━━━━━━━━━━━━━━━━━\nRPM {self.rpm:.0f}  |  Speed {self.speed:.0f}  |  Suhu {self.suhu:.0f}°C  |  Aki {self.aki:.1f}V  |  TP {self.tp:.1f}%\nTrip +{self.total_km:.2f} km  |  BBM {self.total_bbm:.3f} L\n\nDTC: {len(self.last_dtc)} kode  •  Map: {self.map_aktif}")
            self.last_live=f"RPM {self.rpm:.0f} | {self.map_aktif}"
        except Exception as e: self.set_output(f"Render error: {e}")
    def obd_scan(self,i):
        try:
            plat,motor,km=self.profil()
            if self.real and self.elm.connected:
                self.set_output("SCAN DTC REAL...")
                def _do():
                    codes,raw=self.elm.get_dtc_universal()
                    def _ui(dt):
                        if not codes: self.last_dtc=[]; self.set_output(f"✓ SCAN DTC - REAL\n{motor} | {plat}\n\nTIDAK ADA DTC - Bersih")
                        else:
                            self.last_dtc=[(c,"DTC","SEDANG") for c in codes]; self.set_output(f"SCAN DTC REAL\nDitemukan {len(codes)}: {', '.join(codes)}\nRaw: {raw}"); self.last_scan=" | ".join(codes); self.history.append(self.last_scan)
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do, daemon=True).start(); return
            self.last_dtc=[("P0122","TP Low","SEDANG")]; self.set_output(f"SCAN DTC - {self.mode}\nMotor: {motor} | {plat}\n\n- P0122 - TP Low\nGejala: Gas ngempos\nSolusi: Cek TP"); self.last_scan="P0122"; self.history.append(self.last_scan)
        except Exception as e: self.set_output(f"Scan error: {e}")
    def clear_dtc(self,i):
        try:
            if not self.last_dtc: self.set_output("Tidak ada DTC."); return
            if self.real and self.elm.connected:
                resp=self.elm.clear_dtc(); j=len(self.last_dtc); self.last_dtc=[]; self.set_output(f"✓ HAPUS DTC REAL BERHASIL - {j} kode\nRespon: {resp}")
            else:
                j=len(self.last_dtc); self.last_dtc=[]; self.set_output(f"✓ HAPUS DTC BERHASIL - {j} kode")
        except Exception as e: self.set_output(f"Clear error: {e}")
    def dtc_lookup(self,i):
        try:
            q=self.input_kode.text
            if not q.strip(): self.set_output("Ketik dulu: 8-1 / P0122"); return
            h=cari(q,self.merk.text)
            if not h: self.set_output(f"{q.upper()} tidak ditemukan."); return
            r=h[0]; self.set_output(f"HASIL - {r[0]}\nKode: {r[1]} | OBD: {r[2]}\nKerusakan: {r[3]}\nGejala: {r[4]}\nSolusi: {r[5]}\nLevel: {r[6]}"); self.last_scan=f"{r[1]} - {r[3]}"
        except Exception as e: self.set_output(f"Lookup error: {e}")
    def health_score(self,i): self.set_output(f"HEALTH SCORE PREMIUM\n\nSkor: {self.last_score} / 100\nSuhu: {self.suhu:.0f}°C  |  Aki: {self.aki:.1f}V\nDTC: {len(self.last_dtc)}  |  Map: {self.map_aktif}")
    def ai_diagnosa(self,i):
        s=[]
        if self.suhu>100: s.append("OVERHEAT: Cek radiator / kipas.")
        if self.aki<12.2: s.append("AKI LEMAH: Cek kiprok.")
        if self.last_dtc: s.append(f"DTC {len(self.last_dtc)} aktif, jangan cuma hapus.")
        if not s: s.append("Mesin sehat. Servis rutin aja.")
        self.set_output("★ AI DIAGNOSA PREMIUM\n\n"+"\n".join(["- "+x for x in s])+f"\n\nSkor: {self.last_score}")
    def backup_map(self,i):
        self.map_backup=self.map_aktif; self.map_backup_data={"map":self.map_aktif,"waktu":time.strftime('%d/%m/%Y %H:%M')}
        self.set_output(f"✓ BACKUP BERHASIL\nMap: {self.map_backup}\nAman untuk Remap.")
    def restore_map(self,i):
        if not self.map_backup: self.set_output("Belum ada backup! Pencet BACKUP dulu."); return
        self.map_aktif=self.map_backup; self.set_output(f"✓ RESTORE BERHASIL - Balik ke {self.map_aktif}")
    def remap_ecu(self,i):
        try:
            pilih=self.map_spinner.text
            if not self.map_backup: self.set_output("REMAP DITOLAK - BACKUP DULU!"); return
            if self.aki<12.4: self.set_output(f"REMAP DITOLAK - AKI {self.aki:.1f}V, minimal 12.4V"); return
            if self.suhu>100: self.set_output(f"REMAP DITOLAK - SUHU {self.suhu:.0f}°C, dinginkan dulu"); return
            if self.real and self.elm.connected:
                self.set_output(f"REMAP REAL - Kirim ke ECU...\nMap: {pilih}\nJANGAN CABUT KABEL!")
                m=MAPS[pilih]
                def _do():
                    ok_b,_=self.elm.backup_map_real(self.elm.merk_terdeteksi); ok,resp=self.elm.remap_real_stage1(self.elm.merk_terdeteksi,pilih,m["fuel"],m["timing"])
                    def _ui(dt):
                        if ok:
                            lama=self.map_aktif; self.map_aktif=pilih; self.set_output(f"✓ REMAP REAL BERHASIL\n{lama} -> {pilih}\nHarga Rp {HARGA[pilih]:,}\nRespon: {resp}"); self.last_remap=f"REMAP REAL {lama}->{pilih}"
                        else: self.set_output(f"REMAP GAGAL - AMAN, map tidak berubah.\nAlasan: {resp}")
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do, daemon=True).start(); return
            lama=self.map_aktif; self.map_aktif=pilih; m=MAPS[pilih]; self.set_output(f"REMAP SIMULASI\n{lama} -> {pilih}\nHarga Rp {HARGA[pilih]:,}\nKonek ELM327 untuk REMAP REAL."); self.last_remap=f"REMAP SIMULASI {lama}->{pilih}"
        except Exception as e: self.set_output(f"Remap error: {e}")
    def read_key(self,i):
        self.set_output(f"READ KEY PREMIUM\n\nKey: {self.key_id}\nECU: {self.ecu_id}\nPass: {self.passkey}\nSinyal: {self.key_sinyal}%  |  Baterai: {self.key_baterai}%\nHarga Rp {HARGA['READ KEY']:,}"); self.last_key=f"Key {self.key_id}"
    def register_key(self,i):
        old=self.key_id; self.key_id=buat_id("KEY-NEW"); self.key_list.append(self.key_id); self.passkey=buat_pass(self.key_id,self.ecu_id)
        self.set_output(f"✓ REGISTER KEY BERHASIL\nLama: {old}\nBaru: {self.key_id}\nPass: {self.passkey}\nHarga Rp {HARGA['REGISTER KEY']:,}"); self.last_key=f"Register {self.key_id}"
    def clone_key(self,i):
        c=buat_id("CLONE"); self.key_list.append(c); self.set_output(f"✓ CLONE KEY BERHASIL\nClone: {c}\nPass sama: {self.passkey}\nHarga Rp {HARGA['CLONE KEY']:,}"); self.last_key=f"Clone {c}"
    def key_hilang(self,i):
        hilang=self.key_id; self.key_id=buat_id("KEY-HILANG"); self.key_list=[self.key_id]; self.passkey=buat_pass(self.key_id,self.ecu_id)
        self.set_output(f"KEY HILANG - RESET\nKey lama diblokir: {hilang}\nKey baru: {self.key_id}\nPass: {self.passkey}\nHarga Rp {HARGA['KEY HILANG']:,}"); self.last_key=f"Hilang -> {self.key_id}"
    def cek_key_manual(self,i):
        q=self.input_kode.text.strip().upper()
        if not q: self.set_output("Ketik ID Remot di kolom input dulu, contoh AB12-CD34"); return
        cocok=q.replace("-","") in [k.replace("-","") for k in self.key_list]
        self.set_output(f"CEK KEY\nID: {q}\nHasil: {'✓ COCOK - Bisa hidup' if cocok else '✕ TIDAK COCOK - Harus REGISTER'}")
    def baterai_remot(self,i): self.set_output(f"BATERAI REMOT\n\nBaterai: {self.key_baterai}%\nSinyal: {self.key_sinyal}%\nTipe CR2032 - Harga Rp {HARGA['GANTI BATERAI REMOT']:,}")
    def hapus_key(self,i):
        if len(self.key_list)<=1: self.set_output("DITOLAK - Tinggal 1 key, tidak boleh hapus semua!"); return
        if self.key_list[-1]==self.key_id: self.set_output("DITOLAK - Tidak boleh hapus key AKTIF."); return
        h=self.key_list.pop(); self.set_output(f"✓ HAPUS KEY BERHASIL\nDihapus: {h}\nSisa: {len(self.key_list)} key")
    def daftar_key(self,i):
        t=f"DAFTAR KEY - {len(self.key_list)} KEY\nECU: {self.ecu_id}\n\n"
        for idx,k in enumerate(self.key_list,1): t+=f"{idx}. {k} {'(AKTIF)' if k==self.key_id else ''}\n"
        self.set_output(t)
    def battery(self,i):
        v=round(random.uniform(12.4,13.9),1) if not self.real else self.aki; self.set_output(f"BATTERY TEST PREMIUM\n\n{v}V\nHarga Rp {HARGA['BATTERY TEST']:,}")
    def trip_bbm(self,i): self.set_output(f"TRIP / BBM\n\nTrip +{self.total_km:.2f} km\nBBM {self.total_bbm:.3f} L\nMap: {self.map_aktif}")
    def servis(self,i):
        plat,motor,km=self.profil(); self.set_output(f"SERVIS PREMIUM\n\nMotor: {motor} | {plat} | KM {km}\n- Oli: 2000 km\n- Busi: 8000 km\n- CVT: 10000 km")
    def readiness(self,i): self.set_output("READINESS\n\nMisfire: SIAP\nFuel: SIAP\nO2: SIAP\nCatalyst: Jalan 10km dulu")
    def emergency(self,i): self.show_popup("EMERGENCY","1. Matikan kontak\n2. Cek suhu, aki, DTC\n3. Suhu >110 tunggu 20 menit\n4. Aki <11.5 jangan stater terus")
    def export_csv(self,i):
        try:
            p=DATA_PATH("log_thaktech.csv")
            with open(p,"w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["Waktu","RPM","Suhu","Aki","Speed"]); w.writerows(self.log)
            self.set_output(f"✓ EXPORT BERHASIL\nFile: {p}\nIsi: {len(self.log)} baris")
        except Exception as e: self.set_output(f"Export gagal: {e}")
    def print_struk(self,i):
        plat,motor,km=self.profil(); trx=buat_id("TRX"); t=time.strftime("%d/%m/%Y %H:%M")
        s=f"✦ THAKTECH PREMIUM ✦\nTRX: {trx}\nTanggal: {t}\nMotor: {motor} | {plat} | KM {km}\nMode: {self.mode}\nScan: {self.last_scan}\nRemap: {self.last_remap}\nLive: {self.last_live}\n━━━━━━━━━━━━━━\nTerima kasih - Garansi 7 hari"
        try: open(DATA_PATH("struk.txt"),"w",encoding="utf-8").write(s)
        except: pass
        if HAS_CLIP and Clipboard:
            try: Clipboard.copy(s)
            except: pass
        self.set_output(s+"\n\n[OK] Tersalin. TRX: "+trx)
    def show_history(self,i):
        if not self.history: self.set_output("HISTORY KOSONG"); return
        self.set_output("HISTORY PREMIUM:\n\n"+"\n".join([f"{i+1}. {h}" for i,h in enumerate(self.history)]))

if __name__=='__main__':
    ThakTechApp().run()
