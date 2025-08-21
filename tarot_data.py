# Tarot Kartları Sistemi

import random
from typing import Dict, List

# Major Arcana (Büyük Arkana) Kartları
MAJOR_ARCANA = {
    "major_00_Fool": {
        "name": "Deli",
        "name_tr": "Deli",
        "meaning": "Yeni başlangıçlar, masumiyet, spontanlık, özgürlük, macera",
        "reversed_meaning": "Aptallık, risk alma, düşüncesizlik, kaçırılan fırsatlar",
        "image": "major_00_Fool.jpg"
    },
    "major_01_Magician": {
        "name": "Sihirbaz",
        "name_tr": "Sihirbaz",
        "meaning": "Yaratıcılık, beceri, güç, odaklanma, başarı",
        "reversed_meaning": "Yeteneklerin kötüye kullanımı, manipülasyon, güç kaybı",
        "image": "major_01_Magician.jpg"
    },
    "major_02_High_Priestess": {
        "name": "Yüksek Rahibe",
        "name_tr": "Yüksek Rahibe",
        "meaning": "Sezgi, gizem, bilgelik, içsel bilgi, gizli bilgiler",
        "reversed_meaning": "Sezgilerin reddedilmesi, gizli bilgilerin açığa çıkması",
        "image": "major_02_High_Priestess.jpg"
    },
    "major_03_Empress": {
        "name": "İmparatoriçe",
        "name_tr": "İmparatoriçe",
        "meaning": "Bereket, yaratıcılık, doğurganlık, bolluk, anne sevgisi",
        "reversed_meaning": "Yaratıcılık blokajı, bereket eksikliği, aşırı koruma",
        "image": "major_03_Empress.jpg"
    },
    "major_05_Hierophant": {
        "name": "Hierophant",
        "name_tr": "Hierophant",
        "meaning": "Geleneksel değerler, eğitim, dini inançlar, rehberlik",
        "reversed_meaning": "Dogmatik düşünceler, geleneksel değerlerin reddi",
        "image": "major_05_Hierophant.jpg"
    },
    "major_06_Lovers": {
        "name": "Aşıklar",
        "name_tr": "Aşıklar",
        "meaning": "Aşk, uyum, seçim, ilişki, romantizm",
        "reversed_meaning": "Uyumsuzluk, yanlış seçimler, aşk sorunları",
        "image": "major_06_Lovers.jpg"
    },
    "major_07_Chariot": {
        "name": "Savaş Arabası",
        "name_tr": "Savaş Arabası",
        "meaning": "Zafer, ilerleme, kararlılık, kontrol, başarı",
        "reversed_meaning": "Kontrol kaybı, yenilgi, engeller, kararsızlık",
        "image": "major_07_Chariot.jpg"
    },
    "major_08_Strength": {
        "name": "Güç",
        "name_tr": "Güç",
        "meaning": "İçsel güç, cesaret, sabır, kontrol, dayanıklılık",
        "reversed_meaning": "Güçsüzlük, korku, kontrol kaybı, zayıflık",
        "image": "major_08_Strength.jpg"
    },
    "major_09_Hermit": {
        "name": "Münzevi",
        "name_tr": "Münzevi",
        "meaning": "Yalnızlık, içe dönüş, bilgelik, rehberlik, arama",
        "reversed_meaning": "Aşırı yalnızlık, izolasyon, bilgelik reddi",
        "image": "major_09_Hermit.jpg"
    },
    "major_10_Wheel_of_Fortune": {
        "name": "Şans Çarkı",
        "name_tr": "Şans Çarkı",
        "meaning": "Değişim, şans, döngüler, fırsatlar, kader",
        "reversed_meaning": "Kötü şans, değişim korkusu, engeller",
        "image": "major_10_Wheel_of_Fortune.jpg"
    },
    "major_11_Justice": {
        "name": "Adalet",
        "name_tr": "Adalet",
        "meaning": "Adalet, denge, hakikat, kararlar, dürüstlük",
        "reversed_meaning": "Adaletsizlik, dengesizlik, yanlış kararlar",
        "image": "major_11_Justice.jpg"
    },
    "major_12_Hanged_Man": {
        "name": "Asılı Adam",
        "name_tr": "Asılı Adam",
        "meaning": "Fedakarlık, yeni bakış açısı, bekleme, teslimiyet",
        "reversed_meaning": "Gereksiz fedakarlık, direnç, değişim reddi",
        "image": "major_12_Hanged_Man.jpg"
    },
    "major_14_Temperance": {
        "name": "İtidal",
        "name_tr": "İtidal",
        "meaning": "Denge, uyum, sabır, ılımlılık, iyileşme",
        "reversed_meaning": "Dengesizlik, aşırılık, sabırsızlık",
        "image": "major_14_Temperance.jpg"
    },
    "major_15_Devil": {
        "name": "Şeytan",
        "name_tr": "Şeytan",
        "meaning": "Bağımlılık, karanlık taraf, materyalizm, tutku",
        "reversed_meaning": "Bağımlılıktan kurtulma, aydınlanma, özgürlük",
        "image": "major_15_Devil.jpg"
    },
    "major_16_Tower": {
        "name": "Kule",
        "name_tr": "Kule",
        "meaning": "Ani değişim, yıkım, aydınlanma, kaos, dönüşüm",
        "reversed_meaning": "Değişim korkusu, kaçırılan fırsatlar",
        "image": "major_16_Tower.jpg"
    },
    "major_17_Star": {
        "name": "Yıldız",
        "name_tr": "Yıldız",
        "meaning": "Umut, ilham, iyileşme, rehberlik, manevi yol",
        "reversed_meaning": "Umut kaybı, ilham eksikliği, karamsarlık",
        "image": "major_17_Star.jpg"
    },
    "major_18_Moon": {
        "name": "Ay",
        "name_tr": "Ay",
        "meaning": "Sezgi, gizem, yanılsama, bilinçaltı, korkular",
        "reversed_meaning": "Gizemlerin çözülmesi, netlik, korkuların yenilmesi",
        "image": "major_18_Moon.jpg"
    },
    "major_19_Sun": {
        "name": "Güneş",
        "name_tr": "Güneş",
        "meaning": "Mutluluk, başarı, enerji, pozitiflik, aydınlanma",
        "reversed_meaning": "Geçici mutsuzluk, aşırı iyimserlik",
        "image": "major_19_Sun.jpg"
    },
    "major_20_Judgement": {
        "name": "Yargı",
        "name_tr": "Yargı",
        "meaning": "Yeniden doğuş, aydınlanma, çağrı, dönüşüm",
        "reversed_meaning": "Yeniden doğuş reddi, çağrıyı duymama",
        "image": "major_20_Judgement.jpg"
    },
    "major_21_World": {
        "name": "Dünya",
        "name_tr": "Dünya",
        "meaning": "Tamamlanma, başarı, bütünlük, seyahat, evrensel uyum",
        "reversed_meaning": "Tamamlanmamış işler, eksiklik hissi",
        "image": "major_21_World.jpg"
    }
}

