
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os

from config import Config
from ocr.engine import OCREngine
from parser.address import AddressParser
from ui.styles import Styles
from ui.components import ModernButton, ResultCard, StatusFooter
from ui.image_viewer import ImageViewer

class AddressApp:
    def __init__(self, root):
        self.root = root
        self.root.title(Config.WINDOW_TITLE)
        self.root.geometry(Config.WINDOW_SIZE)
        self.root.minsize(*Config.MIN_WINDOW_SIZE)
        self.root.configure(bg=Config.COLORS['bg_main'])
        
        # Initialize styles
        Styles.configure()
        
        # Initialize core logic
        self.ocr_engine = OCREngine(
            languages=Config.OCR_LANGUAGES, 
            gpu=Config.OCR_GPU
        )
        self.address_parser = AddressParser()
        
        # UI Setup
        self.setup_ui()
        
        # Check model status
        self.check_model_status()

    def setup_ui(self):
        # --- Header ---
        header_frame = tk.Frame(self.root, bg=Config.COLORS['bg_secondary'], pady=10, padx=20)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title_lbl = tk.Label(
            header_frame, 
            text="Распознавание Адреса", 
            font=Config.FONTS['header'],
            bg=Config.COLORS['bg_secondary'],
            fg=Config.COLORS['fg_primary']
        )
        title_lbl.pack(side=tk.LEFT)
        
        self.btn_load = ModernButton(
            header_frame, 
            text="Загрузить фото", 
            command=self.load_image,
            state=tk.DISABLED  # Disabled until model loads
        )
        self.btn_load.pack(side=tk.RIGHT)
        
        # --- Main Content ---
        main_content = tk.Frame(self.root, bg=Config.COLORS['bg_main'])
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left Panel (Image)
        left_panel = tk.Frame(main_content, bg=Config.COLORS['bg_main'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.image_viewer = ImageViewer(left_panel)
        self.image_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel (Results)
        right_panel = tk.Frame(main_content, bg=Config.COLORS['bg_main'], width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        right_panel.pack_propagate(False)
        
        # Results Container
        tk.Label(right_panel, text="Результаты", font=("Arial", 12, "bold"), fg=Config.COLORS['fg_secondary'], bg=Config.COLORS['bg_main']).pack(anchor=tk.W, pady=(0, 10))
        
        self.card_type = ResultCard(right_panel, "Тип объекта", "", icon="📍")
        self.card_type.pack(fill=tk.X, pady=5)
        
        self.card_street = ResultCard(right_panel, "Название улицы", "", icon="🏠")
        self.card_street.pack(fill=tk.X, pady=5)
        
        self.card_number = ResultCard(right_panel, "Номер дома", "", icon="🔢")
        self.card_number.pack(fill=tk.X, pady=5)
        
        tk.Frame(right_panel, height=20, bg=Config.COLORS['bg_main']).pack()
        
        self.card_full = ResultCard(right_panel, "Полный адрес", "", icon="📝")
        self.card_full.pack(fill=tk.X, pady=5)
        
        # --- Footer ---
        self.footer = StatusFooter(self.root)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
        self.footer.set_status("Инициализация OCR модели...", is_loading=True)

    def check_model_status(self):
        if self.ocr_engine.is_loaded:
            self.footer.set_status("Модель загружена. Готово к работе.")
            self.btn_load.config(state=tk.NORMAL)
        elif self.ocr_engine.load_error:
            self.footer.set_status(f"Ошибка загрузки: {self.ocr_engine.load_error}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить OCR модель:\n{self.ocr_engine.load_error}")
        else:
            # Check again in 500ms
            self.root.after(500, self.check_model_status)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return
            
        # UI Updates
        self.image_viewer.load_image(file_path)
        self.footer.set_status("Распознавание...", is_loading=True)
        self.btn_load.config(state=tk.DISABLED)
        
        # Reset results
        self.update_results({})
        
        # Process in thread
        threading.Thread(target=self.process_image, args=(file_path,), daemon=True).start()

    def process_image(self, file_path):
        try:
            results = self.ocr_engine.process_image(file_path)
            
            # Extract text for parser
            raw_texts = [text for (bbox, text, prob) in results if prob > 0.3]
            parsed_address = self.address_parser.parse(raw_texts)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.on_process_complete(results, parsed_address))
            
        except Exception as e:
            self.root.after(0, lambda: self.on_process_error(str(e)))

    def on_process_complete(self, ocr_results, parsed_address):
        self.footer.set_status("Распознавание завершено")
        self.btn_load.config(state=tk.NORMAL)
        
        # Show boxes
        self.image_viewer.set_results(ocr_results)
        
        # Show text results
        self.update_results(parsed_address)

    def on_process_error(self, error_msg):
        self.footer.set_status("Ошибка обработки")
        self.btn_load.config(state=tk.NORMAL)
        messagebox.showerror("Ошибка", f"Ошибка при распознавании:\n{error_msg}")

    def update_results(self, data):
        # Update cards
        # We need a method in ResultCard to update text, simpler to just recreate label or config it
        # Let's assume we can access children
        def update_card(card, text):
            # The 3rd child is the content label (index 2)
            # pack order: header_frame, content_label
            # header_frame is index 0? No, let's look at implementation
            # header_frame pack, then content label pack
            # So children check
            labels = [c for c in card.winfo_children() if isinstance(c, tk.Label)]
            # First label is icon (in header_frame) so we need to look into card children directly
            # Card children: header_frame, label(content)
            content_label = card.winfo_children()[1] 
            content_label.config(text=text if text else "—", font=Config.FONTS['header'] if text else Config.FONTS['normal'])

        update_card(self.card_type, data.get('street_type', ''))
        update_card(self.card_street, data.get('street_name', ''))
        update_card(self.card_number, data.get('house_number', ''))
        
        full = []
        if data.get('street_type'): full.append(data.get('street_type'))
        if data.get('street_name'): full.append(data.get('street_name'))
        if data.get('house_number'): full.append(data.get('house_number'))
        
        full_text = ' '.join(full) if full else data.get('raw', '')
        update_card(self.card_full, full_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = AddressApp(root)
    root.mainloop()
