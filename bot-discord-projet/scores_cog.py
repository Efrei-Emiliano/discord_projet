import discord
from discord import app_commands
from discord.ext import commands

import db


class ScoresCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="score", description="Affiche ton meilleur score au quiz")
    async def score_slash(self, interaction: discord.Interaction):
        try:
            meilleur = await db.meilleur_score(interaction.user.id)
        except Exception as erreur:
            print(f"Erreur MongoDB : {erreur}")
            await interaction.response.send_message("Base de données indisponible.")
            return
        await interaction.response.send_message(
            f"Ton meilleur score : **{meilleur}**")

    @app_commands.command(name="classement", description="Affiche les 10 meilleurs scores")
    async def classement_slash(self, interaction: discord.Interaction):
        try:
            joueurs = await db.top(10)
        except Exception as erreur:
            print(f"Erreur MongoDB : {erreur}")
            await interaction.response.send_message("Base de données indisponible.")
            return
        if not joueurs:
            await interaction.response.send_message("Personne n'a encore joué !")
            return
        lignes = [f"**{i}.** {j['nom']} — {j['best_score']}"
                  for i, j in enumerate(joueurs, start=1)]
        await interaction.response.send_message("**Classement**\n" + "\n".join(lignes))


async def setup(bot: commands.Bot):
    await bot.add_cog(ScoresCog(bot))