#!/usr/bin/env python3
"""
Teste de sintaxe SQL: Valida se o 002_add_admin_items.sql está correto
Uso: python scripts/test_admin_items_sql.py
"""

from pathlib import Path
import re

def test_sql_syntax():
    """Testa a sintaxe básica do SQL de admin items"""
    
    sql_file = Path("db/migrations/002_add_admin_items.sql")
    
    print("=" * 60)
    print("🧪 TESTE: Sintaxe SQL - Admin Items")
    print("=" * 60)
    print()
    
    if not sql_file.exists():
        print("❌ ERRO: Arquivo não encontrado!")
        return False
    
    content = sql_file.read_text(encoding="utf-8")
    
    print(f"📄 Arquivo: {sql_file.name}")
    print(f"📏 Tamanho: {len(content)} caracteres")
    print(f"📝 Linhas: {content.count(chr(10))} linhas")
    print()
    
    # Verificações básicas
    checks = {
        "Tem DO $$ BEGIN": "DO $$" in content and "BEGIN" in content,
        "Tem END $$": "END $$;" in content,
        "Tem INSERT INTO items": "INSERT INTO items" in content,
        "Referencia quality_new": "quality_new" in content,
        "Referencia depth_new": "depth_new" in content,
        "Tem espada_do_desenvolvedor": "espada_do_desenvolvedor" in content,
        "Tem armadura_do_admin": "armadura_do_admin" in content,
    }
    
    print("🔍 Verificações:")
    all_ok = True
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_ok = False
    print()
    
    # Contar INSERTs
    insert_count = content.count("INSERT INTO items")
    print(f"📊 Total de INSERTs encontrados: {insert_count}")
    
    if insert_count != 12:
        print(f"   ⚠ ESPERADO: 12 INSERTs (1 por item)")
        print(f"   ⚠ ENCONTRADO: {insert_count}")
    else:
        print(f"   ✓ Correto! 12 itens serão inseridos")
    print()
    
    # Extrair nomes de itens
    print("📋 Itens que serão inseridos:")
    items = re.findall(r"'([a-z_]+)',\s*\n\s*\d+,\s*--\s*(weapon|chest|head|legs|feet|amulet|ring|shield|consumable)", content)
    
    for i, (item_name, slot) in enumerate(items, 1):
        display_name = item_name.replace('_', ' ').title()
        print(f"  {i:2d}. {display_name:30s} ({slot})")
    
    print()
    
    # Verificar parênteses balanceados (básico)
    open_parens = content.count("(")
    close_parens = content.count(")")
    
    if open_parens != close_parens:
        print(f"⚠ ALERTA: Parênteses desbalanceados!")
        print(f"   Abertos: {open_parens}, Fechados: {close_parens}")
    else:
        print(f"✓ Parênteses balanceados ({open_parens}/{close_parens})")
    
    print()
    print("=" * 60)
    
    if all_ok and insert_count == 12:
        print("✅ SQL PARECE CORRETO!")
        print()
        print("Se não está executando, verifique:")
        print("  1. Bot foi reiniciado? (migrations rodam no startup)")
        print("  2. Logs do bot mostram as migrations?")
        print("  3. Database tem as colunas depth_new/quality_new?")
        return True
    else:
        print("❌ PROBLEMAS DETECTADOS NO SQL!")
        return False

if __name__ == "__main__":
    success = test_sql_syntax()
    exit(0 if success else 1)
