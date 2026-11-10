import os
import random

from pymongo import AsyncMongoClient, ReturnDocument

ANIMAUX = {
    "poule":     {"nom": "Poule",    "emoji": "🐔", "rarete": "Commun",      "poids": 25},
    "lapin":     {"nom": "Lapin",    "emoji": "🐰", "rarete": "Commun",      "poids": 20},
    "canard":    {"nom": "Canard",   "emoji": "🦆", "rarete": "Commun",      "poids": 15},
    "renard":    {"nom": "Renard",   "emoji": "🦊", "rarete": "Peu commun",  "poids": 12},
    "herisson":  {"nom": "Hérisson", "emoji": "🦔", "rarete": "Peu commun",  "poids": 8},
    "loup":      {"nom": "Loup",     "emoji": "🐺", "rarete": "Rare",        "poids": 6},
    "panda":     {"nom": "Panda",    "emoji": "🐼", "rarete": "Rare",        "poids": 5},
    "lion":      {"nom": "Lion",     "emoji": "🦁", "rarete": "Épique",      "poids": 4},
    "elephant":  {"nom": "Éléphant", "emoji": "🐘", "rarete": "Épique",      "poids": 3},
    "baleine":   {"nom": "Baleine",  "emoji": "🐋", "rarete": "Légendaire",  "poids": 2}
}
COUT_FUSION = 3
_client = None


def _collection():
    global _client
    if _client is None:
        # Mêmes variables d'environnement que db.py
        _client = AsyncMongoClient(
            os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        )
    database = os.getenv("MONGODB_DATABASE", "botdiscord")
    return _client[database]["collection_animaux"]


def tirer() -> str:
    """Tire un animal au hasard en fonction de sa rareté et retourne sa clé."""
    cles = list(ANIMAUX)
    poids = [ANIMAUX[c]["poids"] for c in cles]
    return random.choices(cles, weights=poids, k=1)[0]


async def ajouter_animal(user_id: int, nom_user: str, cle: str, quantite: int = 1) -> int:
    """Ajoute des exemplaires à la collection de l'utilisateur.
    Retourne le nombre d'exemplaires possédés après l'ajout."""
    doc = await _collection().find_one_and_update(
        {"_id": user_id},
        {"$inc": {f"animaux.{cle}": quantite}, "$set": {"nom": nom_user}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return doc["animaux"][cle]


async def collection_user(user_id: int) -> dict:
    """Retourne {cle: quantité} pour un utilisateur, {} s'il n'y a rien."""
    doc = await _collection().find_one({"_id": user_id})
    return doc.get("animaux", {}) if doc else {}


async def retirer_animaux(user_id: int, cle: str, quantite: int) -> bool:
    """Retire une quantité d'un animal de la collection de l'utilisateur.
    Retourne True si l'opération a réussi, False sinon."""
    resultat = await _collection().update_one(
        {"_id": user_id, f"animaux.{cle}": {"$gte": quantite}},
        {"$inc": {f"animaux.{cle}": -quantite}}
    )
    return resultat.modified_count == 1