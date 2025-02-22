import requests
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Initialisation de Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Clé API Spoonacular
API_KEY = "TA_CLE_SPOONACULAR"
BASE_URL = "https://api.spoonacular.com/food/ingredients/"

# Limite temporaire pour les tests
MAX_REQUESTS = 5

def get_ingredient_details(ingredient_id):
    url = f"{BASE_URL}{ingredient_id}/information?amount=1&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 402:  # Quota dépassé
        print("Quota atteint. Arrêt du script.")
        return None
    else:
        print(f"Erreur pour l'ingrédient {ingredient_id}: {response.status_code}")
        return None

def main():
    ingredients_ref = db.collection("ingredients")
    all_ingredients = ingredients_ref.stream()
    processed_count = 0
    
    for doc in all_ingredients:
        ingredient_data = doc.to_dict()
        ingredient_id = ingredient_data.get("id")
        
        # Vérifier si l'ingrédient a déjà été traité
        if "details" in ingredient_data:
            print(f"Ingrédient {ingredient_id} déjà traité, on passe.")
            continue
        
        details = get_ingredient_details(ingredient_id)
        if details is None:
            break  # Arrêter en cas de quota atteint
        
        # Sauvegarde dans Firebase
        doc_ref = ingredients_ref.document(doc.id)
        doc_ref.update({"details": details})
        print(f"Détails enregistrés pour {ingredient_id}")
        
        processed_count += 1
        if processed_count >= MAX_REQUESTS:
            print("Limite de requêtes atteinte pour ce test.")
            break
        
        time.sleep(1)  # Éviter de surcharger l'API

if __name__ == "__main__":
    main()