# Minor Arcana (Küçük Arkana) - Cups (Kupa)
CUPS = {
    "cups01": {"name": "Ace of Cups", "name_tr": "Kupa Ası", "meaning": "Yeni aşk, duygusal başlangıç, sevgi", "reversed_meaning": "Duygusal blokaj, aşk kaybı", "image": "cups01.jpg"},
    "cups02": {"name": "Two of Cups", "name_tr": "İki Kupa", "meaning": "Aşk, uyum, ortaklık, dostluk", "reversed_meaning": "Uyumsuzluk, ayrılık, çatışma", "image": "cups02.jpg"},
    "cups03": {"name": "Three of Cups", "name_tr": "Üç Kupa", "meaning": "Kutlama, neşe, arkadaşlık, topluluk", "reversed_meaning": "Yalnızlık, sosyal izolasyon", "image": "cups03.jpg"},
    "cups04": {"name": "Four of Cups", "name_tr": "Dört Kupa", "meaning": "Doyumsuzluk, kaçırılan fırsatlar, içe dönüş", "reversed_meaning": "Yeni fırsatlar, uyanış", "image": "cups04.jpg"},
    "cups05": {"name": "Five of Cups", "name_tr": "Beş Kupa", "meaning": "Hayal kırıklığı, kayıp, üzüntü", "reversed_meaning": "İyileşme, yeni umutlar", "image": "cups05.jpg"},
    "cups06": {"name": "Six of Cups", "name_tr": "Altı Kupa", "meaning": "Nostalji, çocukluk, masumiyet, geçmiş", "reversed_meaning": "Geçmişe takılı kalma", "image": "cups06.jpg"},
    "cups07": {"name": "Seven of Cups", "name_tr": "Yedi Kupa", "meaning": "Seçenekler, hayaller, kararsızlık", "reversed_meaning": "Netlik, karar verme", "image": "cups07.jpg"},
    "cups08": {"name": "Eight of Cups", "name_tr": "Sekiz Kupa", "meaning": "Ayrılış, arama, içe dönüş", "reversed_meaning": "Dönüş, yeniden başlama", "image": "cups08.jpg"},
    "cups09": {"name": "Nine of Cups", "name_tr": "Dokuz Kupa", "meaning": "Doyum, mutluluk, arzuların gerçekleşmesi", "reversed_meaning": "Aşırı doyum, materyalizm", "image": "cups09.jpg"},
    "cups10": {"name": "Ten of Cups", "name_tr": "On Kupa", "meaning": "Aile mutluluğu, tamamlanma, uyum", "reversed_meaning": "Aile sorunları, uyumsuzluk", "image": "cups10.jpg"},
    "cups11": {"name": "Page of Cups", "name_tr": "Kupa Valesi", "meaning": "Yaratıcı mesaj, romantik haber", "reversed_meaning": "Duygusal olgunluk eksikliği", "image": "cups11.jpg"},
    "cups12": {"name": "Knight of Cups", "name_tr": "Kupa Şövalyesi", "meaning": "Romantik teklif, sanatsal ilham", "reversed_meaning": "Duygusal manipülasyon", "image": "cups12.jpg"},
    "cups13": {"name": "Queen of Cups", "name_tr": "Kupa Kraliçesi", "meaning": "Sezgisel, şefkatli, duygusal bilgelik", "reversed_meaning": "Duygusal istismar", "image": "cups13.jpg"},
    "cups14": {"name": "King of Cups", "name_tr": "Kupa Kralı", "meaning": "Duygusal olgunluk, bilgelik, rehberlik", "reversed_meaning": "Duygusal manipülasyon", "image": "cups14.jpg"}
}

