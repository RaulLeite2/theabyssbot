"""
Sistema de Profundidade (Depth System) - Substitui Tier System do Abyss
Implementação: Depth 1-8 + Qualidade (Common/Rare/Epic/Legendary/Mythic)
Segurança Legal: Nomenclatura única, não-Albion, derivado de profundidade oceânica

Mapping Backwards Compatibility:
  T1.0-T1.4 → Depth 1 (Common)
  T2.0-T2.4 → Depth 2 (Common) 
  T3.0-T3.4 → Depth 2-3 (Rare)
  T4.0-T4.4 → Depth 3-4 (Rare)
  T5.0-T5.4 → Depth 4-5 (Epic)
  T6.0-T6.4 → Depth 5-6 (Epic)
  T7.0-T7.4 → Depth 6-7 (Legendary)
  T8.0-T8.4 → Depth 7-8 (Legendary/Mythic)
"""

from enum import Enum
from typing import Dict, Tuple, Optional
import math


class Quality(Enum):
    """Qualidade do item - substituir rarity anterior"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

    def multiplier(self) -> float:
        """Multiplicador de poder baseado em qualidade"""
        return {
            Quality.COMMON: 1.0,
            Quality.UNCOMMON: 1.15,
            Quality.RARE: 1.3,
            Quality.EPIC: 1.6,
            Quality.LEGENDARY: 2.0,
            Quality.MYTHIC: 2.5,
        }[self]

    def color_hex(self) -> str:
        """Cor Discord hex para exibição"""
        return {
            Quality.COMMON: "0xA9A9A9",      # Cinza
            Quality.UNCOMMON: "0x1EFF00",    # Verde
            Quality.RARE: "0x0070DD",        # Azul
            Quality.EPIC: "0xA335EE",        # Roxo
            Quality.LEGENDARY: "0xFF8000",   # Laranja
            Quality.MYTHIC: "0xFFD700",      # Ouro
        }[self]


class DepthTier:
    """
    Representa um item em Profundidade + Qualidade
    Substitui completamente o sistema Tier T1.0-T8.4
    """

    def __init__(self, depth: int, quality: Quality, plus_level: int = 0):
        """
        Args:
            depth: 1-8 (profundidade do abismo)
            quality: Enum Quality
            plus_level: +0 a +10 (enhance level como bonus)
        """
        if not 1 <= depth <= 8:
            raise ValueError(f"Depth deve ser 1-8, recebido: {depth}")
        if not 0 <= plus_level <= 10:
            raise ValueError(f"Plus level deve ser 0-10, recebido: {plus_level}")

        self.depth = depth
        self.quality = quality
        self.plus_level = plus_level

    def power_value(self) -> float:
        """
        Calcula valor de poder do item
        Fórmula: (depth * 15) * quality_multiplier + (plus_level * 5)
        """
        base = self.depth * 15
        with_quality = base * self.quality.multiplier()
        with_plus = with_quality + (self.plus_level * 5)
        return round(with_plus, 2)

    def display_name(self) -> str:
        """Exibição formatada: Depth X [Quality] +Y"""
        base = f"Depth {self.depth} [{self.quality.value.upper()}]"
        if self.plus_level > 0:
            return f"{base} +{self.plus_level}"
        return base

    def __str__(self) -> str:
        return self.display_name()

    def __repr__(self) -> str:
        return f"DepthTier(depth={self.depth}, quality={self.quality.name}, plus={self.plus_level})"


class TierMigrator:
    """Converte itens do sistema Tier antigo para Depth novo"""

    # Mapa de conversão Tier → (Depth, Quality)
    TIER_TO_DEPTH_MAP: Dict[str, Tuple[int, Quality]] = {
        # Tier 1
        "T1.0": (1, Quality.COMMON),
        "T1.1": (1, Quality.COMMON),
        "T1.2": (1, Quality.UNCOMMON),
        "T1.3": (1, Quality.UNCOMMON),
        "T1.4": (1, Quality.RARE),

        # Tier 2
        "T2.0": (2, Quality.COMMON),
        "T2.1": (2, Quality.COMMON),
        "T2.2": (2, Quality.UNCOMMON),
        "T2.3": (2, Quality.UNCOMMON),
        "T2.4": (2, Quality.RARE),

        # Tier 3
        "T3.0": (2, Quality.RARE),
        "T3.1": (3, Quality.RARE),
        "T3.2": (3, Quality.RARE),
        "T3.3": (3, Quality.EPIC),
        "T3.4": (3, Quality.EPIC),

        # Tier 4
        "T4.0": (3, Quality.EPIC),
        "T4.1": (4, Quality.EPIC),
        "T4.2": (4, Quality.EPIC),
        "T4.3": (4, Quality.LEGENDARY),
        "T4.4": (4, Quality.LEGENDARY),

        # Tier 5
        "T5.0": (4, Quality.LEGENDARY),
        "T5.1": (5, Quality.EPIC),
        "T5.2": (5, Quality.EPIC),
        "T5.3": (5, Quality.LEGENDARY),
        "T5.4": (5, Quality.LEGENDARY),

        # Tier 6
        "T6.0": (5, Quality.LEGENDARY),
        "T6.1": (6, Quality.LEGENDARY),
        "T6.2": (6, Quality.LEGENDARY),
        "T6.3": (6, Quality.MYTHIC),
        "T6.4": (6, Quality.MYTHIC),

        # Tier 7
        "T7.0": (6, Quality.LEGENDARY),
        "T7.1": (7, Quality.LEGENDARY),
        "T7.2": (7, Quality.LEGENDARY),
        "T7.3": (7, Quality.MYTHIC),
        "T7.4": (7, Quality.MYTHIC),

        # Tier 8
        "T8.0": (7, Quality.MYTHIC),
        "T8.1": (8, Quality.LEGENDARY),
        "T8.2": (8, Quality.LEGENDARY),
        "T8.3": (8, Quality.MYTHIC),
        "T8.4": (8, Quality.MYTHIC),
    }

    @staticmethod
    def convert_tier_to_depth(tier_str: str) -> Optional[DepthTier]:
        """
        Converte string Tier antigo para DepthTier
        Exemplos:
          "T4.2" → DepthTier(depth=4, quality=EPIC)
          "invalid" → None
        """
        if tier_str not in TierMigrator.TIER_TO_DEPTH_MAP:
            return None

        depth, quality = TierMigrator.TIER_TO_DEPTH_MAP[tier_str]
        return DepthTier(depth=depth, quality=quality)

    @staticmethod
    def bulk_convert(tier_list: list) -> list:
        """Converte lista de tiers antigos para profundidades novas"""
        results = []
        for tier in tier_list:
            converted = TierMigrator.convert_tier_to_depth(tier)
            if converted:
                results.append(converted)
        return results


class DepthCalculator:
    """Utilitários para cálculos com sistems Depth"""

    @staticmethod
    def tier_gap_difficulty(attacker_depth: int, defender_depth: int) -> float:
        """
        Calcula modificador de dano baseado na diferença de profundidade
        Fórmula: 1 + (gap * 0.08)
        """
        gap = abs(attacker_depth - defender_depth)
        return 1 + (gap * 0.08)

    @staticmethod
    def required_depth_for_boss(boss_level: int) -> int:
        """Profundidade mínima recomendada para enfrentar boss"""
        return math.ceil(boss_level / 2)

    @staticmethod
    def quality_affinity_bonus(item_quality: Quality, zone_affinity: str) -> float:
        """
        Bônus de qualidade em zona com afinidade
        Tipos: celestial, abyssal, neutral
        """
        bonuses = {
            (Quality.COMMON, "neutral"): 1.0,
            (Quality.COMMON, "celestial"): 0.9,
            (Quality.COMMON, "abyssal"): 1.1,
            (Quality.UNCOMMON, "neutral"): 1.0,
            (Quality.UNCOMMON, "celestial"): 1.1,
            (Quality.UNCOMMON, "abyssal"): 0.9,
            (Quality.RARE, "neutral"): 1.0,
            (Quality.RARE, "celestial"): 1.15,
            (Quality.RARE, "abyssal"): 0.85,
            (Quality.EPIC, "neutral"): 1.0,
            (Quality.EPIC, "celestial"): 1.2,
            (Quality.EPIC, "abyssal"): 0.8,
            (Quality.LEGENDARY, "neutral"): 1.0,
            (Quality.LEGENDARY, "celestial"): 1.25,
            (Quality.LEGENDARY, "abyssal"): 0.75,
            (Quality.MYTHIC, "neutral"): 1.0,
            (Quality.MYTHIC, "celestial"): 1.3,
            (Quality.MYTHIC, "abyssal"): 0.7,
        }
        return bonuses.get((item_quality, zone_affinity), 1.0)


# Constantes para fácil importação
DEPTH_MIN = 1
DEPTH_MAX = 8
QUALITIES = list(Quality)
