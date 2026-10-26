import customtkinter as ctk
import sqlite3, re, csv
from pathlib import Path
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG, PANEL, CYAN, GREEN, YELLOW, RED, MUTED, WHITE = (
    "#0B1020", "#111A2E", "#38D9F5", "#43E6A0", "#FFC857",
    "#FF647C", "#8EA1C0", "#F3F7FF"
)
DB_PATH = Path.home() / ".cyberops_simulator.db"

SAMPLE = [
    ("INFO","auth","Successful login for user 'maya' from 192.0.2.18"),
    ("WARN","auth","Failed login for user 'admin' from 198.51.100.23"),
    ("WARN","auth","Failed login for user 'admin' from 198.51.100.23"),
    ("WARN","auth","Failed login for user 'admin' from 198.51.100.23"),
    ("ERROR","auth","Failed login for user 'root' from 203.0.113.77"),
    ("INFO","network","Outbound connection established to 192.0.2.80:443"),
    ("WARN","network","Unusual outbound traffic volume detected for host WS-04"),
    ("INFO","system","Scheduled backup completed successfully"),
    ("WARN","system","Unexpected privilege change for account 'temp-user'"),
    ("ERROR","endpoint","Blocked execution of suspicious file: invoice_update.exe"),
    ("INFO","endpoint","Endpoint protection signatures updated"),
    ("WARN","auth","Failed login for user 'analyst' from 203.0.113.77"),
    ("INFO","network","DNS request for example.test"),
    ("ERROR","auth","Account 'service-account' locked after repeated failures"),
    ("WARN","system","New local administrator account created: 'support2'"),
]
CASES = [
    ("Repeated Login Failures","HIGH","Brute-force indicator",
     "Several failed authentication attempts target a privileged account from the same source.",
     "Multiple failed-login events for 'admin' from 198.51.100.23.",
     "Validate the account owner, review surrounding logs, and check rate-limiting or lockout controls."),
    ("Suspicious Executable Blocked","CRITICAL","Endpoint alert",
     "Endpoint protection blocked an executable with a suspicious filename.",
     "Blocked execution of suspicious file: invoice_update.exe",
     "Keep it quarantined, verify the alert in your endpoint tool, and follow incident-response procedures."),
    ("Unexpected Privilege Change","HIGH","Privilege monitoring",
     "An account's permissions may have changed unexpectedly.",
     "Unexpected privilege change for account 'temp-user'.",
     "Confirm authorization, inspect audit records, and revoke excess permissions if needed."),
    ("Unusual Outbound Traffic","MEDIUM","Network anomaly",
     "A workstation generated an unusual amount of outbound traffic.",
     "Unusual outbound traffic volume detected for host WS-04.",
     "Compare with the normal baseline and check approved applications before escalating."),
    ("New Administrator Account","HIGH","Account change",
     "A new local administrator account appeared in the system log.",
     "New local administrator account created: 'support2'.",
     "Verify the change request and account owner; follow policy if unauthorized."),
]

