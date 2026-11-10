import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import wow
import db
import quiz
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    # Envoie les commandes slash a Discord au demarrage.
    await bot.tree.sync()
    print(f"Connecte en tant que {bot.user}")

# Commande prefixee : !ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

#Commande slash : /rules
@bot.tree.command(name = "rules", description = "Affiche les règles du serveur")
async def rules_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Regles du serveur",
        description="A suivre pour pas se faire BAN comme un zwave",
        color=discord.Color.red()
    )
    embed.add_field(name = "Regle 1", value = "Pas d'insultes envers les membres du staff", inline = False)
    embed.add_field(name = "Regle 2", value = "respecter les autres, même leurs avis", inline = False)
    embed.add_field(name = "Regle 3", value = "Ne pas faire de pub", inline = False)
    embed.add_field(name = "Regle 4", value = "Ne pas crier en voc", inline = False)
    embed.add_field(name = "Regle 5", value = "Respecter les animaux", inline = False)
    embed.add_field(name = "Regle 6", value = "S'amuser autant que possible", inline = False)
    
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("✅")

#Guide commandes
@bot.tree.command(name = "help", description = "Affiche le guide des commandes du bot")
async def guide_slash(interaction: discord.Interaction):
    """Affiche le guide des commandes du bot"""
    texte = (
        "**Commandes du bot :**\n"
        "• `/rules` : Affiche les règles du serveur\n"
        "• `/roulette` : Tire un animal au hasard pour ta collection\n"
        "• `/collection` : Affiche ta collection d'animaux\n"
        "• `/fusion` : Fusionne 3 animaux identiques en un nouvel animal\n"
        "• `/wiki <nom>` : Envoie la page Wikipédia d'un animal\n"
        "• `/video` : Envoie une vidéo incroyable\n"
        "• `/quiz` : Propose une question de quiz jusqu'à l'erreur\n"
    )
    await interaction.response.send_message(texte)



# Commande slash : /wiki
@bot.tree.command(name = "wiki", description = "Envoie la page Wikipédia d'un animal")
async def wiki_slash(interaction: discord.Interaction, nom: str):
    """Envoie la page Wikipédia d'un animal"""
    nom = nom.replace(" ", "_")
    await interaction.response.send_message(f"https://fr.wikipedia.org/wiki/{nom}")
    
# Commande slash : /wow
@bot.tree.command(name = "video", description = "Envoie une vidéo incroyable")
async def wow_slash(interaction: discord.Interaction):
    """Envoie une vidéo incroyable"""
    await interaction.response.send_message(wow.choix())


#Commande slash : /quiz
@bot.tree.command(name="quiz", description="Propose une question de quiz jusqu'à l'erreur")
async def quiz_slash(interaction: discord.Interaction):
    """Lance un quiz : le bot pose des questions jusqu'à ce que l'utilisateur se trompe"""
    await quiz.start_quiz(interaction)

@bot.event
async def setup_hook():
    # Charge les extensions (cogs) du bot

    #score_cog procède a la gestion des scores et classemments
    await bot.load_extension("scores_cog")

    #roulette_cog gère la roulette et la collection d'animaux et le reroll
    await bot.load_extension("roulette_cog")


bot.run(os.getenv("DISCORD_TOKEN"))