# Minor Arcana - Swords (Kılıç)
SWORDS = {
    "swords01": {"name": "Ace of Swords", "name_tr": "Kılıç Ası", "meaning": "Yeni fikirler, keskinlik, zafer", "reversed_meaning": "Kafa karışıklığı, keskinlik kaybı", "image": "swords01.jpg"},
    "swords02": {"name": "Two of Swords", "name_tr": "İki Kılıç", "meaning": "Kararsızlık, denge, seçim", "reversed_meaning": "Karar verme, netlik", "image": "swords02.jpg"},
    "swords03": {"name": "Three of Swords", "name_tr": "Üç Kılıç", "meaning": "Kalp kırıklığı, acı, ihanet", "reversed_meaning": "İyileşme, affetme", "image": "swords03.jpg"},
    "swords04": {"name": "Four of Swords", "name_tr": "Dört Kılıç", "meaning": "Dinlenme, iyileşme, meditasyon", "reversed_meaning": "Aşırı dinlenme, tembellik", "image": "swords04.jpg"},
    "swords05": {"name": "Five of Swords", "name_tr": "Beş Kılıç", "meaning": "Yenilgi, çatışma, kayıp", "reversed_meaning": "Uzlaşma, barış", "image": "swords05.jpg"},
    "swords06": {"name": "Six of Swords", "name_tr": "Altı Kılıç", "meaning": "Geçiş, yolculuk, iyileşme", "reversed_meaning": "Geçmişe takılı kalma", "image": "swords06.jpg"},
    "swords07": {"name": "Seven of Swords", "name_tr": "Yedi Kılıç", "meaning": "Gizlilik, kaçış, strateji", "reversed_meaning": "Açıklık, dürüstlük", "image": "swords07.jpg"},
    "swords08": {"name": "Eight of Swords", "name_tr": "Sekiz Kılıç", "meaning": "Kısıtlama, korku, engeller", "reversed_meaning": "Özgürlük, kurtuluş", "image": "swords08.jpg"},
    "swords09": {"name": "Nine of Swords", "name_tr": "Dokuz Kılıç", "meaning": "Endişe, korku, kabuslar", "reversed_meaning": "Endişelerin azalması", "image": "swords09.jpg"},
    "swords10": {"name": "Ten of Swords", "name_tr": "On Kılıç", "meaning": "Son, yenilgi, acı", "reversed_meaning": "Yeni başlangıç, iyileşme", "image": "swords10.jpg"},
    "swords11": {"name": "Page of Swords", "name_tr": "Kılıç Valesi", "meaning": "Yeni fikirler, haberler, öğrenme", "reversed_meaning": "Düşüncesizlik, acelecilik", "image": "swords11.jpg"},
    "swords12": {"name": "Knight of Swords", "name_tr": "Kılıç Şövalyesi", "meaning": "Hızlı hareket, cesaret, çatışma", "reversed_meaning": "Acelecilik, düşüncesizlik", "image": "swords12.jpg"},
    "swords13": {"name": "Queen of Swords", "name_tr": "Kılıç Kraliçesi", "meaning": "Bağımsızlık, keskin zeka, dürüstlük", "reversed_meaning": "Soğukluk, acımasızlık", "image": "swords13.jpg"},
    "swords14": {"name": "King of Swords", "name_tr": "Kılıç Kralı", "meaning": "Mantık, adalet, liderlik", "reversed_meaning": "Katılık, adaletsizlik", "image": "swords14.jpg"}
}

