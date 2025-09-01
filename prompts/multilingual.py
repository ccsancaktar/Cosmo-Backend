"""
Çok dilli prompt sistemi
Her fal türü için farklı dillerde prompt'lar sağlar
"""

# Desteklenen diller
SUPPORTED_LANGUAGES = ['tr', 'en', 'de']

def get_prompt_by_language(fortune_type, language='tr', **kwargs):
    """
    Belirtilen fal türü ve dil için prompt döndürür
    
    Args:
        fortune_type (str): Fal türü (tarot, rune, chinese, coffee, daily, kabala, yildizname)
        language (str): Dil kodu (tr, en, de)
        **kwargs: Prompt için gerekli parametreler
    
    Returns:
        str: Dil bazlı prompt
    """
    if language not in SUPPORTED_LANGUAGES:
        language = 'tr'  # Varsayılan dil
    
    prompt_functions = {
        'tarot': get_tarot_prompt,
        'rune': get_rune_prompt,
        'chinese': get_chinese_prompt,
        'coffee': get_coffee_prompt,
        'daily': get_daily_prompt,
        'kabala': get_kabala_prompt,
        'yildizname': get_yildizname_prompt,
    }
    
    if fortune_type not in prompt_functions:
        raise ValueError(f"Desteklenmeyen fal türü: {fortune_type}")
    
    return prompt_functions[fortune_type](language, **kwargs)

# Tarot prompt'ları
def get_tarot_prompt(language, **kwargs):
    soru = kwargs.get('soru', '')
    cards = kwargs.get('cards', [])
    
    if language == 'tr':
        return f"""
        Sen deneyimli bir tarot uzmanısın. Aşağıdaki soruya göre detaylı bir tarot falı yorumu yap:
        
        Soru: {soru}
        
        Seçilen Kartlar: {', '.join([f"{card['name']} ({card['key']})" for card in cards])}
        
        Lütfen şu konuları kapsayan detaylı bir tarot yorumu yap:
        1. Kartların genel enerjisi ve mesajı
        2. Geçmiş, şimdi ve gelecek açısından yorum
        3. Kişisel ilişkiler ve aşk hayatı
        4. Kariyer ve iş hayatı
        5. Sağlık durumu
        6. Yakın gelecekteki olaylar
        7. Pratik öneriler ve tavsiyeler
        
        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz.
        """
    
    elif language == 'en':
        return f"""
        You are an experienced tarot reader. Please provide a detailed tarot reading based on the following question:
        
        Question: {soru}
        
        Selected Cards: {', '.join([f"{card['name']} ({card['key']})" for card in cards])}
        
        Please provide a detailed tarot reading covering these topics:
        1. General energy and message of the cards
        2. Interpretation from past, present, and future perspectives
        3. Personal relationships and love life
        4. Career and work life
        5. Health status
        6. Upcoming events
        7. Practical advice and recommendations
        
        Write the interpretation in English, using a warm and understandable language.
        """
    
    elif language == 'de':
        return f"""
        Du bist ein erfahrener Tarot-Leser. Bitte erstelle eine detaillierte Tarot-Deutung basierend auf der folgenden Frage:
        
        Frage: {soru}
        
        Ausgewählte Karten: {', '.join([f"{card['name']} ({card['key']})" for card in cards])}
        
        Bitte erstelle eine detaillierte Tarot-Deutung, die diese Themen abdeckt:
        1. Allgemeine Energie und Botschaft der Karten
        2. Deutung aus Vergangenheit, Gegenwart und Zukunft
        3. Persönliche Beziehungen und Liebesleben
        4. Karriere und Arbeitsleben
        5. Gesundheitszustand
        6. Kommende Ereignisse
        7. Praktische Ratschläge und Empfehlungen
        
        Schreibe die Deutung auf Deutsch, verwende eine warme und verständliche Sprache.
        """

