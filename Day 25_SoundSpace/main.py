import os, random, sqlite3, time
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pygame

DB = Path.home() / '.soundspace_history.db'
EXTS = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}
BG, PANEL, ACCENT = '#0B1020', '#151D30', '#8B5CF6'

class SoundSpace(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('SoundSpace — Desktop Music Player')
        self.geometry('1050x700'); self.minsize(850, 580); self.configure(fg_color=BG)
        pygame.mixer.init()
        self.db = sqlite3.connect(DB)
        self.db.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, path TEXT, played_at TEXT)')
        self.db.commit()
        self.library=[]; self.playlists={'My Library': self.library}; self.current_playlist='My Library'
        self.index=-1; self.playing=False; self.paused=False; self.shuffle=False; self.repeat='off'; self.started=0; self.duration=0
        self._ui(); self._refresh(); self.after(150, self._tick); self.protocol('WM_DELETE_WINDOW', self._close)

    def _ui(self):
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        side=ctk.CTkFrame(self, width=205, corner_radius=0, fg_color='#0E1425'); side.grid(row=0,column=0,sticky='nsew'); side.grid_propagate(False)
        ctk.CTkLabel(side,text='♫ SoundSpace',font=ctk.CTkFont(size=24,weight='bold')).pack(anchor='w',padx=20,pady=(28,4))
        ctk.CTkLabel(side,text='YOUR MUSIC, YOUR SPACE',text_color='#9AA6C0',font=ctk.CTkFont(size=10,weight='bold')).pack(anchor='w',padx=22,pady=(0,25))
        for label,cmd in [('♫  Library',self._library_page),('▤  Playlists',self._playlists_page),('◷  Listening History',self._history_page)]:
            ctk.CTkButton(side,text=label,anchor='w',height=40,fg_color='transparent',hover_color='#26324D',command=cmd).pack(fill='x',padx=12,pady=4)
        ctk.CTkFrame(side,height=2,fg_color='#26324D').pack(fill='x',padx=18,pady=18)
        ctk.CTkButton(side,text='＋  Add music',command=self._add,fg_color=ACCENT,hover_color='#7546D8',height=40).pack(fill='x',padx=14,pady=5)
        ctk.CTkButton(side,text='＋  New playlist',command=self._new_playlist,fg_color='#1A2338',height=40).pack(fill='x',padx=14,pady=5)
        ctk.CTkLabel(side,text='Local playback • No account needed',text_color='#65718C',wraplength=165,justify='left').pack(side='bottom',anchor='w',padx=20,pady=22)
        main=ctk.CTkFrame(self,fg_color=BG,corner_radius=0); main.grid(row=0,column=1,sticky='nsew'); main.grid_columnconfigure(0,weight=1); main.grid_rowconfigure(2,weight=1)
        head=ctk.CTkFrame(main,fg_color=BG); head.grid(row=0,column=0,sticky='ew',padx=25,pady=(22,13)); head.grid_columnconfigure(0,weight=1)
        self.heading=ctk.CTkLabel(head,text='Your Library',font=ctk.CTkFont(size=27,weight='bold')); self.heading.grid(row=0,column=0,sticky='w')
        self.search=tk.StringVar(); ctk.CTkEntry(head,textvariable=self.search,placeholder_text='Search tracks…',width=230).grid(row=0,column=1); self.search.trace_add('write',lambda *_:self._refresh())
        hero=ctk.CTkFrame(main,fg_color=PANEL,corner_radius=16); hero.grid(row=1,column=0,sticky='ew',padx=25,pady=(0,14)); hero.grid_columnconfigure(0,weight=1)
        info=ctk.CTkFrame(hero,fg_color='transparent'); info.grid(row=0,column=0,sticky='ew',padx=20,pady=17)
        ctk.CTkLabel(info,text='NOW PLAYING',text_color='#B9A4FF',font=ctk.CTkFont(size=10,weight='bold')).pack(anchor='w')
        self.track_label=ctk.CTkLabel(info,text='Choose a track to begin',font=ctk.CTkFont(size=21,weight='bold'),anchor='w'); self.track_label.pack(fill='x',pady=(6,2))
        self.sub_label=ctk.CTkLabel(info,text='Your next favorite is one click away',text_color='#9AA6C0',anchor='w'); self.sub_label.pack(fill='x')
        self.canvas=tk.Canvas(hero,width=210,height=82,bg=PANEL,highlightthickness=0); self.canvas.grid(row=0,column=1,padx=18,pady=12)
        area=ctk.CTkFrame(main,fg_color=BG); area.grid(row=2,column=0,sticky='nsew',padx=25); area.grid_columnconfigure(0,weight=1); area.grid_rowconfigure(1,weight=1)
        self.section=ctk.CTkLabel(area,text='TRACKS',text_color='#9AA6C0',font=ctk.CTkFont(size=11,weight='bold')); self.section.grid(row=0,column=0,sticky='w',pady=(0,7))
        self.list=ctk.CTkScrollableFrame(area,fg_color=PANEL,corner_radius=13); self.list.grid(row=1,column=0,sticky='nsew'); self.list.grid_columnconfigure(1,weight=1)
        player=ctk.CTkFrame(main,fg_color='#11182A',corner_radius=0); player.grid(row=3,column=0,sticky='ew',pady=(13,0)); player.grid_columnconfigure(1,weight=1)
        self.progress=ctk.CTkProgressBar(player,height=4,progress_color=ACCENT); self.progress.set(0); self.progress.grid(row=0,column=0,columnspan=3,sticky='ew',pady=(0,10))
        self.elapsed=ctk.CTkLabel(player,text='0:00',width=48,text_color='#9AA6C0'); self.elapsed.grid(row=1,column=0,padx=(12,3),pady=(0,12))
        controls=ctk.CTkFrame(player,fg_color='transparent'); controls.grid(row=1,column=1,pady=(0,10))
        self.shuf=ctk.CTkButton(controls,text='⤨',width=34,command=self._shuffle,fg_color='transparent',text_color='#9AA6C0'); self.shuf.grid(row=0,column=0,padx=2)
        ctk.CTkButton(controls,text='|◀',width=42,command=self._previous,fg_color='#1A2338').grid(row=0,column=1,padx=3)
        self.play_btn=ctk.CTkButton(controls,text='▶',width=48,height=38,command=self._toggle,fg_color=ACCENT,hover_color='#7546D8'); self.play_btn.grid(row=0,column=2,padx=4)
        ctk.CTkButton(controls,text='▶|',width=42,command=self._next,fg_color='#1A2338').grid(row=0,column=3,padx=3)
        self.rep=ctk.CTkButton(controls,text='↻',width=40,command=self._repeat,fg_color='transparent',text_color='#9AA6C0'); self.rep.grid(row=0,column=4,padx=2)
        self.total=ctk.CTkLabel(player,text='0:00',width=48,text_color='#9AA6C0'); self.total.grid(row=1,column=2,padx=(3,12),pady=(0,12))

    def _add(self):
        paths=filedialog.askopenfilenames(title='Choose audio files',filetypes=[('Audio files','*.mp3 *.wav *.ogg *.flac *.m4a'),('All files','*.*')])
        added=0
        for p in paths:
            if Path(p).suffix.lower() in EXTS and p not in self.library: self.library.append(p); added+=1
        self.current_playlist='My Library'; self._library_page(); self._status(f'Added {added} track(s).')

    def _new_playlist(self):
        name=ctk.CTkInputDialog(text='Enter a playlist name:',title='New playlist').get_input()
        if name and name.strip() and name.strip() not in self.playlists:
            self.playlists[name.strip()]=[]; self._playlists_page()
        elif name: messagebox.showinfo('SoundSpace','Please choose a unique playlist name.')

    def _playlists_page(self):
        self.heading.configure(text='Your Playlists'); self.section.configure(text='PLAYLISTS'); self._clear()
        for name,tracks in self.playlists.items():
            row=ctk.CTkFrame(self.list,fg_color='#1A2338',corner_radius=9); row.pack(fill='x',padx=6,pady=4)
            ctk.CTkLabel(row,text='▤  '+name,font=ctk.CTkFont(size=14,weight='bold')).pack(side='left',padx=12,pady=12)
            ctk.CTkLabel(row,text=f'{len(tracks)} tracks',text_color='#9AA6C0').pack(side='left',padx=6)
            ctk.CTkButton(row,text='Open',width=65,command=lambda n=name:self._open_playlist(n)).pack(side='right',padx=8,pady=7)
            if name!='My Library': ctk.CTkButton(row,text='+ Add',width=65,command=lambda n=name:self._add_to(n)).pack(side='right',padx=2,pady=7)

    def _add_to(self,name):
        for p in filedialog.askopenfilenames(title='Add tracks',filetypes=[('Audio files','*.mp3 *.wav *.ogg *.flac *.m4a')]):
            if Path(p).suffix.lower() in EXTS and p not in self.playlists[name]: self.playlists[name].append(p)
        self._playlists_page()

    def _open_playlist(self,name): self.current_playlist=name; self.heading.configure(text=name); self._refresh()
    def _library_page(self): self.current_playlist='My Library'; self.heading.configure(text='Your Library'); self.section.configure(text='TRACKS'); self._refresh()

    def _refresh(self):
        if not hasattr(self,'list') or self.heading.cget('text')=='Listening History' or self.heading.cget('text')=='Your Playlists': return
        self._clear(); tracks=self.playlists.get(self.current_playlist,self.library); query=self.search.get().lower().strip()
        visible=[(i,p) for i,p in enumerate(tracks) if query in Path(p).stem.lower() and os.path.isfile(p)]
        if not visible:
            ctk.CTkLabel(self.list,text='No tracks yet. Click “Add music” to import local audio.',text_color='#9AA6C0').pack(pady=35); return
        for number,(i,p) in enumerate(visible,1):
            row=ctk.CTkFrame(self.list,fg_color='#222344' if i==self.index and self.playing else 'transparent',corner_radius=8); row.pack(fill='x',padx=5,pady=2)
            ctk.CTkLabel(row,text=f'{number:02d}',width=32,text_color='#B9A4FF').pack(side='left',padx=6,pady=9)
            labels=ctk.CTkFrame(row,fg_color='transparent'); labels.pack(side='left',fill='x',expand=True,padx=4)
            ctk.CTkLabel(labels,text=Path(p).stem,anchor='w',font=ctk.CTkFont(size=13,weight='bold')).pack(fill='x')
            ctk.CTkLabel(labels,text=Path(p).suffix[1:].upper()+' • Local file',anchor='w',text_color='#9AA6C0',font=ctk.CTkFont(size=10)).pack(fill='x')
            ctk.CTkButton(row,text='▶ Play',width=75,height=30,command=lambda idx=i:self._play(idx)).pack(side='right',padx=8,pady=7)

    def _clear(self):
        for w in self.list.winfo_children(): w.destroy()

    def _play(self,index):
        tracks=self.playlists.get(self.current_playlist,self.library)
        if not tracks:return
        path=tracks[index]
        if not os.path.isfile(path): messagebox.showwarning('Missing file',f'File not found:\n{path}'); return
        try: pygame.mixer.music.stop(); pygame.mixer.music.load(path); pygame.mixer.music.play()
        except pygame.error as e:
            messagebox.showerror('Playback error',f'Could not play this file:\n{e}\n\nTry MP3, WAV, or OGG.'); return
        self.index=index; self.playing=True; self.paused=False; self.started=time.monotonic(); self.duration=self._duration(path)
        self.track_label.configure(text=Path(path).stem); self.sub_label.configure(text=f'{Path(path).suffix[1:].upper()} • {self.current_playlist}')
        self.play_btn.configure(text='Ⅱ'); self.total.configure(text=self._fmt(self.duration)); self.progress.set(0)
        self.db.execute('INSERT INTO history(path,played_at) VALUES (?,?)',(path,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))); self.db.commit()
        self._refresh()

    @staticmethod
    def _duration(path):
        try:
            from mutagen import File
            a=File(path); return int(a.info.length) if a and a.info else 0
        except Exception:return 0
    @staticmethod
    def _fmt(n): n=max(0,int(n)); return f'{n//60}:{n%60:02d}'
    def _toggle(self):
        if self.playing and not self.paused: pygame.mixer.music.pause(); self.paused=True; self.play_btn.configure(text='▶')
        elif self.paused: pygame.mixer.music.unpause(); self.paused=False; self.play_btn.configure(text='Ⅱ')
        elif self.playlists.get(self.current_playlist): self._play(self.index if self.index>=0 else 0)
        else:self._add()
    def _next(self):
        tracks=self.playlists.get(self.current_playlist,[])
        if not tracks:return
        if self.shuffle and len(tracks)>1: i=random.choice([x for x in range(len(tracks)) if x!=self.index])
        else:
            i=self.index+1
            if i>=len(tracks):
                if self.repeat=='all':i=0
                else: pygame.mixer.music.stop(); self.playing=False; self.play_btn.configure(text='▶'); return
        self._play(i)
    def _previous(self):
        tracks=self.playlists.get(self.current_playlist,[])
        if tracks:self._play(max(0,self.index-1))
    def _shuffle(self):
        self.shuffle=not self.shuffle; self.shuf.configure(text_color=ACCENT if self.shuffle else '#9AA6C0')
    def _repeat(self):
        self.repeat={'off':'all','all':'one','one':'off'}[self.repeat]; self.rep.configure(text={'off':'↻','all':'↻ all','one':'↻ 1'}[self.repeat],text_color=ACCENT if self.repeat!='off' else '#9AA6C0')
    def _history_page(self):
        self.heading.configure(text='Listening History'); self.section.configure(text='RECENTLY PLAYED'); self._clear()
        rows=self.db.execute('SELECT path,played_at FROM history ORDER BY id DESC LIMIT 100').fetchall()
        if not rows: ctk.CTkLabel(self.list,text='Your listening history will appear here.',text_color='#9AA6C0').pack(pady=35); return
        for path,stamp in rows:
            row=ctk.CTkFrame(self.list,fg_color='#1A2338',corner_radius=8); row.pack(fill='x',padx=5,pady=3)
            ctk.CTkLabel(row,text='♫',width=28,text_color='#B9A4FF').pack(side='left',padx=7,pady=10)
            ctk.CTkLabel(row,text=Path(path).stem,anchor='w').pack(side='left',fill='x',expand=True)
            ctk.CTkLabel(row,text=stamp,text_color='#9AA6C0',font=ctk.CTkFont(size=10)).pack(side='right',padx=8)
            if os.path.isfile(path): ctk.CTkButton(row,text='Play',width=50,command=lambda p=path:self._play_history(p)).pack(side='right',padx=3)
    def _play_history(self,path):
        if path not in self.library:self.library.append(path)
        self.current_playlist='My Library'; self._play(self.library.index(path)); self._library_page()
    def _tick(self):
        if not self.winfo_exists():return
        if self.playing and not self.paused:
            elapsed=int(time.monotonic()-self.started); self.elapsed.configure(text=self._fmt(elapsed))
            if self.duration:
                self.progress.set(min(1,elapsed/self.duration))
                if elapsed>=self.duration:
                    if self.repeat=='one':self._play(self.index)
                    else:self._next()
        self.canvas.delete('all'); w=max(1,self.canvas.winfo_width()); h=max(1,self.canvas.winfo_height())
        for i in range(23):
            bh=(8+random.randint(4,45)) if self.playing and not self.paused else 7+(i%4)*3
            x=7+i*9; y=(h-bh)/2; self.canvas.create_rectangle(x,y,x+5,y+bh,fill='#34D399' if i%4==0 else ACCENT,outline='')
        self.after(150,self._tick)
    def _status(self,msg): self.title(f'SoundSpace — {msg}')
    def _close(self):
        try: pygame.mixer.music.stop(); pygame.mixer.quit(); self.db.close()
        finally:self.destroy()

if __name__=='__main__':
    ctk.set_appearance_mode('dark'); ctk.set_default_color_theme('dark-blue')
    try: app=SoundSpace(); app.mainloop()
    except pygame.error as e: messagebox.showerror('Audio initialization error',f'Could not initialize audio output:\n{e}')
