
import tkinter as tk
from tkinter import ttk
from config import Config

class ModernButton(tk.Label):
    def __init__(self, master, command=None, **kwargs):
        self.command = command
        # Extract custom colors
        self.bg_color = kwargs.pop('bg', Config.COLORS['bg_secondary'])
        self.fg_color = kwargs.pop('fg', Config.COLORS['fg_primary'])
        self.hover_color = kwargs.pop('hover_bg', Config.COLORS['accent'])
        self.active_color = kwargs.pop('active_bg', Config.COLORS['accent_hover'])
        
        # Clean up kwargs that Label might not support but Button did
        kwargs.pop('activebackground', None)
        kwargs.pop('activeforeground', None)
        
        # Internal state
        self._state = kwargs.get('state', tk.NORMAL)
        
        # Determine initial style
        initial_bg = self.bg_color
        initial_fg = self.fg_color
        initial_cursor = 'hand2'
        
        if self._state == tk.DISABLED:
            initial_fg = Config.COLORS['fg_secondary']
            initial_cursor = 'arrow'
            # Keep bg as bg_secondary (transparent-ish look)
        
        # We manually handle state visuals, so we might want to consume 'state' from kwargs 
        # to prevent Label from applying its own disabled stipple which looks bad on some OS
        if 'state' in kwargs:
            del kwargs['state']
            
        super().__init__(
            master,
            bg=initial_bg,
            fg=initial_fg,
            relief=tk.FLAT,
            borderwidth=0,
            cursor=initial_cursor,
            pady=10,
            padx=20,
            font=Config.FONTS['normal'],
            **kwargs
        )
        
        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_click(self, e):
        if self._state == tk.NORMAL and self.command:
            self.command()

    def on_enter(self, e):
        if self._state == tk.NORMAL:
            self.configure(bg=self.hover_color)

    def on_leave(self, e):
        if self._state == tk.NORMAL:
            self.configure(bg=self.bg_color)

    def config(self, **kwargs):
        if 'state' in kwargs:
            self._state = kwargs['state']
            if self._state == tk.DISABLED:
                self.configure(
                    fg=Config.COLORS['fg_secondary'],
                    cursor='arrow',
                    bg=Config.COLORS['bg_secondary']
                )
            else:
                self.configure(
                    fg=self.fg_color,
                    cursor='hand2',
                    bg=self.bg_color
                )
            # Remove state from kwargs as Label handles it differently (greys out text)
            # We handle visuals manually
            del kwargs['state']
            
        super().config(**kwargs)

    # Alias for consistency
    configure = config

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
