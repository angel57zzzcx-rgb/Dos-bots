import discord
from discord.ext import commands
from discord import app_commands

# --- CLASE PARA LOS BOTONES ---
class ConfirmacionBan(discord.ui.View):
    def __init__(self, target, autor, razon):
        super().__init__(timeout=30) # El botón expira en 30 segundos
        self.target = target
        self.autor = autor
        self.razon = razon

    @discord.ui.button(label="SÍ, EJECUTAR BAN", style=discord.ButtonStyle.danger, emoji="🔨")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verificar que solo quien puso el comando pueda picar el botón
        if interaction.user.id != self.autor.id:
            return await interaction.response.send_message("❌ No puedes confirmar esto, no es tu comando.", ephemeral=True)

        try:
            await self.target.ban(reason=self.razon)
            
            # Embed de éxito final
            embed_exito = discord.Embed(
                title="🚀 EXPULSIÓN COMPLETADA",
                description=f"El sujeto **{self.target.name}** ha sido eliminado del sistema.",
                color=discord.Color.red()
            )
            embed_exito.add_field(name="ID", value=f"`{self.target.id}`")
            embed_exito.set_footer(text="Registro de seguridad actualizado.")
            
            await interaction.response.edit_message(content=None, embed=embed_exito, view=None)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al banear: {e}", ephemeral=True)

    @discord.ui.button(label="CANCELAR", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.autor.id:
            return await interaction.response.send_message("❌ No puedes cancelar esto.", ephemeral=True)
            
        await interaction.response.edit_message(content="✅ **Operación cancelada.** El usuario está a salvo... por ahora.", embed=None, view=None)

# --- CLASE DEL COG ---
class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Banea a un usuario con panel de confirmación")
    @app_commands.describe(usuario="El usuario a banear", razon="Razón del ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = "No especificada"):
        
        # Evitar baneo a sí mismo o al bot
        if usuario.id == interaction.user.id:
            return await interaction.response.send_message("🛡️ No puedes banearte a ti mismo.", ephemeral=True)

        # Crear el Embed de advertencia
        embed = discord.Embed(
            title="⚠️ ORDEN DE BANEO DETECTADA",
            description=f"¿Estás seguro de que deseas banear permanentemente a **{usuario.mention}**?",
            color=discord.Color.from_rgb(255, 0, 0)
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.add_field(name="👤 Usuario", value=f"{usuario.name}#{usuario.discriminator}", inline=True)
        embed.add_field(name="🆔 ID", value=f"`{usuario.id}`", inline=True)
        embed.add_field(name="📝 Razón", value=f"```{razon}```", inline=False)
        embed.set_footer(text="Esta acción es irreversible una vez confirmada.")

        # Enviar el panel con los botones
        view = ConfirmacionBan(usuario, interaction.user, razon)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
        
