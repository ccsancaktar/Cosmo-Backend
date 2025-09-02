from flask import Blueprint, request, jsonify, url_for, redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Reading
from datetime import datetime, timedelta
from tokens import add_registration_bonus
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import re

auth_bp = Blueprint('auth', __name__)

# Google OAuth konfigürasyonu
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5050/api/auth/google/callback')

def validate_email(email):
    """Email formatını kontrol et"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Şifre güvenliğini kontrol et"""
    if len(password) < 8:
        return False, "Şifre en az 8 karakter olmalıdır"
    if not re.search(r'[A-Z]', password):
        return False, "Şifre en az bir büyük harf içermelidir"
    if not re.search(r'[a-z]', password):
        return False, "Şifre en az bir küçük harf içermelidir"
    if not re.search(r'\d', password):
        return False, "Şifre en az bir rakam içermelidir"
    return True, "Şifre güvenli"

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['username', 'email', 'password', 'first_name', ]
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} alanı gereklidir'}), 400
        
        # Email formatını kontrol et
        if not validate_email(data['email']):
            return jsonify({'error': 'Geçersiz email formatı'}), 400
        
        # Kullanıcı adı kontrolü
        if len(data['username']) < 3:
            return jsonify({'error': 'Kullanıcı adı en az 3 karakter olmalıdır'}), 400
        
        # Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir
        if not re.match(r'^[a-zA-Z0-9_]+$', data['username']):
            return jsonify({'error': 'Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir'}), 400
        
        # Kullanıcı zaten var mı kontrol et
        if User.find_by_username(data['username']):
            return jsonify({'error': 'Bu kullanıcı adı zaten kullanılıyor'}), 400
        
        if User.find_by_email(data['email']):
            return jsonify({'error': 'Bu email adresi zaten kayıtlı'}), 400
        
        # Yeni kullanıcı oluştur
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            birth_time=datetime.strptime(data['birth_time'], '%H:%M').time() if data.get('birth_time') else None,
            birth_place=data.get('birth_place'),
            stripe_customer_id=None  # Yeni kullanıcılar için None olarak başlat
        )
        user.set_password(data['password'])
        
        # Burç hesapla
        if data.get('birth_date'):
            user.zodiac_sign = calculate_zodiac_sign(data['birth_date'])
        
        # Çin elementi hesapla (sadece doğum tarihi ile)
        if data.get('birth_date'):
            user.chinese_element = calculate_chinese_element(data['birth_date'], None)
        
        user.save()
        
        # Kayıt bonusu ver
        add_registration_bonus(str(user._id))
        
        # JWT token oluştur
        access_token = create_access_token(
            identity=str(user._id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'message': 'Kullanıcı başarıyla oluşturuldu',
            'user': user.to_dict(),
            'token': access_token
        }), 201
        
    except Exception as e:
        # MongoDB'de session rollback yok, sadece log yazalım
        app.logger.error(f'Kayıt hatası: {str(e)}')
        return jsonify({'error': f'Kayıt hatası: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Kullanıcı adı ve şifre gereklidir'}), 400
        
        # Kullanıcıyı bul (username veya email ile)
        user = User.find_by_username(data['username'])
        if not user:
            user = User.find_by_email(data['username'])
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Geçersiz kullanıcı adı veya şifre'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Hesabınız aktif değil'}), 401
        
        # JWT token oluştur
        access_token = create_access_token(
            identity=str(user._id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'message': 'Giriş başarılı',
            'user': user.to_dict(),
            'token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Giriş hatası: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Fal geçmişi sayısını al
        readings = Reading.find_by_user_id(str(user._id))
        total_readings = len(readings)
        
        return jsonify({
            'user': user.to_dict(),
            'statistics': {
                'total_readings': total_readings,
                'days_registered': (datetime.now() - user.created_at).days if user.created_at else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Profil hatası: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Güncellenebilir alanlar
        updatable_fields = [
            'first_name', 'phone', 'profile_image',
            'birth_date', 'birth_time', 'birth_place',
            'theme', 'language', 'notifications_enabled', 'privacy_level'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'birth_date' and data[field]:
                    user.birth_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                elif field == 'birth_time' and data[field]:
                    user.birth_time = datetime.strptime(data[field], '%H:%M').time()
                else:
                    setattr(user, field, data[field])
        
        # Burç ve element yeniden hesapla
        if data.get('birth_date'):
            user.zodiac_sign = calculate_zodiac_sign(data['birth_date'])
            user.chinese_element = calculate_chinese_element(data['birth_date'], None)
        
        user.save()
        
        return jsonify({
            'message': 'Profil güncellendi',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Güncelleme hatası: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Mevcut şifre ve yeni şifre gereklidir'}), 400
        
        # Mevcut şifreyi kontrol et
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Mevcut şifre yanlış'}), 400
        
        # Yeni şifre güvenliğini kontrol et
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Şifreyi güncelle
        user.set_password(data['new_password'])
        user.save()
        
        return jsonify({'message': 'Şifre başarıyla değiştirildi'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Şifre değiştirme hatası: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # JWT token'ı blacklist'e eklenebilir (opsiyonel)
        return jsonify({'message': 'Başarıyla çıkış yapıldı'}), 200
    except Exception as e:
        return jsonify({'error': f'Çıkış hatası: {str(e)}'}), 500

def calculate_zodiac_sign(birth_date_str):
    """Doğum tarihine göre burç hesapla"""
    try:
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        month = birth_date.month
        day = birth_date.day
        
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return 'Koç'
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return 'Boğa'
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return 'İkizler'
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return 'Yengeç'
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return 'Aslan'
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return 'Başak'
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return 'Terazi'
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return 'Akrep'
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return 'Yay'
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return 'Oğlak'
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return 'Kova'
        else:
            return 'Balık'
    except:
        return None

def calculate_chinese_element(birth_date_str, birth_time_str):
    """Doğum tarihi ve saatine göre Çin elementi hesapla"""
    try:
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        
        # Çin takvimine göre element hesaplama (yıl elementine göre)
        year = birth_date.year
        
        # 5 element döngüsü: Metal, Su, Ağaç, Ateş, Toprak
        # Çin takviminde elementler 2 yıllık döngüler halinde değişir
        if year % 10 == 0 or year % 10 == 1:
            return 'Metal'
        elif year % 10 == 2 or year % 10 == 3:
            return 'Su'
        elif year % 10 == 4 or year % 10 == 5:
            return 'Ağaç'
        elif year % 10 == 6 or year % 10 == 7:
            return 'Ateş'
        else:  # year % 10 == 8 or year % 10 == 9
            return 'Toprak'
    except:
        return None 

# Google OAuth endpoint'leri
@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    """Google OAuth ile giriş başlat"""
    try:
        # Google OAuth flow oluştur
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=['openid', 'email', 'profile']
        )
        
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Authorization URL oluştur
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return jsonify({
            'authorization_url': authorization_url,
            'state': state
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Google login hatası: {str(e)}'}), 500

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Google OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({'error': 'Authorization code bulunamadı'}), 400
        
        # Google OAuth flow ile token al
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=['openid', 'email', 'profile']
        )
        
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Authorization code ile token al
        flow.fetch_token(code=code)
        
        # ID token'dan kullanıcı bilgilerini al
        id_info = id_token.verify_oauth2_token(
            flow.credentials.id_token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Kullanıcı bilgilerini al
        google_id = id_info['sub']
        email = id_info['email']
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        picture = id_info.get('picture', '')
        
        # Kullanıcı zaten var mı kontrol et
        user = User.find_by_email(email)
        
        if not user:
            # Yeni kullanıcı oluştur
            username = f"google_{google_id[:8]}"
            
            # Username benzersiz olana kadar dene
            counter = 1
            original_username = username
            while User.find_by_username(username):
                username = f"{original_username}_{counter}"
                counter += 1
            
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                google_id=google_id,
                profile_picture=picture
            )
            user.save()
            
            # Kayıt bonusu ver
            add_registration_bonus(str(user._id))
        
        # JWT token oluştur
        access_token = create_access_token(
            identity=str(user._id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'message': 'Google ile giriş başarılı',
            'user': user.to_dict(),
            'token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Google callback hatası: {str(e)}'}), 500

@auth_bp.route('/google/verify', methods=['POST'])
def google_verify():
    """Google ID token'ı doğrula ve giriş yap"""
    try:
        data = request.get_json()
        id_token_str = data.get('id_token')
        
        if not id_token_str:
            return jsonify({'error': 'ID token gereklidir'}), 400
        
        # ID token'ı doğrula
        id_info = id_token.verify_oauth2_token(
            id_token_str, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Kullanıcı bilgilerini al
        google_id = id_info['sub']
        email = id_info['email']
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        picture = id_info.get('picture', '')
        
        # Kullanıcı zaten var mı kontrol et
        user = User.find_by_email(email)
        
        if not user:
            # Yeni kullanıcı oluştur
            username = f"google_{google_id[:8]}"
            
            # Username benzersiz olana kadar dene
            counter = 1
            original_username = username
            while User.find_by_username(username):
                username = f"{original_username}_{counter}"
                counter += 1
            
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                google_id=google_id,
                profile_picture=picture
            )
            user.save()
            
            # Kayıt bonusu ver
            add_registration_bonus(str(user._id))
        
        # JWT token oluştur
        access_token = create_access_token(
            identity=str(user._id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'message': 'Google ile giriş başarılı',
            'user': user.to_dict(),
            'token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Google verify hatası: {str(e)}'}), 500 