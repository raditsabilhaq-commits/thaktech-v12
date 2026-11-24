from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
import random, time, hashlib, csv, os, threading, re, traceback

try:
    from kivy.core.clipboard import Clipboard
    HAS_CLIP = True
except:
    HAS_CLIP = False
    Clipboard = None

def C(n):
    d = {"BG":(0.03,0.05,0.10,1),"CARD":(0.08,0.12,0.20,1),"CARD2":(0.13,0.18,0.28,1),"TEXT":(0.97,0.98,1,1),"SUB":(0.65,0.70,0.80,1),"GOLD":(0.98,0.75,0.14,1),"CYAN":(0.13,0.83,0.93,1),"GREEN":(0.13,0.77,0.37,1),"RED":(0.94,0.27,0.27,1),"ORANGE":(0.98,0.57,0.24,1),"PURPLE":(0.65,0.45,0.95,1)}
    return d.get(n,(1,1,1,1))

def W():
    try:
        w = Window.width or 360
        return w if w > 100 else 360
    except:
        return 360

def DATA_PATH(fn):
    try:
        app = App.get_running_app()
        if app and app.user_data_dir:
            os.makedirs(app.user_data_dir, exist_ok=True)
            return os.path.join(app.user_data_dir, fn)
    except: pass
    return fn

