import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Purga(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando de barra (Slash Command)
    @app_commands.command(name="purga", description="Elimina una cantidad específica de mensajes")
    @app_commands.describe(cantidad="Número de mensajes a borrar")
    @app_commands.checks.has_permissions(manage_messages=True) # Solo gente con permiso
    async def purga(self, interaction: discord.Interaction, cantidad: int):
        # 1. Diferir respuesta para evitar error de tiempo de espera
        await interaction.response.defer(ephemeral=True)

        if cantidad <= 0:
            return await interaction.followup.send("⚠️ Debes borrar al menos 1 mensaje.", ephemeral=True)

        try:
            # 2. Realizar la purga
            eliminados = await interaction.channel.purge(limit=cantidad)
            
            # 3. Notificar al usuario (mensaje efímero que solo él ve)
            await interaction.followup.send(f"🧹 **Limpieza completada:** Se han eliminado `{len(eliminados)}` mensajes.", ephemeral=True)
            
            # 4. Mensaje público temporal para intimidar atacantes
            aviso_publico = await interaction.channel.send(f"🛡️ **Protocolo de Limpieza:** {len(eliminados)} registros eliminados por {interaction.user.mention}.")
            await asyncio.sleep(5) # Espera 5 segundos
            await aviso_publico.delete() # Se borra solo

        except discord.Forbidden:
            await interaction.followup.send("❌ No tengo permisos suficientes para gestionar mensajes.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Ocurrió un error: {e}", ephemeral=True)

    # Manejador de errores para permisos
    @purga.error
    async def purga_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("⛔ No tienes permisos de **Gestionar Mensajes** para usar esto.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Purga(bot))
      