# Rune prompt'ları
def get_rune_prompt(language, **kwargs):
    soru = kwargs.get('soru', '')
    runes = kwargs.get('runes', [])
    
    if language == 'tr':
        return f"""
        Sen deneyimli bir rune uzmanısın. Aşağıdaki soruya göre detaylı bir rune falı yorumu yap:
        
        Soru: {soru}
        
        Seçilen Runeler: {', '.join([rune['name'] for rune in runes])}
        
        Lütfen şu konuları kapsayan detaylı bir rune yorumu yap:
        1. Runelerin genel enerjisi ve mesajı
        2. Geçmiş, şimdi ve gelecek açısından yorum
        3. Kişisel ilişkiler ve aşk hayatı
        4. Kariyer ve iş hayatı
        5. Sağlık durumu
        6. Yakın gelecekteki olaylar
        7. Pratik öneriler ve tavsiyeler
        
        Yorumu Türkçe olarak, mistik ve anlaşılır bir dille yaz.
        """
    
    elif language == 'en':
        return f"""
        You are an experienced rune reader. Please provide a detailed rune reading based on the following question:
        
        Question: {soru}
        
        Selected Runes: {', '.join([rune['name'] for rune in runes])}
        
        Please provide a detailed rune reading covering these topics:
        1. General energy and message of the runes
        2. Interpretation from past, present, and future perspectives
        3. Personal relationships and love life
        4. Career and work life
        5. Health status
        6. Upcoming events
        7. Practical advice and recommendations
        
        Write the interpretation in English, using a mystical and understandable language.
        """
    
    elif language == 'de':
        return f"""
        Du bist ein erfahrener Runen-Leser. Bitte erstelle eine detaillierte Runen-Deutung basierend auf der folgenden Frage:
        
        Frage: {soru}
        
        Ausgewählte Runen: {', '.join([rune['name'] for rune in runes])}
        
        Bitte erstelle eine detaillierte Runen-Deutung, die diese Themen abdeckt:
        1. Allgemeine Energie und Botschaft der Runen
        2. Deutung aus Vergangenheit, Gegenwart und Zukunft
        3. Persönliche Beziehungen und Liebesleben
        4. Karriere und Arbeitsleben
        5. Gesundheitszustand
        6. Kommende Ereignisse
        7. Praktische Ratschläge und Empfehlungen
        
        Schreibe die Deutung auf Deutsch, verwende eine mystische und verständliche Sprache.
        """

