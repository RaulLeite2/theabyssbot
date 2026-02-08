"""
Validadores de Segurança para Depth System
Evita erros comuns de validação
"""

from typing import Tuple, Optional, List
from utils.depth_system import DepthTier, Quality, DEPTH_MIN, DEPTH_MAX
import logging

logger = logging.getLogger(__name__)

# Definições de slots válidos
VALID_SLOTS = {
    1: "Accessory/Ring",
    2: "Head/Helmet",
    3: "Legs",
    4: "Main Hand",
    5: "Torso/Chest",
    6: "Off Hand",
    7: "Reserved",
    8: "Feet",
    9: "Collectible/Resource"
}

MAX_PLUS_LEVEL = 10
MAX_QUANTITY = 99999


class DepthValidator:
    """Validações de segurança para Depth System"""

    @staticmethod
    def validate_depth(depth: int) -> Tuple[bool, Optional[str]]:
        """
        Valida se depth está no range correto
        
        Retorna: (is_valid, error_message)
        """
        if not isinstance(depth, int):
            return False, f"Depth deve ser inteiro, recebido: {type(depth)}"
        
        if depth < DEPTH_MIN or depth > DEPTH_MAX:
            return False, f"Depth fora do range ({DEPTH_MIN}-{DEPTH_MAX}): {depth}"
        
        return True, None

    @staticmethod
    def validate_quality(quality: str) -> Tuple[bool, Optional[str]]:
        """Valida se quality é um valor válido"""
        valid = {q.value for q in Quality}
        
        if quality not in valid:
            return False, f"Quality inválida. Válidas: {valid}, recebido: {quality}"
        
        return True, None

    @staticmethod
    def validate_quality_enum(quality: Quality) -> Tuple[bool, Optional[str]]:
        """Valida se quality é Quality enum"""
        if not isinstance(quality, Quality):
            return False, f"Quality deve ser Quality enum, recebido: {type(quality)}"
        
        return True, None

    @staticmethod
    def validate_plus_level(plus: int) -> Tuple[bool, Optional[str]]:
        """Valida Plus level"""
        if not isinstance(plus, int):
            return False, f"Plus level deve ser inteiro, recebido: {type(plus)}"
        
        if plus < 0 or plus > MAX_PLUS_LEVEL:
            return False, f"Plus level fora do range (0-{MAX_PLUS_LEVEL}): {plus}"
        
        return True, None

    @staticmethod
    def validate_slot_id(slot_id: int) -> Tuple[bool, Optional[str]]:
        """Valida slot_id"""
        if not isinstance(slot_id, int):
            return False, f"Slot_id deve ser inteiro, recebido: {type(slot_id)}"
        
        if slot_id not in VALID_SLOTS:
            valid_list = ", ".join(str(s) for s in VALID_SLOTS.keys())
            return False, f"Slot_id inválido. Válidos: {valid_list}, recebido: {slot_id}"
        
        return True, None

    @staticmethod
    def validate_item_quantity(quantity: int) -> Tuple[bool, Optional[str]]:
        """Valida quantidade de items"""
        if not isinstance(quantity, int):
            return False, f"Quantity deve ser inteiro, recebido: {type(quantity)}"
        
        if quantity <= 0 or quantity > MAX_QUANTITY:
            return False, f"Quantity fora do range (1-{MAX_QUANTITY}): {quantity}"
        
        return True, None

    @staticmethod
    def validate_depth_tier(depth_tier: DepthTier) -> Tuple[bool, Optional[str]]:
        """Valida DepthTier completo"""
        is_valid, error = DepthValidator.validate_depth(depth_tier.depth)
        if not is_valid:
            return False, f"DepthTier.depth: {error}"
        
        is_valid, error = DepthValidator.validate_quality_enum(depth_tier.quality)
        if not is_valid:
            return False, f"DepthTier.quality: {error}"
        
        is_valid, error = DepthValidator.validate_plus_level(depth_tier.plus_level)
        if not is_valid:
            return False, f"DepthTier.plus_level: {error}"
        
        return True, None

    @staticmethod
    def validate_item_data(item_data: dict) -> Tuple[bool, List[str]]:
        """
        Valida dicionário de item completo
        
        Retorna: (is_valid, list_of_errors)
        """
        errors = []

        # Validar depth
        if 'depth' in item_data:
            is_valid, error = DepthValidator.validate_depth(item_data['depth'])
            if not is_valid:
                errors.append(f"depth: {error}")
        
        # Validar quality
        if 'quality' in item_data:
            is_valid, error = DepthValidator.validate_quality(item_data['quality'])
            if not is_valid:
                errors.append(f"quality: {error}")
        
        # Validar slot_id
        if 'slot_id' in item_data:
            is_valid, error = DepthValidator.validate_slot_id(item_data['slot_id'])
            if not is_valid:
                errors.append(f"slot_id: {error}")
        
        # Validar plus_level
        if 'plus_level' in item_data:
            is_valid, error = DepthValidator.validate_plus_level(item_data['plus_level'])
            if not is_valid:
                errors.append(f"plus_level: {error}")
        
        # Validar quantity
        if 'quantity' in item_data:
            is_valid, error = DepthValidator.validate_item_quantity(item_data['quantity'])
            if not is_valid:
                errors.append(f"quantity: {error}")
        
        return len(errors) == 0, errors

    @staticmethod
    async def validate_equipment_equip(
        user_id: int,
        item_id: int,
        slot_id: int,
        db
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida antes de equipar um item
        
        Checks:
        - Slot válido
        - Item existe
        - Item pertence ao usuário
        - Tipo de item combina com slot
        """
        
        # 1. Validar slot
        is_valid, error = DepthValidator.validate_slot_id(slot_id)
        if not is_valid:
            return False, error
        
        # 2. Item existe?
        item = await db.fetchrow("SELECT * FROM items WHERE id = $1", item_id)
        if not item:
            return False, f"Item {item_id} não existe"
        
        # 3. Usuário tem o item?
        user_item = await db.fetchrow(
            "SELECT quantity FROM user_items WHERE user_id = $1 AND item_id = $2",
            user_id, item_id
        )
        if not user_item or user_item['quantity'] < 1:
            return False, f"Você não tem o item {item_id}"
        
        # 4. Item combina com slot?
        if item['slot_id'] != slot_id:
            slot_name = VALID_SLOTS.get(item['slot_id'], f"Slot {item['slot_id']}")
            return False, f"Item vai em {slot_name}, não em Slot {slot_id}"
        
        # 5. Depth / Quality validação runtime
        is_valid, errors = DepthValidator.validate_item_data({
            'depth': item['depth_new'],
            'quality': item['quality_new'],
            'plus_level': item.get('plus_level', 0)
        })
        if not is_valid:
            return False, f"Item inválido: {'; '.join(errors)}"
        
        return True, None


class SafeEquipmentManager:
    """Helper para gerenciar equipment com safety checks"""
    
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def equip_item_safe(
        self,
        user_id: int,
        item_id: int,
        slot_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Equipa item com validações completas
        """
        # 1. Validar dados
        is_valid, error = await DepthValidator.validate_equipment_equip(
            user_id, item_id, slot_id, self.db
        )
        
        if not is_valid:
            self.logger.warning(f"❌ Equip rejection: {error}")
            return False, error
        
        # 2. Executar equip em transação
        try:
            async with self.db.pool.acquire() as conn:
                async with conn.transaction():
                    # Get current item in slot (para log)
                    current = await conn.fetchrow(
                        "SELECT item_id FROM equipment WHERE user_id = $1 AND slot_id = $2",
                        user_id, slot_id
                    )
                    
                    # Equip novo
                    await conn.execute(
                        """
                        INSERT INTO equipment (user_id, slot_id, item_id, depth, quality)
                        SELECT $1, $2, id, depth_new, quality_new FROM items WHERE id = $3
                        ON CONFLICT (user_id, slot_id) 
                        DO UPDATE SET item_id = $3
                        """,
                        user_id, slot_id, item_id
                    )
            
            self.logger.info(f"✅ User {user_id} equipped item {item_id} to slot {slot_id}")
            return True, None
            
        except Exception as e:
            self.logger.error(f"❌ Equipment error: {e}", exc_info=True)
            return False, f"Erro ao equipar: {str(e)}"
