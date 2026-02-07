import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Profile(commands.Cog):
    """Sistema de perfil de jogador com estatísticas de fama"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def format_number(self, num: int) -> str:
        """Formata números grandes (1000000 -> 1M)"""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)
    
    async def get_fame_title(self, fame_type: str, fame_amount: int) -> str:
        """Busca o título baseado na fama"""
        title = await self.bot.db.fetchrow(
            """
            SELECT title_name, icon
            FROM fame_titles
            WHERE fame_type = $1 AND required_fame <= $2
            ORDER BY required_fame DESC
            LIMIT 1
            """,
            fame_type, fame_amount
        )
        
        if title:
            return f"{title['icon']} {title['title_name']}"
        return "🔰 Novato"
    
    @app_commands.command(name="profile", description="📊 Ver perfil completo de um jogador")
    @app_commands.describe(player="Jogador para ver o perfil (deixe vazio para ver o seu)")
    async def profile(self, interaction: discord.Interaction, player: discord.User = None):
        """Mostra o perfil completo do jogador com fama separada por categorias"""
        await interaction.response.defer()
        
        target = player or interaction.user
        
        # Busca dados do usuário
        user_data = await self.bot.db.fetchrow(
            """
            SELECT discord_id, level, base_hp, current_hp, zona_id,
                   COALESCE(fame_arena, 0) as fame_arena,
                   COALESCE(fame_combat, 0) as fame_combat,
                   COALESCE(fame_crafting, 0) as fame_crafting,
                   COALESCE(fame_exploration, 0) as fame_exploration,
                   COALESCE(fame_trading, 0) as fame_trading
            FROM users
            WHERE discord_id = $1
            """,
            target.id
        )
        
        if not user_data:
            return await interaction.followup.send(
                f"❌ {target.mention} ainda não começou sua jornada no Abismo!",
                ephemeral=True
            )
        
        # Busca economia
        economy = await self.bot.db.fetchrow(
            "SELECT gold FROM economy WHERE user_id = $1",
            target.id
        )
        gold = economy['gold'] if economy else 0
        
        # Busca guilda
        guild_data = await self.bot.db.fetchrow(
            """
            SELECT g.name, gm.role
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE gm.user_id = $1
            """,
            target.id
        )
        
        # Busca zona atual
        zone = await self.bot.db.fetchrow(
            "SELECT nome FROM zone WHERE zone_id = $1",
            user_data['zona_id']
        )
        
        # Calcula fama total
        fame_total = (
            user_data['fame_arena'] + 
            user_data['fame_combat'] + 
            user_data['fame_crafting'] + 
            user_data['fame_exploration'] + 
            user_data['fame_trading']
        )
        
        # Busca títulos de cada categoria
        title_arena = await self.get_fame_title('arena', user_data['fame_arena'])
        title_combat = await self.get_fame_title('combat', user_data['fame_combat'])
        title_crafting = await self.get_fame_title('crafting', user_data['fame_crafting'])
        title_exploration = await self.get_fame_title('exploration', user_data['fame_exploration'])
        title_trading = await self.get_fame_title('trading', user_data['fame_trading'])
        
        # Cria embed
        embed = discord.Embed(
            title=f"📊 Perfil de {target.display_name}",
            color=discord.Color.purple(),
            timestamp=datetime.datetime.now()
        )
        
        # Avatar do jogador
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Informações básicas
        guild_info = f"{guild_data['role'].title()} - {guild_data['name']}" if guild_data else "Sem Guilda"
        
        embed.add_field(
            name="👤 Informações Básicas",
            value=(
                f"**ID:** `{target.id}`\n"
                f"**Guilda:** {guild_info}\n"
                f"**Zona Atual:** {zone['nome'] if zone else 'Desconhecida'}"
            ),
            inline=False
        )
        
        # Stats
        embed.add_field(
            name="⭐ Status",
            value=(
                f"**Level:** {user_data['level']}\n"
                f"**HP:** {user_data['current_hp']}/{user_data['base_hp']}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="💰 Riqueza",
            value=f"**Gold:** {self.format_number(gold)}",
            inline=True
        )
        
        # Fama Total (destaque)
        embed.add_field(
            name="🏆 Fama Total",
            value=f"**{self.format_number(fame_total)}** pontos",
            inline=False
        )
        
        # Fama por categoria
        embed.add_field(
            name="⚔️ Fama de Arena",
            value=f"**{self.format_number(user_data['fame_arena'])}**\n{title_arena}",
            inline=True
        )
        
        embed.add_field(
            name="💀 Fama de Combate",
            value=f"**{self.format_number(user_data['fame_combat'])}**\n{title_combat}",
            inline=True
        )
        
        embed.add_field(
            name="🔨 Fama de Criação",
            value=f"**{self.format_number(user_data['fame_crafting'])}**\n{title_crafting}",
            inline=True
        )
        
        embed.add_field(
            name="🗺️ Fama de Exploração",
            value=f"**{self.format_number(user_data['fame_exploration'])}**\n{title_exploration}",
            inline=True
        )
        
        embed.add_field(
            name="💎 Fama Comercial",
            value=f"**{self.format_number(user_data['fame_trading'])}**\n{title_trading}",
            inline=True
        )
        
        # Footer com dica
        embed.set_footer(
            text="💡 Ganhe fama em arenas, combates, crafting, exploração e comércio!"
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
