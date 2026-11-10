import asyncio
import random
import re
import unicodedata

import discord

import db
import questions as ques

TEMPS_REPONSE = 30  # secondes pour répondre à chaque question

# Articles ignorés si l'utilisateur écrit "le chiot" au lieu de "chiot"
ARTICLES = {"le", "la", "les", "l", "un", "une", "des", "il", "elle", "d", "de", "du"}

CHIFFRES = {"1": "une", "2": "deux", "3": "trois", "4": "quatre", "5": "cinq",
            "6": "six", "7": "sept", "8": "huit", "9": "neuf", "10": "dix"}


def normaliser(texte: str) -> str:
    """Minuscules, sans accents ni ponctuation, sans article."""
    texte = unicodedata.normalize("NFD", texte.lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    mots = [CHIFFRES.get(m, m) for m in re.findall(r"[a-z0-9]+", texte)]
    sans_articles = [m for m in mots if m not in ARTICLES]
    return " ".join(sans_articles or mots)  # garde "une" si c'est la réponse


def est_correct(reponse_user: str, reponse_attendue: str) -> bool:
    # La réponse attendue peut proposer plusieurs mots séparés par "/"
    user = normaliser(reponse_user)
    return any(user == normaliser(r) for r in reponse_attendue.split("/"))


async def terminer(channel, user, points: int, message: str):
    """Affiche le score final et met à jour le record dans MongoDB."""
    texte = f"{message}\nScore final : **{points}**"
    try:
        record, ancien = await db.enregistrer_score(user.id, user.display_name, points)
        if record:
            texte += f"\n🎉 Nouveau record personnel ! (ancien : {ancien})"
        else:
            texte += f"\n🏅 Ton record : **{ancien}**"
    except Exception as erreur:  # base injoignable : le quiz ne doit pas planter
        print(f"Erreur MongoDB : {erreur}")
        texte += "\n⚠️ Impossible d'enregistrer ton score pour le moment."
    await channel.send(texte)


async def start_quiz(interaction: discord.Interaction):
    """Pose des questions jusqu'à la première erreur."""
    await interaction.response.send_message(
        f"🧠 Quiz lancé pour {interaction.user.mention} ! "
        f"Réponds en un mot ({TEMPS_REPONSE}s par question). Une erreur et c'est fini !"
    )

    channel = interaction.channel
    user = interaction.user
    points = 0

    liste = ques.defi.copy()
    random.shuffle(liste)

    def check(message: discord.Message) -> bool:
        return message.author.id == user.id and message.channel.id == channel.id

    for q in liste:
        await channel.send(f"**Question {points + 1}** : {q['question']}")
        bonne_reponse = q["answer"].replace("/", " ou ")

        try:
            message = await interaction.client.wait_for(
                "message", check=check, timeout=TEMPS_REPONSE)
        except asyncio.TimeoutError:
            await terminer(channel, user, points,
                           f"⏰ Temps écoulé ! Réponse : **{bonne_reponse}**")
            return

        if est_correct(message.content, q["answer"]):
            points += 1
            await channel.send("✅ Bien vu !")
        else:
            await terminer(channel, user, points,
                           f"❌ Raté ! Réponse : **{bonne_reponse}**")
            return

    await terminer(channel, user, points, "🏆 Tu as répondu à toutes les questions !")