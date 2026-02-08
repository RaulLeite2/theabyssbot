"""
Sistema de migrations automático com visual clean
Executa migrations do banco de dados antes dos cogs carregarem
"""
import asyncio
from pathlib import Path
from typing import Optional


class MigrationRunner:
    """Executor de migrations com visual limpo e informativo"""
    
    def __init__(self, db_pool):
        self.db = db_pool
        self.migrations_dir = Path("db/migrations")
        
    def _print_header(self):
        """Cabeçalho bonito para migrations"""
        print("\n" + "─" * 60)
        print("▣ SYSTEM :: DATABASE MIGRATIONS")
        print("─" * 60)
    
    def _print_footer(self):
        """Rodapé bonito"""
        print("─" * 60 + "\n")
    
    def _log(self, emoji: str, msg: str, prefix: str = "MIG"):
        """Log formatado com emoji"""
        print(f"[{prefix}] {emoji} {msg}")
    
    async def run_migration_file(self, migration_file: Path) -> bool:
        """
        Executa um arquivo SQL de migration
        Retorna True se sucesso, False se falhou
        """
        try:
            self._log("📖", f"Reading: {migration_file.name}")
            
            sql_content = migration_file.read_text(encoding="utf-8")
            
            self._log("⏳", "Executing migration...")
            
            async with self.db.acquire() as conn:
                # Executa a migration (ignora outputs de RAISE NOTICE)
                await conn.execute(sql_content)
            
            self._log("✔", f"Migration applied: {migration_file.name}", prefix="MIG")
            return True
            
        except Exception as e:
            self._log("✗", f"Migration failed: {migration_file.name}", prefix="ERR")
            self._log("⚠", f"Error: {str(e)}", prefix="ERR")
            return False
    
    async def check_columns_exist(self) -> dict:
        """Verifica se as colunas críticas existem"""
        try:
            check = await self.db.fetchrow("""
                SELECT 
                    COUNT(*) FILTER (WHERE column_name = 'depth_new') as has_depth,
                    COUNT(*) FILTER (WHERE column_name = 'quality_new') as has_quality
                FROM information_schema.columns 
                WHERE table_name = 'items'
            """)
            
            return {
                "depth_new": check["has_depth"] > 0 if check else False,
                "quality_new": check["has_quality"] > 0 if check else False
            }
        except Exception:
            return {"depth_new": False, "quality_new": False}
    
    async def run_all(self):
        """Executa todas as migrations necessárias"""
        self._print_header()
        
        self._log("▶", "Initializing migration system")
        
        # Verifica se as colunas críticas existem
        self._log("⏳", "Checking database schema...")
        columns = await self.check_columns_exist()
        
        depth_ok = columns.get("depth_new", False)
        quality_ok = columns.get("quality_new", False)
        
        if depth_ok and quality_ok:
            self._log("✔", "Schema up-to-date (depth_new, quality_new exist)")
            self._log("ⓘ", "No migrations needed")
            self._print_footer()
            return True
        
        # Se faltam colunas, executa a migration
        self._log("ⓘ", "Missing columns detected")
        self._log("▶", "Running migration: add_depth_quality_columns.sql")
        
        migration_file = self.migrations_dir / "add_depth_quality_columns.sql"
        
        if not migration_file.exists():
            self._log("✗", f"Migration file not found: {migration_file}", prefix="ERR")
            self._log("⚠", "Critical migration missing - bot may fail!", prefix="ERR")
            self._print_footer()
            return False
        
        success = await self.run_migration_file(migration_file)
        
        if success:
            # Verifica novamente após migration
            self._log("⏳", "Verifying migration results...")
            columns_after = await self.check_columns_exist()
            
            if columns_after["depth_new"] and columns_after["quality_new"]:
                self._log("✔", "Migration completed successfully")
                
                # Mostra estatística rápida
                stats = await self.db.fetchrow("""
                    SELECT 
                        COUNT(*) as total_items,
                        COUNT(depth_new) as with_depth,
                        COUNT(quality_new) as with_quality
                    FROM items
                """)
                
                if stats:
                    self._log("ⓘ", f"Items migrated: {stats['with_depth']}/{stats['total_items']}")
            else:
                self._log("✗", "Migration executed but columns still missing", prefix="ERR")
                success = False
        
        self._print_footer()
        return success


async def run_migrations(db_pool) -> bool:
    """
    Função principal para executar migrations
    Retorna True se tudo OK, False se houve erro
    """
    runner = MigrationRunner(db_pool)
    return await runner.run_all()
