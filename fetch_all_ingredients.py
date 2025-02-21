import requests
import json
import time

API_KEY = "01741075578944dab47a04373aa6c745"  # Remplace par ta clé API
BASE_URL = "https://api.spoonacular.com/food/ingredients/search"
LETTERS = "abcdefghijklmnopqrstuvwxyz"  # Pour couvrir un maximum d'ingrédients
all_ingredients = []

for letter in LETTERS:
    params = {
        "query": letter,
        "number": 100,  # Nombre maximal d'ingrédients pour cette lettre
        "apiKey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    print(f"Requête pour '{letter}' - Code : {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        all_ingredients.extend(results)
    else:
        print(f"Erreur pour la lettre {letter}: {response.status_code}")
    time.sleep(1)  # Respect de la limite (1 requête/seconde)

# Supprimer les doublons en se basant sur l'ID
unique_ingredients = {ingredient["id"]: ingredient for ingredient in all_ingredients}
all_ingredients = list(unique_ingredients.values())

with open("all_ingredients.json", "w", encoding="utf-8") as f:
    json.dump(all_ingredients, f, indent=4, ensure_ascii=False)

print(f"Total d'ingrédients récupérés : {len(all_ingredients)}")
