
import tkinter as tk
from tkinter import ttk
from config import Config

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        # Extract custom properties
        self.bg_color = kwargs.pop('bg', Config.COLORS['bg_secondary'])
        self.fg_color = kwargs.pop('fg', Config.COLORS['fg_primary'])
        self.hover_color = kwargs.pop('hover_bg', Config.COLORS['accent'])
        self.active_color = kwargs.pop('active_bg', Config.COLORS['accent_hover'])
        
        super().__init__(
            master,
            bg=self.bg_color,
            fg=self.fg_color,
            activebackground=self.active_color,
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            borderwidth=0,
            cursor='hand2',
            pady=8,
            padx=15,
            font=Config.FONTS['normal'],
            **kwargs
        )
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        if self['state'] != tk.DISABLED:
            self['bg'] = self.hover_color

    def on_leave(self, e):
        if self['state'] != tk.DISABLED:
            self['bg'] = self.bg_color

class ResultCard(tk.Frame):
    def __init__(self, master, title, content, icon="•", **kwargs):
        super().__init__(master, bg=Config.COLORS['bg_secondary'], padx=10, pady=10, **kwargs)
        
        self.header_frame = tk.Frame(self, bg=Config.COLORS['bg_secondary'])
        self.header_frame.pack(fill=tk.X, anchor=tk.W)
        
        tk.Label(
            self.header_frame, 
            text=icon, 
            bg=Config.COLORS['bg_secondary'], 
            fg=Config.COLORS['accent'],
            font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            self.header_frame, 
            text=title, 
            bg=Config.COLORS['bg_secondary'], 
            fg=Config.COLORS['fg_secondary'],
            font=Config.FONTS['small']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            self, 
            text=content if content else "—", 
            bg=Config.COLORS['bg_secondary'], 
            fg=Config.COLORS['fg_primary'],
            font=Config.FONTS['header'] if content else Config.FONTS['normal'],
            wraplength=250,
            justify=tk.LEFT
        ).pack(fill=tk.X, anchor=tk.W, pady=(5, 0))

class StatusFooter(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=Config.COLORS['bg_secondary'], height=30, **kwargs)
        self.pack_propagate(False)
        
        self.status_label = tk.Label(
            self,
            text="Готово",
            bg=Config.COLORS['bg_secondary'],
            fg=Config.COLORS['fg_secondary'],
            font=Config.FONTS['small']
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        
    def set_status(self, text, is_loading=False):
        self.status_label.config(text=text)
        if is_loading:
            self.progress.pack(side=tk.RIGHT, padx=10, fill=tk.Y, pady=8)
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.pack_forget()
