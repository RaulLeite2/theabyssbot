"""
🔐 Script para Criptografar Configuração de Itens
===================================================
Lê o arquivo data/itens_config.json e gera data/Itens.enc criptografado.

Usage:
    python scripts/encrypt_items.py
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.item_integrity import ItemIntegrityManager


def main():
    """Criptografa o arquivo de configuração de itens"""
    
    # Caminhos
    json_path = Path("data/itens_config.json")
    enc_path = Path("data/Itens.enc")
    
    print("🔐 Iniciando criptografia de itens...")
    print(f"📂 Origem: {json_path}")
    print(f"📂 Destino: {enc_path}")
    print()
    
    # Verifica se arquivo JSON existe
    if not json_path.exists():
        print(f"❌ Arquivo não encontrado: {json_path}")
        print("💡 Crie o arquivo data/itens_config.json primeiro")
        return 1
    
    # Lê JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            items_dict = json.load(f)
        print(f"✅ JSON carregado com sucesso")
        print(f"📊 Total de slots: {len(items_dict)}")
        
        # Conta itens por slot
        total_items = sum(len(items) for items in items_dict.values())
        print(f"📦 Total de itens: {total_items}")
        print()
        
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1
    
    # Criptografa
    manager = ItemIntegrityManager(file_path=str(enc_path))
    
    if manager.encrypt_items(items_dict):
        print()
        print("✅ Arquivo criptografado com sucesso!")
        print(f"📍 Localização: {enc_path.absolute()}")
        print(f"📏 Tamanho: {enc_path.stat().st_size} bytes")
        print()
        print("🔒 IMPORTANTE:")
        print("   - Não compartilhe o arquivo Itens.enc publicamente")
        print("   - Faça backup da chave de criptografia")
        print("   - Adicione Itens.enc ao .gitignore se necessário")
        return 0
    else:
        print()
        print("❌ Falha ao criptografar arquivo")
        print("💡 Verifique os logs para mais detalhes")
        return 1


if __name__ == "__main__":
    exit(main())
