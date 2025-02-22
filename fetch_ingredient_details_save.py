import requests
import json
import time
import os

API_KEY = "01741075578944dab47a04373aa6c745"  # Remplace par ta clé API
BASE_URL_DETAILS = "https://api.spoonacular.com/food/ingredients/{}/information"
INGREDIENTS_FILE = "all_ingredients.json"
OUTPUT_FILE = "ingredients_details.json"
PROGRESS_FILE = "progress.txt"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0

def save_progress(index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

def load_ingredients():
    with open(INGREDIENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_existing_details():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def main():
    ingredients = load_ingredients()
    start_index = load_progress()
    details_list = load_existing_details()

    print(f"Début du traitement à l'indice {start_index} sur {len(ingredients)} ingrédients.")
    for i in range(start_index, len(ingredients)):
        ingredient = ingredients[i]
        ingredient_id = ingredient.get("id")
        url = BASE_URL_DETAILS.format(ingredient_id)
        params = {"amount": 1, "apiKey": API_KEY}
        response = requests.get(url, params=params)
        print(f"Traitement de l'ingrédient ID {ingredient_id} (indice {i}) - Code: {response.status_code}")
        if response.status_code == 200:
            detail = response.json()
            details_list.append(detail)
            # Sauvegarder la progression après chaque ingrédient traité
            save_progress(i + 1)
        else:
            print(f"Erreur {response.status_code} pour l'ingrédient ID {ingredient_id}.")
            print("Quota peut-être dépassé. Arrêt du script pour reprendre plus tard.")
            break

        time.sleep(1)  # Respect de la limite de 1 requête par seconde

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(details_list, f, indent=4, ensure_ascii=False)

    print("Fin du traitement.")

if __name__ == "__main__":
    main()
