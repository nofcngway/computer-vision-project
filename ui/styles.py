
import tkinter as tk
from tkinter import ttk
from config import Config

class Styles:
    @staticmethod
    def configure():
        style = ttk.Style()
        style.theme_use('clam')  # Base theme that supports more customization
        
        # General frame style
        style.configure(
            "TFrame", 
            background=Config.COLORS['bg_main']
        )
        
        # Label styles
        style.configure(
            "TLabel",
            background=Config.COLORS['bg_main'],
            foreground=Config.COLORS['fg_primary'],
            font=Config.FONTS['normal']
        )
        
        style.configure(
            "Header.TLabel",
            background=Config.COLORS['bg_main'],
            foreground=Config.COLORS['fg_primary'],
            font=Config.FONTS['header']
        )
        
        style.configure(
            "Status.TLabel",
            background=Config.COLORS['bg_secondary'],
            foreground=Config.COLORS['fg_secondary'],
            font=Config.FONTS['small']
        )
        
        # Button styles
        style.configure(
            "TButton",
            background=Config.COLORS['bg_secondary'],
            foreground=Config.COLORS['fg_primary'],
            borderwidth=1,
            focuscolor=Config.COLORS['accent'],
            font=Config.FONTS['normal'],
            padding=6
        )
        
        style.map(
            "TButton",
            background=[('active', Config.COLORS['accent']), ('disabled', Config.COLORS['bg_main'])],
            foreground=[('disabled', Config.COLORS['fg_secondary'])]
        )
        
        style.configure(
            "Primary.TButton",
            background=Config.COLORS['accent'],
            foreground='#FFFFFF',
            borderwidth=0
        )
        
        style.map(
            "Primary.TButton",
            background=[('active', Config.COLORS['accent_hover']), ('disabled', Config.COLORS['bg_secondary'])]
        )
        
        # Scrollbar
        style.configure(
            "Vertical.TScrollbar",
            background=Config.COLORS['bg_secondary'],
            troughcolor=Config.COLORS['bg_main'],
            bordercolor=Config.COLORS['bg_main'],
            arrowcolor=Config.COLORS['fg_primary']
        )
