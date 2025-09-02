from models import db
from bson import ObjectId

# Mevcut paketleri listele
packages = list(db.token_packages.find({}))
print("Mevcut paketler:")
for pkg in packages:
    print(f"ID: {pkg['_id']}, Name: {pkg['name']}, Price: {pkg['price']}")

# 50 Token paketi güncelle
result = db.token_packages.update_one(
    {"_id": ObjectId("68b02413a2a671159d8365b3")},
    {"$set": {"price": 29.99}}
)
print(f"50 Token güncellendi: {result.modified_count}")

# 150 Token paketi güncelle
result = db.token_packages.update_one(
    {"_id": ObjectId("68b0241ad830fd7c89f7110e")},
    {"$set": {"price": 79.99}}
)
print(f"150 Token güncellendi: {result.modified_count}")

# 500 Token paketi güncelle
result = db.token_packages.update_one(
    {"_id": ObjectId("68b024235b7fd7df423f7e42")},
    {"$set": {"price": 199.99}}
)
print(f"500 Token güncellendi: {result.modified_count}")

print("Güncelleme tamamlandı!")
