
import os

from pymongo import AsyncMongoClient

_client = None


def _scores():
    global _client

    if _client is None:
        _client = AsyncMongoClient(
            os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        )

    database = os.getenv("MONGODB_DATABASE", "botdiscord")
    return _client[database]["scores"]


# Récupérer le meilleur score d'un utilisateur
async def meilleur_score(user_id: int) -> int:

    doc = await _scores().find_one({"_id": user_id})

    return doc["best_score"] if doc else 0


# Enregistrer un nouveau meilleur score
async def enregistrer_score(user_id: int, nom: str, score: int):

    ancien = await meilleur_score(user_id)

    if score > ancien:
        await _scores().update_one(
            {"_id": user_id},
            {
                "$set": {
                    "best_score": score,
                    "nom": nom
                }
            },
            upsert=True
        )

        return True, ancien

    return False, ancien


# Récupérer le classement des meilleurs scores
async def top(n: int = 10):

    curseur = _scores().find().sort("best_score", -1).limit(n)

    return await curseur.to_list(length=n)