# Minor Arcana - Wands (Değnek)
WANDS = {
    "wands01": {"name": "Ace of Wands", "name_tr": "Değnek Ası", "meaning": "Yeni fırsatlar, yaratıcılık, enerji", "reversed_meaning": "Enerji kaybı, fırsat kaçırma", "image": "wands01.jpg"},
    "wands02": {"name": "Two of Wands", "name_tr": "İki Değnek", "meaning": "Planlama, seçim, gelecek", "reversed_meaning": "Kararsızlık, korku", "image": "wands02.jpg"},
    "wands03": {"name": "Three of Wands", "name_tr": "Üç Değnek", "meaning": "Genişleme, keşif, büyüme", "reversed_meaning": "Gecikme, engeller", "image": "wands03.jpg"},
    "wands04": {"name": "Four of Wands", "name_tr": "Dört Değnek", "meaning": "Kutlama, uyum, başarı", "reversed_meaning": "Geçici mutluluk", "image": "wands04.jpg"},
    "wands05": {"name": "Five of Wands", "name_tr": "Beş Değnek", "meaning": "Rekabet, çatışma, mücadele", "reversed_meaning": "Uzlaşma, işbirliği", "image": "wands05.jpg"},
    "wands06": {"name": "Six of Wands", "name_tr": "Altı Değnek", "meaning": "Zafer, başarı, ilerleme", "reversed_meaning": "Gurur, aşırı güven", "image": "wands06.jpg"},
    "wands07": {"name": "Seven of Wands", "name_tr": "Yedi Değnek", "meaning": "Savunma, kararlılık, mücadele", "reversed_meaning": "Savunmasızlık, zayıflık", "image": "wands07.jpg"},
    "wands08": {"name": "Eight of Wands", "name_tr": "Sekiz Değnek", "meaning": "Hızlı hareket, haberler, ilerleme", "reversed_meaning": "Gecikme, engeller", "image": "wands08.jpg"},
    "wands09": {"name": "Nine of Wands", "name_tr": "Dokuz Değnek", "meaning": "Dayanıklılık, savunma, hazırlık", "reversed_meaning": "Yorgunluk, savunmasızlık", "image": "wands09.jpg"},
    "wands10": {"name": "Ten of Wands", "name_tr": "On Değnek", "meaning": "Yük, sorumluluk, zorluk", "reversed_meaning": "Yükten kurtulma", "image": "wands10.jpg"},
    "wands11": {"name": "Page of Wands", "name_tr": "Değnek Valesi", "meaning": "Yeni fikirler, ilham, mesaj", "reversed_meaning": "Düşüncesizlik, acelecilik", "image": "wands11.jpg"},
    "wands12": {"name": "Knight of Wands", "name_tr": "Değnek Şövalyesi", "meaning": "Aksiyon, macera, tutku", "reversed_meaning": "Acelecilik, düşüncesizlik", "image": "wands12.jpg"},
    "wands13": {"name": "Queen of Wands", "name_tr": "Değnek Kraliçesi", "meaning": "Güçlü, bağımsız, yaratıcı", "reversed_meaning": "Dominant, kontrolcü", "image": "wands13.jpg"},
    "wands14": {"name": "King of Wands", "name_tr": "Değnek Kralı", "meaning": "Liderlik, yaratıcılık, kararlılık", "reversed_meaning": "Dominant, otoriter", "image": "wands14.jpg"}
}