class CyberOps(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberOps | Security Operations Simulator")
        self.geometry("1150x760")
        self.minsize(950, 650)
        self.configure(fg_color=BG)
        self.db = sqlite3.connect(DB_PATH)
        self.db.execute("""CREATE TABLE IF NOT EXISTS case_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, severity TEXT, closed_at TEXT)""")
        self.db.commit()
        now = datetime.now()
        self.events = [{"time": (now-timedelta(minutes=(len(SAMPLE)-i)*7)).strftime("%Y-%m-%d %H:%M:%S"),
                        "level": level, "source": source, "message": message}
                       for i,(level,source,message) in enumerate(SAMPLE)]
        self.cases = [dict(id=i, title=x[0], severity=x[1], category=x[2], description=x[3],
                           evidence=x[4], action=x[5], status="OPEN") for i,x in enumerate(CASES)]
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color="#0E1629")
        self.sidebar.grid(row=0,column=0,sticky="nsew"); self.sidebar.grid_propagate(False)
        ctk.CTkLabel(self.sidebar,text="◈  CyberOps",text_color=CYAN,
                     font=ctk.CTkFont(size=23,weight="bold")).pack(anchor="w",padx=20,pady=(28,4))
        ctk.CTkLabel(self.sidebar,text="TRAINING SIMULATOR",text_color=MUTED,
                     font=ctk.CTkFont(size=10,weight="bold")).pack(anchor="w",padx=22,pady=(0,28))
        self.nav={}
        for label,key in [("⌂  Overview","home"),("▤  Event Logs","logs"),("⚠  Incident Lab","cases"),("◷  Case History","history")]:
            b=ctk.CTkButton(self.sidebar,text=label,anchor="w",height=42,fg_color="transparent",
                hover_color="#17233B",text_color="#C5D2E8",command=lambda k=key:self.show(k))
            b.pack(fill="x",padx=12,pady=4); self.nav[key]=b
        ctk.CTkLabel(self.sidebar,text="● SIMULATION MODE",text_color=GREEN,
            font=ctk.CTkFont(size=10,weight="bold")).pack(side="bottom",anchor="w",padx=20,pady=(0,7))
        ctk.CTkLabel(self.sidebar,text="Fictional data only.\nNo real systems are scanned.",
            text_color=MUTED,font=ctk.CTkFont(size=10),justify="left").pack(side="bottom",anchor="w",padx=20,pady=(0,22))
        self.main=ctk.CTkFrame(self,fg_color=BG,corner_radius=0)
        self.main.grid(row=0,column=1,sticky="nsew"); self.main.grid_columnconfigure(0,weight=1); self.main.grid_rowconfigure(1,weight=1)
        top=ctk.CTkFrame(self.main,fg_color=BG); top.grid(row=0,column=0,sticky="ew",padx=25,pady=(22,12)); top.grid_columnconfigure(0,weight=1)
        self.heading=ctk.CTkLabel(top,text="Security Overview",text_color=WHITE,font=ctk.CTkFont(size=25,weight="bold"))
        self.heading.grid(row=0,column=0,sticky="w")
        ctk.CTkLabel(top,text=datetime.now().strftime("%d %b %Y  •  %H:%M"),text_color=MUTED).grid(row=0,column=1,sticky="e")
        self.page=ctk.CTkScrollableFrame(self.main,fg_color=BG,corner_radius=0)
        self.page.grid(row=1,column=0,sticky="nsew",padx=20,pady=(0,15))
        self.show("home")
        self.protocol("WM_DELETE_WINDOW",self.close)

    def clear(self):
        for w in self.page.winfo_children(): w.destroy()

    def show(self,key):
        self.key=key; self.clear()
        titles={"home":"Security Overview","logs":"Event Log Explorer","cases":"Incident Investigation Lab","history":"Case History"}
        self.heading.configure(text=titles[key])
        for k,b in self.nav.items():
            b.configure(fg_color="#17233B" if k==key else "transparent",text_color=CYAN if k==key else "#C5D2E8")
        if key=="home": self.home()
        elif key=="logs": self.logs()
        elif key=="cases": self.case_list()
        else: self.history()

    def card(self,parent,title,value,note,color=CYAN):
        f=ctk.CTkFrame(parent,fg_color=PANEL,corner_radius=13,border_width=1,border_color="#1D2A44")
        ctk.CTkLabel(f,text=title.upper(),text_color=MUTED,font=ctk.CTkFont(size=10,weight="bold")).pack(anchor="w",padx=15,pady=(14,4))
        ctk.CTkLabel(f,text=str(value),text_color=color,font=ctk.CTkFont(size=27,weight="bold")).pack(anchor="w",padx=15)
        ctk.CTkLabel(f,text=note,text_color="#A8B7CF",font=ctk.CTkFont(size=10)).pack(anchor="w",padx=15,pady=(2,14))
        return f

    def home(self):
        intro=ctk.CTkFrame(self.page,fg_color=PANEL,corner_radius=14); intro.pack(fill="x",padx=3,pady=(3,15))
        ctk.CTkLabel(intro,text="Your training SOC, at a glance.",text_color=WHITE,font=ctk.CTkFont(size=19,weight="bold")).pack(anchor="w",padx=20,pady=(18,4))
        ctk.CTkLabel(intro,text="Review fictional telemetry, investigate alerts, and practice incident triage.",text_color=MUTED).pack(anchor="w",padx=20,pady=(0,18))
        stats=ctk.CTkFrame(self.page,fg_color="transparent"); stats.pack(fill="x",padx=3,pady=(0,15))
        for i in range(4): stats.grid_columnconfigure(i,weight=1)
        opened=sum(x["status"]=="OPEN" for x in self.cases)
        priority=sum(x["status"]=="OPEN" and x["severity"] in ("HIGH","CRITICAL") for x in self.cases)
        closed=self.db.execute("SELECT COUNT(*) FROM case_history").fetchone()[0]
        for i,args in enumerate([("Events analyzed",len(self.events),"Sample telemetry",CYAN),("Open incidents",opened,"Awaiting investigation",YELLOW),("Priority alerts",priority,"High / critical",RED),("Cases closed",closed,"Saved locally",GREEN)]):
            self.card(stats,*args).grid(row=0,column=i,sticky="ew",padx=(0 if i==0 else 4,0 if i==3 else 4))
        ctk.CTkLabel(self.page,text="Quick actions",text_color=WHITE,font=ctk.CTkFont(size=16,weight="bold")).pack(anchor="w",padx=4,pady=(5,9))
        row=ctk.CTkFrame(self.page,fg_color="transparent"); row.pack(fill="x",padx=3)
        for i in range(3): row.grid_columnconfigure(i,weight=1)
        for i,(title,desc,button,key) in enumerate([
            ("Review event logs","Search and filter sample security events.","Open logs →","logs"),
            ("Investigate an alert","Review evidence and suggested next steps.","Open incident lab →","cases"),
            ("Run log analysis","Detect repeated failed-login patterns.","Analyze events →","analyze")]):
            f=ctk.CTkFrame(row,fg_color=PANEL,corner_radius=12); f.grid(row=0,column=i,sticky="nsew",padx=4)
            ctk.CTkLabel(f,text=title,text_color=WHITE,font=ctk.CTkFont(size=13,weight="bold")).pack(anchor="w",padx=13,pady=(14,5))
            ctk.CTkLabel(f,text=desc,text_color=MUTED,wraplength=205,justify="left").pack(anchor="w",padx=13)
            ctk.CTkButton(f,text=button,fg_color="#17334B",hover_color="#214B68",text_color=CYAN,
                          command=self.analyze if key=="analyze" else lambda k=key:self.show(k)).pack(anchor="w",padx=13,pady=13)
        note=ctk.CTkFrame(self.page,fg_color="#14263A",corner_radius=10); note.pack(fill="x",padx=3,pady=16)
        ctk.CTkLabel(note,text="LEARNING NOTE",text_color=CYAN,font=ctk.CTkFont(size=11,weight="bold")).pack(anchor="w",padx=14,pady=(12,3))
        ctk.CTkLabel(note,text="Alerts are clues, not proof. Confirm context before taking action. This app uses fictional data and does not connect to real systems.",text_color="#B8C8DD",wraplength=850,justify="left").pack(anchor="w",padx=14,pady=(0,12))

    def logs(self):
        bar=ctk.CTkFrame(self.page,fg_color=PANEL,corner_radius=10); bar.pack(fill="x",padx=3,pady=(3,10))
        self.query=ctk.CTkEntry(bar,placeholder_text="Search event, source, or level…",width=300); self.query.pack(side="left",padx=10,pady=10)
        self.level=ctk.CTkOptionMenu(bar,values=["ALL","INFO","WARN","ERROR"],width=100); self.level.pack(side="left",padx=5)
        ctk.CTkButton(bar,text="Apply",command=self.render_logs,fg_color="#17334B",text_color=CYAN).pack(side="left",padx=5)
        ctk.CTkButton(bar,text="Export CSV",command=self.export,fg_color="#1B3A32",text_color=GREEN).pack(side="right",padx=10)
        self.log_frame=ctk.CTkFrame(self.page,fg_color=PANEL,corner_radius=10); self.log_frame.pack(fill="x",padx=3)
        self.render_logs()

    def render_logs(self):
        if not hasattr(self,"log_frame") or not self.log_frame.winfo_exists(): return
        for w in self.log_frame.winfo_children(): w.destroy()
        q=self.query.get().lower().strip(); level=self.level.get(); shown=0
        for e in self.events:
            if q and q not in " ".join(e.values()).lower(): continue
            if level!="ALL" and e["level"]!=level: continue
            row=ctk.CTkFrame(self.log_frame,fg_color="transparent"); row.pack(fill="x",padx=8,pady=3)
            color={"INFO":CYAN,"WARN":YELLOW,"ERROR":RED}[e["level"]]
            ctk.CTkLabel(row,text=e["time"],width=145,anchor="w",text_color=MUTED,font=ctk.CTkFont(size=10)).pack(side="left",padx=5)
            ctk.CTkLabel(row,text=e["level"],width=55,anchor="w",text_color=color,font=ctk.CTkFont(size=10,weight="bold")).pack(side="left",padx=5)
            ctk.CTkLabel(row,text=e["source"],width=70,anchor="w",text_color="#B6C6DE").pack(side="left",padx=5)
            ctk.CTkLabel(row,text=e["message"],anchor="w",justify="left",wraplength=480,text_color=WHITE).pack(side="left",fill="x",expand=True,padx=5)
            shown+=1
        ctk.CTkLabel(self.log_frame,text=f"{shown} event(s) shown • fictional sample data",text_color=MUTED).pack(anchor="w",padx=14,pady=10)

    def analyze(self):
        pattern=re.compile(r"Failed login for user '([^']+)' from ((?:\d{1,3}\.){3}\d{1,3})",re.I)
        found={}
        for e in self.events:
            m=pattern.search(e["message"])
            if m:
                user,ip=m.groups(); found.setdefault(ip,{"count":0,"users":set()})
                found[ip]["count"]+=1; found[ip]["users"].add(user)
        lines=[f"{ip}: {v['count']} failed attempts across {len(v['users'])} account(s)" for ip,v in found.items() if v["count"]>=3]
        messagebox.showinfo("Demo analysis","Potential repeated-login pattern(s):\n\n"+"\n".join(lines)+
            "\n\nThis is a training heuristic, not proof of an attack." if lines else "No repeated-login pattern met the demo threshold.")
        if self.key=="home": self.show("logs")

    def export(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV files","*.csv")],initialfile="cyberops_sample_logs.csv")
        if not path:return
        try:
            with open(path,"w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=["time","level","source","message"]); w.writeheader(); w.writerows(self.events)
            messagebox.showinfo("Export complete",f"Saved sample logs to:\n{path}")
        except OSError as exc: messagebox.showerror("Export failed",str(exc))

    def case_list(self):
        ctk.CTkLabel(self.page,text="Review evidence and suggested actions. Case resolution only updates this simulator's local history.",text_color=MUTED,wraplength=850,justify="left").pack(anchor="w",padx=4,pady=(3,12))
        for case in self.cases:
            f=ctk.CTkFrame(self.page,fg_color=PANEL,corner_radius=12,border_width=1,border_color="#1D2A44"); f.pack(fill="x",padx=3,pady=6)
            color=RED if case["severity"] in ("HIGH","CRITICAL") else YELLOW
            top=ctk.CTkFrame(f,fg_color="transparent"); top.pack(fill="x",padx=14,pady=(12,2))
            ctk.CTkLabel(top,text=case["severity"],text_color=color,font=ctk.CTkFont(size=10,weight="bold")).pack(side="left")
            ctk.CTkLabel(top,text=case["category"],text_color=MUTED).pack(side="left",padx=10)
            ctk.CTkLabel(top,text=case["status"],text_color=GREEN if case["status"]=="CLOSED" else YELLOW).pack(side="right")
            ctk.CTkLabel(f,text=case["title"],text_color=WHITE,font=ctk.CTkFont(size=15,weight="bold")).pack(anchor="w",padx=14,pady=3)
            ctk.CTkLabel(f,text=case["description"],text_color="#B8C8DD",wraplength=830,justify="left").pack(anchor="w",padx=14)
            ev=ctk.CTkFrame(f,fg_color="#0B1425",corner_radius=7); ev.pack(fill="x",padx=14,pady=8)
            ctk.CTkLabel(ev,text="EVIDENCE",text_color=CYAN,font=ctk.CTkFont(size=9,weight="bold")).pack(anchor="w",padx=9,pady=(7,2))
            ctk.CTkLabel(ev,text=case["evidence"],text_color="#C9D6E9",wraplength=810,justify="left").pack(anchor="w",padx=9,pady=(0,7))
            ctk.CTkLabel(f,text="Suggested next step: "+case["action"],text_color=MUTED,wraplength=830,justify="left").pack(anchor="w",padx=14,pady=(0,9))
            buttons=ctk.CTkFrame(f,fg_color="transparent"); buttons.pack(fill="x",padx=14,pady=(0,12))
            ctk.CTkButton(buttons,text="Response checklist",height=30,fg_color="#17334B",text_color=CYAN,
                          command=lambda x=case:self.checklist(x)).pack(side="left")
            if case["status"]=="OPEN":
                ctk.CTkButton(buttons,text="Mark resolved",height=30,fg_color="#1B3A32",text_color=GREEN,
                    command=lambda x=case:self.resolve(x)).pack(side="right")

    def checklist(self,case):
        win=ctk.CTkToplevel(self); win.title("Response checklist"); win.geometry("500x390"); win.configure(fg_color=BG); win.transient(self)
        ctk.CTkLabel(win,text=case["title"],text_color=WHITE,font=ctk.CTkFont(size=19,weight="bold"),wraplength=440).pack(anchor="w",padx=22,pady=(22,8))
        ctk.CTkLabel(win,text="Training checklist — follow your organization's procedures.",text_color=MUTED,wraplength=440).pack(anchor="w",padx=22,pady=(0,12))
        for text in ["Confirm alert source and timestamp.","Preserve relevant logs and evidence.","Check whether activity was authorized.","Document findings and escalation decisions.","Follow approved response procedures."]:
            ctk.CTkCheckBox(win,text=text,text_color="#D4DFF0",fg_color="#147D91",border_color="#526783").pack(anchor="w",padx=24,pady=8)
        ctk.CTkButton(win,text="Close",command=win.destroy,fg_color="#17334B",text_color=CYAN).pack(anchor="e",padx=22,pady=18)

    def resolve(self,case):
        if not messagebox.askyesno("Resolve training case",f"Mark '{case['title']}' resolved in this simulation?"): return
        case["status"]="CLOSED"
        self.db.execute("INSERT INTO case_history(title,severity,closed_at) VALUES(?,?,?)",(case["title"],case["severity"],datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.db.commit(); self.show("cases")

    def history(self):
        bar=ctk.CTkFrame(self.page,fg_color="transparent"); bar.pack(fill="x",padx=3,pady=(3,10))
        ctk.CTkLabel(bar,text="Resolved cases saved locally",text_color=WHITE,font=ctk.CTkFont(size=16,weight="bold")).pack(side="left")
        ctk.CTkButton(bar,text="Clear history",fg_color="#442433",text_color="#FFB3C0",command=self.clear_history).pack(side="right")
        f=ctk.CTkFrame(self.page,fg_color=PANEL,corner_radius=10); f.pack(fill="x",padx=3)
        rows=self.db.execute("SELECT id,title,severity,closed_at FROM case_history ORDER BY id DESC").fetchall()
        if not rows:
            ctk.CTkLabel(f,text="No resolved cases yet. Investigate an alert in Incident Lab.",text_color=MUTED).pack(anchor="w",padx=16,pady=22)
        for rid,title,sev,closed in rows:
            line=ctk.CTkFrame(f,fg_color="transparent"); line.pack(fill="x",padx=12,pady=6)
            ctk.CTkLabel(line,text=f"#{rid}",width=40,text_color=MUTED).pack(side="left")
            ctk.CTkLabel(line,text=title,text_color=WHITE,anchor="w").pack(side="left",fill="x",expand=True,padx=5)
            ctk.CTkLabel(line,text=sev,width=80,text_color=RED if sev in ("HIGH","CRITICAL") else YELLOW).pack(side="left")
            ctk.CTkLabel(line,text=closed,text_color=MUTED).pack(side="right")

    def clear_history(self):
        if messagebox.askyesno("Clear history","Delete all locally saved case-history entries?"):
            self.db.execute("DELETE FROM case_history"); self.db.commit(); self.show("history")

    def close(self):
        self.db.close(); self.destroy()

if __name__=="__main__":
    CyberOps().mainloop()