# Çin falı prompt'ları
def get_chinese_prompt(language, **kwargs):
    dogum_tarihi = kwargs.get("dogumTarihi", "")
    dogum_saati = kwargs.get("dogumSaati", "")
    ba_zi_result = kwargs.get("ba_zi", {})
    element_counts = kwargs.get("element_counts", "")
    dogum_tarihi = kwargs.get('dogumTarihi', '')
    dogum_saati = kwargs.get('dogumSaati', '')
    
    element_counts = kwargs.get('element_counts', '')
    
    if language == 'tr':
        return f"""
        Sen deneyimli bir Çin falı uzmanısın. Aşağıdaki bilgilere göre detaylı bir Çin falı yorumu yap:
        
        Doğum Tarihi: {dogum_tarihi}
        Doğum Saati: {dogum_saati}
        
        Ba Zi Analizi:
        
        
        
        
        
        
        
        Lütfen şu konuları kapsayan detaylı bir Çin falı yorumu yap:
        
        **🌟 KİŞİLİK ÖZELLİKLERİ VE KARAKTER ANALİZİ** (3-4 cümle)
        - Element kombinasyonuna göre kişilik yapısı
        - Güçlü ve zayıf yönler
        - Karakter özellikleri ve davranış kalıpları
        
        **💼 KARİYER VE İŞ HAYATI** (3-4 cümle)
        - Meslek uyumluluğu ve öneriler
        - Kariyer fırsatları ve gelişim alanları
        - İş hayatındaki zorluklar ve çözümler
        
        **❤️ AŞK VE İLİŞKİLER** (3-4 cümle)
        - Romantik uyumluluk analizi
        - İlişki dinamikleri ve gelecek
        - Duygusal ihtiyaçlar ve beklentiler
        
        **🏥 SAĞLIK DURUMU** (3-4 cümle)
        - Element dengesine göre sağlık önerileri
        - Dikkat edilmesi gereken sağlık konuları
        - Yaşam tarzı önerileri
        
        **⚖️ ELEMENT DENGESİ VE EKSİKLİKLERİ** (3-4 cümle)
        - Element dağılımının analizi
        - Eksik elementlerin etkileri
        - Dengeleme önerileri
        
        **🔮 GELECEK DÖNEMLERDEKİ FIRSATLAR** (3-4 cümle)
        - Önümüzdeki dönemlerdeki fırsatlar
        - Element döngülerinin etkileri
        - Uzun vadeli planlar ve hedefler
        
        **🛤️ GENEL YAŞAM YOLU VE KADER** (3-4 cümle)
        - Yaşam amacı ve misyon
        - Karmik dersler ve öğrenmeler
        - Ruhsal gelişim yolu
        
        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz.
        """
    
    elif language == 'en':
        return f"""
        You are an experienced Chinese fortune teller. Please provide a detailed Chinese fortune reading based on the following information:
        
        Birth Date: {dogum_tarihi}
        Birth Time: {dogum_saati}
        
        Ba Zi Analysis:
        - Year element: {ba_zi_result.get('year_element', 'Unknown')}
        - Month element: {ba_zi_result.get('month_element', 'Unknown')}
        - Day element: {ba_zi_result.get('day_element', 'Unknown')}
        - Hour element: {ba_zi_result.get('hour_element', 'Unknown')}
        
        Element distribution: {element_counts}
        
        Please provide a detailed Chinese fortune reading covering these topics:
        
        **🌟 PERSONALITY TRAITS AND CHARACTER ANALYSIS** (3-4 sentences)
        - Personality structure based on element combination
        - Strengths and weaknesses
        - Character traits and behavior patterns
        
        **💼 CAREER AND WORK LIFE** (3-4 sentences)
        - Professional compatibility and recommendations
        - Career opportunities and development areas
        - Challenges and solutions in work life
        
        **❤️ LOVE AND RELATIONSHIPS** (3-4 sentences)
        - Romantic compatibility analysis
        - Relationship dynamics and future
        - Emotional needs and expectations
        
        **🏥 HEALTH STATUS** (3-4 sentences)
        - Health recommendations based on element balance
        - Health issues to pay attention to
        - Lifestyle recommendations
        
        **⚖️ ELEMENT BALANCE AND DEFICIENCIES** (3-4 sentences)
        - Analysis of element distribution
        - Effects of missing elements
        - Balancing recommendations
        
        **🔮 FUTURE OPPORTUNITIES** (3-4 sentences)
        - Opportunities in upcoming periods
        - Effects of element cycles
        - Long-term plans and goals
        
        **🛤️ GENERAL LIFE PATH AND DESTINY** (3-4 sentences)
        - Life purpose and mission
        - Karmic lessons and learnings
        - Spiritual development path
        
        Write the interpretation in English, using a warm and understandable language.
        """
    
    elif language == 'de':
        return f"""
        Du bist ein erfahrener chinesischer Wahrsager. Bitte erstelle eine detaillierte chinesische Wahrsagung basierend auf den folgenden Informationen:
        
        Geburtsdatum: {dogum_tarihi}
        Geburtszeit: {dogum_saati}
        
        Ba Zi-Analyse:
        - Jahreselement: {ba_zi_result.get('year_element', 'Unbekannt')}
        - Monatselement: {ba_zi_result.get('month_element', 'Unbekannt')}
        - Tageselement: {ba_zi_result.get('day_element', 'Unbekannt')}
        - Stundenelement: {ba_zi_result.get('hour_element', 'Unbekannt')}
        
        Elementverteilung: {element_counts}
        
        Bitte erstelle eine detaillierte chinesische Wahrsagung, die diese Themen abdeckt:
        
        **🌟 PERSÖNLICHKEITSZÜGE UND CHARAKTERANALYSE** (3-4 Sätze)
        - Persönlichkeitsstruktur basierend auf Elementkombination
        - Stärken und Schwächen
        - Charaktereigenschaften und Verhaltensmuster
        
        **💼 KARRIERE UND ARBEITSLEBEN** (3-4 Sätze)
        - Berufliche Kompatibilität und Empfehlungen
        - Karrierechancen und Entwicklungsbereiche
        - Herausforderungen und Lösungen im Arbeitsleben
        
        **❤️ LIEBE UND BEZIEHUNGEN** (3-4 Sätze)
        - Romantische Kompatibilitätsanalyse
        - Beziehungsdynamik und Zukunft
        - Emotionale Bedürfnisse und Erwartungen
        
        **🏥 GESUNDHEITSZUSTAND** (3-4 Sätze)
        - Gesundheitsempfehlungen basierend auf Elementgleichgewicht
        - Gesundheitsprobleme, auf die geachtet werden sollte
        - Lebensstil-Empfehlungen
        
        **⚖️ ELEMENTGLEICHGEWICHT UND DEFIZITE** (3-4 Sätze)
        - Analyse der Elementverteilung
        - Auswirkungen fehlender Elemente
        - Ausgleichsempfehlungen
        
        **🔮 ZUKÜNFTIGE CHANCEN** (3-4 Sätze)
        - Chancen in kommenden Zeiträumen
        - Auswirkungen von Elementzyklen
        - Langfristige Pläne und Ziele
        
        **🛤️ ALLGEMEINER LEBENSWEG UND SCHICKSAL** (3-4 Sätze)
        - Lebenszweck und Mission
        - Karmische Lektionen und Lernprozesse
        - Spiritueller Entwicklungsweg
        
        Schreibe die Deutung auf Deutsch, verwende eine warme und verständliche Sprache.
        """

