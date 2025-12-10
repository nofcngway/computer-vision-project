
import cv2
import numpy as np

class ImagePreprocessor:
    @staticmethod
    def process(image_path):
        """
        Предобработка изображения для улучшения качества OCR.
        Возвращает обработанное изображение (numpy array).
        """
        # Читаем изображение
        img = cv2.imread(image_path)
        
        if img is None:
            return None
        
        # 1. Увеличиваем изображение, если оно маленькое
        height, width = img.shape[:2]
        if width < 800:
            scale = 800 / width
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # 2. Конвертируем в оттенки серого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Улучшаем контраст с помощью CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 4. Применяем адаптивную бинаризацию
        # Это помогает OCR лучше видеть текст
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        # 5. Убираем шум
        denoised = cv2.fastNlMeansDenoising(binary, h=10)
        
        return denoised
