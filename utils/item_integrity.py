"""
🔐 Sistema de Integridade de Itens
====================================
Módulo responsável por criptografia e validação do arquivo de configuração de itens.

Filosofia:
- Descriptografia silenciosa (fail-safe)
- Validação de schema JSON
- Nenhuma exposição de erros ao usuário
- Cache em memória após carregamento
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet, InvalidToken
import os

logger = logging.getLogger(__name__)

# Chave de criptografia (deve estar em variável de ambiente em produção)
# Para desenvolvimento, usa uma chave fixa (gerada com Fernet.generate_key())
# Em produção, defina ITEMS_ENCRYPTION_KEY nas variáveis de ambiente
DEFAULT_ENCRYPTION_KEY = b'Yhx0ZsIjHST3_nnWFWjLbdAx_Ou1yHXoCOELVHDx_PM='

def get_encryption_key() -> bytes:
    """Obtém chave de criptografia da env var ou usa a chave padrão"""
    env_key = os.getenv("ITEMS_ENCRYPTION_KEY")
    if env_key:
        # Tenta usar a chave da env var
        try:
            key_bytes = env_key.encode() if isinstance(env_key, str) else env_key
            # Valida se é uma chave Fernet válida
            Fernet(key_bytes)
            return key_bytes
        except Exception as e:
            logger.warning(f"Chave de env var inválida, usando chave padrão: {e}")
            return DEFAULT_ENCRYPTION_KEY
    
    # Retorna chave padrão para desenvolvimento
    return DEFAULT_ENCRYPTION_KEY


class ItemIntegrityManager:
    """Gerenciador de integridade do arquivo de configuração de itens"""
    
    def __init__(self, file_path: str = "data/Itens.enc"):
        self.file_path = Path(file_path)
        
        # Usa chave consistente (nunca gera aleatória)
        key = get_encryption_key()
        self.fernet = Fernet(key)
        
        self._cache: Optional[Dict[str, Any]] = None
        
    def encrypt_items(self, items_dict: Dict[str, Any]) -> bool:
        """
        Criptografa dicionário de itens e salva no arquivo.
        
        Args:
            items_dict: Dicionário com configuração de itens
            
        Returns:
            True se sucesso, False se falhar
        """
        try:
            # Valida schema antes de criptografar
            if not self._validate_schema(items_dict):
                logger.error("Schema inválido ao tentar criptografar itens")
                return False
            
            # Serializa para JSON
            json_data = json.dumps(items_dict, indent=2, ensure_ascii=False)
            
            # Criptografa
            encrypted_data = self.fernet.encrypt(json_data.encode('utf-8'))
            
            # Salva no arquivo
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_bytes(encrypted_data)
            
            # Atualiza cache
            self._cache = items_dict
            
            logger.info(f"✅ Arquivo de itens criptografado: {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criptografar itens: {e}")
            return False
    
    def decrypt_items(self) -> Optional[Dict[str, Any]]:
        """
        Descriptografa arquivo de itens.
        
        Returns:
            Dicionário com configuração ou None se falhar (fail-safe silencioso)
        """
        # Se já carregou em cache, retorna
        if self._cache is not None:
            return self._cache
        
        try:
            # Verifica se arquivo existe
            if not self.file_path.exists():
                logger.warning(f"⚠️ Arquivo de itens não encontrado: {self.file_path}")
                return None
            
            # Lê dados criptografados
            encrypted_data = self.file_path.read_bytes()
            
            # Descriptografa
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Parse JSON
            items_dict = json.loads(decrypted_data.decode('utf-8'))
            
            # Valida schema
            if not self._validate_schema(items_dict):
                logger.error("❌ Schema inválido no arquivo descriptografado")
                return None
            
            # Salva em cache
            self._cache = items_dict
            
            logger.info(f"✅ Arquivo de itens descriptografado com sucesso")
            return items_dict
            
        except InvalidToken:
            logger.error("❌ Token de criptografia inválido (arquivo corrompido ou chave errada)")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON inválido no arquivo descriptografado: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao descriptografar itens: {e}")
            return None
    
    def _validate_schema(self, items_dict: Dict[str, Any]) -> bool:
        """
        Valida estrutura do dicionário de itens.
        
        Schema esperado:
        {
            "slot_id": {
                "item_identifier": {
                    "base_damage": int,
                    "base_defense": int,
                    "scaling": {"str": float, "dex": float, ...},
                    "buffs": [{"type": str, "value": float}],
                    "flags": {"legendary": bool, "tradeable": bool, ...}
                }
            }
        }
        """
        try:
            if not isinstance(items_dict, dict):
                return False
            
            for slot_id, slot_items in items_dict.items():
                # Slot ID deve ser string numérica (1-9)
                if not slot_id.isdigit():
                    logger.error(f"Slot ID inválido: {slot_id}")
                    return False
                
                if not isinstance(slot_items, dict):
                    logger.error(f"Slot {slot_id} não é dicionário")
                    return False
                
                for item_id, item_config in slot_items.items():
                    # Cada item deve ter configuração
                    if not isinstance(item_config, dict):
                        logger.error(f"Configuração inválida para {item_id}")
                        return False
                    
                    # Campos obrigatórios
                    required_fields = ["base_damage", "base_defense"]
                    for field in required_fields:
                        if field not in item_config:
                            logger.error(f"Campo {field} ausente em {item_id}")
                            return False
                        if not isinstance(item_config[field], (int, float)):
                            logger.error(f"Campo {field} não é numérico em {item_id}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de schema: {e}")
            return False
    
    def clear_cache(self):
        """Limpa cache em memória (útil para recarregar após mudanças)"""
        self._cache = None
        logger.info("🗑️ Cache de itens limpo")
    
    def get_item_config(self, slot_id: int, item_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Busca configuração de um item específico.
        
        Args:
            slot_id: ID do slot (1-9)
            item_identifier: Identificador interno do item
            
        Returns:
            Dicionário com configuração ou None se não encontrado
        """
        items = self.decrypt_items()
        
        if items is None:
            return None
        
        slot_key = str(slot_id)
        if slot_key not in items:
            logger.warning(f"⚠️ Slot {slot_id} não encontrado em Itens.enc")
            return None
        
        if item_identifier not in items[slot_key]:
            logger.warning(f"⚠️ Item '{item_identifier}' não encontrado no slot {slot_id}")
            return None
        
        return items[slot_key][item_identifier]


# Instância global (singleton)
item_integrity = ItemIntegrityManager()


def get_item_config(slot_id: int, item_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Função helper para buscar configuração de item.
    
    Usage:
        config = get_item_config(slot_id=2, item_identifier="item_027")
        if config:
            damage = config["base_damage"]
            defense = config["base_defense"]
    """
    return item_integrity.get_item_config(slot_id, item_identifier)
