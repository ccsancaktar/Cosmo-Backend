# Çin Falı (Ba Zi - Sekiz Karakter) Sistemi

import datetime
from typing import Dict, List, Tuple

# 5 Element ve özellikleri
ELEMENTS = {
    "Metal": {
        "name_tr": "Metal",
        "nature": "Yin",
        "color": "Beyaz, Gümüş",
        "direction": "Batı",
        "season": "Sonbahar",
        "characteristics": "Güçlü irade, kararlılık, adalet, liderlik"
    },
    "Water": {
        "name_tr": "Su",
        "nature": "Yin", 
        "color": "Siyah, Mavi",
        "direction": "Kuzey",
        "season": "Kış",
        "characteristics": "Bilgelik, uyum, esneklik, sezgi"
    },
    "Wood": {
        "name_tr": "Ağaç",
        "nature": "Yang",
        "color": "Yeşil",
        "direction": "Doğu", 
        "season": "İlkbahar",
        "characteristics": "Büyüme, yaratıcılık, esneklik, vizyon"
    },
    "Fire": {
        "name_tr": "Ateş",
        "nature": "Yang",
        "color": "Kırmızı",
        "direction": "Güney",
        "season": "Yaz",
        "characteristics": "Enerji, tutku, liderlik, dönüşüm"
    },
    "Earth": {
        "name_tr": "Toprak",
        "nature": "Neutral",
        "color": "Sarı, Kahverengi",
        "direction": "Merkez",
        "season": "Geçiş dönemleri",
        "characteristics": "Denge, güvenilirlik, pratiklik, sabır"
    }
}

# Çin Takvimi - Yıl Elementleri
YEAR_ELEMENTS = {
    0: "Metal", 1: "Metal", 2: "Water", 3: "Water", 4: "Wood", 
    5: "Wood", 6: "Fire", 7: "Fire", 8: "Earth", 9: "Earth"
}

# Çin Takvimi - Ay Elementleri  
MONTH_ELEMENTS = {
    1: "Water", 2: "Water", 3: "Wood", 4: "Wood", 5: "Fire",
    6: "Fire", 7: "Earth", 8: "Earth", 9: "Metal", 10: "Metal",
    11: "Water", 12: "Water"
}

# Çin Takvimi - Gün Elementleri (1-31 arası)
DAY_ELEMENTS = {
    1: "Metal", 2: "Water", 3: "Wood", 4: "Fire", 5: "Earth",
    6: "Metal", 7: "Water", 8: "Wood", 9: "Fire", 10: "Earth",
    11: "Metal", 12: "Water", 13: "Wood", 14: "Fire", 15: "Earth",
    16: "Metal", 17: "Water", 18: "Wood", 19: "Fire", 20: "Earth",
    21: "Metal", 22: "Water", 23: "Wood", 24: "Fire", 25: "Earth",
    26: "Metal", 27: "Water", 28: "Wood", 29: "Fire", 30: "Earth",
    31: "Metal"
}

# Saat Elementleri
HOUR_ELEMENTS = {
    23: "Water", 0: "Water", 1: "Water", 2: "Water", 3: "Wood",
    4: "Wood", 5: "Wood", 6: "Wood", 7: "Fire", 8: "Fire",
    9: "Fire", 10: "Fire", 11: "Earth", 12: "Earth", 13: "Earth",
    14: "Earth", 15: "Metal", 16: "Metal", 17: "Metal", 18: "Metal",
    19: "Water", 20: "Water", 21: "Water", 22: "Water"
}

# Element Uyumları
ELEMENT_COMPATIBILITY = {
    "Metal": {"generates": "Water", "controls": "Wood", "controlled_by": "Fire"},
    "Water": {"generates": "Wood", "controls": "Fire", "controlled_by": "Earth"},
    "Wood": {"generates": "Fire", "controls": "Earth", "controlled_by": "Metal"},
    "Fire": {"generates": "Earth", "controls": "Metal", "controlled_by": "Water"},
    "Earth": {"generates": "Metal", "controls": "Water", "controlled_by": "Wood"}
}

def calculate_ba_zi(birth_date: str, birth_time: str) -> Dict:
    """
    Ba Zi (Sekiz Karakter) hesaplama
    """
    try:
        # Tarih ve saati parse et
        date_obj = datetime.datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
        
        # Yıl, ay, gün, saat elementlerini hesapla
        print(f"DEBUG: Date: {date_obj}, Year: {date_obj.year}, Month: {date_obj.month}, Day: {date_obj.day}, Hour: {date_obj.hour}")
        year_element = YEAR_ELEMENTS[date_obj.year % 10]
        print(f"DEBUG: Year element: {year_element}")
        month_element = MONTH_ELEMENTS[date_obj.month]
        print(f"DEBUG: Month element: {month_element}")
        day_element = DAY_ELEMENTS[date_obj.day]
        print(f"DEBUG: Day element: {day_element}")
        hour_element = HOUR_ELEMENTS[date_obj.hour]
        print(f"DEBUG: Hour element: {hour_element}")
        
        # Yin-Yang analizi
        yin_yang_balance = analyze_yin_yang([year_element, month_element, day_element, hour_element])
        
        # Element analizi
        element_analysis = analyze_elements([year_element, month_element, day_element, hour_element])
        
        # Uyumlu elementler
        compatible_elements = find_compatible_elements(element_analysis)
        
        # Kişilik analizi
        personality = analyze_personality(element_analysis, yin_yang_balance)
        
        return {
            "year_element": year_element,
            "month_element": month_element, 
            "day_element": day_element,
            "hour_element": hour_element,
            "yin_yang_balance": yin_yang_balance,
            "element_analysis": element_analysis,
            "compatible_elements": compatible_elements,
            "personality": personality,
            "birth_date": birth_date,
            "birth_time": birth_time
        }
        
    except Exception as e:
        return {"error": f"Hesaplama hatası: {str(e)}"}

