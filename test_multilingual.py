#!/usr/bin/env python3
"""
Çok dilli prompt sistemi test script'i
"""

import sys
import os

# Prompts modülünü import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompts.multilingual import get_prompt_by_language, SUPPORTED_LANGUAGES

def test_prompts():
    """Tüm prompt'ları test et"""
    
    print("🌍 ÇOK DİLLİ PROMPT SİSTEMİ TESTİ")
    print("=" * 50)
    
    # Test verileri
    test_data = {
        'tarot': {
            'soru': 'Aşk hayatım nasıl olacak?',
            'cards': [
                {'name': 'Aşk', 'suit': 'Kupa'},
                {'name': 'Ay', 'suit': 'Kupa'},
                {'name': 'Yıldız', 'suit': 'Kupa'}
            ]
        },
        'coffee': {
            'soru': 'Kariyerimde ne olacak?'
        },
        'daily': {
            'tarih': '15 Aralık 2024',
            'burc': 'Aslan'
        },
        'kabala': {
            'isim': 'Ahmet',
            'dogumTarihi': '1990-05-15',
            'hebrew_name': 'אחמט',
            'name_value': 45,
            'reduced_value': 9,
            'selected_sefirot': [
                {'name': 'Keter (Taç)', 'description': 'İlahi irade, yüksek bilinç'},
                {'name': 'Hokmah (Bilgelik)', 'description': 'Erkek enerji, yaratıcı güç'}
            ]
        },
        'yildizname': {
            'isim': 'Fatma',
            'anneAdi': 'Ayşe',
            'dogumTarihi': '1985-08-20',
            'dogumYeri': 'İstanbul',
            'dogumSaati': '14:30'
        }
    }
    
    # Her fal türü için test et
    for fortune_type, data in test_data.items():
        print(f"\n🔮 {fortune_type.upper()} FALI TESTİ")
        print("-" * 30)
        
        for lang in SUPPORTED_LANGUAGES:
            try:
                prompt = get_prompt_by_language(fortune_type, lang, **data)
                
                # Prompt'un ilk 100 karakterini göster
                preview = prompt[:100].replace('\n', ' ').strip()
                print(f"✅ {lang.upper()}: {preview}...")
                
            except Exception as e:
                print(f"❌ {lang.upper()}: HATA - {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 TEST TAMAMLANDI!")

def test_language_validation():
    """Dil doğrulama testi"""
    
    print("\n🔍 DİL DOĞRULAMA TESTİ")
    print("-" * 30)
    
    # Geçerli diller
    valid_languages = ['tr', 'en', 'de']
    for lang in valid_languages:
        try:
            prompt = get_prompt_by_language('tarot', lang, soru='Test sorusu')
            print(f"✅ {lang.upper()}: Geçerli")
        except Exception as e:
            print(f"❌ {lang.upper()}: HATA - {str(e)}")
    
    # Geçersiz dil
    try:
        prompt = get_prompt_by_language('tarot', 'fr', soru='Test sorusu')
        print("✅ FR: Geçerli (varsayılan dil kullanıldı)")
    except Exception as e:
        print(f"❌ FR: HATA - {str(e)}")
    
    # Geçersiz fal türü
    try:
        prompt = get_prompt_by_language('invalid_type', 'tr', soru='Test sorusu')
        print("✅ Geçersiz fal türü: Hata yakalandı")
    except Exception as e:
        print(f"❌ Geçersiz fal türü: {str(e)}")

if __name__ == "__main__":
    test_prompts()
    test_language_validation()
