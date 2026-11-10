import discord
from discord import app_commands
from discord.ext import commands

import roulette


CHOIX_ANIMAUX = [
    app_commands.Choice(name=a["nom"], value=cle)
    for cle, a in roulette.ANIMAUX.items()
]


class RouletteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roulette", description="Tire un animal au hasard pour ta collection")
    async def roulette_slash(self, interaction: discord.Interaction):
        cle = roulette.tirer()
        animal = roulette.ANIMAUX[cle]
        try:
            quantite = await roulette.ajouter_animal(
                interaction.user.id, interaction.user.display_name, cle)
        except Exception as erreur:
            print(f"Erreur MongoDB : {erreur}")
            await interaction.response.send_message(
                "Base de données indisponible.")
            return
        texte = (f"🎰 {interaction.user.mention} a obtenu : "
                 f"{animal['emoji']} **{animal['nom']}** ({animal['rarete']}, {animal['poids']} %)")
        if quantite == 1:
            texte += "\n✨ Nouvel animal dans ta collection !"
        else:
            texte += f"\nTu en as maintenant **{quantite}**."
        await interaction.response.send_message(texte)

    @app_commands.command(name="collection", description="Affiche ta collection d'animaux")
    async def collection_slash(self, interaction: discord.Interaction):
        try:
            possedes = await roulette.collection_user(interaction.user.id)
        except Exception as erreur:
            print(f"Erreur MongoDB : {erreur}")
            await interaction.response.send_message("Base de données indisponible.")
            return
        lignes = []
        for cle, a in roulette.ANIMAUX.items():
            qte = possedes.get(cle, 0)
            if qte:
                lignes.append(f"{a['emoji']} **{a['nom']}** x{qte} - {a['rarete']}")
            else:
                lignes.append(f"❔ ??? - {a['rarete']}")
        decouverts = sum(1 for c in roulette.ANIMAUX if possedes.get(c, 0))
        await interaction.response.send_message(
            f"**Collection de {interaction.user.display_name}** "
            f"({decouverts}/{len(roulette.ANIMAUX)})\n" + "\n".join(lignes))

    @app_commands.command(name="fusion", description="Fusionne 3 animaux identiques en un nouvel animal")
    @app_commands.describe(animal="L'animal à fusionner (3 exemplaires requis)")
    @app_commands.choices(animal=CHOIX_ANIMAUX)
    async def fusion_slash(self, interaction: discord.Interaction, animal: app_commands.Choice[str]):
        cle = animal.value
        cout = roulette.COUT_FUSION
        retires = False
        try:
            ok = await roulette.retirer_animaux(interaction.user.id, cle, cout)
            if not ok:
                await interaction.response.send_message(
                    f"Il te faut **{cout}** {roulette.ANIMAUX[cle]['nom']} pour fusionner.",
                    ephemeral=True)
                return
            retires = True
            nouvelle_cle = roulette.tirer()
            quantite = await roulette.ajouter_animal(
                interaction.user.id, interaction.user.display_name, nouvelle_cle)
        except Exception as erreur:
            print(f"Erreur MongoDB : {erreur}")
            # Si les animaux ont été retirés mais que le nouveau n'a pas été
            # ajouté, on rend les animaux à l'utilisateur.
            if retires:
                try:
                    await roulette.ajouter_animal(
                        interaction.user.id, interaction.user.display_name, cle, cout)
                except Exception as erreur2:
                    print(f"Erreur MongoDB (remboursement) : {erreur2}")
            await interaction.response.send_message("Base de données indisponible.")
            return

        ancien = roulette.ANIMAUX[cle]
        nouveau = roulette.ANIMAUX[nouvelle_cle]
        texte = (f"🔮 {interaction.user.mention} fusionne {cout} x {ancien['emoji']} **{ancien['nom']}** "
                 f"et obtient : {nouveau['emoji']} **{nouveau['nom']}** ({nouveau['rarete']})")
        if quantite == 1:
            texte += "\n✨ Nouvel animal dans ta collection !"
        else:
            texte += f"\nTu en as maintenant **{quantite}**."
        await interaction.response.send_message(texte)


async def setup(bot: commands.Bot):
    await bot.add_cog(RouletteCog(bot))