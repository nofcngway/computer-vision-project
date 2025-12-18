
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
        
        
        # 4. Бинаризация (выбор метода)
        # 'sauvola' - наш ручной алгоритм (лучше для текста с тенями)
        # 'standard' - стандартный OpenCV (быстрее, но хуже качество)
        method = 'sauvola' 
        
        if method == 'sauvola':
            from ocr.manual_algorithms import ManualBinarization
            # window_size=25, k=0.2 дают хорошие результаты для документов
            binary = ManualBinarization.sauvola(enhanced, window_size=25, k=0.2)
        else:
            # Стандартный OpenCV подход
            binary = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )
        
        # 5. Убираем шум
        # Для Сауволы шум обычно меньше, но почистить полезно
        denoised = cv2.fastNlMeansDenoising(binary, h=5) # h поменьше, чтобы не размыть буквы
        
        return denoised
