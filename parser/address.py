import re


class AddressParser:
    STREET_PREFIXES = [
        "улица",
        "ул.",
        "ул",
        "проспект",
        "пр-т",
        "пр.",
        "пр",
        "переулок",
        "пер.",
        "пер",
        "бульвар",
        "б-р",
        "бул.",
        "проезд",
        "пр-д",
        "шоссе",
        "ш.",
        "набережная",
        "наб.",
        "площадь",
        "пл.",
        "микрорайон",
        "мкр.",
        "мкр",
        "тупик",
        "аллея",
        "квартал",
    ]

    BUILDING_KEYWORDS = [
        "корпус",
        "корп",
        "к",
        "строение",
        "стр",
        "с",
        "блок",
        "block",
        "bldg",
    ]

    @staticmethod
    def normalize_text(text):
        if not text:
            return ""

        text = re.sub(r"[\[\]\{\}\|]", "", text)
        text = re.sub(r"[^\w\s\-.,/]", "", text, flags=re.UNICODE)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    @staticmethod
    def _fix_split_street_type(text):
        """
        Исправляет разбитые типы улиц внутри одного текстового блока.
        'ТАЙНИНСКАЯ УЛ И ЦА' -> 'ТАЙНИНСКАЯ УЛИЦА'
        'Счастливая ули ца' -> 'Счастливая улица'
        """
        # Убираем пробелы между частями слова "УЛИЦА"
        # Паттерны для разных вариантов разбития
        patterns = [
            (r"\bУЛ\s+И\s+ЦА\b", "УЛИЦА"),
            (r"\bул\s+и\s+ца\b", "улица"),
            (r"\bУл\s+и\s+ца\b", "Улица"),
            (r"\bУЛИ\s+ЦА\b", "УЛИЦА"),
            (r"\bули\s+ца\b", "улица"),
            (r"\bУ\s+Л\s+И\s+Ц\s+А\b", "УЛИЦА"),
            (r"\bу\s+л\s+и\s+ц\s+а\b", "улица"),
            # Для других типов
            (r"\bПРО\s+СПЕКТ\b", "ПРОСПЕКТ"),
            (r"\bпро\s+спект\b", "проспект"),
            (r"\bПЕРЕ\s+УЛОК\b", "ПЕРЕУЛОК"),
            (r"\bпере\s+улок\b", "переулок"),
        ]

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def _fix_split_words(texts):
        """
        Склеивает разбитые слова в массиве текстов.
        ['УЛ', 'И', 'ЦА'] -> ['УЛИЦА']
        """
        fixed = []
        i = 0
        while i < len(texts):
            current = texts[i]

            # Проверяем трехчастные склейки: УЛ + И + ЦА
            if i + 2 < len(texts):
                combined = (
                    (current + texts[i + 1] + texts[i + 2]).replace(" ", "").lower()
                )

                if combined == "улица":
                    fixed.append("УЛИЦА")
                    i += 3
                    continue

            # Проверяем двухчастные склейки
            if i + 1 < len(texts):
                combined = (current + texts[i + 1]).replace(" ", "").lower()

                split_words = {
                    "улица": [("ул", "ица"), ("ули", "ца")],
                    "проспект": [("про", "спект"), ("проспе", "кт")],
                    "переулок": [("пере", "улок"), ("переу", "лок")],
                }

                for full_word, variants in split_words.items():
                    for part1, part2 in variants:
                        if (
                            current.lower().strip() == part1
                            and texts[i + 1].lower().strip() == part2
                        ):
                            fixed.append(full_word.upper())
                            i += 2
                            break
                    else:
                        continue
                    break
                else:
                    fixed.append(current)
                    i += 1
                    continue
                continue

            fixed.append(current)
            i += 1

        return fixed

    @staticmethod
    def _extract_house_from_street(text):
        """
        Извлекает номер дома из названия улицы.
        'Счастливая 25' -> ('Счастливая', '25')
        """
        match = re.search(r"^(.*?)\s+(\d+[а-яА-Яa-zA-Z]?)$", text)
        if match:
            street = match.group(1).strip()
            house = match.group(2).strip()

            if house.isdigit() and int(house) <= 1000:
                return street, house

        return text, None

    @staticmethod
    def _is_similar(word1, word2):
        if abs(len(word1) - len(word2)) > 1:
            return False

        errors = 0
        min_len = min(len(word1), len(word2))

        for i in range(min_len):
            if word1[i] != word2[i]:
                errors += 1

        return errors <= (len(word2) // 4 + 1)

    def parse(self, raw_texts):
        print("\n" + "=" * 50)
        print("ОТЛАДКА ПАРСЕРА")
        print("=" * 50)
        print(f"Входные тексты: {raw_texts}")

        # Нормализуем каждый текстовый блок
        normalized_texts = [
            self.normalize_text(t) for t in raw_texts if self.normalize_text(t)
        ]
        print(f"После нормализации: {normalized_texts}")

        # Исправляем разбитые типы улиц внутри каждого блока
        normalized_texts = [self._fix_split_street_type(t) for t in normalized_texts]
        print(f"После склейки внутри блоков: {normalized_texts}")

        # Склеиваем разбитые слова между блоками
        normalized_texts = self._fix_split_words(normalized_texts)
        print(f"После склейки между блоками: {normalized_texts}")

        # Объединяем для общего анализа
        combined = " ".join(normalized_texts)
        print(f"Объединенный текст: {combined}")

        result = {
            "street_type": "",
            "street_name": "",
            "house_number": "",
            "raw": combined,
        }

        if not combined:
            return result

        # === ШАГ 1: Поиск типа улицы ===
        combined_lower = combined.lower()
        sorted_prefixes = sorted(self.STREET_PREFIXES, key=len, reverse=True)

        found_prefix = None
        found_prefix_normalized = None
        prefix_index = -1

        # Ищем тип улицы в отдельных блоках
        for idx, text in enumerate(normalized_texts):
            text_lower = text.lower()
            for prefix in sorted_prefixes:
                if text_lower == prefix or text_lower == prefix + ".":
                    found_prefix = text
                    found_prefix_normalized = prefix
                    prefix_index = idx
                    print(f"Найден тип улицы в блоке {idx}: {prefix}")
                    break
            if found_prefix:
                break

        # Если не нашли в отдельных блоках, ищем в общем тексте
        if not found_prefix:
            for prefix in sorted_prefixes:
                if re.search(r"\b" + re.escape(prefix) + r"\b", combined_lower):
                    found_prefix = prefix
                    found_prefix_normalized = prefix
                    print(f"Найден тип улицы в общем тексте: {prefix}")
                    break

        if found_prefix_normalized:
            result["street_type"] = found_prefix_normalized

        # === ШАГ 2: Поиск номера дома и корпуса ===
        house_parts = []
        house_indices = set()

        for idx, text in enumerate(normalized_texts):
            # Проверяем блоки с корпусом/строением
            is_building_block = False
            for keyword in self.BUILDING_KEYWORDS:
                pattern = r"\b" + re.escape(keyword) + r"[\s.]*\d+[а-яА-Яa-zA-Z]?\b"
                if re.search(pattern, text, re.IGNORECASE):
                    house_parts.append(text)
                    house_indices.add(idx)
                    is_building_block = True
                    print(f"Найден блок корпуса в {idx}: {text}")
                    break

            if is_building_block:
                continue

            # Ищем просто номер дома (отдельно стоящую цифру)
            if re.match(r"^\d+[а-яА-Яa-zA-Z]?$", text):
                house_parts.insert(0, text)
                house_indices.add(idx)
                print(f"Найден номер дома в {idx}: {text}")
                continue

        if house_parts:
            result["house_number"] = " ".join(house_parts)

        # === ШАГ 3: Формирование названия улицы ===
        street_parts = []

        for idx, text in enumerate(normalized_texts):
            text_lower = text.lower()

            # Пропускаем тип улицы
            if idx == prefix_index or (
                found_prefix_normalized and text_lower == found_prefix_normalized
            ):
                print(f"Пропускаем тип улицы в {idx}: {text}")
                continue

            # Пропускаем блоки с номером дома/корпусом
            if idx in house_indices:
                print(f"Пропускаем номер/корпус в {idx}: {text}")
                continue

            # Пропускаем блоки, которые выглядят как номер
            if re.match(r"^\d+[а-яА-Яa-zA-Z]?$", text):
                print(f"Пропускаем номер в {idx}: {text}")
                continue

            # Пропускаем блоки с ключевыми словами корпус/строение
            is_building = False
            for keyword in self.BUILDING_KEYWORDS:
                if re.search(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE):
                    is_building = True
                    break

            if is_building:
                print(f"Пропускаем строение в {idx}: {text}")
                continue

            # Добавляем в название улицы
            print(f"Добавляем в название улицы из {idx}: {text}")
            street_parts.append(text)

        if street_parts:
            street_name = " ".join(street_parts)

            # Пытаемся извлечь номер дома из названия улицы, если он там есть
            if not result["house_number"]:
                original_name = street_name
                street_name, extracted_house = self._extract_house_from_street(
                    street_name
                )
                if extracted_house:
                    result["house_number"] = extracted_house
                    print(
                        f"Извлечен номер из названия: {original_name} -> {street_name} + {extracted_house}"
                    )

            result["street_name"] = street_name

        # === ШАГ 4: Если тип не определен, но есть "улица" в названии ===
        if not result["street_type"] and result["street_name"]:
            for prefix in sorted_prefixes:
                if prefix in result["street_name"].lower():
                    result["street_type"] = prefix
                    # Убираем из названия
                    result["street_name"] = re.sub(
                        r"\b" + re.escape(prefix) + r"\b",
                        "",
                        result["street_name"],
                        flags=re.IGNORECASE,
                    ).strip()
                    print(f"Извлечен тип из названия: {prefix}")
                    break

        # === Финальная очистка ===
        result["street_name"] = re.sub(r"\s+", " ", result["street_name"]).strip()
        result["house_number"] = re.sub(r"\s+", " ", result["house_number"]).strip()

        print("\nИтоговый результат:")
        print(f"  Тип: {result['street_type']}")
        print(f"  Название: {result['street_name']}")
        print(f"  Номер: {result['house_number']}")
        print("=" * 50 + "\n")

        return result