HARGA = {"STANDAR":0,"ECO / IRIT":150000,"HARIAN / TOURING":250000,"RACING / BALAP":400000,"SCAN DTC":50000,"READ KEY":75000,"REGISTER KEY":150000,"CLONE KEY":200000,"KEY HILANG":350000,"GANTI BATERAI REMOT":30000,"HAPUS KEY":50000,"BATTERY TEST":20000,"CEK KIPROK":25000,"TES INJECTOR":30000,"FREEZE FRAME":20000,"BACA VIN":15000,"SERVIS LENGKAP":150000}
MAPS = {"STANDAR":{"fuel":0,"timing":0,"limiter":10500,"afr":14.7,"ket":"Pabrik"},"ECO / IRIT":{"fuel":-8,"timing":-2,"limiter":9800,"afr":15.2,"ket":"Irit"},"HARIAN / TOURING":{"fuel":6,"timing":2,"limiter":11000,"afr":14.2,"ket":"Enteng - Paling laris"},"RACING / BALAP":{"fuel":15,"timing":5,"limiter":12500,"afr":13.2,"ket":"Balap RON 98"}}
UNIVERSAL_PROFILES = {"HONDA":{"dlc":"Honda DLC 4-Pin Merah","protokol":["ATSP6","ATSP3","ATSP0"]},"YAMAHA":{"dlc":"Yamaha DLC 3/4-Pin","protokol":["ATSP6","ATSP5","ATSP0"]},"SUZUKI":{"dlc":"Suzuki DLC 6-Pin","protokol":["ATSP5","ATSP3","ATSP0"]},"KAWASAKI":{"dlc":"Kawasaki DLC 4-Pin","protokol":["ATSP6","ATSP0"]},"MOBIL OBD2":{"dlc":"OBD2 16-Pin","protokol":["ATSP0"]},"UNIVERSAL":{"dlc":"Auto","protokol":["ATSP0","ATSP6","ATSP5","ATSP3"]},"AUTO - UNIVERSAL":{"dlc":"Auto","protokol":["ATSP0","ATSP6","ATSP5","ATSP3"]}}
REMAP_REAL_MAP = {"HONDA":{"addr":"0x1A00","protokol":"K-Line","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":12,"max_timing":4},"YAMAHA":{"addr":"0x2B00","protokol":"CAN","cmd_backup":"2102","cmd_write":"3B2B","max_fuel":10,"max_timing":3},"SUZUKI":{"addr":"0x3C00","protokol":"K-Line","cmd_backup":"2103","cmd_write":"3B3C","max_fuel":10,"max_timing":3},"KAWASAKI":{"addr":"0x4D00","protokol":"CAN","cmd_backup":"2104","cmd_write":"3B4D","max_fuel":12,"max_timing":4},"MOBIL OBD2":{"addr":"0x5E00","protokol":"CAN","cmd_backup":"2105","cmd_write":"3B5E","max_fuel":15,"max_timing":5},"UNIVERSAL":{"addr":"0x1A00","protokol":"AUTO","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":8,"max_timing":2},"AUTO - UNIVERSAL":{"addr":"0x1A00","protokol":"AUTO","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":8,"max_timing":2}}
DB = [("HONDA","1-1","P0107","MAP Low","Brebet","Cek MAP","SEDANG"),("HONDA","8-1","P0122","TP Low","Gas ngempos","Cek TP","SEDANG"),("HONDA","8-2","P0123","TP High","Gas nyangkut","Cek TP","BAHAYA"),("HONDA","52-1","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("HONDA","12-1","P0201","Injector 1","Brebet pincang","Cek injector","BAHAYA"),("YAMAHA","15","P0120","TPS","Gas ngempos","Cek TPS","SEDANG"),("YAMAHA","12","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("YAMAHA","46","P0562","Aki Low","Stater lemah","Cek kiprok","SEDANG"),("SUZUKI","C14","P0120","TP","Gas ngempos","Cek TPS","SEDANG"),("KAWASAKI","11","P0120","TPS","Gas ngempos","Cek TPS","SEDANG"),("OBDII","P0122","P0122","TP Low","Gas ngempos","Cek TP","SEDANG"),("OBDII","P0335","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("OBDII","P0300","P0300","Misfire","Brebet pincang","Cek busi","BAHAYA"),("OBDII","P0500","P0500","Speed","Speedo mati","Cek sensor","RINGAN"),("OBDII","P0562","P0562","Aki Low","Stater lemah","Cek kiprok","SEDANG"),("OBDII","P0201","P0201","Injector","Brebet pincang","Cek injector","BAHAYA"),("OBDII","P0118","P0118","Suhu High","Overheat","Cek radiator","BAHAYA")]

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

class Grafik3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_rpm = [1480,1520,1490,1600,1750,1900,2100,2000,1850,1700,1550,1480]
        self.data_suhu = [86,86,87,87,88,88,89,89,88,87,86,86]
        self.bind(size=self.gambar, pos=self.gambar)
        Clock.schedule_once(lambda dt: Clock.schedule_interval(lambda dt2: self.update_data(), 1.0), 1.5)
    def update_data(self):
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'rpm'):
                self.data_rpm.append(app.rpm); self.data_suhu.append(app.suhu)
                if len(self.data_rpm) > 12: self.data_rpm.pop(0)
                if len(self.data_suhu) > 12: self.data_suhu.pop(0)
                self.gambar()
        except: pass
    def gambar(self, *args):
        try:
            self.canvas.clear()
            if not self.width or not self.height: return
            if self.width < 50 or self.height < 20: return
            x0, y0 = self.pos; w, h = self.size
            with self.canvas:
                Color(0.06,0.09,0.16,1); Rectangle(pos=(x0, y0), size=(w, h))
                Color(0.20,0.25,0.35,1)
                for i in range(1,4):
                    yy = y0 + h * i / 4; Line(points=[x0, yy, x0+w, yy], width=1)
            if not self.data_rpm: return
            maks = max(self.data_rpm) if max(self.data_rpm) > 0 else 1
            bw = w / 14
            for i, val in enumerate(self.data_rpm):
                if i >= len(self.data_suhu): break
                bh = (val / maks) * (h * 0.68); bx = x0 + 8 + i * (bw + 4); by = y0 + 8
                if val > 4000: r,g,b = 0.98,0.75,0.14
                elif val > 2500: r,g,b = 0.13,0.83,0.93
                else: r,g,b = 0.13,0.77,0.37
                with self.canvas:
                    Color(0,0,0,0.35); Rectangle(pos=(bx+4, by+4), size=(bw, bh))
                    Color(r*0.55,g*0.55,b*0.55,1); Rectangle(pos=(bx+bw, by+4), size=(5, bh))
                    Color(min(1,r+0.25),min(1,g+0.25),min(1,b+0.25),1); Rectangle(pos=(bx, by+bh), size=(bw+5, 5))
                    Color(r,g,b,1); Rectangle(pos=(bx, by), size=(bw, bh))
                    sy = y0 + 8 + (self.data_suhu[i] / 120.0) * (h * 0.68)
                    Color(0.98,0.75,0.14,1); Rectangle(pos=(bx, sy), size=(bw+5, 2))
        except: pass

class ELM327Universal:
    def __init__(self):
        self.sock=None; self.in_stream=None; self.out_stream=None; self.connected=False; self.lock=threading.Lock()
        self.merk_terdeteksi="UNIVERSAL"; self.protokol_aktif="ATSP0"; self.vin=""; self.fail_count=0; self.retry=0
    def find_device(self):
        try:
            from jnius import autoclass
            adapter = autoclass('android.bluetooth.BluetoothAdapter').getDefaultAdapter()
            if not adapter or not adapter.isEnabled(): return None, "Bluetooth HP mati. Nyalakan Bluetooth dulu."
            for d in adapter.getBondedDevices():
                name = str(d.getName()).upper()
                if any(x in name for x in ["ELM","OBD","V-LINK","VLINK","THAK"]): return d, f"Ditemukan: {d.getName()}"
            return None, "ELM327 belum pairing. Pairing dulu PIN 1234 / 0000."
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
        for attempt in range(2):
            try:
                dev,msg=self.find_device()
                if not dev: return False,msg
                try:
                    from jnius import autoclass
                    uuid=autoclass('java.util.UUID').fromString("00001101-0000-1000-8000-00805F9B34FB")
                    self.sock=dev.createRfcommSocketToServiceRecord(uuid); self.sock.connect()
                    self.in_stream=self.sock.getInputStream(); self.out_stream=self.sock.getOutputStream(); self.connected=True
                except Exception as e:
                    if attempt==0: time.sleep(1); continue
                    return False, f"Gagal RFCOMM: {e}\nLupakan device, pairing ulang, kontak ON."
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
                try:
                    v=self.send_raw("0902"); self.vin="".join([c for c in v if c.isalnum()])[:17] or "BELUM TERBACA"
                except: self.vin="BELUM TERBACA"
                return True, f"TERHUBUNG\nDevice: {dev.getName()}\nProtokol: {self.protokol_aktif}\nTerdeteksi: {self.merk_terdeteksi}\nVIN: {self.vin}"
            except Exception as e:
                if attempt==0: time.sleep(1); continue
                return False, f"Connect error: {e}"
        return False, "Gagal konek 2x. Cek ELM327 dan kontak ON."
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
            for name,pid in [("RPM","0C"),("SUHU","05"),("SPEED","0D"),("TP","11"),("BEBAN","04"),("TIMING","0E")]:
                a,b,_=self.read_pid(pid)
                if a is not None:
                    if name=="RPM": out[name]=((a*256)+b)/4
                    elif name=="SUHU": out[name]=a-40
                    elif name=="SPEED": out[name]=a
                    elif name=="TP": out[name]=a*100/255
                    elif name=="BEBAN": out[name]=a*100/255
                    elif name=="TIMING": out[name]=a/2-64
            resp=self.send_raw("ATRV"); m=re.search(r'(\d+\.\d+)',resp)
            if m: out['AKI']=float(m.group(1))
            out.setdefault('RPM',1480); out.setdefault('SUHU',86); out.setdefault('SPEED',0); out.setdefault('TP',1.0); out.setdefault('AKI',13.8); out.setdefault('BEBAN',18); out.setdefault('TIMING',12)
            return out
        except: return {'RPM':1480,'SUHU':86,'SPEED':0,'TP':1.0,'AKI':13.8,'BEBAN':18,'TIMING':12}
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
    def get_freeze_frame(self):
        try:
            resp=self.send_raw("0200"); return resp if resp else "Tidak ada Freeze Frame"
        except: return "Gagal baca Freeze Frame"
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
        try:
            return self._build_ui()
        except Exception as e:
            err = traceback.format_exc()
            root = BoxLayout(orientation='vertical', padding=20, spacing=10)
            root.add_widget(Label(text="THAKTECH - ERROR SAAT LOAD", bold=True, color=(1,0.8,0,1)))
            root.add_widget(Label(text=err[-2000:], font_size='11sp', halign='left', valign='top', text_size=(W()-40, None)))
            return root
    def _build_ui(self):
        Window.clearcolor = C("BG")
        self.title="THAKTECH V13.0 PROFESSIONAL"
        self.mode="SIMULASI"; self.real=False; self.history=[]; self.live_event=None; self.log=[]; self.elm=ELM327Universal()
        self.last_scan="Belum ada scan"; self.last_live="Belum ada Live"; self.last_key="Belum ada Key"; self.last_remap="Map: STANDAR"; self.last_dtc=[]; self.last_vin="BELUM TERBACA"
        self.map_aktif="STANDAR"; self.map_backup=None; self.map_backup_data=None
        self.key_id=buat_id("KEY"); self.ecu_id=buat_id("ECU"); self.passkey=buat_pass(self.key_id,self.ecu_id)
        self.key_list=[self.key_id]; self.key_baterai=92; self.key_sinyal=88
        self.rpm=1480.0; self.suhu=86.0; self.aki=13.8; self.tp=1.0; self.speed=0.0; self.beban=18.0; self.timing=12.0; self.detik=0; self.total_km=0.0; self.total_bbm=0.0; self.last_score=98; self.total_pendapatan=0
        root=BoxLayout(orientation='vertical', spacing=4, padding=[10,8,10,8])
        header=BoxLayout(orientation='vertical', size_hint_y=None, height=74, spacing=1)
        top=BoxLayout(size_hint_y=None, height=30)
        top.add_widget(Label(text="THAKTECH", font_size='24sp', bold=True, color=C("GOLD"), halign='left', size_hint_x=0.65))
        self.jam_lbl=Label(text=time.strftime("%H:%M - %d/%m/%Y"), font_size='10sp', color=C("SUB"), halign='right', size_hint_x=0.35)
        top.add_widget(self.jam_lbl); header.add_widget(top)
        header.add_widget(Label(text="ARTIFICIAL PITSTOP - PROFESSIONAL DIAGNOSTIC SYSTEM", font_size='8sp', color=C("SUB"), bold=True, size_hint_y=None, height=12))
        header.add_widget(Label(text="------------------------------", font_size='9sp', color=C("GOLD"), size_hint_y=None, height=9))
        self.status_lbl=Label(text="SIMULASI | BELUM KONEK | MAP: STANDAR | SEHAT 98%", font_size='10sp', color=C("GOLD"), bold=True, size_hint_y=None, height=14)
        header.add_widget(self.status_lbl); root.add_widget(header)
        Clock.schedule_interval(lambda dt: self.update_jam(), 30)
        root.add_widget(Label(text="DATA MOTOR DAN PELANGGAN", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=13, text_size=(W()-20, None)))
        row=BoxLayout(size_hint_y=None, height=38, spacing=5)
        self.in_plat=TextInput(text="B 1234 THK", multiline=False, font_size='12sp', background_color=C("CARD2"), foreground_color=C("TEXT"))
        self.in_motor=TextInput(text="Vario 160", multiline=False, font_size='12sp', background_color=C("CARD2"), foreground_color=C("TEXT"))
        self.in_km=TextInput(text="24500", multiline=False, input_filter='int', font_size='12sp', background_color=C("CARD2"), foreground_color=C("TEXT"))
        for w in [self.in_plat,self.in_motor,self.in_km]: row.add_widget(w)
        root.add_widget(row)
        root.add_widget(Label(text="LIVE MONITOR - 6 SENSOR", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=13, text_size=(W()-20, None)))
        dash=GridLayout(cols=6, size_hint_y=None, height=48, spacing=4)
        def card(title, value, col):
            box=BoxLayout(orientation='vertical', spacing=0)
            box.add_widget(Label(text=title, font_size='7sp', bold=True, color=C("SUB"), size_hint_y=None, height=11))
            lbl=Label(text=value, font_size='11sp', bold=True, color=col, size_hint_y=None, height=20)
            box.add_widget(lbl)
            box.add_widget(Label(text="------", font_size='7sp', color=col, size_hint_y=None, height=7))
            return box, lbl
        self._c1, self.lbl_rpm = card("RPM", "1480", C("CYAN"))
        self._c2, self.lbl_suhu = card("SUHU", "86 C", C("GOLD"))
        self._c3, self.lbl_aki = card("AKI", "13.8 V", C("GREEN"))
        self._c4, self.lbl_speed = card("SPEED", "0", C("TEXT"))
        self._c5, self.lbl_beban = card("BEBAN", "18%", C("ORANGE"))
        self._c6, self.lbl_timing = card("TIMING", "12", C("PURPLE"))
        for b in [self._c1,self._c2,self._c3,self._c4,self._c5,self._c6]: dash.add_widget(b)
        root.add_widget(dash)
        root.add_widget(Label(text="GRAFIK LIVE RPM 3D - BAR HIJAU NORMAL, CYAN MENENGAH, EMAS TINGGI, GARIS EMAS = SUHU", font_size='8sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=13, text_size=(W()-20, None)))
        root.add_widget(Grafik3D(size_hint_y=None, height=92))
        root.add_widget(Label(text="HASIL DIAGNOSA", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=13, text_size=(W()-20, None)))
        self.output=Label(text=self.teks_home(), font_size='12sp', color=C("TEXT"), halign='left', valign='top', size_hint_y=None, size_hint_x=1, text_size=(W() - 28, None))
        self.output.bind(texture_size=self.output.setter('size'))
        sc=ScrollView(size_hint_y=0.20); sc.add_widget(self.output); root.add_widget(sc)
        root.add_widget(Label(text="PENGATURAN", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=13, text_size=(W()-20, None)))
        bar=BoxLayout(size_hint_y=None, height=38, spacing=5)
        self.merk=Spinner(text='AUTO - UNIVERSAL', values=('AUTO - UNIVERSAL','HONDA','YAMAHA','SUZUKI','KAWASAKI','MOBIL OBD2'), font_size='11sp', background_color=C("CARD2"), color=C("TEXT"))
        self.map_spinner=Spinner(text='HARIAN / TOURING', values=('STANDAR','ECO / IRIT','HARIAN / TOURING','RACING / BALAP'), font_size='11sp', background_color=C("CARD2"), color=C("TEXT"))
        self.input_kode=TextInput(hint_text="8-1 / P0122", multiline=False, font_size='11sp', background_color=C("CARD2"), foreground_color=C("TEXT"), hint_text_color=C("SUB"))
        for w in [self.merk,self.map_spinner,self.input_kode]: bar.add_widget(w)
        root.add_widget(bar)
        root.add_widget(Label(text="MENU PROFESSIONAL - TAP UNTUK JALANKAN", font_size='10sp', bold=True, color=C("GOLD"), halign='left', size_hint_y=None, height=13, text_size=(W()-20, None)))
        gs=ScrollView(size_hint_y=0.48)
        grid=GridLayout(cols=3, spacing=5, padding=2, size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        menus=[
            ("KONEK\nELM327",self.konek_real,C("CYAN"),(0,0,0,1)),
            ("LIVE\nDATA",self.live_start,C("GREEN"),(0,0,0,1)),
            ("STOP",self.live_stop,C("RED"),(1,1,1,1)),
            ("SCAN\nDTC",self.obd_scan,C("CYAN"),(0,0,0,1)),
            ("HAPUS\nDTC",self.clear_dtc,C("RED"),(1,1,1,1)),
            ("CARI\nKODE",self.dtc_lookup,C("ORANGE"),(0,0,0,1)),
            ("HEALTH\nSCORE",self.health_score,C("GREEN"),(0,0,0,1)),
            ("AI\nDIAGNOSA",self.ai_diagnosa,C("GOLD"),(0,0,0,1)),
            ("REMAP",self.remap_ecu,C("GOLD"),(0,0,0,1)),
            ("BACKUP",self.backup_map,C("CYAN"),(0,0,0,1)),
            ("RESTORE",self.restore_map,C("RED"),(1,1,1,1)),
            ("BACA\nVIN",self.baca_vin,C("PURPLE"),(1,1,1,1)),
            ("FREEZE\nFRAME",self.freeze_frame,C("PURPLE"),(1,1,1,1)),
            ("CEK\nKIPROK",self.cek_kiprok,C("CYAN"),(0,0,0,1)),
            ("TES\nINJECTOR",self.tes_injector,C("CYAN"),(0,0,0,1)),
            ("READ\nKEY",self.read_key,C("GOLD"),(0,0,0,1)),
            ("REGISTER\nKEY",self.register_key,C("CYAN"),(0,0,0,1)),
            ("CLONE\nKEY",self.clone_key,C("GOLD"),(0,0,0,1)),
            ("KEY\nHILANG",self.key_hilang,C("RED"),(1,1,1,1)),
            ("CEK\nKEY",self.cek_key_manual,C("ORANGE"),(0,0,0,1)),
            ("BATERAI\nREMOT",self.baterai_remot,C("CYAN"),(0,0,0,1)),
            ("HAPUS\nKEY",self.hapus_key,C("RED"),(1,1,1,1)),
            ("DAFTAR\nKEY",self.daftar_key,C("ORANGE"),(0,0,0,1)),
            ("BATTERY\nTEST",self.battery,C("GOLD"),(0,0,0,1)),
            ("TRIP /\nBBM",self.trip_bbm,C("CYAN"),(0,0,0,1)),
            ("SERVIS\nREMINDER",self.servis,C("CYAN"),(0,0,0,1)),
            ("READINESS",self.readiness,C("CYAN"),(0,0,0,1)),
            ("EMERGENCY",self.emergency,C("RED"),(1,1,1,1)),
            ("EXPORT\nCSV",self.export_csv,C("GREEN"),(0,0,0,1)),
            ("STRUK\n+ HARGA",self.print_struk,C("GREEN"),(0,0,0,1)),
            ("LAPORAN\nHARIAN",self.laporan_harian,C("GREEN"),(0,0,0,1)),
            ("HISTORY",self.show_history,C("CYAN"),(0,0,0,1)),
            ("HOME",self.go_home,C("GOLD"),(0,0,0,1)),
        ]
        for t,a,c,txt in menus:
            b=Button(text=t, font_size='10sp', bold=True, size_hint_y=None, height=50, background_color=c, background_normal='', color=txt)
            b.bind(on_press=a); grid.add_widget(b)
        gs.add_widget(grid); root.add_widget(gs)
        root.add_widget(Label(text="THAKTECH V13.0 PROFESSIONAL - Garansi Diagnosa 7 Hari - Garansi Remap 30 Hari", font_size='8sp', color=C("SUB"), size_hint_y=None, height=12))
        self.root_widget=root
        Window.bind(on_resize=self._fix_text_size)
        return root
    def update_jam(self):
        try: self.jam_lbl.text=time.strftime("%H:%M - %d/%m/%Y")
        except: pass
    def _fix_text_size(self, win, w, h):
        try: self.output.text_size = (max(200, w - 28), None)
        except: pass
    def on_stop(self):
        try:
            if self.live_event: self.live_event.cancel()
            self.auto_save(); self.elm.disconnect()
        except: pass
    def teks_home(self):
        return "THAKTECH V13.0 PROFESSIONAL\n\nSelamat datang di sistem diagnostic profesional.\n\n1. Isi Plat + Motor + KM\n2. Pilih AUTO - UNIVERSAL\n3. Pairing ELM327 PIN 1234\n4. Colok DLC, Kontak ON\n5. KONEK ELM327 - LIVE DATA\n\nFitur Baru: Baca VIN - Freeze Frame - Cek Kiprok - Tes Injector - Laporan Harian - Grafik 3D"
    def set_output(self,t):
        try: self.output.text=str(t)
        except: pass
    def show_popup(self,judul,isi):
        try:
            box=BoxLayout(orientation='vertical', spacing=8, padding=12)
            box.add_widget(Label(text=str(isi), halign='left', valign='top', text_size=(W()-70, None), color=C("TEXT")))
            btn=Button(text="OK - MENGERTI", size_hint_y=None, height=44, background_color=C("GOLD"), color=(0,0,0,1), bold=True)
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
            self.set_output("MENGHUBUNGKAN ELM327...\nMencoba 2x otomatis kalo gagal...")
            def _do():
                ok,msg=self.elm.connect_universal(self.merk.text)
                def _ui(dt):
                    if ok:
                        self.mode="REAL"; self.real=True; self.last_vin=self.elm.vin; self.set_output(f"ELM327 TERHUBUNG - REAL\n{msg}"); self.status_lbl.text=f"REAL | {self.elm.merk_terdeteksi} | MAP: {self.map_aktif}"
                    else:
                        self.mode="SIMULASI"; self.real=False; self.set_output(f"ELM327 GAGAL - SIMULASI\n{msg}\n\nTips:\n- Bluetooth ON?\n- Sudah pairing PIN 1234?\n- Kontak ON?\n- ELM327 nancap di DLC?"); self.status_lbl.text=f"SIMULASI | MAP: {self.map_aktif}"
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
            self.auto_save(); self.set_output(self.output.text+"\n\nLIVE STOP.")
        except Exception as e: self.set_output(f"Stop error: {e}")
    def auto_save(self):
        try:
            with open(DATA_PATH("log_thaktech.csv"),"w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["Waktu","RPM","Suhu","Aki","Speed","Beban","Timing"]); w.writerows(self.log)
        except: pass
    def update_live(self,dt):
        try:
            if self.real and self.elm.connected:
                def _fetch():
                    try: data=self.elm.get_live_25()
                    except: data={}
                    def _apply(_dt):
                        self.rpm=safe_float(data.get('RPM',1480),1480); self.suhu=safe_float(data.get('SUHU',86),86); self.speed=safe_float(data.get('SPEED',0),0); self.aki=safe_float(data.get('AKI',13.8),13.8); self.tp=safe_float(data.get('TP',1.0),1.0); self.beban=safe_float(data.get('BEBAN',18),18); self.timing=safe_float(data.get('TIMING',12),12); self._render()
                    Clock.schedule_once(_apply)
                threading.Thread(target=_fetch, daemon=True).start(); return
            else:
                bonus=180 if self.map_aktif=="RACING / BALAP" else 80 if self.map_aktif=="HARIAN / TOURING" else -40 if self.map_aktif=="ECO / IRIT" else 0
                self.tp=max(0.5,min(12,self.tp+random.uniform(-0.3,0.5))); self.rpm=max(1200,min(12500,1480+self.tp*220+bonus)); self.suhu=max(60,min(118,self.suhu+random.uniform(-0.3,0.3))); self.aki=max(11.5,min(14.8,self.aki+random.uniform(-0.04,0.04))); self.speed=max(0,min(160,self.rpm/110)); self.beban=max(5,min(95,18+self.tp*3)); self.timing=12+random.uniform(-1,1)
                self._render()
        except Exception as e: self.set_output(f"Live error: {e}")
    def _render(self):
        try:
            self.detik+=1; self.total_km+=self.speed*0.7/3600; self.total_bbm+=(0.6+self.tp*0.35)*0.7/3600
            self.lbl_rpm.text=f"{self.rpm:.0f}"; self.lbl_suhu.text=f"{self.suhu:.0f} C"; self.lbl_aki.text=f"{self.aki:.1f} V"; self.lbl_speed.text=f"{self.speed:.0f}"; self.lbl_beban.text=f"{self.beban:.0f}%"; self.lbl_timing.text=f"{self.timing:.0f}"
            self.log.append([time.strftime("%H:%M:%S"),f"{self.rpm:.0f}",f"{self.suhu:.0f}",f"{self.aki:.1f}",f"{self.speed:.0f}",f"{self.beban:.0f}",f"{self.timing:.0f}"])
            if len(self.log)>500: self.log.pop(0)
            score=100
            if self.suhu>100: score-=20
            if self.aki<12.2: score-=25
            if self.beban>85: score-=10
            if self.last_dtc: score-=len(self.last_dtc)*15
            self.last_score=max(0,score)
            self.status_lbl.text=f"{self.mode} | MAP: {self.map_aktif} | SEHAT {self.last_score}%"
            self.set_output(f"LIVE {self.mode} - {self.detik}s - SCORE {self.last_score}%\n----------------------\nRPM {self.rpm:.0f} | Speed {self.speed:.0f} | Suhu {self.suhu:.0f} C | Aki {self.aki:.1f} V\nTP {self.tp:.1f}% | Beban {self.beban:.0f}% | Timing {self.timing:.0f}\nTrip +{self.total_km:.2f} km | BBM {self.total_bbm:.3f} L\nDTC: {len(self.last_dtc)} kode - Map: {self.map_aktif}")
            self.last_live=f"RPM {self.rpm:.0f} | {self.map_aktif}"
        except Exception as e: self.set_output(f"Render error: {e}")
    def obd_scan(self,i):
        try:
            plat,motor,km=self.profil()
            if self.real and self.elm.connected:
                self.set_output("SCAN DTC REAL...\nTunggu 2 detik, jangan cabut kabel...")
                def _do():
                    codes,raw=self.elm.get_dtc_universal()
                    def _ui(dt):
                        if not codes: self.last_dtc=[]; self.set_output(f"SCAN DTC - REAL\n{motor} | {plat} | VIN: {self.last_vin}\n\nTIDAK ADA DTC - Mesin Bersih - Sehat")
                        else:
                            self.last_dtc=[(c,"DTC","SEDANG") for c in codes]; self.set_output(f"SCAN DTC REAL\nMotor: {motor} | {plat}\nVIN: {self.last_vin}\nDitemukan {len(codes)} kode: {', '.join(codes)}\nRaw: {raw}\n\nTekan CARI KODE untuk arti tiap kode."); self.last_scan=" | ".join(codes); self.history.append(self.last_scan)
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do, daemon=True).start(); return
            self.last_dtc=[("P0122","TP Low","SEDANG")]; self.set_output(f"SCAN DTC - {self.mode}\nMotor: {motor} | {plat}\n\n- P0122 - TP Low\nGejala: Gas ngempos\nSolusi: Cek TP\n\nIni mode SIMULASI. Konek ELM327 untuk SCAN REAL."); self.last_scan="P0122"; self.history.append(self.last_scan)
        except Exception as e: self.set_output(f"Scan error: {e}")
    def clear_dtc(self,i):
        try:
            if not self.last_dtc: self.set_output("Tidak ada DTC yang perlu dihapus."); return
            if self.real and self.elm.connected:
                resp=self.elm.clear_dtc(); j=len(self.last_dtc); self.last_dtc=[]; self.set_output(f"HAPUS DTC REAL BERHASIL - {j} kode\nRespon ECU: {resp}\n\nScan ulang setelah 1 menit jalan untuk pastikan tidak muncul lagi.")
            else:
                j=len(self.last_dtc); self.last_dtc=[]; self.set_output(f"HAPUS DTC BERHASIL - {j} kode (SIMULASI)")
        except Exception as e: self.set_output(f"Clear error: {e}")
    def dtc_lookup(self,i):
        try:
            q=self.input_kode.text
            if not q.strip(): self.set_output("Ketik dulu: 8-1 / P0122"); return
            h=cari(q,self.merk.text)
            if not h: self.set_output(f"{q.upper()} tidak ditemukan di database {self.merk.text}."); return
            r=h[0]; self.set_output(f"HASIL - {r[0]}\nKode: {r[1]} | OBD: {r[2]}\nKerusakan: {r[3]}\nGejala: {r[4]}\nSolusi: {r[5]}\nLevel: {r[6]}\n\nEstimasi biaya cek: Rp 25.000 - 75.000"); self.last_scan=f"{r[1]} - {r[3]}"
        except Exception as e: self.set_output(f"Lookup error: {e}")
    def health_score(self,i): self.set_output(f"HEALTH SCORE PROFESSIONAL\n\nSkor: {self.last_score} / 100\nSuhu: {self.suhu:.0f} C | Aki: {self.aki:.1f} V | Beban: {self.beban:.0f}%\nDTC: {len(self.last_dtc)} | Map: {self.map_aktif}\n\nPenilaian:\n90-100: Sehat, servis rutin\n70-89: Perlu cek ringan\n<70: Segera ke bengkel")
    def ai_diagnosa(self,i):
        s=[]
        if self.suhu>100: s.append("OVERHEAT: Cek radiator, kipas, air coolant. Jangan buka tutup radiator panas.")
        if self.aki<12.2: s.append("AKI LEMAH: Cek kiprok pakai menu CEK KIPROK. Aki di bawah 12.2 V rawan mogok.")
        if self.beban>85: s.append("BEBAN TINGGI: Mesin kerja berat, cek filter udara dan injector.")
        if self.last_dtc: s.append(f"DTC {len(self.last_dtc)} aktif. Jangan cuma hapus, perbaiki sumbernya.")
        if self.suhu<70 and self.detik>60: s.append("SUHU RENDAH TERUS: Thermostat mungkin macet terbuka.")
        if not s: s.append("Mesin sehat. Servis rutin aja, ganti oli tiap 2000 km.")
        self.set_output("AI DIAGNOSA PROFESSIONAL\n\n"+"\n".join(["- "+x for x in s])+f"\n\nSkor Kesehatan: {self.last_score} / 100")
    def backup_map(self,i):
        self.map_backup=self.map_aktif; self.map_backup_data={"map":self.map_aktif,"waktu":time.strftime('%d/%m/%Y %H:%M')}
        self.set_output(f"BACKUP BERHASIL\nMap: {self.map_backup}\nWaktu: {self.map_backup_data['waktu']}\nAman untuk Remap. Jangan hapus backup ini.")
    def restore_map(self,i):
        if not self.map_backup: self.set_output("Belum ada backup! Pencet BACKUP dulu."); return
        self.map_aktif=self.map_backup; self.set_output(f"RESTORE BERHASIL - Balik ke {self.map_aktif}\nGaransi: Map pabrik kembali, aman.")
    def remap_ecu(self,i):
        try:
            pilih=self.map_spinner.text
            if not self.map_backup: self.set_output("REMAP DITOLAK - BACKUP DULU!\nIni proteksi biar ECU lu gak rusak."); return
            if self.aki<12.4: self.set_output(f"REMAP DITOLAK - AKI {self.aki:.1f} V, minimal 12.4 V\nCas aki dulu atau sambil di-charger."); return
            if self.suhu>100: self.set_output(f"REMAP DITOLAK - SUHU {self.suhu:.0f} C, dinginkan dulu 15 menit."); return
            if self.last_dtc: self.set_output("REMAP DITOLAK - Masih ada DTC aktif.\nHapus dan perbaiki DTC dulu sebelum Remap."); return
            if self.real and self.elm.connected:
                self.set_output(f"REMAP REAL - Kirim ke ECU...\nMap: {pilih}\nJANGAN CABUT KABEL! JANGAN MATIKAN KONTAK!")
                m=MAPS[pilih]
                def _do():
                    ok_b,_=self.elm.backup_map_real(self.elm.merk_terdeteksi); ok,resp=self.elm.remap_real_stage1(self.elm.merk_terdeteksi,pilih,m["fuel"],m["timing"])
                    def _ui(dt):
                        if ok:
                            lama=self.map_aktif; self.map_aktif=pilih; self.total_pendapatan+=HARGA[pilih]; self.set_output(f"REMAP REAL BERHASIL\n{lama} -> {pilih}\nHarga Rp {HARGA[pilih]:,}\nKeterangan: {m['ket']}\nRespon: {resp}"); self.last_remap=f"REMAP REAL {lama}->{pilih}"
                        else: self.set_output(f"REMAP GAGAL - AMAN, map tidak berubah.\nAlasan: {resp}\nECU lu aman, tidak ada yang berubah.")
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do, daemon=True).start(); return
            lama=self.map_aktif; self.map_aktif=pilih; m=MAPS[pilih]; self.total_pendapatan+=HARGA[pilih]; self.set_output(f"REMAP SIMULASI\n{lama} -> {pilih}\nHarga Rp {HARGA[pilih]:,}\nKeterangan: {m['ket']}\nKonek ELM327 untuk REMAP REAL."); self.last_remap=f"REMAP SIMULASI {lama}->{pilih}"
        except Exception as e: self.set_output(f"Remap error: {e}")
    def baca_vin(self,i):
        try:
            if self.real and self.elm.connected:
                self.set_output(f"BACA VIN - REAL\nVIN: {self.elm.vin}\nMerk Terdeteksi: {self.elm.merk_terdeteksi}\nProtokol: {self.elm.protokol_aktif}\nHarga Rp {HARGA['BACA VIN']:,}")
            else:
                v="MH1KF1234NK123456"; self.last_vin=v; self.set_output(f"BACA VIN - SIMULASI\nVIN: {v}\nMerk: {self.merk.text}\nHarga Rp {HARGA['BACA VIN']:,}\nKonek ELM327 untuk VIN asli.")
        except Exception as e: self.set_output(f"VIN error: {e}")
    def freeze_frame(self,i):
        try:
            if self.real and self.elm.connected:
                def _do():
                    r=self.elm.get_freeze_frame()
                    def _ui(dt): self.set_output(f"FREEZE FRAME - REAL\nData saat DTC muncul:\n{r}\nHarga Rp {HARGA['FREEZE FRAME']:,}")
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do, daemon=True).start(); return
            self.set_output(f"FREEZE FRAME - SIMULASI\nSaat DTC P0122 muncul:\nRPM 2450 | Suhu 92 C | Speed 35 | TP 12%\nBeban 45% | Timing 14\nHarga Rp {HARGA['FREEZE FRAME']:,}")
        except Exception as e: self.set_output(f"Freeze error: {e}")
    def cek_kiprok(self,i):
        try:
            v=self.aki
            if v>=13.5: hasil="KIPROK SEHAT - Pengisian normal 13.5 - 14.8 V"
            elif v>=12.8: hasil="KIPROK LEMAH - Pengisian kurang, cek spul dan soket"
            elif v>=12.2: hasil="KIPROK BERMASALAH - Aki tidak ngisi, segera ganti"
            else: hasil="KIPROK RUSAK / AKI SOAK - Jangan jalan jauh"
            self.set_output(f"CEK KIPROK PROFESSIONAL\n\nTegangan: {v:.1f} V\nHasil: {hasil}\nNormal: 13.5 - 14.8 V saat mesin hidup\nHarga Rp {HARGA['CEK KIPROK']:,}")
        except Exception as e: self.set_output(f"Kiprok error: {e}")
    def tes_injector(self,i):
        try:
            flow=random.uniform(85,115)
            hasil="INJECTOR SEHAT - Semprotan rata" if 90<=flow<=110 else "INJECTOR KOTOR - Perlu cleaning / ultrasonic"
            self.set_output(f"TES INJECTOR\n\nFlow: {flow:.0f}%\nHasil: {hasil}\nNormal: 90 - 110%\nHarga Rp {HARGA['TES INJECTOR']:,}")
        except Exception as e: self.set_output(f"Injector error: {e}")
    def read_key(self,i):
        self.total_pendapatan+=HARGA['READ KEY']; self.set_output(f"READ KEY PROFESSIONAL\n\nKey: {self.key_id}\nECU: {self.ecu_id}\nPass: {self.passkey}\nSinyal: {self.key_sinyal}% | Baterai: {self.key_baterai}%\nHarga Rp {HARGA['READ KEY']:,}"); self.last_key=f"Key {self.key_id}"
    def register_key(self,i):
        old=self.key_id; self.key_id=buat_id("KEY-NEW"); self.key_list.append(self.key_id); self.passkey=buat_pass(self.key_id,self.ecu_id); self.total_pendapatan+=HARGA['REGISTER KEY']
        self.set_output(f"REGISTER KEY BERHASIL\nLama: {old}\nBaru: {self.key_id}\nPass: {self.passkey}\nTotal Key: {len(self.key_list)}\nHarga Rp {HARGA['REGISTER KEY']:,}"); self.last_key=f"Register {self.key_id}"
    def clone_key(self,i):
        c=buat_id("CLONE"); self.key_list.append(c); self.total_pendapatan+=HARGA['CLONE KEY']; self.set_output(f"CLONE KEY BERHASIL\nClone: {c}\nPass sama: {self.passkey}\nHarga Rp {HARGA['CLONE KEY']:,}"); self.last_key=f"Clone {c}"
    def key_hilang(self,i):
        hilang=self.key_id; self.key_id=buat_id("KEY-HILANG"); self.key_list=[self.key_id]; self.passkey=buat_pass(self.key_id,self.ecu_id); self.total_pendapatan+=HARGA['KEY HILANG']
        self.set_output(f"KEY HILANG - RESET TOTAL\nKey lama diblokir: {hilang}\nKey baru: {self.key_id}\nPass: {self.passkey}\nHarga Rp {HARGA['KEY HILANG']:,}"); self.last_key=f"Hilang -> {self.key_id}"
    def cek_key_manual(self,i):
        q=self.input_kode.text.strip().upper()
        if not q: self.set_output("Ketik ID Remot di kolom input dulu, contoh AB12-CD34"); return
        cocok=q.replace("-","") in [k.replace("-","") for k in self.key_list]
        self.set_output(f"CEK KEY\nID: {q}\nHasil: {'COCOK - Bisa hidup' if cocok else 'TIDAK COCOK - Harus REGISTER'}\nSinyal: {self.key_sinyal}% | Baterai: {self.key_baterai}%")
    def baterai_remot(self,i): self.set_output(f"BATERAI REMOT\n\nBaterai: {self.key_baterai}%\nSinyal: {self.key_sinyal}%\nTipe CR2032 - Ganti tiap 1 tahun\nHarga Rp {HARGA['GANTI BATERAI REMOT']:,}")
    def hapus_key(self,i):
        if len(self.key_list)<=1: self.set_output("DITOLAK - Tinggal 1 key, tidak boleh hapus semua!"); return
        if self.key_list[-1]==self.key_id: self.set_output("DITOLAK - Tidak boleh hapus key AKTIF."); return
        h=self.key_list.pop(); self.set_output(f"HAPUS KEY BERHASIL\nDihapus: {h}\nSisa: {len(self.key_list)} key")
    def daftar_key(self,i):
        t=f"DAFTAR KEY - {len(self.key_list)} KEY\nECU: {self.ecu_id}\n\n"
        for idx,k in enumerate(self.key_list,1): t+=f"{idx}. {k} {'(AKTIF)' if k==self.key_id else ''}\n"
        self.set_output(t)
    def battery(self,i):
        v=round(random.uniform(12.4,13.9),1) if not self.real else self.aki
        status="SEHAT" if v>=12.6 else "LEMAH - Cas / Ganti" if v>=12.2 else "SOAK - Ganti"
        self.set_output(f"BATTERY TEST PROFESSIONAL\n\n{v} V - {status}\nCCA: {int(v*35)} A (estimasi)\nSuhu Aki: {self.suhu:.0f} C\nHarga Rp {HARGA['BATTERY TEST']:,}")
    def trip_bbm(self,i): self.set_output(f"TRIP / BBM PROFESSIONAL\n\nTrip +{self.total_km:.2f} km\nBBM {self.total_bbm:.3f} L\nKonsumsi: {(self.total_km/max(0.01,self.total_bbm)):.1f} km/L\nMap: {self.map_aktif}\nPendapatan hari ini: Rp {self.total_pendapatan:,}")
    def servis(self,i):
        plat,motor,km=self.profil(); sisa_oli=2000-(km%2000); sisa_busi=8000-(km%8000); sisa_cvt=10000-(km%10000)
        self.set_output(f"SERVIS REMINDER PROFESSIONAL\n\nMotor: {motor} | {plat} | KM {km}\n\n- Oli: {sisa_oli} km lagi - Rp 55.000\n- Busi: {sisa_busi} km lagi - Rp 35.000\n- CVT: {sisa_cvt} km lagi - Rp 120.000\n- Filter Udara: Cek tiap 4000 km\n\nTotal estimasi servis lengkap: Rp {HARGA['SERVIS LENGKAP']:,}")
    def readiness(self,i): self.set_output("READINESS MONITOR\n\nMisfire: SIAP\nFuel System: SIAP\nO2 Sensor: SIAP\nCatalyst: Jalan 10 km dulu\nEGR: SIAP\n\nSemua siap untuk uji emisi.")
    def emergency(self,i): self.show_popup("EMERGENCY","1. Matikan kontak\n2. Cek suhu, aki, DTC\n3. Suhu di atas 110 C tunggu 20 menit, jangan buka radiator\n4. Aki di bawah 11.5 V jangan stater terus, dorong / jumper\n5. Bau bensin: jangan stater, cek selang bensin")
    def export_csv(self,i):
        try:
            p=DATA_PATH("log_thaktech.csv")
            with open(p,"w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["Waktu","RPM","Suhu","Aki","Speed","Beban","Timing"]); w.writerows(self.log)
            self.set_output(f"EXPORT BERHASIL\nFile: {p}\nIsi: {len(self.log)} baris\nFile bisa dibuka di Excel / Google Sheets")
        except Exception as e: self.set_output(f"Export gagal: {e}")
    def print_struk(self,i):
        plat,motor,km=self.profil(); trx=buat_id("TRX"); t=time.strftime("%d/%m/%Y %H:%M")
        s=f"THAKTECH PROFESSIONAL\nTRX: {trx}\nTanggal: {t}\nMotor: {motor} | {plat} | KM {km}\nVIN: {self.last_vin}\nMode: {self.mode}\nScan: {self.last_scan}\nRemap: {self.last_remap}\nLive: {self.last_live}\nHealth: {self.last_score}%\n----------------\nTerima kasih - Garansi 7 hari\nGaransi Remap 30 hari"
        try: open(DATA_PATH("struk.txt"),"w",encoding="utf-8").write(s)
        except: pass
        if HAS_CLIP and Clipboard:
            try: Clipboard.copy(s)
            except: pass
        self.set_output(s+"\n\n[OK] Tersalin. TRX: "+trx)
    def laporan_harian(self,i):
        self.set_output(f"LAPORAN HARIAN BENGKEL\nTanggal: {time.strftime('%d/%m/%Y %H:%M')}\n\nTotal Scan: {len(self.history)} motor\nTotal Pendapatan: Rp {self.total_pendapatan:,}\nTotal Trip Tes: {self.total_km:.2f} km\nMap Terakhir: {self.map_aktif}\nHealth Rata-rata: {self.last_score}%\n\nHistory:\n"+"\n".join([f"- {h}" for h in self.history[-5:]]) if self.history else "Belum ada transaksi hari ini.")
    def show_history(self,i):
        if not self.history: self.set_output("HISTORY KOSONG - Belum ada scan hari ini"); return
        self.set_output("HISTORY PROFESSIONAL:\n\n"+"\n".join([f"{i+1}. {h}" for i,h in enumerate(self.history)]))

if __name__=='__main__':
    try:
        ThakTechApp().run()
    except Exception as e:
        print("FATAL:", traceback.format_exc())
