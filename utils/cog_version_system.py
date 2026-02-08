"""
Gerenciador de Cogs com Suporte Dual: Tier ↔ Depth System
Permite carregar cogs modernos (Depth) enquanto mantém compatibilidade com Tier
"""

import logging
from discord.ext import commands
from pathlib import Path

logger = logging.getLogger(__name__)


class CogVersionSystem:
    """Gerencia versões de cogs durante migração"""
    
    DEPTH_MODE = "depth"
    TIER_MODE = "tier"
    
    MODE = TIER_MODE  # Default: manter modo antigo até migração completa
    
    # Cogs que já foram refatorados para Depth
    REFACTORED_COGS = {
        "rpg_refactored": "cogs.rpg.rpg_refactored",  # Novo RPG com Depth
        "wiki": "cogs.wiki.wiki",  # Wiki já suporta ambos
    }
    
    # Cogs ainda em Tier (antigos)
    LEGACY_COGS = {
        "rpg": "cogs.rpg.rpg",
        "rpg_battle": "cogs.rpg.rpg_battle",
        "rpg_craft": "cogs.rpg.rpg_craft",
        "rpg_explore": "cogs.rpg.rpg_explore",
        "economy": "cogs.economy.economy",
        "arena": "cogs.arena.arena_ui",
    }

    @classmethod
    def get_cogs_to_load(cls, mode: str = None) -> dict:
        """
        Retorna mapa de cogs a carregar baseado no modo
        
        Args:
            mode: "depth" (novo) ou "tier" (compatibilidade)
        """
        if mode is None:
            mode = cls.MODE
        
        cogs_to_load = {}
        
        if mode == cls.DEPTH_MODE:
            # Carregar refatorados + wiki + manter legados que ainda usam tier
            cogs_to_load.update(cls.REFACTORED_COGS)
            cogs_to_load.update({
                k: v for k, v in cls.LEGACY_COGS.items()
                if k not in ["rpg", "rpg_battle", "rpg_craft", "rpg_explore"]
            })
            logger.info("📦 Modo DEPTH: Carregando cogs refatorados + legados")
        
        else:  # TIER_MODE
            # Carregar apenas legacy (modo compatibilidade total)
            cogs_to_load.update(cls.LEGACY_COGS)
            cogs_to_load.update({"wiki": cls.REFACTORED_COGS["wiki"]})
            logger.info("📦 Modo TIER: Carregando cogs legados (compatibilidade completa)")
        
        return cogs_to_load

    @classmethod
    async def load_cogs(cls, bot: commands.Bot, mode: str = None):
        """Carrega cogs apropriados baseado no modo"""
        cogs = cls.get_cogs_to_load(mode)
        
        failed = []
        for cog_name, cog_module in cogs.items():
            try:
                await bot.load_extension(cog_module)
                logger.info(f"✅ Cog carregado: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar {cog_name}: {e}")
                failed.append((cog_name, str(e)))
        
        if failed:
            logger.warning(f"⚠️  {len(failed)} cogs falharam ao carregar")
        
        return len(cogs) - len(failed), len(cogs)

    @classmethod
    def switch_mode(cls, new_mode: str):
        """Alterna o modo de operação"""
        if new_mode not in [cls.DEPTH_MODE, cls.TIER_MODE]:
            raise ValueError(f"Modo inválido: {new_mode}")
        
        cls.MODE = new_mode
        logger.info(f"🔄 Modo alterado para: {new_mode}")


# Helper functions para uso em main.py

async def load_adaptive_cogs(bot: commands.Bot):
    """Carrega cogs com suporte automático a ambos sistemas"""
    # Verificar se banco está em Depth Mode
    try:
        migrated = await bot.db.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='sanctuary')"
        )
        
        if migrated:
            mode = CogVersionSystem.DEPTH_MODE
            logger.info("✅ Banco em DEPTH mode - carregando cogs refatorados")
        else:
            mode = CogVersionSystem.TIER_MODE
            logger.info("⚠️  Banco ainda em TIER mode - modo compatibilidade")
        
    except Exception as e:
        logger.warning(f"Não foi possível detectar modo, usando TIER: {e}")
        mode = CogVersionSystem.TIER_MODE
    
    loaded, total = await CogVersionSystem.load_cogs(bot, mode)
    logger.info(f"📦 {loaded}/{total} cogs carregados com sucesso")