# Diğer prompt fonksiyonları buraya eklenebilir...
def get_coffee_prompt(language, **kwargs):
    soru = kwargs.get('soru', '')
    
    if language == 'tr':
        return f"""
        Sen deneyimli bir kahve falı uzmanısın. Aşağıdaki soruya göre detaylı bir kahve falı yorumu yap:

        Soru: {soru}

        Lütfen şu konuları kapsayan detaylı bir kahve falı yorumu yap:
        1. Fincanın genel görünümü ve enerji
        2. Fincanın farklı bölgelerindeki semboller
        3. Geçmiş, şimdi ve gelecek açısından yorum
        4. Kişisel ilişkiler ve aşk hayatı
        5. Kariyer ve iş hayatı
        6. Sağlık durumu
        7. Yakın gelecekteki olaylar
        8. Pratik öneriler ve tavsiyeler

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz. Kahve falı geleneğine uygun olarak yaz.
        """
    
    elif language == 'en':
        return f"""
        You are an experienced coffee fortune teller. Please provide a detailed coffee fortune reading based on the following question:

        Question: {soru}

        Please provide a detailed coffee fortune reading covering these topics:
        1. General appearance and energy of the cup
        2. Symbols in different areas of the cup
        3. Interpretation from past, present, and future perspectives
        4. Personal relationships and love life
        5. Career and work life
        6. Health status
        7. Upcoming events
        8. Practical advice and recommendations

        Write the interpretation in English, using a warm and understandable language. Follow coffee fortune telling traditions.
        """
    
    elif language == 'de':
        return f"""
        Du bist ein erfahrener Kaffeesatzleser. Bitte erstelle eine detaillierte Kaffeesatz-Deutung basierend auf der folgenden Frage:

        Frage: {soru}

        Bitte erstelle eine detaillierte Kaffeesatz-Deutung, die diese Themen abdeckt:
        1. Allgemeines Aussehen und Energie der Tasse
        2. Symbole in verschiedenen Bereichen der Tasse
        3. Deutung aus Vergangenheit, Gegenwart und Zukunft
        4. Persönliche Beziehungen und Liebesleben
        5. Karriere und Arbeitsleben
        6. Gesundheitszustand
        7. Kommende Ereignisse
        8. Praktische Ratschläge und Empfehlungen

        Schreibe die Deutung auf Deutsch, verwende eine warme und verständliche Sprache. Folge den Kaffeesatzlesen-Traditionen.
        """