# Minor Arcana - Pentacles (Para)
PENTACLES = {
    "pents01": {"name": "Ace of Pentacles", "name_tr": "Para Ası", "meaning": "Yeni fırsatlar, maddi başarı", "reversed_meaning": "Fırsat kaçırma, maddi kayıp", "image": "pents01.jpg"},
    "pents02": {"name": "Two of Pentacles", "name_tr": "İki Para", "meaning": "Denge, uyum, esneklik", "reversed_meaning": "Dengesizlik, kararsızlık", "image": "pents02.jpg"},
    "pents03": {"name": "Three of Pentacles", "name_tr": "Üç Para", "meaning": "İşbirliği, beceri, başarı", "reversed_meaning": "Uyumsuzluk, beceri eksikliği", "image": "pents03.jpg"},
    "pents04": {"name": "Four of Pentacles", "name_tr": "Dört Para", "meaning": "Materyalizm, güvenlik, tutuculuk", "reversed_meaning": "Cömertlik, açıklık", "image": "pents04.jpg"},
    "pents05": {"name": "Five of Pentacles", "name_tr": "Beş Para", "meaning": "Yoksulluk, izolasyon, hastalık", "reversed_meaning": "İyileşme, toparlanma", "image": "pents05.jpg"},
    "pents06": {"name": "Six of Pentacles", "name_tr": "Altı Para", "meaning": "Cömertlik, yardım, denge", "reversed_meaning": "Cimrilik, dengesizlik", "image": "pents06.jpg"},
    "pents07": {"name": "Seven of Pentacles", "name_tr": "Yedi Para", "meaning": "Sabır, yatırım, bekleme", "reversed_meaning": "Sabırsızlık, acelecilik", "image": "pents07.jpg"},
    "pents08": {"name": "Eight of Pentacles", "name_tr": "Sekiz Para", "meaning": "Çalışma, beceri geliştirme", "reversed_meaning": "Tembellik, beceri eksikliği", "image": "pents08.jpg"},
    "pents09": {"name": "Nine of Pentacles", "name_tr": "Dokuz Para", "meaning": "Bağımsızlık, lüks, başarı", "reversed_meaning": "Bağımlılık, materyalizm", "image": "pents09.jpg"},
    "pents10": {"name": "Ten of Pentacles", "name_tr": "On Para", "meaning": "Aile, zenginlik, güvenlik", "reversed_meaning": "Aile sorunları, maddi kayıp", "image": "pents10.jpg"},
    "pents11": {"name": "Page of Pentacles", "name_tr": "Para Valesi", "meaning": "Yeni fırsatlar, öğrenme", "reversed_meaning": "Fırsat kaçırma, tembellik", "image": "pents11.jpg"},
    "pents12": {"name": "Knight of Pentacles", "name_tr": "Para Şövalyesi", "meaning": "Çalışma, güvenilirlik", "reversed_meaning": "Tembellik, güvenilmezlik", "image": "pents12.jpg"},
    "pents13": {"name": "Queen of Pentacles", "name_tr": "Para Kraliçesi", "meaning": "Pratiklik, bereket, şefkat", "reversed_meaning": "Materyalizm, cimrilik", "image": "pents13.jpg"},
    "pents14": {"name": "King of Pentacles", "name_tr": "Para Kralı", "meaning": "Başarı, güvenilirlik, pratiklik", "reversed_meaning": "Materyalizm, katılık", "image": "pents14.jpg"}
}

