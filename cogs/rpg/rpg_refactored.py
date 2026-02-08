"""
RPG Cog Refatorado - Suporte para Depth System
Mantém compatibilidade com dados antigos (tier)
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.depth_system import DepthTier, Quality, TierMigrator, DepthCalculator

CAPITAL_ZONE_ID = 0


class RPGRefactored(commands.Cog):
    """RPG com suporte a Depth System"""
    rpg = app_commands.Group(name="rpg", description="Comandos do RPG - Depth System")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_item_depth_info(self, item_id: int, tier: str = None) -> DepthTier:
        """Obtém DepthTier de um item (com fallback para dados antigos)"""
        # Tentar buscar depth_new primeiro
        result = await self.bot.db.fetchrow(
            "SELECT depth_new, quality_new, plus_level FROM items WHERE id = $1",
            item_id
        )
        
        if result and result['depth_new'] is not None:
            return DepthTier(
                depth=result['depth_new'],
                quality=Quality(result['quality_new'] or 'common'),
                plus_level=result['plus_level'] or 0
            )
        
        # Fallback: converter tier antigo
        if tier:
            converted = TierMigrator.convert_tier_to_depth(tier)
            if converted:
                return converted
        
        # Default se nada funcionar
        return DepthTier(depth=1, quality=Quality.COMMON)

    @rpg.command(name="start", description="Inicia sua jornada no Abismo com Depth System")
    async def start(self, interaction: discord.Interaction):
        """Inicia novo personagem com itens depth"""
        try:
            if not hasattr(self.bot, 'db'):
                return await interaction.response.send_message(
                    "❌ Database não disponível.",
                    ephemeral=True
                )
            
            # Verificar se usuário existe
            existing = await self.bot.db.fetchval(
                "SELECT 1 FROM users WHERE discord_id = $1",
                interaction.user.id
            )
            if existing:
                return await interaction.response.send_message(
                    "⚠️ Você já iniciou sua jornada no Abismo!",
                    ephemeral=True
                )
            
            # Criar usuário
            await self.bot.db.execute(
                """
                INSERT INTO users (discord_id, level, exp, hp, max_hp)
                VALUES ($1, 1, 0, 100, 100)
                """,
                interaction.user.id
            )
            
            # Buscar itens iniciais por slot (Depth 1, Common)
            slot_ids = [4, 5, 2, 3, 8, 6]  # Main, Torso, Head, Legs, Feet, Off
            starter_items = []
            
            for slot_id in slot_ids:
                item = await self.bot.db.fetchrow(
                    """
                    SELECT id, name, depth_new, quality_new FROM items 
                    WHERE slot_id = $1 AND depth_new = 1 AND quality_new = 'common'
                    ORDER BY id ASC 
                    LIMIT 1
                    """,
                    slot_id
                )
                
                if item:
                    starter_items.append({
                        'id': item['id'],
                        'name': item['name'],
                        'slot_id': slot_id,
                        'depth': item['depth_new'],
                        'quality': item['quality_new']
                    })
            
            if not starter_items:
                return await interaction.response.send_message(
                    "⚠️ Itens iniciais Depth 1 não disponíveis. Contate admin.",
                    ephemeral=True
                )
            
            # Adicionar itens ao inventário e equip
            for item in starter_items:
                # Inventário
                await self.bot.db.execute(
                    """
                    INSERT INTO user_items (user_id, item_id, depth, quality, quantity)
                    VALUES ($1, $2, $3, $4, 1)
                    ON CONFLICT (user_id, item_id) DO UPDATE SET quantity = quantity + 1
                    """,
                    interaction.user.id, item['id'], item['depth'], item['quality']
                )
                
                # Equip
                await self.bot.db.execute(
                    """
                    INSERT INTO equipment (user_id, slot_id, item_id, depth, quality)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id, slot_id) 
                    DO UPDATE SET item_id = $3, depth = $4, quality = $5
                    """,
                    interaction.user.id, item['slot_id'], item['id'],
                    item['depth'], item['quality']
                )
            
            # Embed de boas-vindas
            embed = discord.Embed(
                title="🕳️ Bem-vindo ao Abismo",
                description="*As trevas te abraçam... sua jornada começa agora.*",
                color=0x2C2F33
            )
            
            items_text = "\n".join([
                f"• **{item['name']}** (Profundidade {item['depth']})"
                for item in starter_items
            ])
            
            embed.add_field(
                name="⚔️ Kit Inicial (Depth 1)",
                value=items_text,
                inline=False
            )
            
            embed.add_field(
                name="📊 Status Inicial",
                value="**HP**: 100 | **Level**: 1 | **Exp**: 0",
                inline=False
            )
            
            embed.add_field(
                name="💡 Dicas",
                value=(
                    "• `/rpg profile` - Ver seu perfil\n"
                    "• `/rpg explore` - Explorar o Abismo\n"
                    "• `/wiki` - Enciclopédia de items"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                f"❌ Erro ao iniciar: {str(e)}",
                ephemeral=True
            )

    @rpg.command(name="profile", description="Ver seu perfil de aventureiro")
    async def profile(self, interaction: discord.Interaction):
        """Mostra perfil com stats em Depth"""
        try:
            await interaction.response.defer()
            
            # Buscar dados do usuário
            user = await self.bot.db.fetchrow(
                "SELECT * FROM users WHERE discord_id = $1",
                interaction.user.id
            )
            
            if not user:
                return await interaction.followup.send(
                    "❌ Você não tem um personagem. Use `/rpg start`",
                    ephemeral=True
                )
            
            # Buscar equipamento
            equipment = await self.bot.db.fetch(
                """
                SELECT e.slot_id, i.name, e.depth, e.quality, i.base_damage, i.base_defense
                FROM equipment e
                JOIN items i ON e.item_id = i.id
                WHERE e.user_id = $1
                ORDER BY e.slot_id
                """,
                interaction.user.id
            )
            
            # Calcular stats
            total_damage = 0
            total_defense = 0
            avg_depth = 0
            
            for eq in equipment:
                depth_tier = DepthTier(
                    depth=eq['depth'],
                    quality=Quality(eq['quality'])
                )
                power = depth_tier.power_value()
                total_damage += (eq['base_damage'] or 0) + (power * 0.3)
                total_defense += (eq['base_defense'] or 0) + (power * 0.2)
                avg_depth += eq['depth']
            
            if equipment:
                avg_depth = avg_depth / len(equipment)
            
            # Montar embed
            embed = discord.Embed(
                title=f"⚔️ Perfil de {interaction.user.name}",
                color=0x1f8b4c,
                url="https://discord.gg/theabyss"
            )
            
            embed.add_field(
                name="📊 Stats Principal",
                value=(
                    f"**Nível**: {user['level']}\n"
                    f"**Experiência**: {user['exp']} / {user['level'] * 100}\n"
                    f"**HP**: {user['hp']} / {user['max_hp']}\n"
                    f"**Profundidade Média**: Depth {avg_depth:.1f}"
                ),
                inline=False
            )
            
            embed.add_field(
                name="⚡ Poder de Combate",
                value=(
                    f"**Dano**: +{total_damage:.0f}\n"
                    f"**Defesa**: +{total_defense:.0f}\n"
                    f"**Poder Total**: {(total_damage + total_defense):.0f}"
                ),
                inline=False
            )
            
            # Equipamento atual
            eq_text = ""
            slot_names = {
                2: "👤 Cabeça",
                3: "🦵 Pernas",
                4: "⚔️ Mão Principal",
                5: "🛡️ Torso",
                6: "🗡️ Mão Secundária",
                8: "👢 Pés"
            }
            
            for eq in equipment:
                name = slot_names.get(eq['slot_id'], f"Slot {eq['slot_id']}")
                eq_text += f"{name}: **{eq['name']}** (Depth {eq['depth']})\n"
            
            embed.add_field(
                name="🎖️ Equipamento",
                value=eq_text or "Nenhum item equipado",
                inline=False
            )
            
            embed.set_thumbnail(url=interaction.user.avatar.url)
            embed.set_footer(text="The Abyss RPG • Depth System")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            await interaction.followup.send(
                f"❌ Erro ao carregar perfil: {str(e)}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Carrega o cog refatorado"""
    await bot.add_cog(RPGRefactored(bot))
