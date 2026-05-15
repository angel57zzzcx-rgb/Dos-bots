import discord
from discord.ext import commands
from discord import app_commands

class Verificar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Nota: Para un bot real de GitHub, considera usar una base de datos 
        # para que la config no se borre al reiniciar.
        self.config = {} 

    # --- COMANDO SLASH PARA ADMINS ---
    @app_commands.command(name="verificar_setup", description="Configura el canal y el rol de verificación")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(canal="Canal para el comando !verificar", rol="Rol que se entregará")
    async def verificar_setup(self, interaction: discord.Interaction, canal: discord.TextChannel, rol: discord.Role):
        """Configura el sistema de verificación (Solo Administradores)"""
        self.config[interaction.guild.id] = {
            "canal_id": canal.id,
            "rol_id": rol.id
        }
        
        await interaction.response.send_message(
            f"✅ **Configuración exitosa**\nCanal: {canal.mention}\nRol: {rol.mention}",
            ephemeral=True
        )

    # --- COMANDO DE TEXTO PARA USUARIOS ---
    @commands.command(name="verificar")
    async def verificar(self, ctx):
        """Comando para que los miembros obtengan el rol"""
        guild_id = ctx.guild.id
        
        # 1. Verificar si está configurado
        if guild_id not in self.config:
            return await ctx.send("❌ El sistema de verificación no ha sido configurado por un admin.")

        conf = self.config[guild_id]

        # 2. Verificar si es el canal correcto
        if ctx.channel.id != conf["canal_id"]:
            return # Silencio si lo escriben en otro lado

        role = ctx.guild.get_role(conf["rol_id"])
        if not role:
            return await ctx.send("❌ El rol de verificación ya no existe.")

        # 3. Lógica de verificación
        if role in ctx.author.roles:
            await ctx.send(f"⚠️ {ctx.author.mention}, ya estás verificado.")
        else:
            try:
                await ctx.author.add_roles(role)
                await ctx.send(f"✅ {ctx.author.mention}, verificado correctamente.")
            except discord.Forbidden:
                await ctx.send("❌ Error: No tengo permisos suficientes para dar ese rol (sube mi rol en la lista).")

    # Manejador de errores para el comando slash
    @verificar_setup.error
    async def setup_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Necesitas permisos de Administrador.", ephemeral=True)

# Función necesaria para cargar el Cog
async def setup(bot):
    await bot.add_cog(Verificar(bot))
        
