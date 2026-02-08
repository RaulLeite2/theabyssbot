"""
🎯 Sistema de Resolução de Itens
==================================
Serviço que resolve atributos de itens a partir do arquivo criptografado.

Filosofia:
- Carrega Itens.enc na inicialização do bot
- Cache em memória para performance
- Fail-safe silencioso (retorna None se item não existe)
- Desacoplamento total: comandos não definem poder
"""

import logging
from typing import Optional, Dict, Any
from utils.item_integrity import item_integrity

logger = logging.getLogger(__name__)


class ItemResolverService:
    """Serviço de resolução de atributos de itens"""
    
    def __init__(self):
        self._loaded = False
        self._items_cache: Optional[Dict[str, Any]] = None
        
    def load(self) -> bool:
        """
        Carrega arquivo de itens criptografado na inicialização.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        logger.info("🔄 Carregando configuração de itens...")
        
        self._items_cache = item_integrity.decrypt_items()
        
        if self._items_cache is None:
            logger.error("❌ Falha ao carregar arquivo de itens")
            self._loaded = False
            return False
        
        # Estatísticas
        total_slots = len(self._items_cache)
        total_items = sum(len(items) for items in self._items_cache.values())
        
        logger.info(f"✅ Itens carregados: {total_slots} slots, {total_items} itens")
        self._loaded = True
        return True
    
    def is_loaded(self) -> bool:
        """Verifica se o sistema está carregado"""
        return self._loaded
    
    def reload(self) -> bool:
        """
        Recarrega o arquivo de itens (útil após atualização).
        
        Returns:
            True se recarregado com sucesso
        """
        item_integrity.clear_cache()
        return self.load()
    
    def resolve_item(self, slot_id: int, item_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Resolve atributos de um item específico.
        
        Args:
            slot_id: ID do slot (1-9)
            item_identifier: Identificador interno do item (ex: "espada_iniciante")
            
        Returns:
            Dict com atributos ou None se não encontrado
            
        Example:
            >>> attrs = resolver.resolve_item(4, "lamina_abissal")
            >>> if attrs:
            ...     damage = attrs["base_damage"]
            ...     buffs = attrs.get("buffs", [])
        """
        if not self._loaded:
            logger.warning("⚠️ Sistema de itens não carregado, tentando carregar...")
            if not self.load():
                return None
        
        if self._items_cache is None:
            return None
        
        slot_key = str(slot_id)
        
        if slot_key not in self._items_cache:
            logger.debug(f"Slot {slot_id} não existe em Itens.enc")
            return None
        
        if item_identifier not in self._items_cache[slot_key]:
            logger.debug(f"Item '{item_identifier}' não encontrado no slot {slot_id}")
            return None
        
        return self._items_cache[slot_key][item_identifier].copy()
    
    def get_all_items_in_slot(self, slot_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Retorna todos os itens de um slot específico.
        
        Args:
            slot_id: ID do slot (1-9)
            
        Returns:
            Dict com todos os itens do slot ou dict vazio
        """
        if not self._loaded or self._items_cache is None:
            return {}
        
        slot_key = str(slot_id)
        return self._items_cache.get(slot_key, {}).copy()
    
    def list_item_identifiers(self, slot_id: int) -> list:
        """
        Lista todos os identificadores de itens em um slot.
        
        Args:
            slot_id: ID do slot (1-9)
            
        Returns:
            Lista de identificadores
            
        Example:
            >>> identifiers = resolver.list_item_identifiers(4)
            >>> # ["espada_iniciante", "lamina_abissal"]
        """
        items = self.get_all_items_in_slot(slot_id)
        return list(items.keys())
    
    def validate_item_exists(self, slot_id: int, item_identifier: str) -> bool:
        """
        Valida se um item existe no sistema.
        
        Args:
            slot_id: ID do slot (1-9)
            item_identifier: Identificador interno
            
        Returns:
            True se existe, False caso contrário
        """
        return self.resolve_item(slot_id, item_identifier) is not None
    
    def get_item_power(self, slot_id: int, item_identifier: str) -> tuple[int, int]:
        """
        Retorna poder base de um item (damage, defense).
        
        Args:
            slot_id: ID do slot
            item_identifier: Identificador interno
            
        Returns:
            Tuple (base_damage, base_defense) ou (0, 0) se não encontrado
        """
        attrs = self.resolve_item(slot_id, item_identifier)
        
        if attrs is None:
            return (0, 0)
        
        return (attrs.get("base_damage", 0), attrs.get("base_defense", 0))


# Instância global (singleton)
item_resolver = ItemResolverService()


def resolve_item_attributes(slot_id: int, item_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Função helper para resolver atributos de item.
    
    Usage:
        from services.item_resolver import resolve_item_attributes
        
        attrs = resolve_item_attributes(slot_id=4, item_identifier="lamina_abissal")
        if attrs:
            damage = attrs["base_damage"]
            defense = attrs["base_defense"]
            buffs = attrs.get("buffs", [])
    """
    return item_resolver.resolve_item(slot_id, item_identifier)
