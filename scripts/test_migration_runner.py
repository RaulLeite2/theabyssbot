#!/usr/bin/env python3
"""
Teste rápido: Simula o migration runner localmente
Uso: python scripts/test_migration_runner.py
"""

from pathlib import Path

def test_migration_discovery():
    """Testa se as migrations serão encontradas"""
    
    migrations_dir = Path("db/migrations")
    
    print("=" * 60)
    print("🧪 TESTE: Migration Discovery")
    print("=" * 60)
    print()
    
    # Simular o que o migration_runner faz
    print("📂 Pasta de migrations:", migrations_dir)
    print()
    
    if not migrations_dir.exists():
        print("❌ ERRO: Pasta db/migrations não existe!")
        return False
    
    # Buscar todos .sql
    all_files = list(migrations_dir.glob("*.sql"))
    print(f"📄 Arquivos .sql encontrados: {len(all_files)}")
    for f in sorted(all_files):
        print(f"   • {f.name}")
    print()
    
    # Filtrar (como o migration_runner faz)
    migration_files = [
        f for f in all_files 
        if not f.name.endswith("_rollback.sql") 
        and not f.name.startswith("README")
    ]
    
    print(f"✅ Migrations a serem executadas: {len(migration_files)}")
    for f in sorted(migration_files):
        print(f"   {f.name}")
        
        # Verificar se o arquivo pode ser lido
        try:
            content = f.read_text(encoding="utf-8")
            lines = content.count('\n')
            print(f"      ✓ Legível ({lines} linhas)")
            
            # Verificar se tem admin items
            if 'admin' in f.name.lower():
                if 'espada_do_desenvolvedor' in content:
                    print(f"      ✓ Contém items de admin")
                else:
                    print(f"      ⚠ NÃO contém items de admin!")
        except Exception as e:
            print(f"      ❌ ERRO ao ler: {e}")
    
    print()
    print("=" * 60)
    
    if len(migration_files) >= 3:
        print("✅ TUDO OK! Migrations serão executadas.")
        print()
        print("Ordem de execução:")
        for i, f in enumerate(sorted(migration_files), 1):
            print(f"  {i}. {f.name}")
        return True
    else:
        print("⚠ ALERTA: Esperado pelo menos 3 migrations!")
        return False

if __name__ == "__main__":
    success = test_migration_discovery()
    exit(0 if success else 1)
