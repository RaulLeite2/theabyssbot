"""
Sistema de Ranks do The Abyss
Substitui o sistema de Tiers para originalidade legal
Inspirado em animes/mangás com F-Rank até SS-Rank
"""

from enum import Enum
from typing import Tuple

# ===========================
# RANK SYSTEM (Depth → Rank)
# ===========================

RANK_NAMES = {
    1: "F-Rank",
    2: "E-Rank",
    3: "D-Rank",
    4: "C-Rank",
    5: "B-Rank",
    6: "A-Rank",
    7: "S-Rank",
    8: "SS-Rank",
}

RANK_ABBREVIATIONS = {
    1: "F",
    2: "E",
    3: "D",
    4: "C",
    5: "B",
    6: "A",
    7: "S",
    8: "SS",
}

RANK_EMOJIS = {
    1: "🟫",  # F-Rank - Brown
    2: "🟩",  # E-Rank - Green
    3: "🟦",  # D-Rank - Blue
    4: "🟪",  # C-Rank - Purple
    5: "🟥",  # B-Rank - Red
    6: "🟨",  # A-Rank - Yellow
    7: "⭐",  # S-Rank - Star
    8: "💫",  # SS-Rank - Magic
}

# ===========================
# QUALITY SYSTEM (Stars)
# ===========================

QUALITY_NAMES = {
    "COMMON": "Common",
    "UNCOMMON": "Uncommon",
    "RARE": "Rare",
    "EPIC": "Epic",
    "LEGENDARY": "Legendary",
    "MYTHIC": "Mythic",
}

QUALITY_STARS = {
    "COMMON": "☆",
    "UNCOMMON": "★",
    "RARE": "★★",
    "EPIC": "★★★",
    "LEGENDARY": "★★★★",
    "MYTHIC": "★★★★★",
}

QUALITY_EMOJIS = {
    "COMMON": "⬜",
    "UNCOMMON": "🟦",
    "RARE": "🟪",
    "EPIC": "🟥",
    "LEGENDARY": "🟨",
    "MYTHIC": "✨",
}


# ===========================
# CONVERSION FUNCTIONS
# ===========================

def depth_to_rank(depth: int) -> str:
    """Converte depth (1-8) para rank name (F-Rank até SS-Rank)"""
    return RANK_NAMES.get(depth, f"Unknown Rank {depth}")


def depth_to_rank_abbr(depth: int) -> str:
    """Converte depth para abbreviação de rank (F, E, D, C, B, A, S, SS)"""
    return RANK_ABBREVIATIONS.get(depth, "?")


def depth_to_rank_emoji(depth: int) -> str:
    """Retorna emoji do rank"""
    return RANK_EMOJIS.get(depth, "❓")


def quality_to_stars(quality: str) -> str:
    """Converte quality para representação com estrelas"""
    return QUALITY_STARS.get(quality, "☆")


def quality_to_emoji(quality: str) -> str:
    """Retorna emoji da qualidade"""
    return QUALITY_EMOJIS.get(quality, "⬜")


# ===========================
# FORMATTING FUNCTIONS
# ===========================

def format_item_rank(depth: int, quality: str) -> str:
    """
    Formata o rank completo do item em estilo anime
    
    Exemplo: format_item_rank(4, "RARE") -> "C-Rank ★★"
    """
    rank_name = depth_to_rank(depth)
    stars = quality_to_stars(quality)
    return f"{rank_name} {stars}"


def format_item_rank_full(depth: int, quality: str) -> str:
    """
    Formata o rank completo com emoji e nome completo
    
    Exemplo: format_item_rank_full(4, "RARE") -> "🟪 C-Rank ★★ (Rare)"
    """
    rank_name = depth_to_rank(depth)
    rank_abbr = depth_to_rank_abbr(depth)
    stars = quality_to_stars(quality)
    quality_name = QUALITY_NAMES.get(quality, quality)
    rank_emoji = depth_to_rank_emoji(depth)
    
    return f"{rank_emoji} {rank_abbr}-Rank {stars} ({quality_name})"


def format_item_rank_compact(depth: int, quality: str) -> str:
    """
    Formata o rank de forma compacta
    
    Exemplo: format_item_rank_compact(4, "RARE") -> "C-R⭐⭐"
    """
    rank_abbr = depth_to_rank_abbr(depth)
    stars = quality_to_stars(quality)
    quality_abbr = quality[0]  # C, U, R, E, L, M
    
    return f"{rank_abbr}-{quality_abbr} {stars}"


# ===========================
# REVERSE FUNCTIONS (para compatibilidade)
# ===========================

def rank_to_depth(rank_name: str) -> int:
    """Converte rank name de volta para depth"""
    for depth, name in RANK_NAMES.items():
        if name.lower() == rank_name.lower():
            return depth
    return 1  # Padrão: F-Rank


def stars_to_quality(stars: str) -> str:
    """Converte estrelas para quality"""
    for quality, star_rep in QUALITY_STARS.items():
        if star_rep == stars:
            return quality
    return "COMMON"


# ===========================
# HELPER CLASSES
# ===========================

class ItemRank:
    """Classe helper para encapsular informações de rank do item"""
    
    def __init__(self, depth: int, quality: str):
        self.depth = depth
        self.quality = quality
    
    def rank_name(self) -> str:
        return depth_to_rank(self.depth)
    
    def rank_abbr(self) -> str:
        return depth_to_rank_abbr(self.depth)
    
    def quality_name(self) -> str:
        return QUALITY_NAMES.get(self.quality, self.quality)
    
    def stars(self) -> str:
        return quality_to_stars(self.quality)
    
    def rank_emoji(self) -> str:
        return depth_to_rank_emoji(self.depth)
    
    def format(self) -> str:
        """Retorna formatação padrão"""
        return format_item_rank(self.depth, self.quality)
    
    def format_full(self) -> str:
        """Retorna formatação completa"""
        return format_item_rank_full(self.depth, self.quality)
    
    def format_compact(self) -> str:
        """Retorna formatação compacta"""
        return format_item_rank_compact(self.depth, self.quality)
    
    def __str__(self) -> str:
        return self.format()
    
    def __repr__(self) -> str:
        return f"ItemRank({self.depth}, {self.quality})"


# ===========================
# EXPORT
# ===========================

__all__ = [
    # Dicts
    "RANK_NAMES",
    "RANK_ABBREVIATIONS",
    "RANK_EMOJIS",
    "QUALITY_NAMES",
    "QUALITY_STARS",
    "QUALITY_EMOJIS",
    # Conversion functions
    "depth_to_rank",
    "depth_to_rank_abbr",
    "depth_to_rank_emoji",
    "quality_to_stars",
    "quality_to_emoji",
    # Formatting functions
    "format_item_rank",
    "format_item_rank_full",
    "format_item_rank_compact",
    # Reverse functions
    "rank_to_depth",
    "stars_to_quality",
    # Classes
    "ItemRank",
]
