
import re

class AddressParser:
    # Ключевые слова для определения типа улицы
    STREET_PREFIXES = [
        'улица', 'ул.', 'ул', 
        'проспект', 'пр-т', 'пр.', 'пр',
        'переулок', 'пер.', 'пер',
        'бульвар', 'б-р', 'бул.',
        'проезд', 'пр-д',
        'шоссе', 'ш.',
        'набережная', 'наб.',
        'площадь', 'пл.',
        'микрорайон', 'мкр.', 'мкр',
        'тупик', 'аллея', 'квартал',
    ]

    @staticmethod
    def normalize_text(text):
        """
        Очистка текста от артефактов OCR.
        Убирает мусорные символы, лишние пробелы и т.д.
        """
        if not text:
            return ""
        
        # Убираем квадратные и фигурные скобки (частые артефакты OCR)
        text = re.sub(r'[\[\]\{\}\|]', '', text)
        
        # Убираем другие мусорные символы (оставляем буквы, цифры, пробелы, дефисы, точки, запятые)
        text = re.sub(r'[^\w\s\-.,/]', '', text, flags=re.UNICODE)
        
        # Убираем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Убираем пробелы в начале и конце
        text = text.strip()
        
        return text

    @staticmethod
    def _is_similar(word1, word2):
        """Простая проверка похожести строк (допускается 1 ошибка на 4 символа)"""
        if abs(len(word1) - len(word2)) > 1:
            return False
            
        errors = 0
        min_len = min(len(word1), len(word2))
        
        for i in range(min_len):
            if word1[i] != word2[i]:
                errors += 1
                
        return errors <= (len(word2) // 4 + 1)

    def parse(self, raw_texts):
        """
        Парсинг распознанного текста в структурированный адрес.
        Возвращает словарь с полями: street_type, street_name, house_number, raw
        """
        # Объединяем все распознанные тексты
        combined = ' '.join([self.normalize_text(t) for t in raw_texts])
        
        result = {
            'street_type': '',      # тип улицы (улица, проспект и т.д.)
            'street_name': '',      # название улицы
            'house_number': '',     # номер дома
            'raw': combined,        # исходный (нормализованный) текст
        }
        
        if not combined:
            return result
        
        # 1. Ищем номер дома сложной структуры (5 корп 2, 5 строение 1, 5/2)
        # Поддержка: 25, 25а, 25/1, 25 к2, 25 стр 1, 25 корпус 2
        house_regex = r'\b\d+[а-яА-Яa-zA-Z]?(?:[/-]\d+)?(?:[\s,.]*(?:корпус|корп|к|строение|стр|с|block|bldg)[\s.]*\d+[а-яА-Яa-zA-Z]?)?\b'
        house_match = re.search(house_regex, combined, re.IGNORECASE)
        
        if house_match:
            result['house_number'] = house_match.group(0)
        
        # Ищем тип улицы (с нечетким поиском)
        combined_lower = combined.lower()
        
        # Подготовка списка префиксов (сортируем по длине, чтобы сначала искать длинные: "улица", потом "ул")
        sorted_prefixes = sorted(self.STREET_PREFIXES, key=len, reverse=True)
        
        found_prefix = None
        # 1. Точное совпадение
        for prefix in sorted_prefixes:
            # Ищем слово целиком или как часть, но с границами
            if re.search(r'\b' + re.escape(prefix) + r'\b', combined_lower):
                found_prefix = prefix
                break
            # Или если просто входит (для длинных слов типа "проспект")
            if len(prefix) > 3 and prefix in combined_lower:
                found_prefix = prefix
                break
        
        # 2. Если не нашли, пробуем нечеткий поиск
        if not found_prefix:
            words = combined_lower.split()
            for word in words:
                if len(word) < 3: continue
                # Пропускаем, если слово похоже на цифры или номер
                if any(c.isdigit() for c in word): continue
                
                for prefix in sorted_prefixes:
                    if len(prefix) < 3: continue
                    if self._is_similar(word, prefix):
                        found_prefix = prefix
                        # Исправляем опечатку в исходном тексте для чистоты
                        combined = re.sub(r'\b' + re.escape(word) + r'\b', prefix, combined, flags=re.IGNORECASE)
                        break
                if found_prefix: break

        if found_prefix:
            result['street_type'] = found_prefix

        # --- Формирование названия улицы ---
        street_name = combined
        
        # 1. Убираем найденный тип улицы
        if result['street_type']:
            pattern = re.compile(re.escape(result['street_type']), re.IGNORECASE)
            street_name = pattern.sub('', street_name)
        
        # 2. Убираем "ошметки" от типа улицы (например "и ца" от "улица")
        # Частая проблема OCR с разрядкой: "У Л И Ц А" -> "УЛ И ЦА"
        # Если тип "улица", убираем "ица", "лица" и т.д.
        if result['street_type'] in ['улица', 'ул', 'ул.']:
            street_name = re.sub(r'\b(лица|ица|и ца|ли ца)\b', '', street_name, flags=re.IGNORECASE)
        
        # 3. Убираем номер дома
        if result['house_number']:
            street_name = street_name.replace(result['house_number'], '')
            # Также убираем части номера, если они остались (например "корпус 2" если не удалилось целиком)
            street_name = re.sub(house_regex, '', street_name, flags=re.IGNORECASE)

        # 4. Финальная очистка
        street_name = re.sub(r'[\s.,-]+', ' ', street_name).strip()
        
        result['street_name'] = street_name
        
        return result
