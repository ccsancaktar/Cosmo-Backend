from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, TokenTransaction, TokenPackage, FAL_TOKEN_COSTS
from datetime import datetime, timedelta, time
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

tokens_bp = Blueprint('tokens', __name__)

@tokens_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_token_balance():
    """Kullanıcının token bakiyesini getir"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        balance = user.get_token_balance()
        
        return jsonify({
            'balance': balance,
            'message': 'Token bakiyesi başarıyla getirildi'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Token bakiyesi hatası: {str(e)}'}), 500

@tokens_bp.route('/packages', methods=['GET'])
def get_token_packages():
    """Aktif token paketlerini getir"""
    try:
        packages = TokenPackage.find_all_active()
        packages_data = [package.to_dict() for package in packages]
        
        return jsonify({
            'packages': packages_data,
            'message': 'Token paketleri başarıyla getirildi'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Paket listesi hatası: {str(e)}'}), 500

@tokens_bp.route('/purchase', methods=['POST'])
@jwt_required()
def purchase_tokens():
    """Token paketi satın al"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        package_id = data.get('package_id')
        
        if not package_id:
            return jsonify({'error': 'Paket ID gereklidir'}), 400
        
        # Paketi bul
        try:
            package_data = db.token_packages.find_one({'_id': ObjectId(package_id)})
            if not package_data:
                return jsonify({'error': 'Paket bulunamadı'}), 404
        except Exception as e:
            return jsonify({'error': 'Geçersiz paket ID'}), 400
        
        # Ödeme işlemi burada yapılacak (Stripe, PayPal vb.)
        # Şimdilik simüle ediyoruz
        payment_successful = True  # Bu kısım ödeme sistemi entegrasyonu ile değişecek
        
        if payment_successful:
            # Token transaction kaydet
            transaction = TokenTransaction(
                user_id=str(user._id),
                transaction_type='purchase',
                amount=package_data['token_amount'],
                description=f"{package_data['name']} paketi satın alındı",
                package_id=str(package_data['_id'])
            )
            transaction.save()
            
            # Kullanıcı bakiyesini güncelle
            user.update_token_balance()
            
            return jsonify({
                'message': 'Token satın alma başarılı',
                'new_balance': user.token_balance,
                'purchased_amount': package_data['token_amount']
            }), 200
        else:
            return jsonify({'error': 'Ödeme başarısız'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Token satın alma hatası: {str(e)}'}), 500

@tokens_bp.route('/history', methods=['GET'])
@jwt_required()
def get_token_history():
    """Kullanıcının token geçmişini getir"""
    try:
        user_id = get_jwt_identity()
        
        transactions = TokenTransaction.find_by_user_id(user_id)
        transactions_data = [transaction.to_dict() for transaction in transactions]
        
        return jsonify({
            'transactions': transactions_data,
            'message': 'Token geçmişi başarıyla getirildi'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Token geçmişi hatası: {str(e)}'}), 500

@tokens_bp.route('/video-reward', methods=['POST'])
@jwt_required()
def video_reward():
    """Video izleme ödülü"""
    try:
        print("Video reward endpoint çağrıldı")
        user_id = get_jwt_identity()
        print(f"User ID: {user_id}")
        
        user = User.find_by_id(user_id)
        print(f"User bulundu: {user is not None}")
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # AdMob'dan gelen reward miktarını al
        data = request.get_json()
        reward_amount = data.get('reward_amount', 10)  # Sabit 10 token
        
        # 24 saat içindeki video sayısını kontrol et
        last_24_hours = datetime.now() - timedelta(hours=24)
        videos_last_24h = db.token_transactions.count_documents({
            'user_id': str(user_id),
            'transaction_type': 'video_reward',
            'created_at': {'$gte': last_24_hours}
        })
        
        daily_limit = 5  # Sabit günlük limit
        if videos_last_24h >= daily_limit:
            return jsonify({'error': 'Günlük video limiti doldu'}), 400
        
        # AdMob'dan gelen gerçek reward miktarını ver
        transaction = TokenTransaction(
            user_id=str(user._id),
            transaction_type='video_reward',
            amount=reward_amount,
            description='Video izleme ödülü'
        )
        transaction.save()
        
        # Kullanıcı bakiyesini güncelle
        user.update_token_balance()
        
        return jsonify({
            'message': f'{reward_amount} token kazandınız!',
            'new_balance': user.token_balance,
            'daily_videos_watched': videos_last_24h + 1,
            'daily_limit': daily_limit
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Video reward hatası: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Video ödülü hatası: {str(e)}'}), 500

@tokens_bp.route('/video-limit-status', methods=['GET'])
@jwt_required()
def video_limit_status():
    """Video limit durumunu kontrol et"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # 24 saat içindeki video sayısını kontrol et
        last_24_hours = datetime.now() - timedelta(hours=24)
        videos_last_24h = db.token_transactions.count_documents({
            'user_id': str(user_id),
            'transaction_type': 'video_reward',
            'created_at': {'$gte': last_24_hours}
        })
        
        daily_limit = 5  # Sabit günlük limit
        limit_reached = videos_last_24h >= daily_limit
        
        # En eski video'nun tarihini bul (reset zamanı hesaplaması için)
        oldest_video = db.token_transactions.find({
            'user_id': str(user_id),
            'transaction_type': 'video_reward',
            'created_at': {'$gte': last_24_hours}
        }).sort('created_at', 1).limit(1)
        
        reset_time = None
        if oldest_video and videos_last_24h >= daily_limit:
            oldest_video_data = list(oldest_video)
            if oldest_video_data:
                reset_time = (oldest_video_data[0]['created_at'] + timedelta(hours=24)).isoformat()
        
        return jsonify({
            'limit_reached': limit_reached,
            'videos_watched': videos_last_24h,
            'daily_limit': daily_limit,
            'remaining_videos': max(0, daily_limit - videos_last_24h),
            'reset_time': reset_time
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Video limit durumu hatası: {str(e)}'}), 500

@tokens_bp.route('/daily-bonus', methods=['POST'])
@jwt_required()
def daily_bonus():
    """Günlük bonus token"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Bugün bonus alınmış mı kontrol et
        today = datetime.now().date()
        today_bonus = db.token_transactions.find_one({
            'user_id': str(user_id),
            'transaction_type': 'daily_bonus',
            'created_at': {'$gte': datetime.combine(today, time.min)}
        })
        
        if today_bonus:
            # Kalan süreyi hesapla
            next_bonus_time = today_bonus['created_at'] + timedelta(days=1)
            remaining_seconds = int((next_bonus_time - datetime.now()).total_seconds())
            
            return jsonify({
                'error': 'Bugün zaten bonus aldınız',
                'remaining_seconds': remaining_seconds,
                'next_bonus_time': next_bonus_time.isoformat()
            }), 400
        
        # Bonus token ver
        bonus_amount = 5  # Sabit 5 token
        transaction = TokenTransaction(
            user_id=str(user._id),
            transaction_type='daily_bonus',
            amount=bonus_amount,
            description='Günlük bonus token'
        )
        transaction.save()
        
        # Kullanıcı bakiyesini güncelle
        user.update_token_balance()
        
        return jsonify({
            'message': f'Günlük {bonus_amount} token bonusu!',
            'new_balance': user.token_balance
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Günlük bonus hatası: {str(e)}'}), 500

@tokens_bp.route('/daily-bonus-status', methods=['GET'])
@jwt_required()
def daily_bonus_status():
    """Günlük bonus durumunu kontrol et"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Bugün bonus alınmış mı kontrol et
        today = datetime.now().date()
        today_bonus = db.token_transactions.find_one({
            'user_id': str(user_id),
            'transaction_type': 'daily_bonus',
            'created_at': {'$gte': datetime.combine(today, time.min)}
        })
        
        if today_bonus:
            # Kalan süreyi hesapla
            next_bonus_time = today_bonus['created_at'] + timedelta(days=1)
            remaining_seconds = int((next_bonus_time - datetime.now()).total_seconds())
            
            return jsonify({
                'can_claim': False,
                'remaining_seconds': remaining_seconds,
                'next_bonus_time': next_bonus_time.isoformat(),
                'last_claimed': today_bonus['created_at'].isoformat()
            }), 200
        else:
            return jsonify({
                'can_claim': True,
                'remaining_seconds': 0,
                'next_bonus_time': None,
                'last_claimed': None
            }), 200
        
    except Exception as e:
        return jsonify({'error': f'Bonus durumu hatası: {str(e)}'}), 500

def spend_tokens_for_reading(user_id, reading_type):
    """Fal için token harcama fonksiyonu"""
    try:
        cost = FAL_TOKEN_COSTS.get(reading_type, 0)
        if cost == 0:
            return False, "Geçersiz fal türü"
        
        user = User.find_by_id(user_id)
        if not user:
            return False, "Kullanıcı bulunamadı"
        
        current_balance = user.get_token_balance()
        
        if current_balance < cost:
            return False, f"Yetersiz token bakiyesi. Gerekli: {cost}, Mevcut: {current_balance}"
        
        # Token harcama transaction'ı kaydet
        transaction = TokenTransaction(
            user_id=str(user._id),
            transaction_type='spend',
            amount=-cost,  # Negatif değer = harcama
            description=f"{reading_type} falı için token harcandı"
        )
        transaction.save()
        
        # Kullanıcı bakiyesini güncelle
        user.update_token_balance()
        
        return True, f"{cost} token harcandı"
        
    except Exception as e:
        print(f"Token harcama hatası: {str(e)}")
        return False, f"Token harcama hatası: {str(e)}"

def add_registration_bonus(user_id):
    """Yeni kullanıcıya kayıt bonusu ver"""
    try:
        bonus_amount = 50  # Sabit 50 token
        transaction = TokenTransaction(
            user_id=user_id,
            transaction_type='registration_bonus',
            amount=bonus_amount,
            description='Kayıt bonusu'
        )
        transaction.save()
        return True
    except Exception as e:
        print(f"Kayıt bonusu hatası: {str(e)}")
        return False 