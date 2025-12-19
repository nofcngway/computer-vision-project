import os


class Config:
    # Окно приложения
    WINDOW_TITLE = "Распознавание адреса"
    WINDOW_SIZE = "1200x800"
    MIN_WINDOW_SIZE = (1000, 700)

    # Цветовая палитра (Тёмная тема)
    COLORS = {
        "bg_main": "#1E1E1E",  # Основной фон
        "bg_secondary": "#252526",  # Фон панелей
        "fg_primary": "#FFFFFF",  # Основной текст
        "fg_secondary": "#CCCCCC",  # Вторичный текст
        "accent": "#007ACC",  # Акцентный цвет (синий)
        "accent_hover": "#0098FF",  # Акцент при наведении
        "border": "#3E3E42",  # Окантовки
        "success": "#4EC9B0",  # Зеленый (успех)
        "warning": "#CE9178",  # Оранжевый (предупреждение)
        "error": "#F44747",  # Красный (ошибка)
        "overlay": "rgba(0, 0, 0, 0.5)",  # Затемнение
    }

    # Настройки OCR
    OCR_LANGUAGES = ["ru", "en"]
    OCR_GPU = False  # Set to True if NVIDIA GPU is available

    # Тюнинг OCR для улучшения распознавания мелкого текста
    OCR_PARAMS = {
        "text_threshold": 0.6,  # Возвращаем к 0.6
        "low_text": 0.35,
        "link_threshold": 0.4,
        "canvas_size": 2560,
        "mag_ratio": 2.0,  # Увеличиваем увеличение (было 1.5)
        "contrast_ths": 0.3,  # Добавляем контрастность
        "adjust_contrast": 0.8,  # Усиливаем контраст
    }

    # Настройки шрифтов
    FONTS = {
        "header": ("Segoe UI", 14, "bold"),
        "normal": ("Segoe UI", 11),
        "small": ("Segoe UI", 10),
        "code": ("Consolas", 11),
    }

    # Пути
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
