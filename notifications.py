import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import json

load_dotenv()

class NotificationService:
    def __init__(self):
        self.expo_api_url = "https://exp.host/--/api/v2/push/send"
        self.logger = logging.getLogger(__name__)

    def send_notification(self, push_token, title, body, data=None, sound="default"):
        """Push notification gönder - HTTP requests kullanarak"""
        try:
            # Expo push notification payload
            payload = {
                "to": push_token,
                "title": title,
                "body": body,
                "data": data or {},
                "sound": sound,
                "badge": 1,
                "priority": "high"
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-encoding": "gzip, deflate"
            }

            self.logger.info(f"Notification gönderiliyor: {title} -> {push_token[:20]}...")
            self.logger.info(f"Payload: {payload}")
            self.logger.info(f"Headers: {headers}")

            # Expo API'ye POST request gönder
            response = requests.post(
                self.expo_api_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            self.logger.info(f"Response status: {response.status_code}")
            self.logger.info(f"Response text: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('data') and result['data'].get('status') == 'ok':
                    self.logger.info(f"Notification gönderildi: {title} -> {push_token[:20]}...")
                    return True
                else:
                    self.logger.error(f"Notification gönderilemedi: {result}")
                    return False
            else:
                self.logger.error(f"Notification API hatası: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Notification gönderme hatası: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def send_daily_fal_reminder(self, push_token, user_name):
        """Günlük fal hatırlatıcısı"""
        return self.send_notification(
            push_token=push_token,
            title="🔮 Günlük Falınız Hazır!",
            body=f"Merhaba {user_name}, bugünkü falınızı çekmeyi unutmayın!",
            data={
                "type": "daily_reminder", 
                "screen": "Daily",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_weekly_summary(self, push_token, user_name):
        """Haftalık fal özeti"""
        return self.send_notification(
            push_token=push_token,
            title="📊 Haftalık Fal Özetiniz",
            body=f"{user_name}, bu hafta hangi falları çektiniz? Kontrol edin!",
            data={
                "type": "weekly_summary", 
                "screen": "Profile",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_premium_expiry_reminder(self, push_token, user_name, days_left):
        """Premium üyelik sona erme hatırlatıcısı"""
        return self.send_notification(
            push_token=push_token,
            title="⭐ Premium Üyeliğiniz Sona Eriyor",
            body=f"{user_name}, premium üyeliğiniz {days_left} gün sonra sona erecek.",
            data={
                "type": "premium_expiry", 
                "screen": "Premium",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_fal_result_ready(self, push_token, user_name, fal_type):
        """Fal sonucu hazır bildirimi"""
        fal_names = {
            "yildizname": "Yıldızname",
            "tarot": "Tarot",
            "rune": "Rün",
            "chinese": "Çin",
            "coffee": "Kahve",
            "kabala": "Kabala"
        }
        
        return self.send_notification(
            push_token=push_token,
            title="✨ Fal Sonucunuz Hazır!",
            body=f"{user_name}, {fal_names.get(fal_type, fal_type)} falınızın sonucu hazır!",
            data={
                "type": "fal_result", 
                "fal_type": fal_type,
                "screen": "Result",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_new_feature_announcement(self, push_token, user_name, feature_name):
        """Yeni özellik duyurusu"""
        return self.send_notification(
            push_token=push_token,
            title="🎉 Yeni Özellik!",
            body=f"{user_name}, {feature_name} özelliği eklendi! Hemen deneyin!",
            data={
                "type": "new_feature", 
                "feature": feature_name,
                "screen": "Home",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_birthday_notification(self, push_token, user_name):
        """Doğum günü bildirimi"""
        return self.send_notification(
            push_token=push_token,
            title="🎂 Doğum Gününüz Kutlu Olsun!",
            body=f"{user_name}, bugün özel gününüz! Özel falınızı çekin!",
            data={
                "type": "birthday", 
                "screen": "Daily",
                "timestamp": datetime.now().isoformat()
            },
            sound="birthday"
        )
    
    def send_special_day_notification(self, push_token, user_name, special_day):
        """Özel gün bildirimi"""
        return self.send_notification(
            push_token=push_token,
            title="🎊 Özel Gün Bildirimi",
            body=f"{user_name}, bugün {special_day}! Özel falınızı çekin!",
            data={
                "type": "special_day", 
                "special_day": special_day,
                "screen": "Daily",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_test_notification(self, push_token, user_name):
        """Test notification"""
        return self.send_notification(
            push_token=push_token,
            title="🧪 Test Bildirimi",
            body=f"Merhaba {user_name}, bu bir test bildirimidir!",
            data={
                "type": "test",
                "timestamp": datetime.now().isoformat()
            }
        )
