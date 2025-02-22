import requests
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Initialisation Firebase
cred = credentials.Certificate("firebase_key.json")  # 🔹 Remplace par ton chemin de clé Firebase
firebase_admin.initialize_app(cred)
db = firestore.client()

API_KEY = "01741075578944dab47a04373aa6c745"
BASE_URL = "https://api.spoonacular.com/food/ingredients/search"
LETTERS = "abcdefghijklmnopqrstuvwxyz"  # 🔹 Change ça si besoin

all_ingredients = []

for letter in LETTERS:
    params = {"query": letter, "number": 100, "apiKey": API_KEY}
    response = requests.get(BASE_URL, params=params)
    print(f"Requête pour '{letter}' - Code : {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        all_ingredients.extend(results)
    else:
        print(f"Erreur pour {letter}: {response.status_code}")

    time.sleep(1)  # 🔹 Respect des limites API

# Supprimer les doublons
unique_ingredients = {ingredient["id"]: ingredient for ingredient in all_ingredients}
all_ingredients = list(unique_ingredients.values())

# 🔹 Ajout dans Firebase Firestore
for ingredient in all_ingredients:
    ingredient_id = str(ingredient["id"])  # ID en string pour Firebase
    db.collection("ingredients").document(ingredient_id).set(ingredient)

print(f"Total d'ingrédients ajoutés à Firebase : {len(all_ingredients)}")
