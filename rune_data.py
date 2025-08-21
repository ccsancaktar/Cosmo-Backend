# Gerçek Rün Alfabesi (Elder Futhark)
RUNES = [
    {
        "name": "Fehu",
        "symbol": "ᚠ",
        "meaning": "Sığır, zenginlik, refah, güç, enerji, yaratıcılık"
    },
    {
        "name": "Uruz", 
        "symbol": "ᚢ",
        "meaning": "Yaban öküzü, güç, dayanıklılık, cesaret, vahşi doğa"
    },
    {
        "name": "Thurisaz",
        "symbol": "ᚦ", 
        "meaning": "Dev, koruma, savunma, güç, çatışma, dönüşüm"
    },
    {
        "name": "Ansuz",
        "symbol": "ᚨ",
        "meaning": "Tanrı, ilham, bilgelik, iletişim, yaratıcılık, Odin"
    },
    {
        "name": "Raidho",
        "symbol": "ᚱ",
        "meaning": "Yolculuk, hareket, ilerleme, değişim, ritim, düzen"
    },
    {
        "name": "Kenaz",
        "symbol": "ᚲ",
        "meaning": "Meşale, aydınlanma, bilgi, yaratıcılık, dönüşüm, ateş"
    },
    {
        "name": "Gebo",
        "symbol": "ᚷ",
        "meaning": "Hediye, değişim, denge, ortaklık, cömertlik, uyum"
    },
    {
        "name": "Wunjo",
        "symbol": "ᚹ",
        "meaning": "Sevinç, mutluluk, uyum, başarı, iyi şans, topluluk"
    },
    {
        "name": "Hagalaz",
        "symbol": "ᚺ",
        "meaning": "Dolu, yıkım, doğal güçler, dönüşüm, temizlik, yenilik"
    },
    {
        "name": "Nauthiz",
        "symbol": "ᚾ",
        "meaning": "İhtiyaç, zorluk, sabır, dayanıklılık, büyüme, öğrenme"
    },
    {
        "name": "Isa",
        "symbol": "ᛁ",
        "meaning": "Buz, durağanlık, bekleme, içe dönüş, temizlik, netlik"
    },
    {
        "name": "Jera",
        "symbol": "ᛃ",
        "meaning": "Hasat, mevsimsel değişim, döngü, ödül, sabır, zaman"
    },
    {
        "name": "Eihwaz",
        "symbol": "ᛇ",
        "meaning": "Porsuk ağacı, dayanıklılık, koruma, güç, yaşam ağacı"
    },
    {
        "name": "Perthro",
        "symbol": "ᛈ",
        "meaning": "Zar, şans, gizem, kader, olasılık, gizli bilgi"
    },
    {
        "name": "Algiz",
        "symbol": "ᛉ",
        "meaning": "Geyik boynuzu, koruma, savunma, güvenlik, ilahi koruma"
    },
    {
        "name": "Sowilo",
        "symbol": "ᛊ",
        "meaning": "Güneş, enerji, güç, başarı, aydınlanma, yaşam gücü"
    },
    {
        "name": "Tiwaz",
        "symbol": "ᛏ",
        "meaning": "Savaş tanrısı, adalet, cesaret, zafer, liderlik, onur"
    },
    {
        "name": "Berkana",
        "symbol": "ᛒ",
        "meaning": "Huş ağacı, büyüme, yenilik, doğurganlık, aile, koruma"
    },
    {
        "name": "Ehwaz",
        "symbol": "ᛖ",
        "meaning": "At, hareket, güven, ortaklık, ilerleme, uyum"
    },
    {
        "name": "Mannaz",
        "symbol": "ᛗ",
        "meaning": "İnsan, topluluk, akıl, iletişim, sosyal bağlar, bilgelik"
    },
    {
        "name": "Laguz",
        "symbol": "ᛚ",
        "meaning": "Su, sezgi, duygular, akış, uyum, gizli bilgi"
    },
    {
        "name": "Ingwaz",
        "symbol": "ᛜ",
        "meaning": "Bereket tanrısı, büyüme, potansiyel, iç güç, dönüşüm"
    },
    {
        "name": "Dagaz",
        "symbol": "ᛞ",
        "meaning": "Gün, aydınlanma, dönüşüm, değişim, netlik, başlangıç"
    },
    {
        "name": "Othala",
        "symbol": "ᛟ",
        "meaning": "Mülk, miras, kökler, aile, güvenlik, geleneksel değerler"
    }
]

import random

def get_random_runes(count=3):
    """Rastgele rün seç ve %30 ihtimalle ters çevir"""
    selected_runes = random.sample(RUNES, min(count, len(RUNES)))
    
    # Her rün için %30 ihtimalle ters çevir
    for rune in selected_runes:
        if random.random() < 0.3:  # %30 ihtimal
            rune["reversed"] = True
            rune["reversed_meaning"] = get_reversed_meaning(rune["name"])
        else:
            rune["reversed"] = False
            rune["reversed_meaning"] = None
    
    return selected_runes

def get_rune_by_name(name):
    """İsme göre rün bul"""
    for rune in RUNES:
        if rune["name"].lower() == name.lower():
            return rune
    return None

def get_reversed_meaning(rune_name):
    """Rünün ters anlamını döndür"""
    reversed_meanings = {
        "Fehu": "Zenginlik kaybı, maddi zorluklar, israf",
        "Uruz": "Güçsüzlük, cesaretsizlik, enerji eksikliği",
        "Thurisaz": "Savunmasızlık, saldırı, kontrol kaybı",
        "Ansuz": "İletişim sorunları, ilham eksikliği, yanlış anlaşılma",
        "Raidho": "Yolculuk gecikmesi, hareket engeli, durgunluk",
        "Kenaz": "Bilgi eksikliği, karanlık, yaratıcılık engeli",
        "Gebo": "Dengesizlik, bencillik, ortaklık sorunları",
        "Wunjo": "Mutluluk kaybı, uyumsuzluk, başarısızlık",
        "Hagalaz": "Kontrolsüz değişim, yıkım, kaos",
        "Nauthiz": "Sabırsızlık, zorlukların artması, engeller",
        "Isa": "Hareket engeli, donma, ilerleme yokluğu",
        "Jera": "Gecikmiş ödüller, zaman kaybı, sabırsızlık",
        "Eihwaz": "Koruma eksikliği, güçsüzlük, dayanıksızlık",
        "Perthro": "Kötü şans, gizli tehlikeler, belirsizlik",
        "Algiz": "Koruma eksikliği, savunmasızlık, güvenlik sorunları",
        "Sowilo": "Enerji eksikliği, başarısızlık, karanlık dönem",
        "Tiwaz": "Adaletsizlik, cesaretsizlik, liderlik eksikliği",
        "Berkana": "Büyüme engeli, aile sorunları, koruma eksikliği",
        "Ehwaz": "Hareket engeli, güvensizlik, ilerleme yokluğu",
        "Mannaz": "İletişim sorunları, yalnızlık, akıl karışıklığı",
        "Laguz": "Duygusal karışıklık, sezgi engeli, akış sorunları",
        "Ingwaz": "Büyüme engeli, potansiyel kaybı, durgunluk",
        "Dagaz": "Değişim engeli, belirsizlik, aydınlanma gecikmesi",
        "Othala": "Miras sorunları, kök kaybı, güvenlik eksikliği"
    }
    
    return reversed_meanings.get(rune_name, "Ters anlam belirtilmemiş") 