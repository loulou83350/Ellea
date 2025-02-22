import os
import json
import requests
import time
import firebase_admin
from firebase_admin import credentials, firestore

# 🔑 Récupérer la clé Firebase depuis les variables d'environnement
firebase_key_json = os.getenv("FIREBASE_KEY")

if not firebase_key_json:
    raise ValueError("❌ Clé Firebase non définie ! Vérifie tes variables d'environnement.")

try:
    # 📥 Charger la clé Firebase depuis la variable d'environnement (et non un fichier)
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)

    # 🔥 Initialiser Firebase
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Connexion à Firebase réussie !")

except json.JSONDecodeError:
    raise ValueError("❌ Erreur : Impossible de parser la clé Firebase. Vérifie le format JSON.")

# 📂 Charger la liste des ingrédients
with open("all_ingredients.json", "r", encoding="utf-8") as f:
    ingredients = json.load(f)

API_KEY = "01741075578944dab47a04373aa6c745"  # Remplace par ta clé API Spoonacular
BASE_URL = "https://api.spoonacular.com/food/ingredients/{id}/information"

# 🔄 Limite à 3 ingrédients pour le test
test_limit = 3  
processed_count = 0  

# 🔄 Récupérer les détails des ingrédients
for ingredient in ingredients:
    if processed_count >= test_limit:
        break  # Stop après 3 ingrédients

    ingredient_id = ingredient.get("id")
    if not ingredient_id:
        continue

    url = BASE_URL.format(id=ingredient_id)
    params = {"apiKey": API_KEY, "amount": 1, "unit": "gram"}

    response = requests.get(url, params=params)
    print(f"📦 Récupération {ingredient['name']} (ID {ingredient_id}) - Code : {response.status_code}")

    if response.status_code == 200:
        details = response.json()

        # 📤 Sauvegarde dans Firestore
        doc_ref = db.collection("ingredients").document(str(ingredient_id))
        doc_ref.set(details)
        print(f"✅ Ajouté dans Firebase : {ingredient['name']}")

    else:
        print(f"❌ Erreur pour {ingredient['name']} (ID {ingredient_id}) : {response.status_code}")

    processed_count += 1  # Incrémenter le compteur
    time.sleep(1)  # Respect de la limite d'1 requête/seconde

print(f"🎉 Test terminé ! {processed_count} ingrédients enregistrés dans Firebase.")