def get_daily_prompt(language, **kwargs):
    tarih = kwargs.get('tarih', '')
    burc = kwargs.get('burc', '')
    
    if language == 'tr':
        return f"""
        Sen deneyimli bir günlük fal uzmanısın. Aşağıdaki bilgilere göre detaylı bir günlük fal yorumu yap:

        Tarih: {tarih}
        Burç: {burc}

        Lütfen şu konuları kapsayan detaylı bir günlük fal yorumu yap:
        1. Bugünün genel enerjisi ve atmosferi
        2. Burç özelliklerine göre günlük yorum
        3. Aşk ve ilişkiler açısından bugün
        4. Kariyer ve iş hayatı için bugün
        5. Sağlık ve enerji durumu
        6. Bugün dikkat edilmesi gerekenler
        7. Bugün yapılması önerilen aktiviteler
        8. Yarın için hazırlık önerileri

        Yorumu Türkçe olarak, samimi ve motive edici bir dille yaz.
        """
    
    elif language == 'en':
        return f"""
        You are an experienced daily fortune teller. Please provide a detailed daily fortune reading based on the following information:

        Date: {tarih}
        Zodiac Sign: {burc}

        Please provide a detailed daily fortune reading covering these topics:
        1. Today's general energy and atmosphere
        2. Daily interpretation based on zodiac characteristics
        3. Love and relationships for today
        4. Career and work life for today
        5. Health and energy status
        6. Things to pay attention to today
        7. Recommended activities for today
        8. Preparation suggestions for tomorrow

        Write the interpretation in English, using a warm and motivating language.
        """
    
    elif language == 'de':
        return f"""
        Du bist ein erfahrener Tageswahrsager. Bitte erstelle eine detaillierte Tageswahrsagung basierend auf den folgenden Informationen:

        Datum: {tarih}
        Tierkreiszeichen: {burc}

        Bitte erstelle eine detaillierte Tageswahrsagung, die diese Themen abdeckt:
        1. Heutige allgemeine Energie und Atmosphäre
        2. Tägliche Deutung basierend auf Tierkreiszeichen-Eigenschaften
        3. Liebe und Beziehungen für heute
        4. Karriere und Arbeitsleben für heute
        5. Gesundheits- und Energiezustand
        6. Dinge, auf die heute geachtet werden sollte
        7. Empfohlene Aktivitäten für heute
        8. Vorbereitungsvorschläge für morgen

        Schreibe die Deutung auf Deutsch, verwende eine warme und motivierende Sprache.
        """

