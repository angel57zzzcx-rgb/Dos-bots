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
    return "Servidor Multibot: Carpetas Cogs Separadas Activas."

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CLASE PRINCIPAL DEL BOT ---
class VigilanteBot(commands.Bot):
    def __init__(self, folder_name):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=".", 
            intents=intents,
            help_command=None
        )
        self.folder_name = folder_name  # Carpeta asignada a este bot
        self.canal_bienvenida = None
        self.user_cooldowns = {}

    async def setup_hook(self):
        # 1. Cargar la carpeta de Cogs asignada de forma independiente
        if os.path.exists(f'./{self.folder_name}'):
            for filename in os.listdir(f'./{self.folder_name}'):
                if filename.endswith('.py') and filename != '__init__.py':
                    try:
                        await self.load_extension(f'{self.folder_name}.{filename[:-3]}')
                        print(f'✅ [{self.user or "Bot"}] Módulo cargado desde {self.folder_name}: {filename}')
                    except Exception as e:
                        print(f'❌ [{self.user or "Bot"}] Error en {filename}: {e}')
        
        # 2. Sincronizar comandos de barra (Slash Commands)
        try:
            await self.tree.sync()
            print(f"⚡ [{self.user or 'Bot'}] Comandos de barra (/) sincronizados.")
        except Exception as e:
            print(f"❌ [{self.user or 'Bot'}] Error sincronizando comandos de barra: {e}")

# --- INSTANCIACIÓN DE LOS DOS BOTS CON SUS RESPECTIVAS CARPETAS ---
bot1 = VigilanteBot(folder_name="cogs_bot1")
bot2 = VigilanteBot(folder_name="cogs_bot2")

# --- EVENTOS DE INICIO ---
@bot1.event
async def on_ready():
    print(f'------\n[Bot 1] Sesión iniciada como: {bot1.user.name}\nID: {bot1.user.id}\nCarpeta: cogs_bot1\n------')

@bot2.event
async def on_ready():
    print(f'------\n[Bot 2] Sesión iniciada como: {bot2.user.name}\nID: {bot2.user.id}\nCarpeta: cogs_bot2\n------')

# --- EJECUCIÓN CONCURRENTE ---
async def main():
    keep_alive()
    
    token_bot1 = os.getenv('DISCORD_TOKEN_BOT_1')
    token_bot2 = os.getenv('DISCORD_TOKEN_BOT_2')
    
    if not token_bot1:
        print("❌ ERROR: No se encontró 'DISCORD_TOKEN_BOT_1' en Render.")
    if not token_bot2:
        print("❌ ERROR: No se encontró 'DISCORD_TOKEN_BOT_2' en Render.")

    tareas = []
    if token_bot1:
        tareas.append(bot1.start(token_bot1))
    if token_bot2:
        tareas.append(bot2.start(token_bot2))
        
    if tareas:
        async with bot1, bot2:
            await asyncio.gather(*tareas)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bots apagados.")
        
