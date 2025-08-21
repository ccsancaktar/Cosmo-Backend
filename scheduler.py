from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from notifications import NotificationService
from models import User, Reading
from datetime import datetime, timedelta
import logging

scheduler = BackgroundScheduler()
notification_service = NotificationService()
logger = logging.getLogger(__name__)

def send_daily_fal_reminders():
    """Günlük fal hatırlatıcılarını gönder"""
    try:
        users = User.objects(notification_settings__daily_reminders=True)
        sent_count = 0
        
        for user in users:
            if user.push_token and user.is_active:
                try:
                    notification_service.send_daily_fal_reminder(
                        user.push_token, 
                        user.name or "Değerli Kullanıcı"
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"User {user.id} için daily reminder gönderilemedi: {e}")
        
        logger.info(f"Daily reminder gönderildi: {sent_count} kullanıcı")
        
    except Exception as e:
        logger.error(f"Daily reminder job hatası: {e}")

def send_weekly_summaries():
    """Haftalık fal özetlerini gönder"""
    try:
        users = User.objects(notification_settings__weekly_summaries=True)
        sent_count = 0
        
        for user in users:
            if user.push_token and user.is_active:
                try:
                    notification_service.send_weekly_summary(
                        user.push_token, 
                        user.name or "Değerli Kullanıcı"
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"User {user.id} için weekly summary gönderilemedi: {e}")
        
        logger.info(f"Weekly summary gönderildi: {sent_count} kullanıcı")
        
    except Exception as e:
        logger.error(f"Weekly summary job hatası: {e}")

def send_premium_expiry_reminders():
    """Premium üyelik sona erme hatırlatıcılarını gönder"""
    try:
        # Premium üyeliği 7 gün içinde sona erecek kullanıcıları bul
        seven_days_from_now = datetime.now() + timedelta(days=7)
        
        # Bu kısmı premium.py'deki premium expiry logic ile entegre et
        # Şimdilik placeholder olarak bırakıyorum
        
        logger.info("Premium expiry reminders kontrol edildi")
        
    except Exception as e:
        logger.error(f"Premium expiry reminder job hatası: {e}")

def send_birthday_notifications():
    """Doğum günü bildirimlerini gönder"""
    try:
        today = datetime.now()
        users = User.objects(
            notification_settings__birthday_notifications=True,
            birth_date__day=today.day,
            birth_date__month=today.month
        )
        
        sent_count = 0
        for user in users:
            if user.push_token and user.is_active:
                try:
                    notification_service.send_birthday_notification(
                        user.push_token, 
                        user.name or "Değerli Kullanıcı"
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"User {user.id} için birthday notification gönderilemedi: {e}")
        
        logger.info(f"Birthday notifications gönderildi: {sent_count} kullanıcı")
        
    except Exception as e:
        logger.error(f"Birthday notification job hatası: {e}")

def check_special_days():
    """Özel günleri kontrol et ve bildirim gönder"""
    try:
        today = datetime.now()
        special_days = {
            (12, 31): "Yılbaşı",
            (1, 1): "Yılbaşı",
            (5, 1): "İşçi Bayramı",
            (10, 29): "Cumhuriyet Bayramı",
            # Daha fazla özel gün eklenebilir
        }
        
        if (today.month, today.day) in special_days:
            special_day_name = special_days[(today.month, today.day)]
            users = User.objects(notification_settings__special_day_notifications=True)
            
            sent_count = 0
            for user in users:
                if user.push_token and user.is_active:
                    try:
                        notification_service.send_special_day_notification(
                            user.push_token, 
                            user.name or "Değerli Kullanıcı",
                            special_day_name
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"User {user.id} için special day notification gönderilemedi: {e}")
            
            logger.info(f"Special day notifications gönderildi: {sent_count} kullanıcı")
        
    except Exception as e:
        logger.error(f"Special day check job hatası: {e}")

def setup_scheduler():
    """Scheduler'ı başlat ve job'ları ekle"""
    try:
        # Günlük fal hatırlatıcısı - her gün saat 9:00'da
        scheduler.add_job(
            send_daily_fal_reminders,
            CronTrigger(hour=9, minute=0),
            id='daily_fal_reminders',
            name='Günlük Fal Hatırlatıcıları'
        )
        
        # Haftalık fal özeti - her pazartesi saat 18:00'da
        scheduler.add_job(
            send_weekly_summaries,
            CronTrigger(day_of_week='mon', hour=18, minute=0),
            id='weekly_fal_summaries',
            name='Haftalık Fal Özetleri'
        )
        
        # Premium üyelik hatırlatıcısı - her gün saat 10:00'da
        scheduler.add_job(
            send_premium_expiry_reminders,
            CronTrigger(hour=10, minute=0),
            id='premium_expiry_reminders',
            name='Premium Üyelik Hatırlatıcıları'
        )
        
        # Doğum günü bildirimleri - her gün saat 8:00'da
        scheduler.add_job(
            send_birthday_notifications,
            CronTrigger(hour=8, minute=0),
            id='birthday_notifications',
            name='Doğum Günü Bildirimleri'
        )
        
        # Özel gün kontrolü - her gün saat 7:00'da
        scheduler.add_job(
            check_special_days,
            CronTrigger(hour=7, minute=0),
            id='special_days_check',
            name='Özel Gün Kontrolü'
        )
        
        # Scheduler'ı başlat
        scheduler.start()
        logger.info("Notification scheduler başlatıldı")
        
    except Exception as e:
        logger.error(f"Scheduler kurulum hatası: {e}")

def stop_scheduler():
    """Scheduler'ı durdur"""
    try:
        scheduler.shutdown()
        logger.info("Notification scheduler durduruldu")
    except Exception as e:
        logger.error(f"Scheduler durdurma hatası: {e}")
