from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Reading
from tokens import spend_tokens_for_reading
from prompts.multilingual import get_prompt_by_language
from g4f import Client
from chinese_data import calculate_ba_zi, ELEMENTS
from rate_limiting import fal_rate_limit

# G4F client'ı başlat
client = Client()

def format_element_counts(element_counts):
    """Element sayılarını formatla"""
    formatted = []
    for element, count in element_counts.items():
        if count > 0:
            formatted.append(f"{element}: {count}")
    return ", ".join(formatted) if formatted else "Hiçbiri"

def register_chinese_routes(app):
    @app.route('/api/chinese', methods=['POST'])
    @jwt_required()
    @fal_rate_limit()
    def chinese_fortune():
        try:
            user_id = get_jwt_identity()
            user = User.find_by_id(user_id)
            
            if not user:
                return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
            
            data = request.get_json()
            
            # Gerekli alanları kontrol et
            required_fields = ['dogumTarihi', 'dogumSaati']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} alanı gereklidir'}), 422
            
            # Dil parametresini al (varsayılan: Türkçe)
            language = data.get('language', 'tr')
            if language not in ['tr', 'en', 'de']:
                language = 'tr'
            
            # Premium durumunu kontrol et
            is_premium = user.has_active_premium()
            
            # Premium değilse token kontrolü yap
            if not is_premium:
                success, message = spend_tokens_for_reading(user_id, 'chinese')
                if not success:
                    return jsonify({'error': message}), 400
                # Token harcandıktan sonra kullanıcı bilgilerini güncelle
                user = User.find_by_id(user_id)
            
            # Ba Zi hesapla
            print(f"Chinese API - Dogum tarihi: {data['dogumTarihi']}, Dogum saati: {data['dogumSaati']}")
            ba_zi_result = calculate_ba_zi(data['dogumTarihi'], data['dogumSaati'])
            
            if not ba_zi_result or 'error' in ba_zi_result:
                error_msg = ba_zi_result.get('error', 'Doğum tarihi ve saati hesaplanamadı') if ba_zi_result else 'Doğum tarihi ve saati hesaplanamadı'
                return jsonify({'error': error_msg}), 422
            
            # Element sayılarını hesapla
            element_counts = {}
            for element in ELEMENTS:
                element_counts[element] = 0
            
            for pillar in ['year', 'month', 'day', 'hour']:
                if pillar in ba_zi_result:
                    element = ba_zi_result[f"{pillar}_element"]
                    element_counts[element] += 1
            
            # Çok dilli prompt sistemi kullan
            prompt = get_prompt_by_language(
                'chinese', 
                language, 
                dogumTarihi=data['dogumTarihi'],
                dogumSaati=data['dogumSaati'],
                ba_zi=ba_zi_result,
                element_counts=format_element_counts(element_counts)
            )
            
            # G4F ile yanıt al
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    web_search=False
                )
                
                yorum = response.choices[0].message.content
                print(f"Chinese Fortune - Generated content length: {len(yorum) if yorum else 0}")
                print(f"Chinese Fortune - First 200 chars: {yorum[:200] if yorum else 'EMPTY'}")
            except Exception as g4f_error:
                print(f"G4F hatası: {str(g4f_error)}")
                # Fallback yorum - çok dilli
                if language == 'tr':
                    yorum = f"""
                    Çin falı yorumu:
                    
                    Doğum tarihi: {data['dogumTarihi']}
                    Doğum saati: {data['dogumSaati']}
                    
                    Ba Zi analizi sonucunda:
                    - Yıl elementi: {ba_zi_result.get('year_element', 'Bilinmiyor')}
                    - Ay elementi: {ba_zi_result.get('month_element', 'Bilinmiyor')}
                    - Gün elementi: {ba_zi_result.get('day_element', 'Bilinmiyor')}
                    - Saat elementi: {ba_zi_result.get('hour_element', 'Bilinmiyor')}
                    
                    Element dağılımı: {element_counts}
                    
                    Bu element kombinasyonuna göre kişilik özellikleri, kariyer yönelimi, aşk hayatı ve genel yaşam yolu analiz edilmiştir.
                    """
                elif language == 'en':
                    yorum = f"""
                    Chinese Fortune Reading:
                    
                    Birth Date: {data['dogumTarihi']}
                    Birth Time: {data['dogumSaati']}
                    
                    Ba Zi Analysis Result:
                    - Year Element: {ba_zi_result.get('year_element', 'Unknown')}
                    - Month Element: {ba_zi_result.get('month_element', 'Unknown')}
                    - Day Element: {ba_zi_result.get('day_element', 'Unknown')}
                    - Hour Element: {ba_zi_result.get('hour_element', 'Unknown')}
                    
                    Element Distribution: {element_counts}
                    
                    Based on this element combination, personality traits, career orientation, love life and general life path have been analyzed.
                    """
                else:  # German
                    yorum = f"""
                    Chinesische Wahrsagung:
                    
                    Geburtsdatum: {data['dogumTarihi']}
                    Geburtszeit: {data['dogumSaati']}
                    
                    Ba Zi-Analyseergebnis:
                    - Jahreselement: {ba_zi_result.get('year_element', 'Unbekannt')}
                    - Monatselement: {ba_zi_result.get('month_element', 'Unbekannt')}
                    - Tageselement: {ba_zi_result.get('day_element', 'Unbekannt')}
                    - Stundenelement: {ba_zi_result.get('hour_element', 'Unbekannt')}
                    
                    Elementverteilung: {element_counts}
                    
                    Basierend auf dieser Elementkombination wurden Persönlichkeitsmerkmale, Karriereorientierung, Liebesleben und allgemeiner Lebensweg analysiert.
                    """
            
            # Reading'i kaydet
            reading = Reading(
                user_id=user_id,
                reading_type='chinese',
                input_data=data,
                result=yorum
            )
            
            reading.save()
            
            return jsonify({
                'success': True,
                'ba_zi': ba_zi_result,
                'element_counts': element_counts,
                'yorum': yorum,
                'reading_id': str(reading._id),
                'language': language
            })
            
        except Exception as e:
            import traceback
            print(f"Çin falı hatası: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Çin falı oluşturulurken bir hata oluştu: {str(e)}'}), 500
