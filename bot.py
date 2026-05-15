import discord
import os
import asyncio
import datetime
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- SERVIDOR WEB PARA RENDER (UPTIME) ---
app = Flask('')

@app.route('/')
def home():
    return "Servidor Multibot: Ambos Bots con Prefijo '.' y Barra '/' Activos."

def run():
    # Render asigna dinámicamente el puerto; usamos 8080 como alternativa por defecto
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CLASE PRINCIPAL DEL BOT ---
class VigilanteBot(commands.Bot):
    def __init__(self):
        # Activamos todos los intents para detectar miembros y mensajes
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=".",  # Configurado con punto (.) para ambos bots
            intents=intents,
            help_command=None
        )
        # Variables globales para que los Cogs las usen
        self.canal_bienvenida = None
        self.user_cooldowns = {}

    async def setup_hook(self):
        # 1. Cargar la carpeta de Cogs
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py') and filename != '__init__.py':
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f'✅ [{self.user or "Bot"}] Módulo cargado: {filename}')
                    except Exception as e:
                        print(f'❌ [{self.user or "Bot"}] Error en {filename}: {e}')
        
        # 2. Sincronizar comandos de barra (Slash Commands) para que funcionen con la barra (/)
        try:
            await self.tree.sync()
            print(f"⚡ [{self.user or 'Bot'}] Comandos de barra (/) sincronizados globalmente.")
        except Exception as e:
            print(f"❌ [{self.user or 'Bot'}] Error sincronizando comandos de barra: {e}")

# --- INSTANCIACIÓN DE LOS DOS BOTS ---
# Ambos bots se crean a partir de la misma clase compartiendo la configuración de punto (.)
bot1 = VigilanteBot()
bot2 = VigilanteBot()

# --- EVENTOS DE INICIO ---
@bot1.event
async def on_ready():
    print(f'------\n[Bot 1] Sesión iniciada como: {bot1.user.name}\nID: {bot1.user.id}\nPrefijo: .\n------')

@bot2.event
async def on_ready():
    print(f'------\n[Bot 2] Sesión iniciada como: {bot2.user.name}\nID: {bot2.user.id}\nPrefijo: .\n------')

# --- EJECUCIÓN CONCURRENTE ---
async def main():
    # Iniciamos el servidor Flask antes que los bots
    keep_alive()
    
    # Cargamos ambos TOKENS desde las variables de entorno de Render
    token_bot1 = os.getenv('DISCORD_TOKEN_BOT_1')
    token_bot2 = os.getenv('DISCORD_TOKEN_BOT_2')
    
    # Validaciones individuales de tokens antes de arrancar los contextos
    if not token_bot1:
        print("❌ ERROR: No se encontró la variable 'DISCORD_TOKEN_BOT_1' en Render.")
    if not token_bot2:
        print("❌ ERROR: No se encontró la variable 'DISCORD_TOKEN_BOT_2' en Render.")

    # Agrupamos las tareas asíncronas de inicio para ejecutarlas en paralelo
    tareas = []
    if token_bot1:
        tareas.append(bot1.start(token_bot1))
    if token_bot2:
        tareas.append(bot2.start(token_bot2))
        
    if tareas:
        # Abrimos el contexto asíncrono para ambos clientes en paralelo
        async with bot1, bot2:
            await asyncio.gather(*tareas)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bots apagados.")
