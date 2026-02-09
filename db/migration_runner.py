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
        
        # Buscar todos os arquivos .sql na pasta migrations
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        # Filtrar apenas arquivos que não são rollback ou README
        migration_files = [
            f for f in migration_files 
            if not f.name.endswith("_rollback.sql") 
            and not f.name.startswith("README")
        ]
        
        if not migration_files:
            self._log("ⓘ", "No migration files found")
            self._print_footer()
            return True
        
        self._log("ⓘ", f"Found {len(migration_files)} migration file(s)")
        
        # Executar cada migration
        all_success = True
        executed_count = 0
        
        for migration_file in migration_files:
            self._log("▶", f"Running: {migration_file.name}")
            
            success = await self.run_migration_file(migration_file)
            
            if success:
                executed_count += 1
            else:
                all_success = False
                self._log("⚠", f"Migration failed, continuing with others...", prefix="WARN")
        
        # Sumário final
        print()  # Espaço
        if all_success:
            self._log("✔", f"All migrations completed ({executed_count}/{len(migration_files)})")
        else:
            self._log("⚠", f"Some migrations failed ({executed_count}/{len(migration_files)})", prefix="WARN")
        
        self._print_footer()
        return all_success


async def run_migrations(db_pool) -> bool:
    """
    Função principal para executar migrations
    Retorna True se tudo OK, False se houve erro
    """
    runner = MigrationRunner(db_pool)
    return await runner.run_all()
