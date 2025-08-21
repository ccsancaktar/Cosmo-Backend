from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Reading
from datetime import datetime, timedelta

readings_bp = Blueprint('readings', __name__)

@readings_bp.route('/history', methods=['GET'])
@jwt_required()
def get_reading_history():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Sayfalama parametreleri
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        reading_type = request.args.get('type')  # Filtreleme için
        
        # MongoDB'den fal kayıtlarını al
        readings = Reading.find_by_user_id(user_id)
        
        # Fal türüne göre filtrele
        if reading_type:
            readings = [r for r in readings if r.reading_type == reading_type]
        
        # Tarihe göre sırala
        readings.sort(key=lambda x: x.created_at, reverse=True)
        
        # Sayfalama
        total = len(readings)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_readings = readings[start_idx:end_idx]
        
        # Sonuçları formatla
        history = []
        for reading in paginated_readings:
            history.append({
                'id': str(reading._id),
                'reading_type': reading.reading_type,
                'type_display': get_reading_type_display(reading.reading_type),
                'input_data': reading.input_data,
                'result': reading.result,
                'is_public': reading.is_public,
                'created_at': reading.created_at.isoformat() if reading.created_at else None,
                'created_at_display': reading.created_at.strftime('%d.%m.%Y %H:%M') if reading.created_at else None
            })
        
        return jsonify({
            'readings': history,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'has_next': end_idx < total,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Fal geçmişi hatası: {str(e)}'}), 500

@readings_bp.route('/history/<reading_id>', methods=['GET'])
@jwt_required()
def get_reading_detail(reading_id):
    try:
        user_id = get_jwt_identity()
        
        # Fal kaydını bul
        reading = Reading.find_by_id(reading_id)
        
        if not reading or reading.user_id != user_id:
            return jsonify({'error': 'Fal kaydı bulunamadı'}), 404
        
        return jsonify({
            'reading': {
                'id': str(reading._id),
                'reading_type': reading.reading_type,
                'type_display': get_reading_type_display(reading.reading_type),
                'input_data': reading.input_data,
                'result': reading.result,
                'is_public': reading.is_public,
                'created_at': reading.created_at.isoformat() if reading.created_at else None,
                'created_at_display': reading.created_at.strftime('%d.%m.%Y %H:%M') if reading.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Fal detayı hatası: {str(e)}'}), 500

@readings_bp.route('/history/<reading_id>', methods=['DELETE'])
@jwt_required()
def delete_reading(reading_id):
    try:
        user_id = get_jwt_identity()
        
        # Fal kaydını bul
        reading = Reading.find_by_id(reading_id)
        
        if not reading or reading.user_id != user_id:
            return jsonify({'error': 'Fal kaydı bulunamadı'}), 404
        
        # Kaydı sil
        from models import db
        db.readings.delete_one({'_id': reading._id})
        
        return jsonify({'message': 'Fal kaydı başarıyla silindi'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Fal silme hatası: {str(e)}'}), 500

@readings_bp.route('/history/<reading_id>/visibility', methods=['PUT'])
@jwt_required()
def toggle_reading_visibility(reading_id):
    try:
        user_id = get_jwt_identity()
        
        # Fal kaydını bul
        reading = Reading.find_by_id(reading_id)
        
        if not reading or reading.user_id != user_id:
            return jsonify({'error': 'Fal kaydı bulunamadı'}), 404
        
        data = request.get_json()
        is_public = data.get('is_public', False)
        
        # Görünürlüğü güncelle
        from models import db
        db.readings.update_one(
            {'_id': reading._id},
            {'$set': {'is_public': is_public}}
        )
        
        return jsonify({
            'message': f'Fal görünürlüğü güncellendi',
            'is_public': is_public
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Görünürlük güncelleme hatası: {str(e)}'}), 500

@readings_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_reading_statistics():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Kullanıcının tüm fal kayıtlarını al
        readings = Reading.find_by_user_id(user_id)
        
        # Fal türlerine göre istatistikler
        type_stats = {}
        for reading in readings:
            reading_type = reading.reading_type
            type_stats[reading_type] = type_stats.get(reading_type, 0) + 1
        
        # Son 30 günlük fal sayısı
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_count = sum(1 for reading in readings if reading.created_at >= thirty_days_ago)
        
        # Toplam fal sayısı
        total_count = len(readings)
        
        # En popüler fal türü
        most_popular_type = max(type_stats, key=type_stats.get) if type_stats else None
        most_popular_count = type_stats.get(most_popular_type, 0) if most_popular_type else 0
        
        statistics = {
            'total_readings': total_count,
            'recent_readings': recent_count,
            'by_type': type_stats,
            'most_popular_type': most_popular_type,
            'most_popular_count': most_popular_count
        }
        
        return jsonify({'statistics': statistics}), 200
        
    except Exception as e:
        return jsonify({'error': f'İstatistik hatası: {str(e)}'}), 500

def get_reading_type_display(reading_type):
    """Fal türünü Türkçe olarak döndür"""
    type_displays = {
        'yildizname': 'Yıldızname',
        'tarot': 'Tarot',
        'rune': 'Rune',
        'chinese': 'Çin Falı',
        'coffee': 'Kahve Falı'
    }
    return type_displays.get(reading_type, reading_type) 