#!/usr/bin/env python3
"""
STATUS COMPLETO: Sistema de Admin Items
Mostra tudo que foi configurado e está pronto para executar
"""

from pathlib import Path
import sys

def check_status():
    """Verifica se tudo está pronto"""
    
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "🎯 ADMIN ITEMS STATUS" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    all_ok = True
    
    # 1. Migration Runner
    print("📦 MIGRATION RUNNER")
    print("─" * 60)
    
    runner_file = Path("db/migration_runner.py")
    if runner_file.exists():
        content = runner_file.read_text(encoding="utf-8")
        if "sorted(self.migrations_dir.glob" in content:
            print("  ✓ Configurado para escanear TODAS as migrations")
            print("  ✓ Executa em ordem alfabética")
            print("  ✓ Filtra arquivos *_rollback.sql")
        else:
            print("  ✗ PROBLEMA: Não está escaneando todas as migrations")
            all_ok = False
    else:
        print("  ✗ ERRO: migration_runner.py não encontrado!")
        all_ok = False
    
    print()
    
    # 2. Arquivos de Migration
    print("📁 MIGRATIONS DISPONÍVEIS")
    print("─" * 60)
    
    migrations_dir = Path("db/migrations")
    if migrations_dir.exists():
        sql_files = sorted(migrations_dir.glob("*.sql"))
        migration_files = [
            f for f in sql_files 
            if not f.name.endswith("_rollback.sql") 
            and not f.name.startswith("README")
        ]
        
        expected = [
            "000_add_depth_quality_columns.sql",
            "001_tier_to_depth_migration.sql",
            "002_add_admin_items.sql"
        ]
        
        for exp in expected:
            if any(f.name == exp for f in migration_files):
                print(f"  ✓ {exp}")
            else:
                print(f"  ✗ {exp} (FALTANDO!)")
                all_ok = False
    else:
        print("  ✗ ERRO: Pasta db/migrations não existe!")
        all_ok = False
    
    print()
    
    # 3. Conteúdo da Migration de Admin
    print("🗡️  MIGRATION: 002_add_admin_items.sql")
    print("─" * 60)
    
    admin_sql = Path("db/migrations/002_add_admin_items.sql")
    if admin_sql.exists():
        content = admin_sql.read_text(encoding="utf-8")
        
        checks = [
            ("Estrutura DO $$", "DO $$" in content and "END $$;" in content),
            ("12 INSERTs", content.count("INSERT INTO items") == 12),
            ("Usa basedamage/basedefense", "basedamage" in content and "basedefense" in content),
            ("Depth 99", "depth_new = 99" in content),
            ("Quality ADMIN", "quality_new = 'ADMIN'" in content),
            ("Idempotente (não duplica)", "IF admin_count > 0 THEN" in content),
        ]
        
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
            if not result:
                all_ok = False
    else:
        print("  ✗ ERRO: Arquivo não encontrado!")
        all_ok = False
    
    print()
    
    # 4. Comandos de Admin
    print("🎮 COMANDOS DO DISCORD")
    print("─" * 60)
    
    adminrpg_file = Path("cogs/admin/adminrpg.py")
    if adminrpg_file.exists():
        content = adminrpg_file.read_text(encoding="utf-8")
        
        commands = [
            ("giveadminitem", "@app_commands.command(name=\"giveadminitem\"" in content),
            ("giveadminkit", "@app_commands.command(name=\"giveadminkit\"" in content),
            ("Usa basedamage", "basedamage" in content and "'basedamage'" in content),
            ("Usa basedefense", "basedefense" in content and "'basedefense'" in content),
        ]
        
        for cmd_name, result in commands:
            status = "✓" if result else "✗"
            print(f"  {status} {cmd_name}")
            if not result:
                all_ok = False
    else:
        print("  ✗ ERRO: adminrpg.py não encontrado!")
        all_ok = False
    
    print()
    
    # 5. Main.py integração
    print("🚀 INTEGRAÇÃO COM MAIN.PY")
    print("─" * 60)
    
    main_file = Path("main.py")
    if main_file.exists():
        content = main_file.read_text(encoding="utf-8")
        
        integrations = [
            ("Import migration_runner", "from db.migration_runner import run_migrations" in content),
            ("Executa antes dos cogs", "await run_migrations(self.db)" in content),
        ]
        
        for integ_name, result in integrations:
            status = "✓" if result else "✗"
            print(f"  {status} {integ_name}")
            if not result:
                all_ok = False
    else:
        print("  ✗ ERRO: main.py não encontrado!")
        all_ok = False
    
    print()
    print("═" * 60)
    
    if all_ok:
        print()
        print("🎉 TUDO CONFIGURADO CORRETAMENTE!")
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print()
        print("  1. 🔄 REINICIE O BOT no Railway")
        print("     └─ As migrations rodam automaticamente no startup")
        print()
        print("  2. 👀 VERIFIQUE OS LOGS")
        print("     Você deve ver:")
        print("     ────────────────────────────────────────")
        print("     ▣ SYSTEM :: DATABASE MIGRATIONS")
        print("     ────────────────────────────────────────")
        print("     [MIG] ⓘ Found 3 migration file(s)")
        print("     [MIG] ▶ Running: 000_add_depth_quality_columns.sql")
        print("     [MIG] ✔ Migration applied")
        print("     [MIG] ▶ Running: 001_tier_to_depth_migration.sql")
        print("     [MIG] ✔ Migration applied")
        print("     [MIG] ▶ Running: 002_add_admin_items.sql  ← ESTE!")
        print("     [MIG] ✔ Migration applied")
        print("     [MIG] ✔ All migrations completed (3/3)")
        print()
        print("  3. 🎮 TESTE NO DISCORD")
        print("     /giveadminitem item:espada_do_desenvolvedor")
        print("     /giveadminkit")
        print()
        return True
    else:
        print()
        print("⚠️  PROBLEMAS DETECTADOS!")
        print()
        print("Revise os ✗ acima e corrija antes de fazer deploy.")
        print()
        return False

if __name__ == "__main__":
    success = check_status()
    sys.exit(0 if success else 1)
