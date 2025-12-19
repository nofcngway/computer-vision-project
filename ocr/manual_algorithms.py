import numpy as np
import cv2


class ManualBinarization:
    @staticmethod
    def integral_image(img):
        """
        Вычисляет интегральное изображение (Summed-area table).
        Каждая точка (x, y) содержит сумму всех пикселей в прямоугольнике от (0,0) до (x,y).
        Это позволяет считать сумму в любом прямоугольнике за O(1).
        """
        # Используем float64, чтобы избежать переполнения при суммировании квадратов
        return cv2.integral(img).astype(np.float64)

    @staticmethod
    def niblack_sauvola_formula(img, window_size=25, k=0.34, r=128, method="sauvola"):
        """
        Ручная реализация алгоритмов адаптивной бинаризации.
        Поддерживает Niblack и Sauvola.

        Параметры:
        img - полутоновое изображение (grayscale)
        window_size - размер окна (нечетное число)
        k - коэффициент чувствительности (обычно 0.2 - 0.5)
        r - динамический диапазон стандартного отклонения (обычно 128)
        """
        # Проверки входных данных
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        rows, cols = img.shape
        pad = window_size // 2

        # 1. Считаем интегральные изображения для I и I^2
        # Это нужно для быстрого расчета среднего и дисперсии
        # Пэддинг изображения для обработки краев
        padded_img = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REFLECT)

        integral_sum = cv2.integral(padded_img).astype(np.float64)
        integral_sq_sum = cv2.integral(padded_img**2).astype(np.float64)

        # Размеры интегральных изображений на 1 больше, чем padded_img
        # Нам нужно вырезать правильные области, соответствующие окнам вокруг каждого пикселя

        # Координаты углов окон для всех пикселей сразу (векторизация)
        # x1, y1 - верхний левый угол окна
        # x2, y2 - нижний правый угол окна

        # Т.к. мы сделали паддинг 'pad', то для пикселя (0,0) исходного изображения
        # в padded изображении координаты (pad, pad).
        # Окно вокруг него будет от (0, 0) до (2*pad, 2*pad).

        # Сдвиги для получения сумм по окнам из интегрального изображения
        # S(D) + S(A) - S(B) - S(C)
        # A=(y1, x1), B=(y1, x2), C=(y2, x1), D=(y2, x2)
        # Но в integral() индексы сдвинуты на 1.
        # Пусть Y, X - координаты в результирующей матрице (размером как исходная img)
        # Окно размером w (window_size)

        w = window_size

        # Вырезаем нужные части интегральных матриц
        # S_D: нижний правый угол окна
        s_d = integral_sum[w : rows + w, w : cols + w]
        # S_A: верхний левый угол
        s_a = integral_sum[0:rows, 0:cols]
        # S_B: верхний правый
        s_b = integral_sum[0:rows, w : cols + w]
        # S_C: нижний левый
        s_c = integral_sum[w : rows + w, 0:cols]

        # Сумма внутри окна для каждого пикселя
        window_sum = s_d + s_a - s_b - s_c

        # То же самое для квадратов
        sq_d = integral_sq_sum[w : rows + w, w : cols + w]
        sq_a = integral_sq_sum[0:rows, 0:cols]
        sq_b = integral_sq_sum[0:rows, w : cols + w]
        sq_c = integral_sq_sum[w : rows + w, 0:cols]

        window_sq_sum = sq_d + sq_a - sq_b - sq_c

        # 2. Считаем локальное среднее (Mean) и стандартное отклонение (Std)
        # N = w * w
        n = w * w

        mean = window_sum / n

        # Вар(X) = E[X^2] - (E[X])^2
        variance = (window_sq_sum / n) - (mean**2)
        # Из-за погрешности float может быть крошечный минус
        variance[variance < 0] = 0
        std = np.sqrt(variance)

        # 3. Считаем порог T
        threshold = np.zeros_like(mean)

        if method == "sauvola":
            # T = m * (1 + k * (s/R - 1))
            threshold = mean * (1 + k * ((std / r) - 1))
        elif method == "niblack":
            # T = m + k * s
            threshold = mean + k * std

        # 4. Бинаризация
        # Если пиксель > порога -> Белый (255), иначе Черный (0)
        binarized = np.zeros_like(img)
        binarized[img > threshold] = 255

        return binarized

    @staticmethod
    def sauvola(img, window_size=25, k=0.34):
        return ManualBinarization.niblack_sauvola_formula(
            img, window_size, k, method="sauvola"
        )

    @staticmethod
    def niblack(img, window_size=25, k=-0.2):
        return ManualBinarization.niblack_sauvola_formula(
            img, window_size, k, method="niblack"
        )
