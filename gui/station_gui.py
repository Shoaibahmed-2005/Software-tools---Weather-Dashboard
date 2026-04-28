"""
station_gui.py — Experiment 10: Python GUI using Tkinter
Allows manual submission of sensor readings to the Flask server.
Run:  python gui/station_gui.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import urllib.error
import json

SERVER_URL = 'http://127.0.0.1:5000'


class WeatherStationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Station — Manual Input Console")
        self.root.geometry("520x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')

        self._setup_styles()
        self._build_header()
        self._build_form()
        self._build_status()
        self._fetch_stations()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel',     background='#1a1a2e', foreground='#e0e0e0',
                         font=('Segoe UI', 10))
        style.configure('Header.TLabel', background='#1a1a2e', foreground='#00d4ff',
                         font=('Segoe UI', 16, 'bold'))
        style.configure('Sub.TLabel', background='#1a1a2e', foreground='#888',
                         font=('Segoe UI', 9))
        style.configure('TEntry',     fieldbackground='#16213e', foreground='#ffffff',
                         insertcolor='#00d4ff', font=('Segoe UI', 11), padding=6)
        style.configure('TCombobox',  fieldbackground='#16213e', foreground='#ffffff',
                         font=('Segoe UI', 11))
        style.configure('Submit.TButton', font=('Segoe UI', 11, 'bold'),
                         foreground='#ffffff', background='#0f3460', padding=10)
        style.map('Submit.TButton', background=[('active', '#00d4ff')])
        style.configure('TFrame', background='#1a1a2e')

    def _build_header(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=20, pady=(20, 5))

        ttk.Label(header_frame, text="🌦 Weather Station", style='Header.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Manual Sensor Input Console  |  Exp 10 — Python GUI",
                  style='Sub.TLabel').pack(anchor='w')

        sep = tk.Frame(self.root, height=1, bg='#00d4ff')
        sep.pack(fill='x', padx=20, pady=8)

    def _make_field(self, parent, label, var, unit='', row=0):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=6)

        lbl_frame = ttk.Frame(frame)
        lbl_frame.pack(fill='x')
        ttk.Label(lbl_frame, text=label, font=('Segoe UI', 10, 'bold'),
                  background='#1a1a2e', foreground='#c0c0c0').pack(side='left')
        if unit:
            ttk.Label(lbl_frame, text=f'  ({unit})', style='Sub.TLabel').pack(side='left')

        entry = ttk.Entry(frame, textvariable=var, width=30)
        entry.pack(fill='x')
        return entry

    def _build_form(self):
        form = ttk.Frame(self.root)
        form.pack(fill='both', padx=25, pady=5)

        # Station selector
        ttk.Label(form, text="Station", font=('Segoe UI', 10, 'bold'),
                  background='#1a1a2e', foreground='#c0c0c0').pack(anchor='w', pady=(8, 2))
        self.station_var = tk.StringVar()
        self.station_combo = ttk.Combobox(form, textvariable=self.station_var,
                                          state='readonly', width=40)
        self.station_combo.pack(fill='x', pady=2)

        # Numeric inputs
        self.temp_var  = tk.StringVar(value='28.5')
        self.hum_var   = tk.StringVar(value='60.0')
        self.pres_var  = tk.StringVar(value='1013.25')
        self.wind_var  = tk.StringVar(value='12.0')

        self._make_field(form, 'Temperature',  self.temp_var,  '°C')
        self._make_field(form, 'Humidity',     self.hum_var,   '%')
        self._make_field(form, 'Pressure',     self.pres_var,  'hPa')
        self._make_field(form, 'Wind Speed',   self.wind_var,  'km/h')

        # Wind direction
        ttk.Label(form, text="Wind Direction", font=('Segoe UI', 10, 'bold'),
                  background='#1a1a2e', foreground='#c0c0c0').pack(anchor='w', pady=(8, 2))
        self.wind_dir_var = tk.StringVar(value='N')
        wind_dir_combo = ttk.Combobox(
            form, textvariable=self.wind_dir_var, width=15, state='readonly',
            values=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        )
        wind_dir_combo.pack(anchor='w')

        # Submit button
        sep = tk.Frame(self.root, height=1, bg='#333')
        sep.pack(fill='x', padx=20, pady=12)

        btn = tk.Button(
            self.root,
            text='  📡  Submit Reading to Server  ',
            command=self._submit,
            font=('Segoe UI', 12, 'bold'),
            bg='#0f3460', fg='#00d4ff',
            activebackground='#00d4ff', activeforeground='#1a1a2e',
            relief='flat', cursor='hand2', pady=10
        )
        btn.pack(padx=25, fill='x')

    def _build_status(self):
        self.status_var = tk.StringVar(value="Ready — fill in values and submit.")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            bg='#16213e', fg='#00d4ff',
            font=('Segoe UI', 9), anchor='w', padx=12, pady=6
        )
        status_bar.pack(fill='x', side='bottom')

    def _fetch_stations(self):
        """Fetch station list from server to populate dropdown."""
        try:
            req = urllib.request.urlopen(f'{SERVER_URL}/api/stations', timeout=3)
            data = json.loads(req.read())
            stations = data.get('stations', [])
            labels = [f"{s['id']} — {s['name']} ({s['location']})" for s in stations]
            self.station_combo['values'] = labels
            self._station_ids = {lbl: s['id'] for lbl, s in zip(labels, stations)}
            if labels:
                self.station_combo.current(0)
            self._set_status("✓ Connected to server. Stations loaded.", '#00d4ff')
        except Exception:
            self.station_combo['values'] = ['1 — Station Alpha (Main Campus)']
            self._station_ids = {'1 — Station Alpha (Main Campus)': 1}
            self.station_combo.current(0)
            self._set_status("⚠ Server not reachable — using default station.", '#ffaa00')

    def _get_station_id(self):
        selected = self.station_var.get()
        return self._station_ids.get(selected, 1)

    def _set_status(self, msg, color='#00d4ff'):
        self.status_var.set(msg)
        self.root.nametowidget(str(self.root.children['!label'])).config(fg=color)

    def _submit(self):
        """Validate and POST reading to Flask API."""
        errors = []

        def parse(var, label, lo, hi):
            try:
                v = float(var.get())
                if not lo <= v <= hi:
                    errors.append(f"{label}: must be {lo}–{hi}")
                return v
            except ValueError:
                errors.append(f"{label}: enter a valid number")
                return None

        temp  = parse(self.temp_var,  'Temperature', -50, 60)
        hum   = parse(self.hum_var,   'Humidity',    0,   100)
        pres  = parse(self.pres_var,  'Pressure',    870, 1085)
        wind  = parse(self.wind_var,  'Wind Speed',  0,   200)

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        payload = json.dumps({
            'station_id':    self._get_station_id(),
            'temperature':   temp,
            'humidity':      hum,
            'pressure':      pres,
            'wind_speed':    wind,
            'wind_direction': self.wind_dir_var.get()
        }).encode('utf-8')

        try:
            req = urllib.request.Request(
                f'{SERVER_URL}/api/submit',
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            resp = urllib.request.urlopen(req, timeout=5)
            result = json.loads(resp.read())
            if result.get('success'):
                self.status_var.set(f"✓ {result['message']}")
                messagebox.showinfo("Success", "Reading submitted to server!")
            else:
                messagebox.showerror("Server Error", str(result.get('errors', 'Unknown error')))
        except urllib.error.HTTPError as e:
            body = json.loads(e.read())
            messagebox.showerror("Validation Error", str(body.get('errors', e)))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot reach server.\n{e}")
            self.status_var.set("✗ Server not reachable.")


if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherStationGUI(root)
    root.mainloop()
