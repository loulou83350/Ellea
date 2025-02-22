import os
import json
import requests
import time
import firebase_admin
from firebase_admin import credentials, firestore

# 🔑 Récupérer la clé Firebase depuis GitHub Secrets (via les variables d'environnement)
firebase_key_json = os.getenv("FIREBASE_KEY")

if not firebase_key_json:
    raise ValueError("❌ Clé Firebase non définie ! Vérifie tes variables d'environnement.")

# 📥 Charger la clé Firebase depuis JSON
cred_dict = json.loads(firebase_key_json)
cred = credentials.Certificate(cred_dict)

# 🔥 Initialiser Firebase
firebase_admin.initialize_app(cred)
db = firestore.client()
print("✅ Connexion à Firebase réussie !")

# 📂 Charger la liste des ingrédients depuis all_ingredients.json
with open("all_ingredients.json", "r", encoding="utf-8") as f:
    ingredients = json.load(f)

API_KEY = "01741075578944dab47a04373aa6c745"  # Remplace par ta clé API Spoonacular
BASE_URL = "https://api.spoonacular.com/food/ingredients/{id}/information"

# 🔄 Traiter chaque ingrédient
for ingredient in ingredients:
    ingredient_id = ingredient.get("id")
    ingredient_name = ingredient.get("name")

    if not ingredient_id:
        continue  # Ignorer si l'ingrédient n'a pas d'ID

    # 🔍 Vérifier si l'ingrédient est déjà enregistré dans Firestore
    doc_ref = db.collection("ingredients").document(str(ingredient_id))
    doc = doc_ref.get()

    if doc.exists:
        existing_data = doc.to_dict()
        
        # Vérifier si les détails sont déjà enregistrés
        if "calories" in existing_data and "nutrients" in existing_data:
            print(f"✅ {ingredient_name} (ID {ingredient_id}) déjà complet, ignoré.")
            continue  # Ignorer cet ingrédient

    # 📡 Appeler l'API Spoonacular
    url = BASE_URL.format(id=ingredient_id)
    params = {"apiKey": API_KEY, "amount": 1, "unit": "gram"}

    response = requests.get(url, params=params)
    print(f"📦 Récupération {ingredient_name} (ID {ingredient_id}) - Code : {response.status_code}")

    if response.status_code == 200:
        details = response.json()

        # 📤 Mettre à jour Firestore
        doc_ref.set(details, merge=True)  # merge=True permet de compléter sans écraser les données existantes
        print(f"✅ Ajouté/Mis à jour dans Firebase : {ingredient_name}")

    else:
        print(f"❌ Erreur API pour {ingredient_name} (ID {ingredient_id}) : {response.status_code}")

    time.sleep(1)  # Respect de la limite d’1 requête/seconde

print("🎉 Script terminé !")
