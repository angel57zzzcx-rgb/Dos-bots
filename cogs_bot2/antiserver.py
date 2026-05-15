import discord
from discord.ext import commands
from discord import app_commands
import re # Librería para detectar patrones de texto

class AntiLinks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = True # Estado por defecto
        # Patrón que detecta discord.gg, ://discord.com, discord.me, etc.
        self.invitelink_pattern = re.compile(
            r'(https?://)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite|discord\.com/invite)/[a-zA-Z0-9]+',
            re.IGNORECASE
        )

    @app_commands.command(name="anti_server", description="Activa o desactiva el filtro de invitaciones a otros servidores")
    @app_commands.describe(estado="Activar o Desactivar el filtro")
    @app_commands.choices(estado=[
        app_commands.Choice(name="Activar", value="on"),
        app_commands.Choice(name="Desactivar", value="off")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def anti_server(self, interaction: discord.Interaction, estado: app_commands.Choice[str]):
        self.enabled = (estado.value == "on")
        status_text = "activado ✅" if self.enabled else "desactivado ❌"
        await interaction.response.send_message(f"El filtro de invitaciones ha sido {status_text}.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # No actuar si: el filtro está apagado, es un bot, o es admin
        if not self.enabled or message.author.bot or message.author.guild_permissions.administrator:
            return

        # Buscar el patrón en el contenido del mensaje
        if self.invitelink_pattern.search(message.content):
            try:
                await message.delete()
                await message.channel.send(
                    f"🚫 {message.author.mention}, no se permiten invitaciones a otros servidores.",
                    delete_after=5
                )
            except discord.Forbidden:
                print(f"Error: No tengo permisos para borrar mensajes en {message.channel.name}")

    # Opcional: Detectar también si editan un mensaje viejo para poner el link
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not self.enabled or after.author.bot or after.author.guild_permissions.administrator:
            return

        if self.invitelink_pattern.search(after.content):
            try:
                await after.delete()
                await after.channel.send(
                    f"🚫 {after.author.mention}, no intentes camuflar invitaciones editando mensajes.",
                    delete_after=5
                )
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(AntiLinks(bot))
        
