# Token Sistemi Dokümantasyonu

## Genel Bakış

Bu dokümantasyon, FAL-APP'in token sistemi hakkında detaylı bilgi içermektedir. Token sistemi, kullanıcıların fal çekmek için kullanabilecekleri sanal para birimidir.

## Token Türleri

### 1. Fal Token Maliyetleri

| Fal Türü | Token Maliyeti |
|-----------|----------------|
| Yıldızname | 50 token |
| Tarot | 35 token |
| Kahve | 25 token |
| Rune | 30 token |
| Çin | 40 token |
| Günlük | 15 token |
| Kabala | 45 token |

### 2. Token Kazanma Yöntemleri

#### Video İzleme Ödülü
- **Miktar**: 10 token per video
- **Günlük Limit**: 5 video
- **Reset**: 24 saat sonra

#### Günlük Bonus
- **Miktar**: 5 token
- **Frekans**: Günde 1 kez
- **Reset**: Her gün 00:00'da

#### Kayıt Bonusu
- **Miktar**: 50 token
- **Frekans**: Sadece kayıt sırasında

#### Token Paketi Satın Alma
- Başlangıç Paketi: 100 token - 19.99 TL
- Popüler Paket: 250 token - 44.99 TL
- Premium Paket: 500 token - 79.99 TL
- Mega Paket: 1000 token - 149.99 TL
- Ultra Paket: 2000 token - 279.99 TL

## Backend API Endpoints

### Token Yönetimi

#### GET `/api/tokens/balance`
- **Açıklama**: Kullanıcının token bakiyesini getirir
- **Auth**: JWT gerekli
- **Response**: `{ "balance": 150, "message": "..." }`

#### GET `/api/tokens/packages`
- **Açıklama**: Aktif token paketlerini listeler
- **Auth**: Gerekli değil
- **Response**: `{ "packages": [...], "message": "..." }`

#### POST `/api/tokens/purchase`
- **Açıklama**: Token paketi satın alma
- **Auth**: JWT gerekli
- **Body**: `{ "package_id": "..." }`
- **Response**: `{ "message": "...", "new_balance": 250 }`

#### GET `/api/tokens/history`
- **Açıklama**: Token işlem geçmişi
- **Auth**: JWT gerekli
- **Response**: `{ "transactions": [...], "message": "..." }`

### Video Ödülleri

#### POST `/api/tokens/video-reward`
- **Açıklama**: Video izleme ödülü
- **Auth**: JWT gerekli
- **Body**: `{ "reward_amount": 10 }`
- **Response**: `{ "message": "...", "new_balance": 160 }`

#### GET `/api/tokens/video-limit-status`
- **Açıklama**: Video limit durumu
- **Auth**: JWT gerekli
- **Response**: `{ "limit_reached": false, "videos_watched": 2, "daily_limit": 5 }`

### Günlük Bonus

#### POST `/api/tokens/daily-bonus`
- **Açıklama**: Günlük bonus alma
- **Auth**: JWT gerekli
- **Response**: `{ "message": "...", "new_balance": 165 }`

#### GET `/api/tokens/daily-bonus-status`
- **Açıklama**: Günlük bonus durumu
- **Auth**: JWT gerekli
- **Response**: `{ "can_claim": true, "remaining_seconds": 0 }`

## Veritabanı Modelleri

### TokenTransaction
```python
class TokenTransaction:
    user_id: str           # Kullanıcı ID
    transaction_type: str   # İşlem türü
    amount: int            # Token miktarı (pozitif/negatif)
    description: str       # Açıklama
    package_id: str        # Paket ID (opsiyonel)
    created_at: datetime   # Oluşturulma tarihi
```

### TokenPackage
```python
class TokenPackage:
    name: str              # Paket adı
    token_amount: int      # Token miktarı
    price: float           # Fiyat (TL)
    description: str       # Açıklama
    is_active: bool        # Aktif mi?
    created_at: datetime   # Oluşturulma tarihi
```

## Frontend Kullanımı

### TokenContext
```javascript
import { useToken } from '../context/TokenContext';

const { 
  balance, 
  watchVideo, 
  claimDailyBonus, 
  purchaseTokens 
} = useToken();
```

### Video İzleme
```javascript
const handleWatchVideo = async () => {
  try {
    const result = await watchVideo(10);
    console.log('Kazanılan token:', result);
  } catch (error) {
    console.error('Video hatası:', error);
  }
};
```

### Günlük Bonus
```javascript
const handleDailyBonus = async () => {
  try {
    const result = await claimDailyBonus();
    console.log('Bonus alındı:', result);
  } catch (error) {
    console.error('Bonus hatası:', error);
  }
};
```

## Güvenlik Önlemleri

1. **Rate Limiting**: Video ödülleri ve günlük bonus için limitler
2. **JWT Authentication**: Tüm token işlemleri için kimlik doğrulama
3. **Input Validation**: Paket ID ve diğer parametreler için doğrulama
4. **Transaction Logging**: Tüm işlemler veritabanında saklanır

## Hata Yönetimi

### Yaygın Hatalar

1. **Yetersiz Bakiye**: `"Yetersiz token bakiyesi. Gerekli: 50, Mevcut: 30"`
2. **Günlük Limit**: `"Günlük video limiti doldu"`
3. **Bonus Zaten Alındı**: `"Bugün zaten bonus aldınız"`
4. **Geçersiz Paket**: `"Paket bulunamadı"`

### Hata Kodları

- `400`: Bad Request (Yetersiz bakiye, limit doldu)
- `404`: Not Found (Kullanıcı/paket bulunamadı)
- `500`: Internal Server Error (Sunucu hatası)

## Test Etme

Token sistemini test etmek için:

```bash
cd backend
python test_token_system.py
```

## Monitoring ve Logging

- Tüm token işlemleri MongoDB'de saklanır
- Hata durumları console'a loglanır
- Sentry entegrasyonu ile hata takibi

## Gelecek Geliştirmeler

1. **Referans Sistemi**: Arkadaş davet etme bonusu
2. **Seviye Sistemi**: Kullanım sıklığına göre bonus artışı
3. **Özel Kampanyalar**: Belirli günlerde ekstra bonus
4. **Token Transfer**: Kullanıcılar arası token transferi
5. **Token Çekme**: Gerçek para ile token satışı
