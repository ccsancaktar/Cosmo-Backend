#!/usr/bin/env python3
"""
Token paketleri için seed data
"""

from models import db, TokenPackage
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def seed_token_packages():
    """Token paketlerini veritabanına ekle"""
    
    packages = [
        {
            'name': 'Başlangıç Paketi',
            'token_amount': 100,
            'price': 19.99,
            'description': '100 token ile fal deneyimine başlayın'
        },
        {
            'name': 'Popüler Paket',
            'token_amount': 250,
            'price': 44.99,
            'description': '250 token ile daha fazla fal çektirin'
        },
        {
            'name': 'Premium Paket',
            'token_amount': 500,
            'price': 79.99,
            'description': '500 token ile sınırsız fal deneyimi'
        },
        {
            'name': 'Mega Paket',
            'token_amount': 1000,
            'price': 149.99,
            'description': '1000 token ile uzun süreli kullanım'
        },
        {
            'name': 'Ultra Paket',
            'token_amount': 2000,
            'price': 279.99,
            'description': '2000 token ile maksimum değer'
        }
    ]
    
    for package_data in packages:
        # Paket zaten var mı kontrol et
        existing = db.token_packages.find_one({
            'name': package_data['name']
        })
        
        if not existing:
            package = TokenPackage(
                name=package_data['name'],
                token_amount=package_data['token_amount'],
                price=package_data['price'],
                description=package_data['description']
            )
            package.save()
            print(f"Paket eklendi: {package_data['name']}")
        else:
            print(f"Paket zaten mevcut: {package_data['name']}")

if __name__ == '__main__':
    print("Token paketleri ekleniyor...")
    seed_token_packages()
    print("Token paketleri eklendi!")
