import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import discord
from discord import app_commands
from discord.ext import commands

from services.item_resolver import item_resolver

SLOT_NAMES = {
    1: "Amuleto",
    2: "Cabeca",
    3: "Pernas",
    4: "Arma",
    5: "Torso",
    6: "Escudo",
    7: "Capa",
    8: "Pes",
    9: "Anel",
}

DATA_FALLBACK_PATH = Path("data/itens_config.json")


def _safe_title(text: str) -> str:
    return text.replace("_", " ").strip().title()


def _normalize(text: str) -> str:
    return text.replace("_", " ").strip().lower()


def _load_items_cache() -> Optional[Dict[str, Dict[str, Dict[str, Any]]]]:
    if not item_resolver.is_loaded():
        item_resolver.load()

    if item_resolver.is_loaded():
        if item_resolver._items_cache is not None:
            return item_resolver._items_cache

    if DATA_FALLBACK_PATH.exists():
        try:
            return json.loads(DATA_FALLBACK_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None

    return None


def _iter_all_items(items_cache: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Tuple[int, str, Dict[str, Any]]]:
    items: List[Tuple[int, str, Dict[str, Any]]] = []
    for slot_key, slot_items in items_cache.items():
        if not isinstance(slot_items, dict):
            continue
        if not str(slot_key).isdigit():
            continue
        slot_id = int(slot_key)
        for item_id, item_data in slot_items.items():
            if isinstance(item_data, dict):
                items.append((slot_id, item_id, item_data))
    return items


from utils.rank_system import format_item_rank_full, depth_to_rank_emoji, RANK_EMOJIS


def _display_name(item_id: str, item_data: Dict[str, Any]) -> str:
    name = item_data.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return _safe_title(item_id)


def _tier_text(item_data: Dict[str, Any]) -> str:
    """Formata tier usando o novo Rank System (anime-style)"""
    depth = item_data.get("depth_new")
    quality = item_data.get("quality_new")
    
    # Fallback para tier/subtier antigos se não houver depth_new
    if depth is None:
        tier = item_data.get("tier")
        subtier = item_data.get("subtier")
        if tier is None:
            return "Desconhecido"
        if subtier is None:
            return f"T{tier}"
        return f"T{tier}.{subtier}"
    
    # Usar novo rank system
    if quality is None:
        quality = "COMMON"
    
    return format_item_rank_full(depth, quality)


def _rarity_text(item_data: Dict[str, Any]) -> str:
    if "rarity" in item_data and isinstance(item_data["rarity"], str):
        return item_data["rarity"].strip()
    flags = item_data.get("flags", {}) if isinstance(item_data.get("flags"), dict) else {}
    if flags.get("legendary") is True:
        return "Lendario"
    if flags.get("rare") is True:
        return "Raro"
    return "Comum"


def _flags_text(item_data: Dict[str, Any]) -> str:
    flags = item_data.get("flags", {}) if isinstance(item_data.get("flags"), dict) else {}
    if not flags:
        return "Nenhuma"

    pairs = []
    for key, value in flags.items():
        if isinstance(value, bool):
            label = "Sim" if value else "Nao"
        else:
            label = str(value)
        pairs.append(f"{key}: {label}")

    return ", ".join(pairs)


def _buffs_text(item_data: Dict[str, Any]) -> str:
    buffs = item_data.get("buffs")
    if not isinstance(buffs, list) or not buffs:
        return "Nenhuma"

    parts = []
    for buff in buffs:
        if not isinstance(buff, dict):
            continue
        btype = buff.get("type", "buff")
        bvalue = buff.get("value")
        if bvalue is None:
            parts.append(str(btype))
        else:
            parts.append(f"{btype} +{bvalue}")

    return ", ".join(parts) if parts else "Nenhuma"


def _scaling_text(item_data: Dict[str, Any]) -> str:
    scaling = item_data.get("scaling")
    if not isinstance(scaling, dict) or not scaling:
        return "Nenhum"

    parts = []
    for key in ("str", "dex", "int", "vit", "luk"):
        if key in scaling:
            parts.append(f"{key}: {scaling[key]}")

    if not parts:
        parts = [f"{k}: {v}" for k, v in scaling.items()]

    return ", ".join(parts)


def _curiosities_text(item_data: Dict[str, Any]) -> str:
    flags = item_data.get("flags", {}) if isinstance(item_data.get("flags"), dict) else {}
    curiosities = []
    if flags.get("legendary") is True:
        curiosities.append("Forjado por maos lendarias")
    if flags.get("quest_item") is True:
        curiosities.append("Ligado a missao")
    if flags.get("tradeable") is False:
        curiosities.append("Nao negociavel")
    if flags.get("is_collectible") is True:
        curiosities.append("Colecionavel")

    if not curiosities:
        curiosities.append("Sem registros antigos")

    return "; ".join(curiosities)


def _build_item_embed(slot_id: int, item_id: str, item_data: Dict[str, Any], index: int, total: int) -> discord.Embed:
    name = _display_name(item_id, item_data)
    slot_name = SLOT_NAMES.get(slot_id, f"Slot {slot_id}")

    embed = discord.Embed(
        title=f"Wiki: {name}",
        description=f"{slot_name} | Pagina {index}/{total}",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Identificador", value=item_id, inline=False)
    embed.add_field(name="📊 Rank", value=_tier_text(item_data), inline=True)
    embed.add_field(name="Raridade", value=_rarity_text(item_data), inline=True)

    base_damage = item_data.get("base_damage", 0)
    base_defense = item_data.get("base_defense", 0)
    embed.add_field(name="Base", value=f"Dano {base_damage} | Defesa {base_defense}", inline=False)

    embed.add_field(name="Scaling", value=_scaling_text(item_data), inline=False)
    embed.add_field(name="Propriedades", value=_buffs_text(item_data), inline=False)
    embed.add_field(name="Flags", value=_flags_text(item_data), inline=False)
    embed.add_field(name="Curiosidades", value=_curiosities_text(item_data), inline=False)

    return embed


class TomeView(discord.ui.View):
    def __init__(self, owner_id: int, items: List[Tuple[int, str, Dict[str, Any]]], timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.owner_id = owner_id
        self.items = items
        self.index = 0
        self.message: Optional[discord.Message] = None

    def current(self) -> Tuple[int, str, Dict[str, Any]]:
        return self.items[self.index]

    def build_embed(self) -> discord.Embed:
        slot_id, item_id, item_data = self.current()
        return _build_item_embed(slot_id, item_id, item_data, self.index + 1, len(self.items))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Este tomo nao pertence a voce.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.items)
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Proximo", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.items)
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class Wiki(commands.Cog):
    """Enciclopedia interativa de itens."""

    wiki = app_commands.Group(name="wiki", description="Enciclopedia de itens")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @wiki.command(name="buscar", description="Busca itens por nome")
    @app_commands.describe(nome="Nome ou trecho do nome do item")
    async def buscar(self, interaction: discord.Interaction, nome: str):
        items_cache = _load_items_cache()
        if not items_cache:
            return await interaction.response.send_message("Banco de itens indisponivel.", ephemeral=True)

        query = _normalize(nome)
        results = []
        for slot_id, item_id, item_data in _iter_all_items(items_cache):
            display = _display_name(item_id, item_data)
            if query in _normalize(display) or query in _normalize(item_id):
                results.append((slot_id, item_id, item_data))

        if not results:
            return await interaction.response.send_message("Nenhum item encontrado.", ephemeral=True)

        results.sort(key=lambda x: (_display_name(x[1], x[2]).lower(), x[0]))

        view = TomeView(interaction.user.id, results)
        embed = view.build_embed()
        embed.set_footer(text=f"Encontrados {len(results)} itens. Use os botoes para folhear.")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

    @wiki.command(name="item", description="Mostra detalhes completos de um item")
    @app_commands.describe(slot_id="Slot do item", item_id="Identificador interno do item")
    async def item(self, interaction: discord.Interaction, slot_id: int, item_id: str):
        items_cache = _load_items_cache()
        if not items_cache:
            return await interaction.response.send_message("Banco de itens indisponivel.", ephemeral=True)

        slot_items = items_cache.get(str(slot_id), {})
        if item_id not in slot_items:
            return await interaction.response.send_message("Item nao encontrado nesse slot.", ephemeral=True)

        view = TomeView(interaction.user.id, [(slot_id, item_id, slot_items[item_id])])
        embed = view.build_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

    @wiki.command(name="slot", description="Lista itens por slot")
    @app_commands.describe(slot_id="Slot a listar")
    async def slot(self, interaction: discord.Interaction, slot_id: int):
        items_cache = _load_items_cache()
        if not items_cache:
            return await interaction.response.send_message("Banco de itens indisponivel.", ephemeral=True)

        slot_items = items_cache.get(str(slot_id), {})
        if not slot_items:
            return await interaction.response.send_message("Slot vazio ou inexistente.", ephemeral=True)

        slot_name = SLOT_NAMES.get(slot_id, f"Slot {slot_id}")
        item_list = []
        for item_id, item_data in slot_items.items():
            item_list.append(_display_name(item_id, item_data))

        item_list.sort()
        total = len(item_list)
        preview = item_list[:20]
        preview_text = "\n".join(f"- {name}" for name in preview)
        if total > len(preview):
            preview_text += f"\n... e mais {total - len(preview)}"

        embed = discord.Embed(
            title=f"Wiki: {slot_name}",
            description="Lista de itens do slot",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Itens", value=preview_text, inline=False)
        embed.set_footer(text="Use /wiki tomo para folhear os itens desse slot.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @wiki.command(name="tomo", description="Folheia itens como um tomo antigo")
    @app_commands.describe(slot_id="Slot para folhear")
    async def tomo(self, interaction: discord.Interaction, slot_id: int):
        items_cache = _load_items_cache()
        if not items_cache:
            return await interaction.response.send_message("Banco de itens indisponivel.", ephemeral=True)

        slot_items = items_cache.get(str(slot_id), {})
        if not slot_items:
            return await interaction.response.send_message("Slot vazio ou inexistente.", ephemeral=True)

        items = []
        for item_id, item_data in slot_items.items():
            items.append((slot_id, item_id, item_data))

        items.sort(key=lambda x: _display_name(x[1], x[2]).lower())

        view = TomeView(interaction.user.id, items)
        embed = view.build_embed()
        embed.set_footer(text="Folheie com os botoes.")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

    @wiki.command(name="curiosidades", description="Raridades e progressao de tier")
    @app_commands.describe(slot_id="Slot para analisar")
    async def curiosidades(self, interaction: discord.Interaction, slot_id: int):
        items_cache = _load_items_cache()
        if not items_cache:
            return await interaction.response.send_message("Banco de itens indisponivel.", ephemeral=True)

        slot_items = items_cache.get(str(slot_id), {})
        if not slot_items:
            return await interaction.response.send_message("Slot vazio ou inexistente.", ephemeral=True)

        tier_counts: Dict[str, int] = {}
        rarity_counts: Dict[str, int] = {}
        collectible_count = 0
        power_values = []

        for item_id, item_data in slot_items.items():
            tier_label = _tier_text(item_data)
            tier_counts[tier_label] = tier_counts.get(tier_label, 0) + 1

            rarity_label = _rarity_text(item_data)
            rarity_counts[rarity_label] = rarity_counts.get(rarity_label, 0) + 1

            flags = item_data.get("flags", {}) if isinstance(item_data.get("flags"), dict) else {}
            if flags.get("is_collectible") is True:
                collectible_count += 1

            base_damage = item_data.get("base_damage", 0)
            base_defense = item_data.get("base_defense", 0)
            power_values.append(base_damage + base_defense)

        tier_line = ", ".join(f"{k}: {v}" for k, v in sorted(tier_counts.items()))
        rarity_line = ", ".join(f"{k}: {v}" for k, v in sorted(rarity_counts.items()))

        power_min = min(power_values) if power_values else 0
        power_max = max(power_values) if power_values else 0
        power_avg = int(sum(power_values) / len(power_values)) if power_values else 0

        slot_name = SLOT_NAMES.get(slot_id, f"Slot {slot_id}")
        embed = discord.Embed(
            title=f"Wiki: Curiosidades de {slot_name}",
            description="Raridades, tiers e progresso base",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Tiers", value=tier_line or "Sem dados", inline=False)
        embed.add_field(name="Raridades", value=rarity_line or "Sem dados", inline=False)
        embed.add_field(name="Colecionaveis", value=str(collectible_count), inline=True)
        embed.add_field(name="Poder Base", value=f"Min {power_min} | Med {power_avg} | Max {power_max}", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @wiki.command(name="guildas", description="Guia completo sobre o sistema de Guildas")
    async def wiki_guildas(self, interaction: discord.Interaction):
        """Explica o sistema de guildas do jogo"""
        embed = discord.Embed(
            title="📖 Wiki: Sistema de Guildas",
            description="Tudo o que você precisa saber sobre guildas",
            color=discord.Color.gold()
        )
        
        # Criação
        embed.add_field(
            name="⚔️ Criação & Requisitos",
            value="**Comando:** `/guild create <nome>`\n"
                  "• Use esse comando em qualquer zona para criar sua guilda\n"
                  "• Você se torna o líder automaticamente\n"
                  "• O nome deve ser único no servidor\n"
                  "• Custa 50.000 gold para criar",
            inline=False
        )
        
        # Membros
        embed.add_field(
            name="👥 Gerenciamento de Membros",
            value="**Convidar:** `/guild invite @usuario`\n"
                  "**Aceitar:** Clique no botão de aceitar convite\n"
                  "**Remover:** `/guild remove @usuario` (apenas líder)\n"
                  "**Sair:** `/guild leave`\n"
                  "• Máximo **50 membros** por guilda",
            inline=False
        )
        
        # Informações
        embed.add_field(
            name="ℹ️ Informações & Status",
            value="**Ver Info:** `/guild info`\n"
                  "• Mostra nome, líder, membros, nível e gold\n"
                  "• Mostra se tem Sanctuary criado\n"
                  "• Lista todas as alianças que a guilda participa",
            inline=False
        )
        
        # Alianças
        embed.add_field(
            name="🤝 Alianças (Coalizões)",
            value="**Criar:** `/alliance create <nome>` (líder de guilda)\n"
                  "**Convidar:** `/alliance invite <guilda>` (líder de aliança)\n"
                  "**Aceitar:** Como membro de guilda, aceite convite de aliança\n"
                  "• Alianças compartilham Sanctuaries e recursos\n"
                  "• Máximo **5 guildas** por aliança",
            inline=False
        )
        
        # Recursos
        embed.add_field(
            name="💰 Recursos & Economia",
            value="• **Gold:** Ganhado por membros, compartilhado na guilda\n"
                  "• **Exp:** Guilda sobe de nível com atividades\n"
                  "• **Depósito:** `/guild deposit <amount>`\n"
                  "• **Saque:** `/guild withdraw <amount>` (apenas líder)",
            inline=False
        )
        
        # Perks
        embed.add_field(
            name="🎁 Benefícios de Ser Membro",
            value="✅ Compartilhamento de gold com aliados\n"
                  "✅ Acesso a Sanctuaries da guilda/aliança\n"
                  "✅ Bônus de exp em dungeons de guilda\n"
                  "✅ Proteção em PvP zones (com aliados)",
            inline=False
        )
        
        embed.set_footer(text="Use /wiki sanctuaries para aprender sobre Sanctuaries!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @wiki.command(name="sanctuaries", description="Guia completo sobre o sistema de Sanctuaries")
    async def wiki_sanctuaries(self, interaction: discord.Interaction):
        """Explica o sistema de Sanctuaries (bases de guilda)"""
        embed = discord.Embed(
            title="🏰 Wiki: Sistema de Sanctuaries",
            description="Tudo sobre as bases de guilda",
            color=discord.Color.dark_gold()
        )
        
        # O que é
        embed.add_field(
            name="🏠 O que é um Sanctuary?",
            value="Um Sanctuary é uma **base de guilda permanente** instalada em uma zona.\n"
                  "• Cada guilda pode ter até **7 Sanctuaries**\n"
                  "• Sanctuaries de guildas aliadas podem ser acessados\n"
                  "• Permanece mesmo quando ninguém está na zona",
            inline=False
        )
        
        # Criação
        embed.add_field(
            name="⚒️ Criação",
            value="**Comando:** `/sanc create` (apenas líder de guilda)\n"
                  "• Você deve estar na zona desejada\n"
                  "• Cria automaticamente um clone da zona para sua guilda\n"
                  "• Limite: 5 Sanctuaries por zona de Zahuv (especiais)\n"
                  "• Limite: 1 Sanctuary por zona normal",
            inline=False
        )
        
        # Energia & Durabilidade
        embed.add_field(
            name="⚡ Energia & 🛡️ Durabilidade",
            value="**Energia:** Necessária para usar funcionalidades\n"
                  "• Máximo: 100%\n"
                  "• Regenera completamente a cada 1 hora\n"
                  "• Comando: `/sanc recharge` (apenas líder)\n"
                  "\n**Durabilidade:** Barra de resistência do Sanctuary\n"
                  "• Máximo: 100\n"
                  "• Degrada em 10 pontos a cada 30 min SEM energia\n"
                  "• Com 0 durabilidade, o Sanctuary é destruído!",
            inline=False
        )
        
        # Comandos Básicos
        embed.add_field(
            name="📋 Comandos Básicos",
            value="**Info:** `/sanc info` - Ver status do Sanctuary\n"
                  "**Entrar:** `/sanc entrar` - Entra no Sanctuary\n"
                  "**Sair:** `/sanc sair` - Sai do Sanctuary\n"
                  "**List:** `/sanc list` - Lista todos os Sanctuaries\n"
                  "**Zone:** `/sanc zone` - Info sobre zona do Sanctuary",
            inline=False
        )
        
        # Instalações
        embed.add_field(
            name="🏗️ Instalações",
            value="**Estação de Crafting:**\n"
                  "• Custo: 500k gold\n"
                  "• Permite craftar itens especiais com receitas\n"
                  "• Comando: `/sanc craft <recipe_id>`\n"
                  "\n**Portal da Dungeon:**\n"
                  "• Custo: 500k gold\n"
                  "• Requer 5 pessoas com 1500+ de power total\n"
                  "• Recompensa: Gold proporcional ao poder",
            inline=False
        )
        
        # Alianças
        embed.add_field(
            name="🤝 Sanctuaries em Alianças",
            value="• Membros de guildas aliadas podem acessar\n"
                  "• Usa comando `/sanc entrar` em qualquer zona\n"
                  "• Compartilham instalações (crafting/dungeon)\n"
                  "• Fortalecimento mútuo da coalizão",
            inline=False
        )
        
        # Administração
        embed.add_field(
            name="🔧 Administração",
            value="**Upgrade:** `/sanc upgrade` - Aumenta nível (máx 20)\n"
                  "**Delete:** `/sanc delete <sanctuary_id>` - Deleta\n"
                  "**Cleanup:** `/sanc cleanup` - Remove órfãos\n"
                  "**Facility:** `/sanc facility <tipo>` - Adiciona instalação",
            inline=False
        )
        
        # Dicas
        embed.add_field(
            name="💡 Dicas Importantes",
            value="🔴 **Sempre mantenha energia acima de 0%!**\n"
                  "🔴 **Durabilidade baixa = Risco de destruição!**\n"
                  "✅ Sanctuaries juntos em alianças ficam mais fortes\n"
                  "✅ Crafting de itens requer um bom preparo de materiais\n"
                  "✅ Faça dungeons para ganhar recursos para upgrades",
            inline=False
        )
        
        embed.set_footer(text="Use /wiki guildas para aprender sobre o sistema de Guildas!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Wiki(bot))
