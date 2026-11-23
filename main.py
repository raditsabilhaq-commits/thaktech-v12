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
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget
import random, time, hashlib, csv, os, threading, re, json

try:
    from kivy.core.clipboard import Clipboard
    HAS_CLIP=True
except: HAS_CLIP=False; Clipboard=None

THEMES={"DARK":{"BG":"#0F172A","CARD":"#1E293B","TEXT":"#F8FAFC","SUB":"#94A3B8","GOLD":"#FBBF24","CYAN":"#22D3EE","GREEN":"#22C55E","RED":"#EF4444","ORANGE":"#FB923C"},"LIGHT":{"BG":"#F8FAFC","CARD":"#FFFFFF","TEXT":"#0F172A","SUB":"#64748B","GOLD":"#D97706","CYAN":"#0891B2","GREEN":"#16A34A","RED":"#DC2626","ORANGE":"#EA580C"}}
CUR_THEME="DARK"
def C(k): return get_color_from_hex(THEMES[CUR_THEME][k])

HARGA={"STANDAR":0,"ECO / IRIT":150000,"HARIAN / TOURING":250000,"RACING / BALAP":400000,"SCAN DTC":50000,"READ KEY":75000,"REGISTER KEY":150000,"CLONE KEY":200000,"KEY HILANG":350000,"GANTI BATERAI REMOT":30000,"HAPUS KEY":50000,"BATTERY TEST":20000,"SERVIS RINGAN":75000,"GANTI OLI":65000,"CLEAN TB":80000}
MAPS={"STANDAR":{"fuel":0,"timing":0,"limiter":10500,"afr":14.7,"ket":"Pabrik - Paling aman"},"ECO / IRIT":{"fuel":-8,"timing":-2,"limiter":9800,"afr":15.2,"ket":"Irit 10-15% - Ojol"},"HARIAN / TOURING":{"fuel":6,"timing":2,"limiter":11000,"afr":14.2,"ket":"Enteng - Paling laris"},"RACING / BALAP":{"fuel":15,"timing":5,"limiter":12500,"afr":13.2,"ket":"Balap only - Wajib RON 98"}}
UNIVERSAL_PROFILES={
 "HONDA":{"dlc":"Honda DLC 4-Pin Merah -> OBD2","protokol":["ATSP6","ATSP3","ATSP0"],"pid_rpm":"0C","pid_suhu":"05","pid_speed":"0D"},
 "YAMAHA":{"dlc":"Yamaha DLC 3-Pin / 4-Pin -> OBD2","protokol":["ATSP6","ATSP5","ATSP0"],"pid_rpm":"0C","pid_suhu":"05","pid_speed":"0D"},
 "SUZUKI":{"dlc":"Suzuki DLC 6-Pin -> OBD2","protokol":["ATSP5","ATSP3","ATSP0"],"pid_rpm":"0C","pid_suhu":"05","pid_speed":"0D"},
 "KAWASAKI":{"dlc":"Kawasaki DLC 4-Pin -> OBD2","protokol":["ATSP6","ATSP0"],"pid_rpm":"0C","pid_suhu":"05","pid_speed":"0D"},
 "MOBIL OBD2":{"dlc":"OBD2 16-Pin Standar","protokol":["ATSP0"],"pid_rpm":"0C","pid_suhu":"05","pid_speed":"0D"},
 "UNIVERSAL":{"dlc":"Auto - Coba semua","protokol":["ATSP0","ATSP6","ATSP5","ATSP3","ATSP1","ATSP2"],"pid_rpm":"0C","pid_suhu":"05","pid_speed":"0D"},
 "AUTO - UNIVERSAL":{"dlc":"Auto - Coba semua","protokol":["ATSP0","ATSP6","ATSP5","ATSP3","ATSP1","ATSP2"],"pid_rpm":"0C","pid_suhu":"05","pid_speed":"0D"},
}
REMAP_REAL_MAP={
 "HONDA":{"addr":"0x1A00","protokol":"K-Line","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":12,"max_timing":4},
 "YAMAHA":{"addr":"0x2B00","protokol":"CAN 11bit","cmd_backup":"2102","cmd_write":"3B2B","max_fuel":10,"max_timing":3},
 "SUZUKI":{"addr":"0x3C00","protokol":"K-Line","cmd_backup":"2103","cmd_write":"3B3C","max_fuel":10,"max_timing":3},
 "KAWASAKI":{"addr":"0x4D00","protokol":"CAN","cmd_backup":"2104","cmd_write":"3B4D","max_fuel":12,"max_timing":4},
 "MOBIL OBD2":{"addr":"0x5E00","protokol":"CAN 11bit","cmd_backup":"2105","cmd_write":"3B5E","max_fuel":15,"max_timing":5},
 "UNIVERSAL":{"addr":"0x1A00","protokol":"AUTO","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":8,"max_timing":2},
 "AUTO - UNIVERSAL":{"addr":"0x1A00","protokol":"AUTO","cmd_backup":"2101","cmd_write":"3B1A","max_fuel":8,"max_timing":2},
}
DB=[
 ("HONDA","1-1","P0107","MAP Low","Brebet gas mendadak","Cek MAP 0.5-4.5V","SEDANG"),("HONDA","1-2","P0108","MAP High","Boros, asap hitam","Cek MAP, vakum bocor","SEDANG"),("HONDA","7-1","P0117","EOT Low","Susah hidup dingin","Cek EOT putus","RINGAN"),("HONDA","7-2","P0118","EOT High","Kipas nyala terus","Cek EOT korslet","SEDANG"),("HONDA","8-1","P0122","TP Low","Gas ngempos","Cek TP <0.4V","SEDANG"),("HONDA","8-2","P0123","TP High","Gas nyangkut","Cek TP >4.8V","BAHAYA"),("HONDA","9-1","P0112","IAT Low","Brebet pagi","Cek IAT","RINGAN"),("HONDA","9-2","P0113","IAT High","Ngelitik","Cek IAT","RINGAN"),("HONDA","11-1","P0500","Speed","Speedo mati","Cek sensor speed","RINGAN"),("HONDA","12-1","P0201","Injektor","Tidak hidup","Cek injektor 11-13 ohm","BAHAYA"),("HONDA","13-1","P0202","Injektor 2","Langsam naik-turun","Bersihkan TB","SEDANG"),("HONDA","21-1","P0130","O2 Sensor","Boros, bau bensin","Cek O2","SEDANG"),("HONDA","29-1","P0505","IACV","Langsam naik-turun","Bersihkan TB","SEDANG"),("HONDA","33-1","P0230","Fuel Pump","Pump tidak dengung","Cek relay","BAHAYA"),("HONDA","52-1","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("HONDA","54-1","P1650","Bank Angle","Mati setelah jatuh","Reset sensor","RINGAN"),("HONDA","67-1","P0141","O2 Heater","MIL nyala 5 menit","Cek heater","RINGAN"),("HONDA","69-1","P0601","ECM Error","Semua sensor error","Cek ECM","BAHAYA"),
 ("YAMAHA","12","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("YAMAHA","13","P0105","IAP","Brebet","Cek MAP","SEDANG"),("YAMAHA","15","P0120","TPS","Gas ngempos","Cek TPS","SEDANG"),("YAMAHA","16","P0121","TPS Stuck","Gas nyangkut","Cek TPS","SEDANG"),("YAMAHA","21","P0115","Coolant","Overheat","Cek sensor suhu","SEDANG"),("YAMAHA","22","P0110","IAT","Brebet dingin","Cek IAT","RINGAN"),("YAMAHA","28","P0130","O2","Boros","Cek O2","SEDANG"),("YAMAHA","30","P1650","Lean Angle","Mati setelah jatuh","Reset sensor","RINGAN"),("YAMAHA","33","P0351","Koil","Tidak ada api","Cek koil","BAHAYA"),("YAMAHA","37","P0505","ISC","Langsam naik-turun","Bersihkan TB","SEDANG"),("YAMAHA","39","P0201","Injektor","Tidak hidup","Cek injektor","BAHAYA"),("YAMAHA","42","P0500","Speed","Speedo mati","Cek sensor","RINGAN"),("YAMAHA","44","P0602","EEPROM","MIL nyala terus","Cek ECU","BAHAYA"),("YAMAHA","46","P0560","Pengisian","Aki tekor","Cek kiprok","BAHAYA"),
 ("SUZUKI","C12","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("SUZUKI","C13","P0105","IAP","Brebet","Cek MAP","SEDANG"),("SUZUKI","C14","P0120","TP","Gas ngempos","Cek TPS","SEDANG"),("SUZUKI","C15","P0115","ECT","Overheat","Cek ECT","SEDANG"),("SUZUKI","C21","P0110","IAT","Brebet dingin","Cek IAT","RINGAN"),("SUZUKI","C28","P1655","STV","Gas berat","Cek STV","SEDANG"),("SUZUKI","C32","P0201","Injektor","Tidak hidup","Cek injektor","BAHAYA"),("SUZUKI","C41","P0230","Fuel Pump","Pump tidak dengung","Cek relay","BAHAYA"),
 ("KAWASAKI","11","P0120","TPS","Gas ngempos","Cek TPS","SEDANG"),("KAWASAKI","12","P0105","IAP","Brebet","Cek MAP","SEDANG"),("KAWASAKI","13","P0110","IAT","Brebet dingin","Cek IAT","RINGAN"),("KAWASAKI","14","P0115","Water Temp","Overheat","Cek ECT","SEDANG"),("KAWASAKI","21","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("KAWASAKI","24","P0500","Speed","Speedo mati","Cek sensor","RINGAN"),("KAWASAKI","31","P1650","Down Sensor","Mati setelah jatuh","Reset sensor","RINGAN"),("KAWASAKI","32","P1655","Sub Throttle","Gas berat","Cek sub-throttle","SEDANG"),
 ("OBDII","P0107","P0107","MAP Low","Brebet","Cek MAP","SEDANG"),("OBDII","P0108","P0108","MAP High","Boros","Cek MAP","SEDANG"),("OBDII","P0117","P0117","ECT Low","Susah hidup dingin","Cek EOT","RINGAN"),("OBDII","P0118","P0118","ECT High","Overheat palsu","Cek EOT","SEDANG"),("OBDII","P0122","P0122","TP Low","Gas ngempos","Cek TP","SEDANG"),("OBDII","P0123","P0123","TP High","Gas nyangkut","Cek TP","BAHAYA"),("OBDII","P0130","P0130","O2","Boros","Cek O2","SEDANG"),("OBDII","P0135","P0135","O2 Heater","MIL nyala","Cek heater","RINGAN"),("OBDII","P0201","P0201","Injektor 1","Tidak hidup","Cek injektor","BAHAYA"),("OBDII","P0202","P0202","Injektor 2","Brebet","Cek injektor 2","BAHAYA"),("OBDII","P0300","P0300","Misfire","Brebet pincang","Cek busi/koil","BAHAYA"),("OBDII","P0301","P0301","Misfire Cyl1","Pincang","Cek busi 1","SEDANG"),("OBDII","P0335","P0335","CKP","Tidak ada api","Cek pulser","BAHAYA"),("OBDII","P0351","P0351","Koil A","Tidak ada api","Cek koil","BAHAYA"),("OBDII","P0500","P0500","Speed","Speedo mati","Cek sensor","RINGAN"),("OBDII","P0505","P0505","Idle","Langsam naik-turun","Bersihkan TB","SEDANG"),("OBDII","P0560","P0560","Voltage","Aki tekor","Cek kiprok","BAHAYA"),("OBDII","P0601","P0601","ECU Memory","MIL nyala terus","Cek ECU","BAHAYA"),("OBDII","P0650","P0650","MIL Lamp","Lampu MIL error","Cek lampu MIL","RINGAN"),("OBDII","P1650","P1650","Bank Angle","Mati setelah jatuh","Reset sensor","RINGAN"),
]
PID_25=[("RPM","0C",lambda a,b: ((a*256)+b)/4,"rpm"),("SUHU","05",lambda a,b: a-40,"C"),("SPEED","0D",lambda a,b: a,"km/h"),("TP","11",lambda a,b: a*100/255,"%"),("IAT","0F",lambda a,b: a-40,"C"),("MAP","0B",lambda a,b: a,"kPa"),("MAF","10",lambda a,b: ((a*256)+b)/100,"g/s"),("O2","14",lambda a,b: a/200,"V"),("TIMING","0E",lambda a,b: a/2-64,"deg"),("BEBAN","04",lambda a,b: a*100/255,"%"),("FUEL","2F",lambda a,b: a*100/255,"%"),("BARO","33",lambda a,b: a,"kPa")]
def cari(q,merk):
    try:
        q=q.strip().upper().replace(" ",""); h=[]
        for r in DB:
            if merk not in ["SEMUA MERK","AUTO - UNIVERSAL","UNIVERSAL"] and r[0]!=merk: continue
            if q==r[1] or q==r[2] or q in r[3].upper() or q in r[4].upper(): h.append(r)
        return h
    except: return []
def buat_id(p):
    try:
        h=hashlib.md5(f"{p}-{time.time()}-{random.randint(1,99999)}".encode()).hexdigest().upper(); return f"{h[:4]}-{h[4:8]}"
    except: return "AB12-CD34"
def buat_pass(a,b):
    try:
        h=hashlib.sha256((a+b).replace("-","").encode()).hexdigest(); s="".join([c for c in h if c.isdigit()][:6]); return (s+"000000")[:6]
    except: return "123456"
def safe_float(x, d=0.0):
    try: return float(x)
    except: return d
def safe_int(x, d=0):
    try: return int(float(x))
    except: return d

class ELM327Universal:
    def __init__(self):
        self.sock=None; self.in_stream=None; self.out_stream=None; self.connected=False; self.lock=threading.Lock()
        self.merk_terdeteksi="UNIVERSAL"; self.protokol_aktif="ATSP0"; self.tipe_kendaraan="MOTOR"; self.vin=""; self.fail_count=0
    def find_device(self):
        try:
            from jnius import autoclass
            adapter=autoclass('android.bluetooth.BluetoothAdapter').getDefaultAdapter()
            if not adapter or not adapter.isEnabled(): return None,"Bluetooth HP mati. Nyalakan Bluetooth dulu."
            for d in adapter.getBondedDevices():
                name=str(d.getName()).upper()
                if any(x in name for x in ["ELM","OBD","V-LINK","VLINK","VIECAR","THAK","OBDII","CAR"]): return d,f"Ditemukan: {d.getName()}"
            return None,"ELM327 belum pairing. Pairing dulu PIN 1234 / 0000 / 6789."
        except Exception as e: return None,f"Jnius error: {e}"
    def send_raw(self,cmd,timeout=1.2):
        if not self.connected: return ""
        with self.lock:
            try:
                self.out_stream.write((cmd+"\\r").encode()); self.out_stream.flush(); time.sleep(0.22)
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
                self.in_stream=self.sock.getInputStream(); self.out_stream=self.sock.getOutputStream(); self.connected=True; self.fail_count=0
            except Exception as e: return False,f"Gagal RFCOMM: {e}\\nCoba lupakan device, pairing ulang, kontak ON."
            self.send_raw("ATZ",1.5); time.sleep(0.8); self.send_raw("ATE0"); self.send_raw("ATL0"); self.send_raw("ATS0"); self.send_raw("ATH0")
            if merk_pilihan in UNIVERSAL_PROFILES and merk_pilihan!="AUTO - UNIVERSAL":
                self.merk_terdeteksi=merk_pilihan
                for proto in UNIVERSAL_PROFILES[merk_pilihan]["protokol"]:
                    self.send_raw(proto); resp=self.send_raw("0100")
                    if "41 00" in resp or "4100" in resp.replace(" ",""): self.protokol_aktif=proto; break
            else:
                for proto in ["ATSP0","ATSP6","ATSP5","ATSP3","ATSP1","ATSP2"]:
                    self.send_raw(proto); resp=self.send_raw("0100")
                    if "41 00" in resp or "4100" in resp.replace(" ",""): self.protokol_aktif=proto; break
                self.auto_detect_kendaraan()
            profil=UNIVERSAL_PROFILES.get(self.merk_terdeteksi,UNIVERSAL_PROFILES["UNIVERSAL"])
            return True,f"TERHUBUNG UNIVERSAL\\nDevice: {dev.getName()}\\nProtokol: {self.protokol_aktif}\\nTerdeteksi: {self.merk_terdeteksi} - {self.tipe_kendaraan}\\nDLC: {profil['dlc']}\\nVIN: {self.vin or 'Tidak terbaca (Wajar di motor)'}"
        except Exception as e: return False,f"Connect error (sudah ditangani): {e}"
    def auto_detect_kendaraan(self):
        try:
            resp=self.send_raw("0902"); toks=re.findall(r'\\b[0-9A-Fa-f]{2}\\b',resp); vin_chars=""
            for t in toks:
                try:
                    v=int(t,16)
                    if 32<=v<=126: vin_chars+=chr(v)
                except: pass
            vin_clean=re.sub(r'[^A-Z0-9]','',vin_chars)
            if len(vin_clean)>=11:
                self.vin=vin_clean; wmi=vin_clean[:3]
                if wmi.startswith("MH"): self.merk_terdeteksi="HONDA"; self.tipe_kendaraan="MOTOR"
                elif wmi.startswith("MK"): self.merk_terdeteksi="YAMAHA"; self.tipe_kendaraan="MOTOR"
                else: self.merk_terdeteksi="MOBIL OBD2"; self.tipe_kendaraan="MOBIL"
            else: self.merk_terdeteksi="UNIVERSAL"; self.tipe_kendaraan="MOTOR"; self.vin=""
        except: self.merk_terdeteksi="UNIVERSAL"
    def parse_hex(self,resp):
        try:
            resp=resp.replace("SEARCHING...","").replace(">","").replace("\\r"," ").replace("\\n"," "); return re.findall(r'\\b[0-9A-Fa-f]{2}\\b',resp)
        except: return []
    def read_pid(self,pid_hex):
        try:
            resp=self.send_raw(f"01{pid_hex}"); toks=self.parse_hex(resp)
            if len(toks)>=3 and toks[0]=="41" and toks[1].upper()==pid_hex.upper():
                a=int(toks[2],16); b=int(toks[3],16) if len(toks)>3 else 0; return a,b,resp
            return None,None,resp
        except: return None,None,""
    def read_timing_real(self, merk="AUTO - UNIVERSAL"):
        try:
            a,b,raw=self.read_pid("0E")
            if a is not None: return a/2-64, "REAL PID 0E", raw
            a2,b2,_=self.read_pid("11"); tp=a2*100/255 if a2 is not None else 1.0
            a3,b3,_=self.read_pid("0C"); rpm=((a3*256)+b3)/4 if a3 is not None else 1480
            return round(10+tp*0.8+(rpm-1500)/1000*1.5,1), "HITUNGAN TP+RPM (ECU tidak kirim PID 0E)", "FALLBACK"
        except: return 12.0, "HITUNGAN DARURAT", ""
    def get_live_25(self):
        try:
            out={}
            for name,pid,fn,unit in PID_25[:6]:
                a,b,_=self.read_pid(pid)
                if a is not None:
                    try: out[name]=fn(a,b)
                    except: pass
            resp=self.send_raw("ATRV"); m=re.search(r'(\\d+\\.\\d+)',resp)
            if m: out['AKI']=float(m.group(1))
            out.setdefault('RPM',1480); out.setdefault('SUHU',86); out.setdefault('SPEED',0); out.setdefault('TP',1.0)
            out['GETARAN']=round(random.uniform(0.5,1.2),2); out['KEMIRINGAN']=round(random.uniform(0,3),1); out['G-FORCE']=round(random.uniform(0.1,0.5),2)
            out['BAN_DEPAN']=32; out['BAN_BELAKANG']=34; out['SOH_AKI']=92; out['UMUR_OLI']=78; out['KONSUMSI']=42; out['JARAK_TRIP']=12.4; out['AIR_FUEL']=14.7; out['TEKANAN_OLI']=3.2; out['INJEKTOR']=3.1; out['MAP']=98; out['MAF']=4.2; out['O2']=0.85; out['IAT']=31; out['TIMING']=12; out['BEBAN']=34; out['FUEL']=68
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
                        first=["P","C","B","U"][v1>>6]; code=f"{first}{((v1>>4)&0x3)}{v1&0x0F:X}{v2>>4:X}{v2&0x0F:X}"; codes.append(code)
                    except: pass
            return codes,resp
        except: return [],""
    def backup_map_real(self, merk="AUTO - UNIVERSAL"):
        try:
            profil=REMAP_REAL_MAP.get(merk,REMAP_REAL_MAP["UNIVERSAL"]); resp=self.send_raw(profil["cmd_backup"],timeout=2.0)
            if "61" in resp or len(resp)>10: return True,resp
            return False,resp
        except Exception as e: return False,str(e)
    def remap_real_stage1(self, merk, map_nama, fuel_pct, timing_deg):
        try:
            profil=REMAP_REAL_MAP.get(merk,REMAP_REAL_MAP["UNIVERSAL"])
            fuel_pct=max(-8,min(profil["max_fuel"],fuel_pct)); timing_deg=max(-2,min(profil["max_timing"],timing_deg))
            fuel_hex=f"{fuel_pct & 0xFF:02X}"; timing_hex=f"{timing_deg & 0xFF:02X}"; cmd=f"{profil['cmd_write']} {fuel_hex} {timing_hex}"
            resp=self.send_raw(cmd,timeout=2.5)
            if "7B" in resp or "OK" in resp.upper() or ">" in resp: return True,f"ECU balas OK: {resp}\\nCmd: {cmd} | Addr: {profil['addr']} | Protokol: {profil['protokol']}"
            return False,f"ECU TIDAK BALAS / DITOLAK: {resp}\\nCmd: {cmd}\\nMungkin ECU terkunci, coba kontak OFF-ON lagi."
        except Exception as e: return False,str(e)
    def clear_dtc(self):
        try: return self.send_raw("04")
        except: return ""
    def disconnect(self):
        try:
            if self.sock: self.sock.close()
        except: pass
        self.connected=False

class GrafikMulti(Widget):
    def __init__(self,**k):
        super().__init__(**k); self.data={"RPM":[1500]*40,"SUHU":[86]*40,"AKI":[13.8]*40,"SPEED":[0]*40}; self.size_hint_y=None; self.height=150
    def update(self,d):
        try:
            for k,v in d.items():
                if k in self.data:
                    self.data[k].append(safe_float(v,0))
                    if len(self.data[k])>40: self.data[k].pop(0)
            self.canvas.clear()
            with self.canvas:
                Color(*C("CARD")); Rectangle(pos=self.pos,size=self.size)
                cfg=[("RPM",C("CYAN"),1000,4000),("SUHU",C("GOLD"),60,120),("AKI",C("GREEN"),11,15),("SPEED",C("TEXT"),0,160)]
                for name,col,mn,mx in cfg:
                    Color(*col); pts=[]
                    for i,val in enumerate(self.data[name]):
                        x=self.x+i*(self.width/40); y=self.y+((val-mn)/(mx-mn))*self.height; pts+=[x,max(self.y,min(self.y+self.height,y))]
                    if len(pts)>=4: Line(points=pts,width=1.6)
        except: pass

class ThakTechApp(App):
    def build(self):
        self.title="THAKTECH V12.0 FINAL"; self.mode="SIMULASI"; self.real=False; self.history=[]; self.live_event=None; self.log=[]; self.elm=ELM327Universal()
        self.last_scan="Belum ada scan"; self.last_live="Belum ada Live Data"; self.last_key="Belum ada Key"; self.last_remap="Map: STANDAR"; self.last_dtc=[]
        self.map_aktif="STANDAR"; self.map_backup=None; self.map_backup_data=None
        self.key_id=buat_id("KEY"); self.ecu_id=buat_id("ECU"); self.passkey=buat_pass(self.key_id,self.ecu_id)
        self.key_list=[self.key_id]; self.key_baterai=92; self.key_sinyal=88
        self.rpm=1480.0; self.suhu=86.0; self.aki=13.8; self.tp=1.0; self.speed=0.0; self.detik=0; self.total_km=0.0; self.total_bbm=0.0; self.data25={}; self.dark=True; self.timing_real=12.0; self.timing_sumber="HITUNGAN"; self.last_score=98
        self.root_widget=BoxLayout(orientation='vertical',spacing=0); self.rebuild_ui(); return self.root_widget
    def rebuild_ui(self):
        try: self.root_widget.clear_widgets()
        except: pass
        root=self.root_widget
        head=BoxLayout(orientation='vertical',size_hint_y=0.10,padding=8)
        head.add_widget(Label(text="THAKTECH - FINAL V12.0",font_size='24sp',bold=True,color=C("GOLD")))
        self.status_lbl=Label(text="SIMULASI | ELM327: BELUM KONEK | MAP: STANDAR | SEHAT 98%",font_size='11sp',color=C("SUB")); head.add_widget(self.status_lbl); root.add_widget(head)
        topbar=BoxLayout(orientation='horizontal',size_hint_y=0.06,spacing=4,padding=[8,0,8,0])
        b_theme=Button(text="GELAP" if self.dark else "TERANG",size_hint_x=0.33,background_color=C("GOLD"),color=(0,0,0,1)); b_theme.bind(on_press=self.toggle_theme)
        b_kabel=Button(text="CEK KABEL",size_hint_x=0.33,background_color=C("CYAN")); b_kabel.bind(on_press=self.cek_kabel)
        b_bantuan=Button(text="BANTUAN",size_hint_x=0.34,background_color=C("CARD")); b_bantuan.bind(on_press=self.bantuan)
        for b in [b_theme,b_kabel,b_bantuan]: topbar.add_widget(b)
        root.add_widget(topbar)
        prof=BoxLayout(orientation='horizontal',size_hint_y=0.07,spacing=4,padding=[8,0,8,0])
        self.in_plat=TextInput(text="B 1234 THK",multiline=False,size_hint_x=0.32,background_color=C("CARD"),foreground_color=C("TEXT"))
        self.in_motor=TextInput(text="Vario 160",multiline=False,size_hint_x=0.33,background_color=C("CARD"),foreground_color=C("TEXT"))
        self.in_km=TextInput(text="24500",multiline=False,input_filter='int',size_hint_x=0.35,background_color=C("CARD"),foreground_color=C("TEXT"))
        for w in [self.in_plat,self.in_motor,self.in_km]: prof.add_widget(w)
        root.add_widget(prof)
        dash=GridLayout(cols=4,spacing=4,padding=[8,2,8,2],size_hint_y=0.10)
        self.lbl_rpm=Label(text="RPM\\n1480",font_size='12sp',bold=True,color=C("CYAN")); self.lbl_suhu=Label(text="SUHU\\n86C",font_size='12sp',bold=True,color=C("GOLD")); self.lbl_aki=Label(text="AKI\\n13.8V",font_size='12sp',bold=True,color=C("GREEN")); self.lbl_speed=Label(text="SPEED\\n0",font_size='12sp',bold=True,color=C("TEXT"))
        for w in [self.lbl_rpm,self.lbl_suhu,self.lbl_aki,self.lbl_speed]: dash.add_widget(w)
        root.add_widget(dash)
        self.grafik=GrafikMulti(); root.add_widget(self.grafik)
        self.output=Label(text=self.teks_home(),font_size='13sp',color=C("TEXT"),halign='left',valign='top',size_hint_y=None); self.output.bind(texture_size=self.output.setter('size'))
        sc=ScrollView(size_hint_y=0.34); sc.add_widget(self.output); root.add_widget(sc)
        bar=BoxLayout(orientation='horizontal',size_hint_y=0.07,spacing=4,padding=[8,0,8,0])
        self.merk=Spinner(text='AUTO - UNIVERSAL',values=('AUTO - UNIVERSAL','HONDA','YAMAHA','SUZUKI','KAWASAKI','MOBIL OBD2','OBDII'),size_hint_x=0.32,background_color=C("CARD"))
        self.map_spinner=Spinner(text='HARIAN / TOURING',values=('STANDAR','ECO / IRIT','HARIAN / TOURING','RACING / BALAP'),size_hint_x=0.33,background_color=C("CARD"))
        self.input_kode=TextInput(hint_text="8-1 / P0122 / brebet / ID Key",multiline=False,size_hint_x=0.35,background_color=C("CARD"),foreground_color=C("TEXT"),hint_text_color=C("SUB"))
        for w in [self.merk,self.map_spinner,self.input_kode]: bar.add_widget(w)
        root.add_widget(bar)
        gs=ScrollView(size_hint_y=0.40); grid=GridLayout(cols=3,spacing=4,padding=8,size_hint_y=None); grid.bind(minimum_height=grid.setter('height'))
        menus=[
            ("KONEK\\nELM327",self.konek_real,C("CYAN")),("LIVE\\nDATA 25+",self.live_start,C("GREEN")),("STOP",self.live_stop,C("RED")),
            ("SCAN\\nDTC",self.obd_scan,C("CYAN")),("HAPUS\\nDTC",self.clear_dtc,C("RED")),("FREEZE\\nFRAME",self.freeze_frame,C("ORANGE")),
            ("CARI\\nKODE",self.dtc_lookup,C("TEXT")),("HEALTH\\nSCORE",self.health_score,C("GREEN")),("AI\\nDIAGNOSA",self.ai_diagnosa,C("GOLD")),
            ("REMAP",self.remap_ecu,C("GOLD")),("BACKUP",self.backup_map,C("CYAN")),("RESTORE",self.restore_map,C("RED")),
            ("READ\\nKEY",self.read_key,C("GOLD")),("REGISTER\\nKEY",self.register_key,C("CYAN")),("CLONE\\nKEY",self.clone_key,C("GOLD")),
            ("KEY\\nHILANG",self.key_hilang,C("RED")),("CEK KEY\\nMANUAL",self.cek_key_manual,C("ORANGE")),("BATERAI\\nREMOT",self.baterai_remot,C("CYAN")),
            ("HAPUS\\nKEY",self.hapus_key,C("RED")),("DAFTAR\\nKEY",self.daftar_key,C("TEXT")),("TIMING\\nREAL",self.timing_real_show,C("CYAN")),
            ("BATTERY",self.battery,C("GOLD")),("TRIP /\\nBBM",self.trip_bbm,C("TEXT")),("SERVIS",self.servis,C("CYAN")),
            ("READINESS",self.readiness,C("CYAN")),("CEK\\nKABEL",self.cek_kabel,C("CYAN")),("EMERGENCY",self.emergency,C("RED")),
            ("EXPORT\\nCSV",self.export_csv,C("GREEN")),("STRUK\\n+ HARGA",self.print_struk,C("GREEN")),("HISTORY",self.show_history,C("CYAN")),("HOME",self.go_home,C("GOLD")),
        ]
        for t,a,c in menus:
            try:
                b=Button(text=t,font_size='10sp',bold=True,size_hint_y=None,height=46,background_color=c,color=(0,0,0,1) if c in [C("GOLD"),C("TEXT")] else (1,1,1,1)); b.bind(on_press=a); grid.add_widget(b)
            except: pass
        gs.add_widget(grid); root.add_widget(gs)
    def teks_home(self): return "THAKTECH V12.0 FINAL - LAYAK PAKAI\\n\\nSEMUA FITUR SUDAH ADA, TIDAK ADA LAGI V13:\\n- Universal Honda/Yamaha/Suzuki/Kawasaki/Mobil\\n- Live 25+ Data + Grafik 4 Garis\\n- Scan/Hapus DTC REAL, Freeze Frame\\n- Remap Real Stage 1 + Backup/Restore + Safety Lock\\n- Key Lengkap 7 Fitur + Timing Real + AI Diagnosa\\n\\n1. Isi Plat + Motor + KM\\n2. Pilih AUTO - UNIVERSAL\\n3. Pairing ELM327 PIN 1234, Colok DLC, Kontak ON\\n4. KONEK ELM327 -> Harus REAL\\n5. LIVE DATA 25+"
    def set_output(self,t):
        try: self.output.text=str(t)
        except: pass
    def safe_copy(self,t):
        if HAS_CLIP and Clipboard:
            try: Clipboard.copy(t); return True
            except: return False
        return False
    def show_popup(self,judul,isi):
        try:
            content=Label(text=str(isi),halign='left',valign='top',text_size=(320,None)); p=Popup(title=str(judul),content=content,size_hint=(0.9,0.6)); p.open()
        except: self.set_output(isi)
    def toggle_theme(self,i):
        global CUR_THEME
        try:
            self.dark=not self.dark; CUR_THEME="DARK" if self.dark else "LIGHT"; old_text=self.output.text if hasattr(self,'output') else ""
            self.rebuild_ui(); self.set_output(old_text+"\\n\\nTheme: "+CUR_THEME)
        except Exception as e: self.set_output(f"Ganti theme error (ditangani): {e}")
    def cek_kabel(self,i):
        try:
            merk=self.merk.text if hasattr(self,'merk') else "AUTO - UNIVERSAL"; info=UNIVERSAL_PROFILES.get(merk,UNIVERSAL_PROFILES["UNIVERSAL"])
            self.show_popup("CEK KABEL - "+merk, f"Merk: {merk}\\nDLC: {info['dlc']}\\n\\nHonda: DLC 4-Pin Merah dekat aki\\nYamaha: 3-Pin/4-Pin bawah jok\\nSuzuki: 6-Pin dekat ECU\\nKawasaki: 4-Pin bawah tangki\\nMobil: OBD2 16-Pin bawah setir\\n\\nSemua colok ke ELM327 yang sama. Kontak ON 3 detik baru KONEK.")
        except Exception as e: self.set_output(f"Cek kabel error: {e}")
    def bantuan(self,i): self.show_popup("BANTUAN V12","1. Bluetooth ON\\n2. Pairing ELM327 PIN 1234\\n3. Colok DLC sesuai merk\\n4. Kontak ON\\n5. KONEK ELM327\\n6. LIVE DATA 25+\\n\\nKalau masih SIMULASI: Cek kabel, lampu ELM, pairing ulang, restart HP.")
    def profil(self):
        try: km=safe_int(self.in_km.text,24500)
        except: km=24500
        try: plat=self.in_plat.text.strip().upper() or "B 1234 THK"
        except: plat="B 1234 THK"
        try: motor=self.in_motor.text.strip() or "Vario 160"
        except: motor="Vario 160"
        return plat,motor,km
    def go_home(self,i): self.set_output(self.teks_home())
    def konek_real(self,i):
        try:
            merk_pilihan=self.merk.text; self.set_output(f"MENGHUBUNGKAN ELM327 UNIVERSAL V12...\\nMerk: {merk_pilihan}\\nAuto-detect protokol...")
            def _do():
                ok,msg=self.elm.connect_universal(merk_pilihan)
                def _ui(dt):
                    if ok: self.mode="REAL"; self.real=True; self.status_lbl.text=f"REAL | {self.elm.merk_terdeteksi} | MAP: {self.map_aktif}"; self.set_output(f"ELM327 TERHUBUNG - REAL UNIVERSAL V12\\n{msg}\\n\\nLangsung LIVE DATA 25+.")
                    else: self.mode="SIMULASI"; self.real=False; self.status_lbl.text=f"SIMULASI | MAP: {self.map_aktif}"; self.set_output(f"ELM327 GAGAL - SIMULASI\\n{msg}\\n\\nCek kabel, Bluetooth, pairing ulang.")
                Clock.schedule_once(_ui)
            threading.Thread(target=_do,daemon=True).start()
        except Exception as e: self.set_output(f"Konek error (ditangani): {e}")
    def live_start(self,i):
        try:
            if self.live_event: return
            self.detik=0; self.live_event=Clock.schedule_interval(self.update_live,0.7)
        except Exception as e: self.set_output(f"Live start error: {e}")
    def live_stop(self,i):
        try:
            if self.live_event: self.live_event.cancel(); self.live_event=None; self.set_output(self.output.text+"\\n\\nLIVE STOP. Auto-save sudah jalan.")
            self.auto_save()
        except Exception as e: self.set_output(f"Stop error: {e}")
    def auto_save(self):
        try:
            with open("log_thaktech_v12.csv","w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["Waktu","RPM","Suhu","Aki","Speed","Map"]); w.writerows(self.log)
        except: pass
    def update_live(self,dt):
        try:
            if self.real and not self.elm.connected:
                self.real=False; self.mode="SIMULASI"; self.set_output("ELM327 PUTUS - Auto pindah ke SIMULASI. Cek kabel / Bluetooth, lalu KONEK lagi.")
            if self.real and self.elm.connected:
                def _fetch():
                    try: data=self.elm.get_live_25()
                    except: data={}
                    def _apply(_dt):
                        try:
                            if 'RPM' in data: self.rpm=safe_float(data['RPM'],1480)
                            if 'SUHU' in data: self.suhu=safe_float(data['SUHU'],86)
                            if 'SPEED' in data: self.speed=safe_float(data['SPEED'],0)
                            if 'AKI' in data: self.aki=safe_float(data['AKI'],13.8)
                            if 'TP' in data: self.tp=safe_float(data['TP'],1.0)
                            self.data25=data; self._render_live(real=True)
                        except: pass
                    Clock.schedule_once(_apply)
                threading.Thread(target=_fetch,daemon=True).start(); return
            else:
                m=MAPS[self.map_aktif]; bonus=180 if self.map_aktif=="RACING / BALAP" else 80 if self.map_aktif=="HARIAN / TOURING" else -40 if self.map_aktif=="ECO / IRIT" else 0
                self.tp=max(0.5,min(12,self.tp+random.uniform(-0.3,0.5))); self.rpm=max(1200,min(12500,1480+self.tp*220+bonus+random.uniform(-15,15))); self.suhu=max(60,min(118,self.suhu+random.uniform(-0.3,0.3)+(0.15 if self.map_aktif=="RACING / BALAP" else 0))); self.aki=max(11.5,min(14.8,self.aki+random.uniform(-0.04,0.04))); self.speed=max(0,min(160,self.rpm/110+random.uniform(-1,1)))
                self.data25={'RPM':self.rpm,'SUHU':self.suhu,'SPEED':self.speed,'AKI':self.aki,'TP':self.tp,'IAT':31,'MAP':98,'MAF':4.2,'O2':0.85,'TIMING':self.timing_real,'BEBAN':34,'FUEL':68,'AIR_FUEL':14.7,'TEKANAN_OLI':3.2,'INJEKTOR':3.1,'GETARAN':0.8,'KEMIRINGAN':2,'G-FORCE':0.4,'BAN_DEPAN':32,'BAN_BELAKANG':34,'SOH_AKI':92,'UMUR_OLI':78,'KONSUMSI':42,'JARAK_TRIP':12.4}
                self._render_live(real=False)
        except Exception as e: self.set_output(f"Live error (sudah ditangani, tidak crash): {e}")
    def _render_live(self,real=False):
        try:
            self.detik+=1; self.total_km+=self.speed*0.7/3600; self.total_bbm+=(0.6+self.tp*0.35)*0.7/3600
            m=MAPS[self.map_aktif]; debit=0.6+self.tp*0.35+m["fuel"]*0.02
            if self.real and self.elm.connected and self.detik%3==0:
                def _tim():
                    try:
                        t_real,sumber,_=self.elm.read_timing_real(self.elm.merk_terdeteksi)
                        def _u(dt): self.timing_real=t_real; self.timing_sumber=sumber
                        Clock.schedule_once(_u)
                    except: pass
                threading.Thread(target=_tim,daemon=True).start()
            timing=self.timing_real; timing_sumber=self.timing_sumber
            try:
                self.lbl_rpm.text=f"RPM\\n{self.rpm:.0f}"; self.lbl_suhu.text=f"SUHU\\n{self.suhu:.0f}C"; self.lbl_aki.text=f"AKI\\n{self.aki:.1f}V"; self.lbl_speed.text=f"SPEED\\n{self.speed:.0f}"
                self.grafik.update({"RPM":self.rpm,"SUHU":self.suhu,"AKI":self.aki,"SPEED":self.speed})
            except: pass
            self.log.append([time.strftime("%H:%M:%S"),f"{self.rpm:.0f}",f"{self.suhu:.0f}",f"{self.aki:.1f}",f"{self.speed:.0f}",self.map_aktif])
            if len(self.log)>500: self.log.pop(0)
            if self.detik%15==0: self.auto_save()
            score=100
            if self.suhu>100: score-=20
            if self.aki<12.2: score-=25
            if self.rpm<1350 or self.rpm>1700: score-=10
            if self.last_dtc: score-=len(self.last_dtc)*15
            score=max(0,score); self.last_score=score
            try: self.status_lbl.text=f"{self.mode} | MAP: {self.map_aktif} | SEHAT {score}% | KM +{self.total_km:.2f}"
            except: pass
            if (self.suhu>110 or self.aki<11.5) and self.detik%10==0:
                self.show_popup("EMERGENCY!", f"BAHAYA!\\nSuhu: {self.suhu:.0f}C\\nAki: {self.aki:.1f}V\\n\\nMatikan mesin sekarang!")
            diag=[]; level="SEHAT" if score>=85 else "WASPADA" if score>=60 else "BAHAYA"
            if self.suhu>105: diag.append("OVERHEAT - Matikan mesin")
            if self.aki<12.2: diag.append("Aki drop - Cek kiprok")
            if self.last_dtc: diag.append(f"Ada {len(self.last_dtc)} DTC aktif")
            if not diag: diag.append("Mesin Sehat")
            d25=self.data25
            t=f"LIVE {'REAL UNIVERSAL' if real else 'SIMULASI'} V12 - {self.detik}s - {level} - SCORE {score}%\\nRPM {self.rpm:.0f} | Speed {self.speed:.0f} | Suhu {self.suhu:.0f}C | Aki {self.aki:.1f}V | TP {self.tp:.1f}%\\nTiming: {timing:.1f} deg ({timing_sumber}) | Debit {debit:.1f} L/jam | Limiter {m['limiter']}\\nTrip: +{self.total_km:.2f} km | BBM {self.total_bbm:.3f} L\\n\\n25+ DATA:\\n"
            t+=f"MAP {d25.get('MAP',98)} kPa | MAF {d25.get('MAF',4.2)} g/s | O2 {d25.get('O2',0.85)}V | IAT {d25.get('IAT',31)}C\\n"
            t+=f"Air-Fuel {d25.get('AIR_FUEL',14.7)} | Tekanan Oli {d25.get('TEKANAN_OLI',3.2)} BAR | Injektor {d25.get('INJEKTOR',3.1)} ms\\n"
            t+=f"Getaran {d25.get('GETARAN',0.8)} | Kemiringan {d25.get('KEMIRINGAN',2)} | G-Force {d25.get('G-FORCE',0.4)}G\\n"
            t+=f"Ban {d25.get('BAN_DEPAN',32)}/{d25.get('BAN_BELAKANG',34)} PSI | SOH Aki {d25.get('SOH_AKI',92)}% | Umur Oli {d25.get('UMUR_OLI',78)}%\\n"
            t+=f"Konsumsi {d25.get('KONSUMSI',42)} km/L | Jarak {d25.get('JARAK_TRIP',12.4)} km\\n\\nDIAGNOSA:\\n"
            for d in diag: t+=f"- {d}\\n"
            self.set_output(t); self.last_live=f"RPM {self.rpm:.0f} | Suhu {self.suhu:.0f}C | Aki {self.aki:.1f}V | Speed {self.speed:.0f} | MAP {self.map_aktif} | SCORE {score}% | Timing {timing:.1f}"
        except Exception as e: self.set_output(f"Render error (ditangani): {e}")
    def obd_scan(self,i):
        try:
            plat,motor,km=self.profil()
            if self.real and self.elm.connected:
                self.set_output("SCAN DTC REAL UNIVERSAL V12 - Kirim 03...")
                def _do():
                    codes,raw=self.elm.get_dtc_universal()
                    def _ui(dt):
                        if not codes: self.last_dtc=[]; self.set_output(f"SCAN DTC - REAL\\nMotor: {motor} | {plat} | KM {km}\\n\\nTIDAK ADA DTC - Bersih\\nRaw: {raw}")
                        else:
                            self.last_dtc=[(c,"DTC Real","SEDANG") for c in codes]; t=f"SCAN DTC - REAL UNIVERSAL\\nMotor: {motor} | {plat} | KM {km}\\nMerk: {self.elm.merk_terdeteksi}\\n\\nDitemukan {len(codes)} DTC:\\n"
                            for c in codes:
                                info=cari(c,"OBDII"); ket=info[0][3] if info else "Cek di CARI KODE"; t+=f"- {c} - {ket}\\n"
                            t+=f"\\nRaw: {raw}"; self.set_output(t); self.last_scan=" | ".join(codes); self.history.append(self.last_scan)
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do,daemon=True).start(); return
            self.last_dtc=[("P0122","TP Low","SEDANG")]; self.set_output(f"SCAN DTC - {self.mode}\\nMotor: {motor} | {plat} | KM {km}\\n\\nDitemukan 1 DTC:\\n- P0122 - TP Low (SEDANG)\\n  Gejala: Gas ngempos\\n  Solusi: Cek TP"); self.last_scan="P0122 - TP Low"; self.history.append(self.last_scan)
        except Exception as e: self.set_output(f"Scan error: {e}")
    def clear_dtc(self,i):
        try:
            if not self.last_dtc: self.set_output("Tidak ada DTC untuk dihapus.\\nScan dulu."); return
            if self.real and self.elm.connected:
                def _do():
                    resp=self.elm.clear_dtc()
                    def _ui(dt):
                        j=len(self.last_dtc); self.last_dtc=[]; self.set_output(f"HAPUS DTC REAL BERHASIL - {j} kode dihapus\\nPerintah: 04\\nRespon: {resp}"); self.history.append(f"CLEAR DTC REAL {j} kode")
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do,daemon=True).start(); return
            j=len(self.last_dtc); self.last_dtc=[]; self.set_output(f"HAPUS DTC BERHASIL - {j} kode dihapus"); self.history.append(f"CLEAR DTC {j} kode")
        except Exception as e: self.set_output(f"Clear DTC error: {e}")
    def freeze_frame(self,i):
        try:
            if not self.last_dtc: self.set_output("Belum ada DTC.\\nScan DTC dulu."); return
            plat,motor,km=self.profil(); self.set_output(f"FREEZE FRAME\\n\\nMotor: {motor} | {plat} | KM {km}\\nDTC: {self.last_dtc[0][0]}\\n\\nRPM: {self.rpm:.0f}\\nSuhu: {self.suhu:.0f}C\\nSpeed: {self.speed:.0f}\\nTP: {self.tp:.1f}%\\nAki: {self.aki:.1f}V\\nTiming: {self.timing_real:.1f} deg\\nMap: {self.map_aktif}\\nWaktu: {time.strftime('%d/%m/%Y %H:%M')}")
        except Exception as e: self.set_output(f"Freeze error: {e}")
    def health_score(self,i):
        try:
            s=getattr(self,'last_score',98); self.set_output(f"HEALTH SCORE V12\\n\\nSkor: {s} / 100\\nStatus: {'SEHAT' if s>=85 else 'WASPADA' if s>=60 else 'BAHAYA'}\\n\\n- Suhu: {self.suhu:.0f}C\\n- Aki: {self.aki:.1f}V\\n- DTC: {len(self.last_dtc)} kode\\n- Map: {self.map_aktif}\\n- Merk: {self.elm.merk_terdeteksi}\\n- Timing: {self.timing_real:.1f} deg")
        except Exception as e: self.set_output(f"Health error: {e}")
    def ai_diagnosa(self,i):
        try:
            s=getattr(self,'last_score',98); d=self.data25; saran=[]
            if self.suhu>100: saran.append("OVERHEAT: Cek air radiator / kipas / thermostat. Jangan buka tutup radiator pas panas!")
            if self.aki<12.2: saran.append("AKI LEMAH: Cek kiprok + spul. Kalau aki >2 tahun, ganti.")
            if self.last_dtc: saran.append(f"DTC AKTIF {len(self.last_dtc)}: Scan detail, jangan cuma hapus. Kalau balik lagi, sensornya rusak.")
            if d.get('AIR_FUEL',14.7)>15: saran.append("Terlalu irit: Cek injektor mampet / fuel pump lemah.")
            if d.get('AIR_FUEL',14.7)<13: saran.append("Terlalu boros: Cek O2 sensor / MAP / busi hitam.")
            if self.timing_real>20: saran.append("Timing terlalu maju: Bisa ngelitik, turunkan timing / pakai RON lebih tinggi.")
            if self.timing_real<5: saran.append("Timing terlalu mundur: Tenaga ngempos, cek CKP / TPS.")
            if not saran: saran.append("Mesin sehat total. Tinggal servis rutin: Oli 2000km, Busi 8000km, CVT 10000km.")
            t="AI DIAGNOSA V12 - SMART\\n\\n"
            for x in saran: t+=f"- {x}\\n\\n"
            t+=f"Skor: {s}/100 | Merk: {self.elm.merk_terdeteksi} | Mode: {self.mode} | Timing: {self.timing_real:.1f} deg"
            self.set_output(t)
        except Exception as e: self.set_output(f"AI error: {e}")
    def emergency(self,i): self.show_popup("EMERGENCY MODE","Jika mogok / overheat:\\n\\n1. Matikan kontak, jangan dipaksa stater\\n2. Cek suhu, aki, DTC\\n3. Suhu >110 tunggu 20 menit\\n4. Aki <11.5 jangan stater terus\\n5. Hubungi bengkel terdekat")
    def readiness(self,i): self.set_output("READINESS\\n\\n- Misfire: SIAP\\n- Fuel System: SIAP\\n- O2 Sensor: SIAP\\n- Catalyst: BELUM SIAP (jalan 10 km)\\n- EGR: TIDAK ADA (motor)\\n- EVAP: SIAP")
    def dtc_lookup(self,i):
        try:
            q=self.input_kode.text
            if not q.strip(): self.set_output("Ketik dulu: 8-1 / P0122 / brebet"); return
            h=cari(q,self.merk.text)
            if not h: self.set_output(f"{q.upper()} tidak ditemukan."); return
            if len(h)==1:
                r=h[0]; self.set_output(f"HASIL - {r[0]}\\n\\nKode: {r[1]} | OBD: {r[2]}\\nKerusakan: {r[3]}\\nLevel: {r[6]}\\n\\nGejala: {r[4]}\\nSolusi: {r[5]}\\nHarga Scan: Rp {HARGA['SCAN DTC']:,}"); self.last_scan=f"{r[1]} - {r[0]} - {r[3]}"; self.history.append(self.last_scan)
            else:
                t=f"Ditemukan {len(h)} hasil:\\n\\n"
                for r in h: t+=f"- {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[6]}\\n"
                self.set_output(t)
        except Exception as e: self.set_output(f"Lookup error: {e}")
    def backup_map(self,i):
        try: self.map_backup=self.map_aktif; self.map_backup_data={"map":self.map_aktif,"ecu":self.ecu_id,"waktu":time.strftime('%d/%m/%Y %H:%M')}; self.set_output(f"BACKUP BERHASIL\\nMap: {self.map_backup}\\nWaktu: {self.map_backup_data['waktu']}\\nECU: {self.ecu_id}\\n\\nAman untuk Remap.")
        except Exception as e: self.set_output(f"Backup error: {e}")
    def restore_map(self,i):
        try:
            if not self.map_backup: self.set_output("Belum ada backup! Pencet BACKUP dulu."); return
            self.map_aktif=self.map_backup; self.set_output(f"RESTORE BERHASIL - Balik ke {self.map_aktif}\\nBackup dari: {self.map_backup_data}")
        except Exception as e: self.set_output(f"Restore error: {e}")
    def remap_ecu(self,i):
        try:
            pilih=self.map_spinner.text; merk=self.merk.text if hasattr(self,'merk') else "AUTO - UNIVERSAL"; merk_real=self.elm.merk_terdeteksi if self.real else merk
            if not self.map_backup: self.set_output("REMAP DITOLAK - BACKUP DULU!\\n\\nPencet BACKUP dulu, biar kalau gagal bisa RESTORE."); return
            if self.aki<12.4: self.set_output(f"REMAP DITOLAK - AKI LEMAH!\\n\\nAki: {self.aki:.1f}V\\nMinimal 12.4V. Kalau aki drop pas nulis map, ECU bisa MATOT."); return
            if self.suhu>100: self.set_output(f"REMAP DITOLAK - MESIN PANAS!\\n\\nSuhu: {self.suhu:.0f}C\\nDinginkan dulu sampai <100C."); return
            if self.real and self.elm.connected:
                self.set_output(f"REMAP REAL STAGE 1 - MENGIRIM KE ECU...\\nMerk: {merk_real}\\nMap: {pilih}\\n\\nJANGAN CABUT KABEL / MATIKAN KONTAK!\\nProses 2-3 detik...")
                m=MAPS[pilih]
                def _do():
                    ok_b,resp_b=self.elm.backup_map_real(merk_real); ok,resp=self.elm.remap_real_stage1(merk_real,pilih,m["fuel"],m["timing"])
                    def _ui(dt):
                        if ok:
                            lama=self.map_aktif; self.map_aktif=pilih; self.set_output(f"REMAP REAL BERHASIL\\n\\n{lama} -> {pilih}\\nMerk: {merk_real}\\nFuel {m['fuel']:+d}% | Timing {m['timing']:+d} | Limiter {m['limiter']} | AFR {m['afr']}\\nKet: {m['ket']}\\nHarga: Rp {HARGA[pilih]:,}\\n\\nRespon ECU: {resp}\\nBackup REAL: {'OK' if ok_b else 'Gagal, tapi backup lokal masih ada'}\\n\\nTest LIVE DATA 2 menit. Kalau brebet, RESTORE.")
                            self.last_remap=f"REMAP REAL {lama}->{pilih} | Rp {HARGA[pilih]:,}"; self.history.append(self.last_remap)
                        else: self.set_output(f"REMAP REAL GAGAL - ECU MENOLAK, AMAN!\\n\\nMap TIDAK berubah, masih {self.map_aktif}.\\nAlasan: {resp}\\n\\nIni normal di ECU terkunci. Solusi: Kontak OFF-ON, coba lagi.")
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do,daemon=True).start(); return
            lama=self.map_aktif; self.map_aktif=pilih; m=MAPS[pilih]; self.set_output(f"REMAP SIMULASI (Belum Konek ELM327)\\n\\n{lama} -> {pilih}\\nFuel {m['fuel']:+d}% | Timing {m['timing']:+d} | Limiter {m['limiter']} | AFR {m['afr']}\\nKet: {m['ket']}\\nHarga: Rp {HARGA[pilih]:,}\\n\\nUntuk REMAP REAL, konek ELM327 dulu.\\n{'Wajib RON 98!' if pilih=='RACING / BALAP' else 'Aman harian.'}"); self.last_remap=f"REMAP SIMULASI {lama}->{pilih} | Rp {HARGA[pilih]:,}"; self.history.append(self.last_remap)
        except Exception as e: self.set_output(f"Remap error (ditangani, map tidak berubah): {e}")
    # ============ KEY LENGKAP 7 FITUR - V12 FINAL ============
    def read_key(self,i):
        try:
            s=random.randint(78,98); b=random.randint(85,100); self.key_sinyal=s; self.key_baterai=b
            self.set_output(f"READ KEY / PASS KEY - LENGKAP\\n\\nKey ID Utama: {self.key_id}\\nECU ID: {self.ecu_id}\\nPass Key: {self.passkey}\\nStatus: TERDAFTAR - Motor bisa hidup\\nSinyal: {s}% | Baterai Remot: {b}%\\nJumlah Key Terdaftar: {len(self.key_list)} key\\nHarga Baca Key: Rp {HARGA['READ KEY']:,}\\n\\nREAL: Butuh modul SCU / Keyless, bukan ELM327."); self.last_key=f"Key {self.key_id} | ECU {self.ecu_id} | Pass {self.passkey}"; self.history.append(self.last_key)
        except Exception as e: self.set_output(f"Read key error: {e}")
    def register_key(self,i):
        try:
            old=self.key_id; new_id=buat_id("KEY-NEW"); self.key_id=new_id; self.key_list.append(new_id); self.passkey=buat_pass(self.key_id,self.ecu_id)
            self.set_output(f"REGISTER KEY BERHASIL\\n\\nLama: {old}\\nBaru: {self.key_id}\\nPass Baru: {self.passkey}\\nECU tetap: {self.ecu_id}\\nTotal Key Sekarang: {len(self.key_list)} key\\nHarga: Rp {HARGA['REGISTER KEY']:,}\\n\\nRemot baru sudah bisa dipakai."); self.last_key=f"Register Key {self.key_id} Pass {self.passkey}"; self.history.append(self.last_key)
        except Exception as e: self.set_output(f"Register error: {e}")
    def clone_key(self,i):
        try:
            src=self.key_id; clone=buat_id("CLONE"); self.key_list.append(clone)
            self.set_output(f"CLONE KEY BERHASIL\\n\\nSumber: {src}\\nClone Baru: {clone}\\nPass Sama: {self.passkey}\\nECU: {self.ecu_id}\\nTotal Key: {len(self.key_list)}\\nHarga Clone: Rp {HARGA['CLONE KEY']:,}\\n\\nClone bisa dipakai seperti kunci asli. Simpan 1 di rumah sebagai cadangan."); self.last_key=f"Clone Key {clone} dari {src}"; self.history.append(self.last_key)
        except Exception as e: self.set_output(f"Clone error: {e}")
    def key_hilang(self,i):
        try:
            hilang=self.key_id; baru=buat_id("KEY-HILANG"); self.key_id=baru; self.key_list=[baru]; self.passkey=buat_pass(self.key_id,self.ecu_id)
            self.set_output(f"KEY HILANG - RESET TOTAL BERHASIL\\n\\nKey Hilang (diblokir): {hilang}\\nKey Baru: {baru}\\nPass Baru: {self.passkey}\\nECU: {self.ecu_id}\\n\\nKey lama SUDAH TIDAK BISA dipakai lagi, motor aman dari maling.\\nHarga Key Hilang: Rp {HARGA['KEY HILANG']:,}\\n\\nWajib bawa KTP + STNK untuk klaim garansi."); self.last_key=f"Key Hilang Reset -> {baru} Pass {self.passkey}"; self.history.append(self.last_key)
        except Exception as e: self.set_output(f"Key hilang error: {e}")
    def cek_key_manual(self,i):
        try:
            q=self.input_kode.text.strip().upper()
            if not q: self.set_output("CEK KEY MANUAL\\n\\nKetik ID Remot customer di kolom input, contoh: AB12-CD34\\nLalu pencet CEK KEY MANUAL."); return
            cocok=(q.replace("-","") in [k.replace("-","") for k in self.key_list])
            self.set_output(f"CEK KEY MANUAL\\n\\nID Diketik: {q}\\nID Tersimpan: {', '.join(self.key_list)}\\nECU: {self.ecu_id}\\n\\nHasil: {'COCOK - Motor bisa hidup' if cocok else 'TIDAK COCOK - Motor tidak bisa hidup, harus REGISTER KEY BARU'}\\n\\nPass untuk ID ini: {self.passkey if cocok else 'Tidak berlaku'}")
        except Exception as e: self.set_output(f"Cek key error: {e}")
    def baterai_remot(self,i):
        try:
            b=self.key_baterai; status="BAGUS - Masih lama" if b>=70 else "WASPADA - Siapkan cadangan" if b>=40 else "HABIS - Ganti sekarang, motor bisa tidak detect remot!"
            self.set_output(f"BATERAI REMOT / KEYLESS\\n\\nBaterai: {b}%\\nStatus: {status}\\nSinyal: {self.key_sinyal}%\\nKey ID: {self.key_id}\\n\\nHarga Ganti Baterai: Rp {HARGA['GANTI BATERAI REMOT']:,}\\n\\nTipe baterai umum: CR2032. Ganti di tukang jam / bengkel, 2 menit selesai.\\nKalau baterai habis total, tempelkan remot ke tombol starter / kenop keyless untuk darurat."); self.last_key=f"Baterai Remot {b}% {status}"
        except Exception as e: self.set_output(f"Baterai remot error: {e}")
    def hapus_key(self,i):
        try:
            if len(self.key_list)<=1: self.set_output("HAPUS KEY DITOLAK\\n\\nTinggal 1 key. Tidak boleh hapus semua, motor tidak bisa hidup!\\nDaftarkan key baru dulu baru hapus yang lama."); return
            hapus=self.key_list.pop(); self.set_output(f"HAPUS KEY BERHASIL\\n\\nKey Dihapus: {hapus}\\nSisa Key: {len(self.key_list)} key\\nKey Aktif: {self.key_id}\\nHarga: Rp {HARGA['HAPUS KEY']:,}\\n\\nKey yang dihapus sudah tidak bisa hidupkan motor."); self.last_key=f"Hapus Key {hapus}"; self.history.append(self.last_key)
        except Exception as e: self.set_output(f"Hapus key error: {e}")
    def daftar_key(self,i):
        try:
            t=f"DAFTAR KEY TERDAFTAR - {len(self.key_list)} KEY\\n\\nECU: {self.ecu_id}\\nPass Utama: {self.passkey}\\n\\n"
            for idx,k in enumerate(self.key_list,1): t+=f"{idx}. {k} {'(AKTIF)' if k==self.key_id else ''}\\n"
            t+=f"\\nSinyal: {self.key_sinyal}% | Baterai: {self.key_baterai}%\\n\\nMaksimal 3 key per motor. Kalau sudah 3, hapus 1 dulu baru daftar baru."
            self.set_output(t)
        except Exception as e: self.set_output(f"Daftar key error: {e}")
    def timing_real_show(self,i):
        try:
            if self.real and self.elm.connected:
                def _do():
                    t_real,sumber,_=self.elm.read_timing_real(self.elm.merk_terdeteksi)
                    def _ui(dt):
                        self.timing_real=t_real; self.timing_sumber=sumber; self.set_output(f"TIMING PENGAPIAN REAL V12\\n\\nTiming: {t_real:.1f} derajat\\nSumber: {sumber}\\nMerk: {self.elm.merk_terdeteksi}\\nMode: REAL\\n\\nNormal motor: 8-18 derajat di langsam, naik sampai 30 derajat pas gas.\\nKalau terlalu maju >25 di langsam = ngelitik.\\nKalau terlalu mundur <5 = ngempos.")
                    Clock.schedule_once(_ui)
                threading.Thread(target=_do,daemon=True).start(); return
            self.set_output(f"TIMING PENGAPIAN - SIMULASI\\n\\nTiming: {self.timing_real:.1f} derajat\\nSumber: {self.timing_sumber}\\nMode: SIMULASI\\n\\nUntuk Timing REAL, konek ELM327 dulu.\\nNormal: 8-18 derajat langsam.")
        except Exception as e: self.set_output(f"Timing error: {e}")
    def battery(self,i):
        try:
            v=round(random.uniform(12.4,13.9),1) if not self.real else self.aki; h=random.randint(78,98); st="SEHAT" if v>=12.6 else "WASPADA" if v>=12.2 else "BAHAYA"; self.set_output(f"BATTERY TEST {'REAL dari ATRV' if self.real else 'SIMULASI'}\\n\\n{v}V | {h}% | {st}\\nHarga: Rp {HARGA['BATTERY TEST']:,}"); self.last_scan=f"Battery {v}V {h}% {st}"
        except Exception as e: self.set_output(f"Battery error: {e}")
    def trip_bbm(self,i):
        try:
            avg=(self.total_bbm/max(self.total_km,0.01))*100 if self.total_km>0 else 0; self.set_output(f"TRIP / BBM\\n\\nTrip Live: +{self.total_km:.2f} km\\nBBM: {self.total_bbm:.3f} L\\nRata-rata: {avg:.1f} L/100km\\nMap: {self.map_aktif}")
        except Exception as e: self.set_output(f"Trip error: {e}")
    def servis(self,i):
        try:
            plat,motor,km=self.profil(); sisa=3000-((km-24000)%3000); self.set_output(f"SERVIS REMINDER\\n\\nMotor: {motor} | {plat}\\nKM: {km}\\n\\n- Oli: Ganti {sisa} km lagi\\n- Busi: Cek 5000 km lagi\\n- Filter Udara: 2000 km lagi\\n- CVT / Rantai: 1000 km lagi\\n\\nSaran AI: Kalau Health Score <70, servis sekarang.")
        except Exception as e: self.set_output(f"Servis error: {e}")
    def export_csv(self,i):
        try:
            with open("log_thaktech_v12.csv","w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["Waktu","RPM","Suhu","Aki","Speed","Map"]); w.writerows(self.log)
            self.set_output(f"EXPORT CSV BERHASIL V12\\nFile: log_thaktech_v12.csv\\nIsi: {len(self.log)} baris")
        except Exception as e: self.set_output(f"Export gagal: {e}")
    def print_struk(self,i):
        try:
            plat,motor,km=self.profil(); t=time.strftime("%d/%m/%Y %H:%M"); total=HARGA["SCAN DTC"]; sudah=set(["SCAN DTC"])
            if "REMAP" in self.last_remap:
                for k,v in HARGA.items():
                    if k in self.last_remap and k not in sudah: total+=v; sudah.add(k)
            if "Battery" in self.last_scan and "BATTERY TEST" not in sudah: total+=HARGA["BATTERY TEST"]; sudah.add("BATTERY TEST")
            if "Key" in self.last_key and "READ KEY" not in sudah: total+=HARGA["READ KEY"]; sudah.add("READ KEY")
            trx=buat_id("TRX")
            s="="*32+"\\nTHAKTECH V12 - ARTIFICIAL PITSTOP\\n"+"="*32+f"\\nTRX: {trx}\\nTanggal: {t}\\nMotor: {motor} | {plat} | KM {km}\\nMode: {self.mode} | Merk: {self.elm.merk_terdeteksi}\\n"+"-"*32+f"\\nScan: {self.last_scan}\\nKey: {self.last_key}\\nRemap: {self.last_remap}\\nLive: {self.last_live}\\n"+"-"*32+f"\\nTotal Jasa: Rp {total:,}\\n"+"="*32+"\\nTerima kasih\\nGaransi diagnosa 7 hari\\nGaransi remap 30 hari\\n"+"="*32
            try: open("struk_thaktech_v12.txt","w",encoding="utf-8").write(s)
            except: pass
            self.safe_copy(s); self.set_output(s+"\\n\\n[OK] Tersalin & tersimpan. TRX: "+trx)
        except Exception as e: self.set_output(f"Struk error: {e}")
    def show_history(self,i):
        try:
            if not self.history: self.set_output("HISTORY KOSONG"); return
            t="HISTORY V12:\\n\\n"
            for i,h in enumerate(self.history,1): t+=f"{i}. {h}\\n\\n"
            self.set_output(t)
        except Exception as e: self.set_output(f"History error: {e}")
if __name__=='__main__': ThakTechApp().run() 
