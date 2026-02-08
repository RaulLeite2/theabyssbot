import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import traceback
import json
import logging
import sys
import asyncio
from pathlib import Path
from db.db import Database

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("theabyssbot")


def _excepthook(exc_type, exc, tb):
    logger.exception("Unhandled exception", exc_info=(exc_type, exc, tb))


sys.excepthook = _excepthook

CRAFTS_PATH = Path("data/crafts.json")


def load_crafts_file() -> dict:
    """Load crafts json for debug/validation only."""
    if not CRAFTS_PATH.exists():
        logger.warning("Crafts file not found: %s", CRAFTS_PATH)
        return {}

    try:
        data = json.loads(CRAFTS_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to read crafts file: %s", exc)
        return {}

    schema = data.get("schema")
    recipes = data.get("recipes")
    runes = data.get("runes")

    if schema != "the_abyss_crafting_v1":
        logger.warning("Crafts schema mismatch: %s", schema)

    if not isinstance(recipes, list):
        logger.warning("Crafts recipes missing or invalid")
        recipes = []

    if not isinstance(runes, list):
        logger.warning("Crafts runes missing or invalid")
        runes = []

    logger.debug("Crafts loaded: recipes=%s runes=%s", len(recipes), len(runes))
    return data

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="l!", intents=intents)
        self.db = Database()

    # ===== SE ESSA MERDA PRECISAR DE MAIS TABELA, E AQUI =====
    async def pools(self):
        await self.db.file_execute("db/schema.sql")

    async def setup_hook(self):
        logger.info("Pre-start: setup_hook iniciando")

        loop = None
        try:
            loop = asyncio.get_running_loop()
        except Exception:
            loop = None

        if loop:
            def loop_exception_handler(_loop, context):
                msg = context.get("message", "Asyncio exception")
                exc = context.get("exception")
                if exc:
                    logger.exception("%s", msg, exc_info=exc)
                else:
                    logger.error("%s", msg)

            loop.set_exception_handler(loop_exception_handler)

        try:
            await self.db.connect()
            logger.info("Database conectado")
            await self.pools()
            logger.info("Database schema ok")
        except Exception:
            logger.exception("Erro ao conectar ou preparar DB")

        load_crafts_file()

        # Carrega sistema de itens criptografados
        from services.item_resolver import item_resolver
        logger.info("Carregando sistema de itens")
        if item_resolver.load():
            logger.info("Sistema de itens carregado")
        else:
            logger.warning("Falha ao carregar arquivo de itens (Itens.enc)")
            logger.warning("Bot continua, mas /genitem pode falhar")

        logger.info("Carregando cogs (rpg primeiro)")
        failed_cogs = []

        # Buscar todos os arquivos .py em cogs/ e subpastas
        cog_files = []
        for root, dirs, files in os.walk("./cogs"):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    # Converter caminho para formato de modulo (cogs.rpg.rpg)
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
                logger.info("Cog carregado: %s", cog_name)
            except Exception:
                failed_cogs.append(cog_name)
                logger.exception("Falha ao carregar cog %s", cog_name)

        # Sincroniza slash commands uma unica vez
        try:
            logger.debug("Comandos registrados (preview)")

            def dump_command(cmd, indent=0, idx=0):
                t = getattr(cmd, "type", None)
                tname = t.name if t is not None else "GROUP"
                opts = getattr(cmd, "options", None)
                optlen = len(opts) if opts is not None else 0
                logger.debug(
                    "%s- [%s] name=%r type=%s options=%s desc=%r",
                    "  " * indent,
                    idx,
                    cmd.name,
                    tname,
                    optlen,
                    getattr(cmd, "description", None),
                )
                # recurse for subcommands if group
                try:
                    children = list(getattr(cmd, "commands", []))
                    for i, ch in enumerate(children):
                        dump_command(ch, indent + 1, i)
                except Exception:
                    pass

            top = list(self.tree.get_commands())
            for i, c in enumerate(top):
                dump_command(c, 0, i)

            await self.tree.sync()
            logger.info("Slash commands sincronizados")
        except Exception:
            logger.exception("Falha ao sincronizar slash commands")

        if failed_cogs:
            logger.warning("Alguns cogs nao foram carregados: %s", failed_cogs)
        else:
            logger.info("Todos os cogs carregados")

bot = MyBot()

@bot.event
async def on_ready():
    logger.info("Conectado como %s", bot.user)

bot.run(TOKEN)
