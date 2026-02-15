#!/usr/bin/env python3
"""
Script para renomear stats de str/dex/int para might/agility/essence
Fase 4 da Refatoração - Originalidade
"""

import json
import re
from pathlib import Path

def rename_stats_in_json(file_path: Path) -> bool:
    """Renomeia stats em um arquivo JSON"""
    try:
        print(f"\n📝 Processando: {file_path.name}")
        
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Substituir scaling stats
        content = re.sub(r'"str":', '"might":', content)
        content = re.sub(r'"dex":', '"agility":', content)
        content = re.sub(r'"int":', '"essence":', content)
        
        # Substituir buff types
        content = re.sub(r'"str_boost"', '"might_boost"', content)
        content = re.sub(r'"dex_boost"', '"agility_boost"', content)
        content = re.sub(r'"int_boost"', '"essence_boost"', content)
        
        if content == original_content:
            print(f"  ⚪ Nenhuma mudança necessária")
            return True
        
        # Escrever de volta
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def rename_stats_in_python(file_path: Path) -> bool:
    """Renomeia stats em um arquivo Python"""
    try:
        print(f"\n📝 Processando: {file_path.name}")
        
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Substituir em dicionários Python
        # "str": -> "might":
        content = re.sub(r'"str":\s*', '"might": ', content)
        content = re.sub(r'"dex":\s*', '"agility": ', content)
        content = re.sub(r'"int":\s*', '"essence": ', content)
        
        # Substituir buff types
        content = re.sub(r'"str_boost"', '"might_boost"', content)
        content = re.sub(r'"dex_boost"', '"agility_boost"', content)
        content = re.sub(r'"int_boost"', '"essence_boost"', content)
        
        # Substituir comentários de documentação
        content = re.sub(r'\bstr\b/dex/int', 'might/agility/essence', content)
        content = re.sub(r'\{"str":', '{"might":', content)
        content = re.sub(r', "dex":', ', "agility":', content)
        content = re.sub(r', "int":', ', "essence":', content)
        
        if content == original_content:
            print(f"  ⚪ Nenhuma mudança necessária")
            return True
        
        # Escrever de volta
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def main():
    """Main execution"""
    base_path = Path(__file__).parent.parent
    
    print("=" * 60)
    print("🎨 FASE 4: RENOMEANDO STATS")
    print("=" * 60)
    print("\n📋 Mudanças:")
    print("  • str → might")
    print("  • dex → agility")
    print("  • int → essence")
    print("  • int_boost → essence_boost")
    print("  • dex_boost → agility_boost")
    print("  • str_boost → might_boost")
    
    # Lista de arquivos JSON
    json_files = [
        base_path / "data" / "itens_config.json",
        base_path / "data" / "admin_items.json",
    ]
    
    # Lista de arquivos Python
    python_files = [
        base_path / "scripts" / "generate_items_sql.py",
        base_path / "scripts" / "generate_items.py",
        base_path / "scripts" / "generate_admin_items_sql.py",
        base_path / "utils" / "item_integrity.py",
    ]
    
    print("\n" + "=" * 60)
    print("📦 ARQUIVOS JSON")
    print("=" * 60)
    
    success_count = 0
    total_count = len(json_files)
    
    for file_path in json_files:
        if file_path.exists():
            if rename_stats_in_json(file_path):
                success_count += 1
        else:
            print(f"\n⚠️  Arquivo não encontrado: {file_path.name}")
    
    print("\n" + "=" * 60)
    print("🐍 ARQUIVOS PYTHON")
    print("=" * 60)
    
    for file_path in python_files:
        if file_path.exists():
            if rename_stats_in_python(file_path):
                success_count += 1
                total_count += 1
        else:
            print(f"\n⚠️  Arquivo não encontrado: {file_path.name}")
    
    print("\n" + "=" * 60)
    print(f"✅ COMPLETO: {success_count}/{total_count} arquivos atualizados")
    print("=" * 60)
    
    print("\n⚠️  PRÓXIMOS PASSOS:")
    print("  1. Regenerar SQL: python scripts/generate_items_sql.py")
    print("  2. Verificar mudanças: git diff")
    print("  3. Testar sistema de itens")

if __name__ == "__main__":
    main()
