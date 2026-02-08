#!/usr/bin/env python3
"""
Script de Migração: Tier → Depth System
Executa a migração do banco de dados de forma segura com validação
Uso: python scripts/migrate_to_depth.py [--rollback]
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

# Importar módulos do bot
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.depth_system import TierMigrator, DepthTier, Quality
from db.db import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class MigrationManager:
    """Gerencia migração de Tier → Depth com rollback seguro"""

    def __init__(self, db: Database):
        self.db = db
        self.migrated_count = 0
        self.error_count = 0
        self.blocked_items = []

    async def backup_database(self) -> bool:
        """Cria backup antes da migração"""
        logger.info("⏳ Criando backup do banco de dados...")
        try:
            backup_path = Path("db/backups") / f"backup_{int(__import__('time').time())}.sql"
            backup_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Usar pg_dump se PostgreSQL
            os.system(f"pg_dump $DATABASE_URL > {backup_path}")
            logger.info(f"✅ Backup criado em {backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return False

    async def validate_migration(self) -> bool:
        """Valida se a migração pode ser executada"""
        logger.info("🔍 Validando banco de dados...")
        
        # Verificar se colunas novas já existem
        query = """
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'items' AND column_name = 'depth_new'
        """
        result = await self.db.fetch(query)
        
        if result:
            logger.warning("⚠️  Colunas de depth_new já existem!")
            return False
        
        logger.info("✅ Validação concluída - seguro para migrar")
        return True

    async def execute_migration(self) -> bool:
        """Executa a migração (em transação para segurança)"""
        logger.info("🚀 Iniciando migração Tier → Depth...")
        
        try:
            # Ler arquivo SQL de migração
            migration_sql = Path("db/migrations/001_tier_to_depth_migration.sql").read_text()
            
            # Executar em transação
            async with self.db.pool.acquire() as conn:
                async with conn.transaction():
                    # Executar migration
                    statements = migration_sql.split(';')
                    for stmt in statements:
                        stmt = stmt.strip()
                        if stmt and not stmt.startswith('--'):
                            await conn.execute(stmt)
            
            logger.info("✅ Migração SQL executada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na migração: {e}")
            return False

    async def validate_conversion(self) -> bool:
        """Valida que todos os items foram convertidos"""
        logger.info("📊 Validando conversão de dados...")
        
        query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN depth_new IS NULL THEN 1 END) as nulls_depth,
            COUNT(CASE WHEN quality_new IS NULL THEN 1 END) as nulls_quality
        FROM items
        """
        
        result = await self.db.fetchrow(query)
        logger.info(f"   Total items: {result['total']}")
        logger.info(f"   Nulls em depth: {result['nulls_depth']}")
        logger.info(f"   Nulls em quality: {result['nulls_quality']}")
        
        if result['nulls_depth'] > 0 or result['nulls_quality'] > 0:
            logger.warning(f"⚠️  {result['nulls_depth'] + result['nulls_quality']} items com problema!")
            return False
        
        logger.info("✅ Todos os items convertidos corretamente")
        return True

    async def rename_hideout_to_sanctuary(self) -> bool:
        """Renomeia hideout para sanctuary na aplicação"""
        logger.info("🏰 Renomeando Hideout → Sanctuary...")
        
        # Criar arquivo de configuração para o bot saber
        config = {
            "version": "2.0",
            "migration_date": __import__('datetime').datetime.now().isoformat(),
            "system": "depth",
            "sanctuary_enabled": True,
            "tier_system_deprecated": True
        }
        
        config_path = Path("config/migration_config.json")
        config_path.parent.mkdir(exist_ok=True, parents=True)
        config_path.write_text(json.dumps(config, indent=2))
        
        logger.info("✅ Configuração de sanctuary criada")
        return True

    async def summary_and_stats(self):
        """Exibe resumo da migração"""
        logger.info("\n" + "="*60)
        logger.info("📋 RESUMO DA MIGRAÇÃO")
        logger.info("="*60)
        
        # Stats do banco
        query1 = "SELECT COUNT(*) as cnt FROM items WHERE depth_new IS NOT NULL"
        query2 = "SELECT COUNT(DISTINCT quality_new) as cnt FROM items"
        
        items_count = (await self.db.fetchrow(query1))['cnt']
        quality_types = (await self.db.fetchrow(query2))['cnt']
        
        logger.info(f"✅ Items convertidos: {items_count}")
        logger.info(f"✅ Tipos de qualidade: {quality_types}")
        logger.info(f"✅ Sistema: Tier → Depth")
        logger.info(f"✅ Sanctuary habilitado: Sim")
        logger.info("="*60 + "\n")

    async def execute_rollback(self) -> bool:
        """Executa rollback da migração"""
        logger.warning("🔄 EXECUTANDO ROLLBACK...")
        logger.warning("⚠️  AVISO: Isto vai reverter TODAS as mudanças da migração!")
        
        if input("Digite 'ROLLBACK' para confirmar: ") != "ROLLBACK":
            logger.info("Rollback cancelado")
            return False
        
        try:
            rollback_sql = Path("db/migrations/001_tier_to_depth_migration_rollback.sql").read_text()
            
            async with self.db.pool.acquire() as conn:
                async with conn.transaction():
                    statements = rollback_sql.split(';')
                    for stmt in statements:
                        stmt = stmt.strip()
                        if stmt and not stmt.startswith('--'):
                            await conn.execute(stmt)
            
            logger.warning("✅ Rollback executado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no rollback: {e}")
            return False


async def main():
    """Função principal"""
    
    # Argumentos
    do_rollback = "--rollback" in sys.argv
    
    # Conectar ao banco
    from db.db import Database
    db = Database()
    await db.connect()
    
    try:
        manager = MigrationManager(db)
        
        if do_rollback:
            # Executar rollback
            success = await manager.execute_rollback()
        else:
            # Executar migração
            logger.info("🔐 MIGRAÇÃO: TIER SYSTEM → DEPTH SYSTEM")
            logger.info("="*60)
            
            # Validações
            if not await manager.backup_database():
                logger.error("Falha ao criar backup - abortando")
                return 1
            
            if not await manager.validate_migration():
                logger.error("Validação falhou - abortando")
                return 1
            
            # Executar
            if not await manager.execute_migration():
                logger.error("Migração falhou - execute rollback")
                return 1
            
            # Validar conversão
            if not await manager.validate_conversion():
                logger.warning("Conversão incompleta - revise manualmente")
                return 1
            
            # Concluir
            await manager.rename_hideout_to_sanctuary()
            await manager.summary_and_stats()
            success = True
        
        return 0 if success else 1
        
    finally:
        await db.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