def get_random_tarot_cards(count: int = 3) -> List[Dict]:
    """
    Rastgele tarot kartları seç
    """
    all_cards = {}
    all_cards.update(MAJOR_ARCANA)
    all_cards.update(CUPS)
    all_cards.update(SWORDS)
    all_cards.update(WANDS)
    all_cards.update(PENTACLES)
    
    selected_cards = []
    card_keys = list(all_cards.keys())
    
    for _ in range(count):
        card_key = random.choice(card_keys)
        card = all_cards[card_key].copy()
        card['key'] = card_key
        
        # Kartın ters olup olmadığını belirle (%30 ihtimal)
        card['reversed'] = random.random() < 0.3
        
        selected_cards.append(card)
    
    return selected_cards

def get_card_meaning(card: Dict) -> str:
    """
    Kartın anlamını döndür (düz veya ters)
    """
    if card.get('reversed', False):
        return card.get('reversed_meaning', card.get('meaning', ''))
    else:
        return card.get('meaning', '')

def get_all_tarot_cards() -> List[Dict]:
    """
    Tüm tarot kartlarını döndür
    """
    all_cards = []
    
    # Major Arcana kartlarını ekle
    for key, card in MAJOR_ARCANA.items():
        card_copy = card.copy()
        card_copy['key'] = key
        all_cards.append(card_copy)
    
    # Minor Arcana kartlarını ekle
    for key, card in CUPS.items():
        card_copy = card.copy()
        card_copy['key'] = key
        all_cards.append(card_copy)
    
    for key, card in SWORDS.items():
        card_copy = card.copy()
        card_copy['key'] = key
        all_cards.append(card_copy)
    
    for key, card in WANDS.items():
        card_copy = card.copy()
        card_copy['key'] = key
        all_cards.append(card_copy)
    
    for key, card in PENTACLES.items():
        card_copy = card.copy()
        card_copy['key'] = key
        all_cards.append(card_copy)
    
    return all_cards

def get_card_description(card: Dict) -> str:
    """
    Kartın açıklamasını döndür
    """
    status = "TERS" if card.get('reversed', False) else "DÜZ"
    return f"{card['name_tr']} ({status}) - {get_card_meaning(card)}" 