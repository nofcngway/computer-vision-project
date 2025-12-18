
import easyocr
import threading
from ocr.preprocessor import ImagePreprocessor
from config import Config

class OCREngine:
    def __init__(self, languages=['ru', 'en'], gpu=False):
        self.languages = languages
        self.gpu = gpu
        self.reader = None
        self.is_loaded = False
        self.load_error = None
        
        # Инициализация в отдельном потоке, чтобы не блокировать UI
        self._load_thread = threading.Thread(target=self._load_model, daemon=True)
        self._load_thread.start()

    def _load_model(self):
        try:
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
            self.is_loaded = True
        except Exception as e:
            self.load_error = str(e)
            print(f"Error loading OCR model: {e}")

    def process_image(self, image_path):
        """
        Запускает процесс распознавания.
        Возвращает список кортежей (bbox, text, prob).
        Использует технику слияния результатов (оригинал + предобработка).
        """
        if not self.is_loaded:
            if self.load_error:
                raise Exception(f"Model failed to load: {self.load_error}")
            raise Exception("Model is still loading...")

        try:
            # 1. OCR на оригинале
            result_original = self.reader.readtext(image_path, **Config.OCR_PARAMS)
            
            # 2. OCR на предобработанном изображении
            preprocessed_img = ImagePreprocessor.process(image_path)
            
            if preprocessed_img is not None:
                result_preprocessed = self.reader.readtext(preprocessed_img, **Config.OCR_PARAMS)
                # Объединяем результаты
                return self._merge_results(result_original, result_preprocessed)
            else:
                return result_original
                
        except Exception as e:
            raise Exception(f"OCR processing error: {e}")

    def _merge_results(self, result_original, result_preprocessed):
        """
        Объединяет результаты от двух OCR-проходов.
        bbox берётся ТОЛЬКО от оригинального изображения (правильные координаты).
        Тексты берутся лучшие по уверенности.
        """
        best_results = {}
        
        # Сначала добавляем результаты от оригинала
        for (bbox, text, prob) in result_original:
            normalized = text.strip().lower()
            if not normalized:
                continue
            best_results[normalized] = (bbox, text, prob)
        
        # Добавляем тексты от предобработанного, если они лучше
        for (bbox_prep, text, prob) in result_preprocessed:
            normalized = text.strip().lower()
            if not normalized:
                continue
            
            if normalized in best_results:
                old_prob = best_results[normalized][2]
                if prob > old_prob:
                    # Обновляем текст и prob, но оставляем bbox от оригинала
                    old_bbox = best_results[normalized][0]
                    best_results[normalized] = (old_bbox, text, prob)
            # Если текста нет в оригинале, мы его НЕ добавляем, 
            # так как у нас нет правильного bbox для оригинала (масштабы могут отличаться)
        
        return list(best_results.values())