def get_kabala_prompt(language, **kwargs):
    isim = kwargs.get('isim', '')
    dogum_tarihi = kwargs.get('dogumTarihi', '')
    hebrew_name = kwargs.get('hebrew_name', '')
    name_value = kwargs.get('name_value', '')
    reduced_value = kwargs.get('reduced_value', '')
    selected_sefirot = kwargs.get('selected_sefirot', [])
    
    sefirot_info = '\n'.join([
        f"- {sef['name']}: {sef['meaning']}"
        for sef in selected_sefirot
    ])
    
    if language == 'tr':
        return f"""
        Sen deneyimli bir Kabala uzmanısın. Aşağıdaki bilgilere göre detaylı bir Kabala falı yorumu yap:

        İsim: {isim}
        Doğum Tarihi: {dogum_tarihi}
        
        İbrani İsim Analizi:
        İbrani Harfler: {hebrew_name}
        İsim Değeri: {name_value}
        İndirgenmiş Değer: {reduced_value}
        
        Seçilen Sefirot:
        {sefirot_info}

        Lütfen şu konuları kapsayan detaylı bir Kabala yorumu yap:

        **🔢 İSİM NUMEROLOJİSİ VE RUHSAL ANLAMI** (3-4 cümle)
        - İsim değerinin ruhsal anlamı
        - İbrani harflerin kişilik üzerindeki etkisi
        - Numerolojik analiz ve yorumu

        **🌟 SEFİROTLARIN KİŞİLİK ÜZERİNDEKİ ETKİSİ** (3-4 cümle)
        - Seçilen sefirotların anlamı
        - Kişilik özelliklerine etkisi
        - Ruhsal enerji analizi

        **🛤️ RUHSAL YOL VE KADER ANALİZİ** (3-4 cümle)
        - Ruhsal yol ve kader çizgisi
        - Karmik etkiler ve dersler
        - Yaşam amacı ve hedefler

        **🎯 HAYAT AMACI VE MİSYON** (3-4 cümle)
        - Dünyevi misyon ve görevler
        - Ruhsal gelişim hedefleri
        - Kişisel potansiyel ve yetenekler

        **🌱 KİŞİSEL GELİŞİM ALANLARI** (3-4 cümle)
        - Geliştirilmesi gereken özellikler
        - Ruhsal büyüme fırsatları
        - Kişisel dönüşüm alanları

        **💫 RUHSAL TAVSİYELER VE REHBERLİK** (3-4 cümle)
        - Kabala felsefesine dayalı öneriler
        - Ruhsal pratikler ve meditasyon
        - Enerji dengeleme teknikleri

        **🔮 GELECEK DÖNEMLERDEKİ RUHSAL FIRSATLAR** (3-4 cümle)
        - Önümüzdeki dönemlerdeki fırsatlar
        - Ruhsal gelişim döngüleri
        - Karmik dersler ve öğrenmeler

        Yorumu Türkçe olarak, mistik ve ruhsal bir dille yaz. Kabala felsefesine uygun olarak yaz.
        """
    
    elif language == 'en':
        return f"""
        You are an experienced Kabala expert. Please provide a detailed Kabala reading based on the following information:

        Name: {isim}
        Birth Date: {dogum_tarihi}
        
        Hebrew Name Analysis:
        Hebrew Letters: {hebrew_name}
        Name Value: {name_value}
        Reduced Value: {reduced_value}
        
        Selected Sefirot:
        {sefirot_info}

        Please provide a detailed Kabala reading covering these topics:

        **🔢 NAME NUMEROLOGY AND SPIRITUAL MEANING** (3-4 sentences)
        - Spiritual meaning of name value
        - Effect of Hebrew letters on personality
        - Numerological analysis and interpretation

        **🌟 INFLUENCE OF SEFIROT ON PERSONALITY** (3-4 sentences)
        - Meaning of selected sefirot
        - Effect on personality traits
        - Spiritual energy analysis

        **🛤️ SPIRITUAL PATH AND DESTINY ANALYSIS** (3-4 sentences)
        - Spiritual path and destiny line
        - Karmic effects and lessons
        - Life purpose and goals

        **🎯 LIFE PURPOSE AND MISSION** (3-4 sentences)
        - Worldly mission and tasks
        - Spiritual development goals
        - Personal potential and talents

        **🌱 PERSONAL DEVELOPMENT AREAS** (3-4 sentences)
        - Traits that need development
        - Spiritual growth opportunities
        - Personal transformation areas

        **💫 SPIRITUAL ADVICE AND GUIDANCE** (3-4 sentences)
        - Recommendations based on Kabala philosophy
        - Spiritual practices and meditation
        - Energy balancing techniques

        **🔮 FUTURE SPIRITUAL OPPORTUNITIES** (3-4 sentences)
        - Opportunities in upcoming periods
        - Spiritual development cycles
        - Karmic lessons and learnings

        Write the interpretation in English, using a mystical and spiritual language. Follow Kabala philosophy.
        """
    
    elif language == 'de':
        return f"""
        Du bist ein erfahrener Kabala-Experte. Bitte erstelle eine detaillierte Kabala-Deutung basierend auf den folgenden Informationen:

        Name: {isim}
        Geburtsdatum: {dogum_tarihi}
        
        Hebräische Namensanalyse:
        Hebräische Buchstaben: {hebrew_name}
        Namenswert: {name_value}
        Reduzierter Wert: {reduced_value}
        
        Ausgewählte Sefirot:
        {sefirot_info}

        Bitte erstelle eine detaillierte Kabala-Deutung, die diese Themen abdeckt:

        **🔢 NAMENS-NUMEROLOGIE UND SPIRITUELLE BEDEUTUNG** (3-4 Sätze)
        - Spirituelle Bedeutung des Namenswerts
        - Wirkung der hebräischen Buchstaben auf die Persönlichkeit
        - Numerologische Analyse und Deutung

        **🌟 EINFLUSS DER SEFIROT AUF DIE PERSÖNLICHKEIT** (3-4 Sätze)
        - Bedeutung der ausgewählten Sefirot
        - Wirkung auf Persönlichkeitsmerkmale
        - Spirituelle Energieanalyse

        **🛤️ SPIRITUELLER WEG UND SCHICKSALSANALYSE** (3-4 Sätze)
        - Spiritueller Weg und Schicksalslinie
        - Karmische Wirkungen und Lektionen
        - Lebenszweck und Ziele

        **🎯 LEBENSZWIECK UND MISSION** (3-4 Sätze)
        - Weltliche Mission und Aufgaben
        - Spirituelle Entwicklungsziele
        - Persönliches Potenzial und Talente

        **🌱 PERSÖNLICHE ENTWICKLUNGSBEREICHE** (3-4 Sätze)
        - Eigenschaften, die entwickelt werden müssen
        - Spirituelle Wachstumschancen
        - Persönliche Transformationsbereiche

        **💫 SPIRITUELLE RATSCHLÄGE UND ANLEITUNG** (3-4 Sätze)
        - Empfehlungen basierend auf Kabala-Philosophie
        - Spirituelle Praktiken und Meditation
        - Energieausgleichstechniken

        **🔮 ZUKÜNFTIGE SPIRITUELLE CHANCEN** (3-4 Sätze)
        - Chancen in kommenden Zeiträumen
        - Spirituelle Entwicklungszyklen
        - Karmische Lektionen und Lernprozesse

        Schreibe die Deutung auf Deutsch, verwende eine mystische und spirituelle Sprache. Folge der Kabala-Philosophie.
        """