def analyze_yin_yang(elements: List[str]) -> Dict:
    """Yin-Yang dengesi analizi"""
    yin_count = sum(1 for elem in elements if ELEMENTS[elem]["nature"] == "Yin")
    yang_count = sum(1 for elem in elements if ELEMENTS[elem]["nature"] == "Yang")
    neutral_count = sum(1 for elem in elements if ELEMENTS[elem]["nature"] == "Neutral")
    
    total = len(elements)
    yin_percentage = (yin_count / total) * 100
    yang_percentage = (yang_count / total) * 100
    
    if yin_percentage > 60:
        balance = "Yin Ağırlıklı"
        description = "Sakin, içe dönük, sezgisel, derin düşünceli"
    elif yang_percentage > 60:
        balance = "Yang Ağırlıklı" 
        description = "Enerjik, dışa dönük, aktif, liderlik özellikli"
    else:
        balance = "Dengeli"
        description = "Denge ve uyum içinde, esnek, adaptif"
    
    return {
        "balance": balance,
        "description": description,
        "yin_percentage": yin_percentage,
        "yang_percentage": yang_percentage,
        "neutral_count": neutral_count
    }

def analyze_elements(elements: List[str]) -> Dict:
    """Element analizi"""
    element_counts = {}
    for element in elements:
        element_counts[element] = element_counts.get(element, 0) + 1
    
    # En güçlü element
    strongest_element = max(element_counts, key=element_counts.get)
    
    # Eksik elementler
    missing_elements = [elem for elem in ELEMENTS.keys() if elem not in element_counts]
    
    return {
        "element_counts": element_counts,
        "strongest_element": strongest_element,
        "missing_elements": missing_elements,
        "total_elements": len(elements)
    }

def find_compatible_elements(element_analysis: Dict) -> List[str]:
    """Uyumlu elementleri bul"""
    strongest = element_analysis["strongest_element"]
    compatible = []
    
    # Üreten element
    compatible.append(ELEMENT_COMPATIBILITY[strongest]["generates"])
    
    # Kontrol edilen element
    compatible.append(ELEMENT_COMPATIBILITY[strongest]["controls"])
    
    return compatible

def analyze_personality(element_analysis: Dict, yin_yang: Dict) -> Dict:
    """Kişilik analizi"""
    strongest = element_analysis["strongest_element"]
    element_info = ELEMENTS[strongest]
    
    return {
        "main_characteristics": element_info["characteristics"],
        "lucky_colors": element_info["color"],
        "lucky_direction": element_info["direction"],
        "lucky_season": element_info["season"],
        "career_suggestions": get_career_suggestions(strongest),
        "relationship_advice": get_relationship_advice(strongest, yin_yang["balance"])
    }

def get_career_suggestions(element: str) -> List[str]:
    """Element bazlı kariyer önerileri"""
    career_map = {
        "Metal": ["Liderlik", "Hukuk", "Finans", "Mühendislik", "Askerlik"],
        "Water": ["Danışmanlık", "Psikoloji", "Sanat", "Araştırma", "Eğitim"],
        "Wood": ["Yaratıcılık", "Tasarım", "Pazarlama", "Çevre", "Sağlık"],
        "Fire": ["Satış", "Medya", "Eğlence", "Spor", "Teknoloji"],
        "Earth": ["Yönetim", "İnşaat", "Tarım", "Hizmet", "Güvenlik"]
    }
    return career_map.get(element, ["Genel işler"])

def get_relationship_advice(element: str, yin_yang_balance: str) -> str:
    """İlişki tavsiyesi"""
    advice_map = {
        "Metal": "Güçlü irade ve kararlılık ile ilişkilerde liderlik rolü üstlenir",
        "Water": "Sezgisel ve uyumlu yaklaşım ile ilişkilerde denge sağlar",
        "Wood": "Yaratıcı ve büyüme odaklı yaklaşım ile ilişkileri geliştirir",
        "Fire": "Tutkulu ve enerjik yaklaşım ile ilişkilerde heyecan yaratır",
        "Earth": "Güvenilir ve pratik yaklaşım ile ilişkilerde istikrar sağlar"
    }
    return advice_map.get(element, "Genel ilişki tavsiyesi") 