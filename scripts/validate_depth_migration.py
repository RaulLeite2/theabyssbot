#!/usr/bin/env python3
"""
Validador de Integridade Pós-Migração
Verifica se a migração Tier → Depth foi bem-sucedida
Uso: python scripts/validate_depth_migration.py
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.depth_system import TierMigrator, Quality
from db.db import Database


class MigrationValidator:
    """Valida integridade da migração"""

    def __init__(self, db: Database):
        self.db = db
        self.checks_passed = 0
        self.checks_failed = 0
        self.issues = []

    def _log_pass(self, msg: str):
        print(f"✅ {msg}")
        self.checks_passed += 1

    def _log_fail(self, msg: str):
        print(f"❌ {msg}")
        self.checks_failed += 1
        self.issues.append(msg)

    def _log_warn(self, msg: str):
        print(f"⚠️  {msg}")

    async def check_columns_exist(self) -> bool:
        """Verifica se colunas novas existem"""
        print("\n🔍 [1] Verificando existência de colunas...")
        
        query = """
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'items' 
        AND column_name IN ('depth_new', 'quality_new', 'plus_level')
        """
        
        result = await self.db.fetch(query)
        columns = set(r['column_name'] for r in result)
        
        required = {'depth_new', 'quality_new', 'plus_level'}
        
        if required == columns:
            self._log_pass("Todas as colunas criadas corretamente")
            return True
        else:
            missing = required - columns
            self._log_fail(f"Colunas faltando: {missing}")
            return False

    async def check_data_conversion(self) -> bool:
        """Verifica se conversão de dados foi bem-sucedida"""
        print("\n🔍 [2] Verificando conversão de dados...")
        
        query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN depth_new IS NOT NULL THEN 1 END) as converted,
            COUNT(CASE WHEN depth_new IS NULL THEN 1 END) as nulls
        FROM items
        """
        
        result = await self.db.fetchrow(query)
        
        if result['total'] == 0:
            self._log_warn("Tabela items vazia")
            return True
        
        conversion_rate = (result['converted'] / result['total']) * 100
        
        if result['nulls'] == 0:
            self._log_pass(f"Todos {result['total']} items convertidos (100%)")
            return True
        else:
            self._log_fail(f"{result['nulls']} items com depth_new = NULL")
            return False

    async def check_quality_values(self) -> bool:
        """Verifica se qualidades correspondem ao enum"""
        print("\n🔍 [3] Verificando valores de qualidade...")
        
        valid_qualities = {q.value for q in Quality}
        
        query = """
        SELECT DISTINCT quality_new FROM items WHERE quality_new IS NOT NULL
        """
        
        result = await self.db.fetch(query)
        found_qualities = {r['quality_new'] for r in result}
        
        invalid = found_qualities - valid_qualities
        
        if not invalid:
            self._log_pass(f"Todas as qualidades válidas: {found_qualities}")
            return True
        else:
            self._log_fail(f"Qualidades inválidas encontradas: {invalid}")
            return False

    async def check_depth_ranges(self) -> bool:
        """Verifica se depth está no range 1-8"""
        print("\n🔍 [4] Verificando ranges de depth...")
        
        query = """
        SELECT 
            MIN(depth_new) as min_depth,
            MAX(depth_new) as max_depth,
            COUNT(*) as count
        FROM items WHERE depth_new IS NOT NULL
        """
        
        result = await self.db.fetchrow(query)
        
        if result['count'] == 0:
            self._log_warn("Nenhum item com depth")
            return True
        
        if 1 <= result['min_depth'] and result['max_depth'] <= 8:
            self._log_pass(f"Depth range válido: {result['min_depth']}-{result['max_depth']}")
            return True
        else:
            self._log_fail(f"Depth fora do range: {result['min_depth']}-{result['max_depth']}")
            return False

    async def check_plus_levels(self) -> bool:
        """Verifica se plus_level está no range 0-10"""
        print("\n🔍 [5] Verificando plus_levels...")
        
        query = """
        SELECT 
            MIN(plus_level) as min_plus,
            MAX(plus_level) as max_plus
        FROM items
        """
        
        result = await self.db.fetchrow(query)
        
        if 0 <= result['min_plus'] and result['max_plus'] <= 10:
            self._log_pass(f"Plus level range válido: {result['min_plus']}-{result['max_plus']}")
            return True
        else:
            self._log_fail(f"Plus level fora do range: {result['min_plus']}-{result['max_plus']}")
            return False

    async def check_sanctuary_tables(self) -> bool:
        """Verifica se tabelas de sanctuary foram atualizadas"""
        print("\n🔍 [6] Verificando tabelas de sanctuary...")
        
        query1 = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'sanctuary'
        )
        """
        
        query2 = """
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'sanctuary' AND column_name = 'energy'
        """
        
        table_exists = (await self.db.fetchrow(query1))['exists']
        energy_col = await self.db.fetch(query2)
        
        if not table_exists:
            self._log_fail("Tabela 'sanctuary' não encontrada (ainda é 'hideout'?)")
            return False
        
        if energy_col:
            self._log_pass("Tabela sanctuary com coluna 'energy'")
            return True
        else:
            self._log_warn("Coluna 'energy' não encontrada em sanctuary")
            return False

    async def check_backward_compatibility(self) -> bool:
        """Verifica se dados antigos (tier) ainda existem"""
        print("\n🔍 [7] Verificando compatibilidade com dados antigos...")
        
        query = """
        SELECT COUNT(*) as cnt FROM items WHERE tier IS NOT NULL
        """
        
        result = await self.db.fetchrow(query)
        
        if result['cnt'] > 0:
            self._log_pass(f"Dados antigos (tier) preservados: {result['cnt']} items")
            return True
        else:
            self._log_warn("Nenhum dado tier encontrado (possível que tenha sido apagado)")
            return False

    async def check_indexes(self) -> bool:
        """Verifica se índices foram criados"""
        print("\n🔍 [8] Verificando índices...")
        
        query = """
        SELECT indexname FROM pg_indexes 
        WHERE tablename IN ('items', 'equipment', 'sanctuary')
        AND indexname LIKE '%depth%quality%'
        """
        
        result = await self.db.fetch(query)
        
        if result:
            self._log_pass(f"Índices de performance criados: {len(result)}")
            return True
        else:
            self._log_warn("Índices não encontrados (performance pode ser afetada)")
            return False

    async def run_all_checks(self) -> bool:
        """Executa todos os checks"""
        print("="*60)
        print("🔐 VALIDADOR DE MIGRAÇÃO DEPTH")
        print("="*60)
        
        checks = [
            ("Colunas", self.check_columns_exist),
            ("Conversão", self.check_data_conversion),
            ("Qualidades", self.check_quality_values),
            ("Depth Range", self.check_depth_ranges),
            ("Plus Levels", self.check_plus_levels),
            ("Sanctuary", self.check_sanctuary_tables),
            ("Compatibilidade", self.check_backward_compatibility),
            ("Índices", self.check_indexes),
        ]
        
        for name, check_func in checks:
            try:
                await check_func()
            except Exception as e:
                self._log_fail(f"{name}: {e}")
        
        return self._print_summary()

    def _print_summary(self) -> bool:
        """Exibe resumo dos checks"""
        print("\n" + "="*60)
        print("📊 RESUMO")
        print("="*60)
        print(f"✅ Passou: {self.checks_passed}")
        print(f"❌ Falhou: {self.checks_failed}")
        
        if self.issues:
            print("\n⚠️  ISSUES ENCONTRADAS:")
            for issue in self.issues:
                print(f"  - {issue}")
        
        print("="*60)
        return self.checks_failed == 0


async def main():
    """Entry point"""
    db = Database()
    await db.connect()
    
    try:
        validator = MigrationValidator(db)
        all_passed = await validator.run_all_checks()
        return 0 if all_passed else 1
    finally:
        await db.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
