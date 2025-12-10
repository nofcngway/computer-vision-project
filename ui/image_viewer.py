
import tkinter as tk
from PIL import Image, ImageTk
from config import Config

class ImageViewer(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(
            master, 
            bg=Config.COLORS['bg_main'], 
            highlightthickness=0,
            **kwargs
        )
        
        self.image = None       # Original PIL Image
        self.tk_image = None    # PhotoImage for display
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Bounding boxes: list of (bbox, text)
        # bbox is usually [[x,y], [x,y]...] from EasyOCR
        self.ocr_results = []
        
        self.bind('<Configure>', self.on_resize)
        
        # Placeholder text
        self.create_text(
            300, 250, 
            text="Перетащите изображение сюда\nили нажмите 'Загрузить фото'", 
            fill=Config.COLORS['fg_secondary'],
            font=Config.FONTS['header'],
            justify=tk.CENTER,
            tags="placeholder"
        )

    def load_image(self, image_path):
        self.image = Image.open(image_path)
        self.ocr_results = []
        self.fit_image()
        self.redraw()

    def fit_image(self):
        if not self.image:
            return
            
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            return

        img_w, img_h = self.image.size
        scale_w = canvas_width / img_w
        scale_h = canvas_height / img_h
        
        self.scale = min(scale_w, scale_h) * 0.9 # 90% fit
        
        # Center image
        new_w = int(img_w * self.scale)
        new_h = int(img_h * self.scale)
        
        self.offset_x = (canvas_width - new_w) // 2
        self.offset_y = (canvas_height - new_h) // 2

    def set_results(self, results):
        self.ocr_results = results
        self.redraw()

    def on_resize(self, event):
        if self.image:
            self.fit_image()
            self.redraw()
        else:
            # Re-center placeholder
            self.delete("placeholder")
            self.create_text(
                event.width // 2, event.height // 2, 
                text="Загрузите изображение", 
                fill=Config.COLORS['fg_secondary'],
                font=Config.FONTS['header'],
                tags="placeholder"
            )

    def redraw(self):
        self.delete("all")
        
        if not self.image:
            return
            
        # Rescale image
        new_w = int(self.image.width * self.scale)
        new_h = int(self.image.height * self.scale)
        
        resized = self.image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)
        
        self.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.tk_image)
        
        # Draw bounding boxes
        for (bbox, text, prob) in self.ocr_results:
            if prob < 0.3:
                continue
                
            pts = []
            for (x, y) in bbox:
                screen_x = x * self.scale + self.offset_x
                screen_y = y * self.scale + self.offset_y
                pts.append(screen_x)
                pts.append(screen_y)
            
            # Draw polygon
            self.create_polygon(pts, outline=Config.COLORS['error'], width=2, fill="")
            
            # Draw text bg
            text_x = pts[0]
            text_y = pts[1] - 20
            
            self.create_text(
                text_x, text_y, 
                text=text, 
                anchor=tk.SW, 
                fill=Config.COLORS['error'], 
                font=("Arial", 12, "bold")
            )
