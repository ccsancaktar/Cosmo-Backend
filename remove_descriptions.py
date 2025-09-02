from models import db
from bson import ObjectId

# Description'ları kaldır
result1 = db.token_packages.update_one(
    {"_id": ObjectId("68b02413a2a671159d8365b3")},
    {"$unset": {"description": ""}}
)
print(f"50 Token description kaldırıldı: {result1.modified_count}")

result2 = db.token_packages.update_one(
    {"_id": ObjectId("68b0241ad830fd7c89f7110e")},
    {"$unset": {"description": ""}}
)
print(f"150 Token description kaldırıldı: {result2.modified_count}")

result3 = db.token_packages.update_one(
    {"_id": ObjectId("68b024235b7fd7df423f7e42")},
    {"$unset": {"description": ""}}
)
print(f"500 Token description kaldırıldı: {result3.modified_count}")

print("Tüm description'lar kaldırıldı!")
