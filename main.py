import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import traceback
from db.db import Database

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="l!", intents=intents)
        self.db = Database()
    
    # ===== SE ESSA MERDA PRECISAR DE MAIS TABELA, É AQUI =====
    async def pools(self):
        await self.db.file_execute("db/schema.sql")

    async def setup_hook(self):
        # Conecta DB e prepara tabelas
        await self.db.connect()
        await self.pools()
        
        # Carrega sistema de itens criptografados
        from services.item_resolver import item_resolver
        print("🔐 Carregando sistema de itens...")
        if item_resolver.load():
            print("✅ Sistema de itens carregado com sucesso")
        else:
            print("⚠️ Falha ao carregar arquivo de itens (Itens.enc)")
            print("   O bot continuará funcionando mas /genitem pode não funcionar corretamente")

        print("📦 Carregando cogs (rpg primeiro)...")
        failed_cogs = []
        
        # Buscar todos os arquivos .py em cogs/ e subpastas
        cog_files = []
        for root, dirs, files in os.walk("./cogs"):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    # Converter caminho para formato de módulo (cogs.rpg.rpg)
                    rel_path = os.path.relpath(os.path.join(root, file), "./cogs")
                    module_path = rel_path.replace("\\", ".").replace("/", ".")[:-3]
                    cog_files.append((file, f"cogs.{module_path}"))
        
        # Garantir que rpg.py carrega primeiro
        ordered = []
        rpg_cog = next((item for item in cog_files if item[0] == "rpg.py"), None)
        if rpg_cog:
            ordered.append(rpg_cog)
            cog_files.remove(rpg_cog)
        
        # Ordenar o resto para determinismo
        ordered.extend(sorted(cog_files, key=lambda x: x[1]))

        for file_name, cog_name in ordered:
            try:
                await self.load_extension(cog_name)
                print(f"✅ Cog carregado: {cog_name}")
            except Exception:
                failed_cogs.append(cog_name)
                print(f"❌ Falha ao carregar cog {cog_name}:")
                traceback.print_exc()

        # Sincroniza slash commands uma única vez
        try:
            # Diagnostic: print command structure to help identify invalid context-menu payloads
            print("🔍 Debug: comandos registrados (preview):")
            def dump_command(cmd, indent=0, idx=0):
                t = getattr(cmd, 'type', None)
                tname = t.name if t is not None else 'GROUP'
                opts = getattr(cmd, 'options', None)
                optlen = len(opts) if opts is not None else 0
                print(('  ' * indent) + f"- [{idx}] name={cmd.name!r} type={tname} options={optlen} desc={getattr(cmd, 'description', None)!r}")
                # recurse for subcommands if group
                try:
                    children = list(getattr(cmd, 'commands', []))
                    for i, ch in enumerate(children):
                        dump_command(ch, indent + 1, i)
                except Exception:
                    pass

            top = list(self.tree.get_commands())
            for i, c in enumerate(top):
                dump_command(c, 0, i)

            await self.tree.sync()
            print("🔥 Slash commands sincronizados com sucesso")
        except Exception as e:
            print("❌ Falha ao sincronizar slash commands:")
            traceback.print_exc()

        if failed_cogs:
            print("⚠️ Alguns cogs não foram carregados:", failed_cogs)
        else:
            print("🔥 Todos os cogs carregados com sucesso")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"🤖 Conectado como {bot.user}")

bot.run(TOKEN)