def get_yildizname_prompt(language, **kwargs):
    isim = kwargs.get('isim', '')
    anne_adi = kwargs.get('anneAdi', '')
    dogum_tarihi = kwargs.get('dogumTarihi', '')
    dogum_yeri = kwargs.get('dogumYeri', '')
    dogum_saati = kwargs.get('dogumSaati', '')
    
    if language == 'tr':
        return f"""
        Sen deneyimli bir yıldızname uzmanısın. Aşağıdaki bilgilere göre detaylı bir yıldızname falı yorumu yap:

        İsim: {isim}
        Anne Adı: {anne_adi}
        Doğum Tarihi: {dogum_tarihi}
        Doğum Yeri: {dogum_yeri}
        Doğum Saati: {dogum_saati}

        Lütfen şu konuları kapsayan detaylı bir yıldızname yorumu yap:

        **🌟 KİŞİLİK ÖZELLİKLERİ VE KARAKTER ANALİZİ** (3-4 cümle)
        - Doğum anındaki yıldız konumlarına göre kişilik
        - Güçlü ve zayıf yönler
        - Karakter özellikleri ve davranış kalıpları

        **💼 KARİYER VE İŞ HAYATI** (3-4 cümle)
        - Meslek uyumluluğu ve öneriler
        - Kariyer fırsatları ve gelişim alanları
        - İş hayatındaki zorluklar ve çözümler

        **❤️ AŞK VE İLİŞKİLER** (3-4 cümle)
        - Romantik uyumluluk analizi
        - İlişki dinamikleri ve gelecek
        - Duygusal ihtiyaçlar ve beklentiler

        **🏥 SAĞLIK DURUMU** (3-4 cümle)
        - Yıldız konumlarına göre sağlık önerileri
        - Dikkat edilmesi gereken sağlık konuları
        - Yaşam tarzı önerileri

        **⚖️ YILDIZ DENGESİ VE EKSİKLİKLERİ** (3-4 cümle)
        - Yıldız dağılımının analizi
        - Eksik yıldızların etkileri
        - Dengeleme önerileri

        **🔮 GELECEK DÖNEMLERDEKİ FIRSATLAR** (3-4 cümle)
        - Önümüzdeki dönemlerdeki fırsatlar
        - Yıldız döngülerinin etkileri
        - Uzun vadeli planlar ve hedefler

        **🛤️ GENEL YAŞAM YOLU VE KADER** (3-4 cümle)
        - Yaşam amacı ve misyon
        - Karmik dersler ve öğrenmeler
        - Ruhsal gelişim yolu

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz.
        """
    
    elif language == 'en':
        return f"""
        You are an experienced Yildizname expert. Please provide a detailed Yildizname reading based on the following information:

        Name: {isim}
        Mother's Name: {anne_adi}
        Birth Date: {dogum_tarihi}
        Birth Place: {dogum_yeri}
        Birth Time: {dogum_saati}

        Please provide a detailed Yildizname reading covering these topics:

        **🌟 PERSONALITY TRAITS AND CHARACTER ANALYSIS** (3-4 sentences)
        - Personality based on star positions at birth
        - Strengths and weaknesses
        - Character traits and behavior patterns

        **💼 CAREER AND WORK LIFE** (3-4 sentences)
        - Professional compatibility and recommendations
        - Career opportunities and development areas
        - Challenges and solutions in work life

        **❤️ LOVE AND RELATIONSHIPS** (3-4 sentences)
        - Romantic compatibility analysis
        - Relationship dynamics and future
        - Emotional needs and expectations

        **🏥 HEALTH STATUS** (3-4 sentences)
        - Health recommendations based on star positions
        - Health issues to pay attention to
        - Lifestyle recommendations

        **⚖️ STAR BALANCE AND DEFICIENCIES** (3-4 sentences)
        - Analysis of star distribution
        - Effects of missing stars
        - Balancing recommendations

        **🔮 FUTURE OPPORTUNITIES** (3-4 sentences)
        - Opportunities in upcoming periods
        - Effects of star cycles
        - Long-term plans and goals

        **🛤️ GENERAL LIFE PATH AND DESTINY** (3-4 sentences)
        - Life purpose and mission
        - Karmic lessons and learnings
        - Spiritual development path

        Write the interpretation in English, using a warm and understandable language.
        """
    
    elif language == 'de':
        return f"""
        Du bist ein erfahrener Yildizname-Experte. Bitte erstelle eine detaillierte Yildizname-Deutung basierend auf den folgenden Informationen:

        Name: {isim}
        Name der Mutter: {anne_adi}
        Geburtsdatum: {dogum_tarihi}
        Geburtsort: {dogum_yeri}
        Geburtszeit: {dogum_saati}

        Bitte erstelle eine detaillierte Yildizname-Deutung, die diese Themen abdeckt:

        **🌟 PERSÖNLICHKEITSZÜGE UND CHARAKTERANALYSE** (3-4 Sätze)
        - Persönlichkeit basierend auf Sternpositionen bei der Geburt
        - Stärken und Schwächen
        - Charaktereigenschaften und Verhaltensmuster

        **💼 KARRIERE UND ARBEITSLEBEN** (3-4 Sätze)
        - Berufliche Kompatibilität und Empfehlungen
        - Karrierechancen und Entwicklungsbereiche
        - Herausforderungen und Lösungen im Arbeitsleben

        **❤️ LIEBE UND BEZIEHUNGEN** (3-4 Sätze)
        - Romantische Kompatibilitätsanalyse
        - Beziehungsdynamik und Zukunft
        - Emotionale Bedürfnisse und Erwartungen

        **🏥 GESUNDHEITSZUSTAND** (3-4 Sätze)
        - Gesundheitsempfehlungen basierend auf Sternpositionen
        - Gesundheitsprobleme, auf die geachtet werden sollte
        - Lebensstil-Empfehlungen

        **⚖️ STERNENGLEICHGEWICHT UND DEFIZITE** (3-4 Sätze)
        - Analyse der Sternverteilung
        - Auswirkungen fehlender Sterne
        - Ausgleichsempfehlungen

        **🔮 ZUKÜNFTIGE CHANCEN** (3-4 Sätze)
        - Chancen in kommenden Zeiträumen
        - Auswirkungen von Sternzyklen
        - Langfristige Pläne und Ziele

        **🛤️ ALLGEMEINER LEBENSWEG UND SCHICKSAL** (3-4 Sätze)
        - Lebenszweck und Mission
        - Karmische Lektionen und Lernprozesse
        - Spiritueller Entwicklungsweg

        Schreibe die Deutung auf Deutsch, verwende eine warme und verständliche Sprache.
        """
