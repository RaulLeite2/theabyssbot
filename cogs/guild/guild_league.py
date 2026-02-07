import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
from typing import Optional

class GuildLeague(commands.Cog):
    """Sistema de Ligas de Guildas com temporadas mensais"""
    
    league_group = app_commands.Group(name="league", description="Sistema de ligas de guildas")
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_season_end.start()
    
    def cog_unload(self):
        self.check_season_end.cancel()
    
    # =========================
    # TASK: VERIFICAR FIM DE TEMPORADA
    # =========================
    @tasks.loop(hours=1)
    async def check_season_end(self):
        """Verifica se a temporada acabou a cada hora"""
        try:
            season = await self.bot.db.fetchrow(
                "SELECT season_id, end_date FROM guild_seasons WHERE status = 'active'"
            )
            
            if season and datetime.datetime.now() >= season['end_date']:
                print("🏆 Temporada de guildas acabou! Finalizando...")
                
                # Finaliza temporada
                await self.bot.db.execute("SELECT finalize_guild_season()")
                
                # Inicia nova temporada
                await self.bot.db.execute("SELECT start_new_guild_season()")
                
                print("✅ Nova temporada iniciada!")
        except Exception as e:
            print(f"❌ Erro ao verificar fim de temporada: {e}")
    
    @check_season_end.before_loop
    async def before_check_season_end(self):
        await self.bot.wait_until_ready()
    
    # =========================
    # COMANDO: /league ranking
    # =========================
    @league_group.command(name="ranking", description="🏆 Ver ranking de guildas da temporada atual")
    @app_commands.describe(limit="Número de guildas para mostrar (padrão: 10)")
    async def ranking(self, interaction: discord.Interaction, limit: Optional[int] = 10):
        """Mostra o ranking de guildas da temporada atual"""
        await interaction.response.defer()
        
        # Limita entre 5 e 25
        limit = max(5, min(25, limit))
        
        # Busca temporada ativa
        season = await self.bot.db.fetchrow(
            "SELECT season_id, season_number, end_date FROM guild_seasons WHERE status = 'active'"
        )
        
        if not season:
            return await interaction.followup.send(
                "❌ Nenhuma temporada ativa no momento.",
                ephemeral=True
            )
        
        # Busca ranking de guildas
        guilds = await self.bot.db.fetch(
            """
            SELECT g.id, g.name, g.season_fame, g.total_fame, 
                   g.current_league, g.league_icon,
                   COUNT(gm.user_id) as member_count
            FROM guilds g
            LEFT JOIN guild_members gm ON gm.guild_id = g.id
            GROUP BY g.id, g.name, g.season_fame, g.total_fame, g.current_league, g.league_icon
            ORDER BY g.season_fame DESC
            LIMIT $1
            """,
            limit
        )
        
        if not guilds:
            return await interaction.followup.send(
                "📊 Nenhuma guilda registrada ainda.",
                ephemeral=True
            )
        
        # Calcula tempo restante
        time_left = season['end_date'] - datetime.datetime.now()
        days_left = time_left.days
        hours_left = time_left.seconds // 3600
        
        embed = discord.Embed(
            title=f"🏆 Liga de Guildas - Temporada {season['season_number']}",
            description=f"⏰ Tempo restante: **{days_left}d {hours_left}h**",
            color=discord.Color.purple(),
            timestamp=datetime.datetime.now()
        )
        
        # Lista de guildas
        ranking_text = []
        for idx, guild in enumerate(guilds, 1):
            # Medalhas para top 3
            if idx == 1:
                medal = "🥇"
            elif idx == 2:
                medal = "🥈"
            elif idx == 3:
                medal = "🥉"
            else:
                medal = f"`{idx}.`"
            
            # Formata fama
            fame = guild['season_fame']
            if fame >= 1_000_000:
                fame_str = f"{fame / 1_000_000:.1f}M"
            elif fame >= 1_000:
                fame_str = f"{fame / 1_000:.1f}K"
            else:
                fame_str = str(fame)
            
            ranking_text.append(
                f"{medal} {guild['league_icon']} **{guild['name']}** - {fame_str} fama ({guild['member_count']} membros)"
            )
        
        embed.add_field(
            name="📊 Ranking Atual",
            value="\n".join(ranking_text),
            inline=False
        )
        
        # Informações sobre ligas
        embed.add_field(
            name="ℹ️ Sobre Ligas",
            value=(
                "🥉 **Bronze** - 0+ fama\n"
                "🥈 **Prata** - 50K+ fama\n"
                "🥇 **Ouro** - 150K+ fama\n"
                "💎 **Platina** - 350K+ fama\n"
                "💠 **Diamante** - 750K+ fama\n"
                "🔷 **Mestre** - 1.5M+ fama\n"
                "🔮 **Cristal** - 3M+ fama (Topo Mundial!)"
            ),
            inline=False
        )
        
        embed.set_footer(text="💡 Ganhe fama para sua guilda através de atividades!")
        
        await interaction.followup.send(embed=embed)
    
    # =========================
    # COMANDO: /league info
    # =========================
    @league_group.command(name="info", description="ℹ️ Ver informações da liga da sua guilda")
    async def info(self, interaction: discord.Interaction):
        """Mostra informações detalhadas da liga da guilda do jogador"""
        await interaction.response.defer()
        
        # Busca guilda do jogador
        guild_data = await self.bot.db.fetchrow(
            """
            SELECT g.id, g.name, g.season_fame, g.total_fame, 
                   g.current_league, g.league_icon, gm.role
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE gm.user_id = $1
            """,
            interaction.user.id
        )
        
        if not guild_data:
            return await interaction.followup.send(
                "🚫 Você não está em nenhuma guilda!",
                ephemeral=True
            )
        
        # Busca temporada ativa
        season = await self.bot.db.fetchrow(
            "SELECT season_id, season_number, end_date FROM guild_seasons WHERE status = 'active'"
        )
        
        if not season:
            return await interaction.followup.send(
                "❌ Nenhuma temporada ativa no momento.",
                ephemeral=True
            )
        
        # Busca posição no ranking
        rank = await self.bot.db.fetchval(
            """
            SELECT COUNT(*) + 1
            FROM guilds
            WHERE season_fame > $1
            """,
            guild_data['season_fame']
        )
        
        # Busca informações da liga atual
        league_info = await self.bot.db.fetchrow(
            "SELECT * FROM guild_leagues WHERE league_name = $1",
            guild_data['current_league']
        )
        
        # Busca próxima liga
        next_league = await self.bot.db.fetchrow(
            """
            SELECT * FROM guild_leagues 
            WHERE rank_order > $1 
            ORDER BY rank_order ASC 
            LIMIT 1
            """,
            league_info['rank_order']
        )
        
        # Busca top 5 contribuidores
        top_contributors = await self.bot.db.fetch(
            """
            SELECT gfc.user_id, gfc.fame_contributed
            FROM guild_fame_contributions gfc
            WHERE gfc.guild_id = $1 AND gfc.season_id = $2
            ORDER BY gfc.fame_contributed DESC
            LIMIT 5
            """,
            guild_data['id'], season['season_id']
        )
        
        # Calcula tempo restante
        time_left = season['end_date'] - datetime.datetime.now()
        days_left = time_left.days
        hours_left = time_left.seconds // 3600
        
        # Cria embed
        embed = discord.Embed(
            title=f"{guild_data['league_icon']} {guild_data['name']}",
            description=f"**Liga {guild_data['current_league']}** | Rank #{rank} | Temporada {season['season_number']}",
            color=int(league_info['color'].replace('#', ''), 16),
            timestamp=datetime.datetime.now()
        )
        
        # Fama
        fame_str = self.format_number(guild_data['season_fame'])
        total_fame_str = self.format_number(guild_data['total_fame'])
        
        embed.add_field(
            name="🏆 Fama",
            value=f"**Temporada:** {fame_str}\n**Total:** {total_fame_str}",
            inline=True
        )
        
        # Tempo restante
        embed.add_field(
            name="⏰ Tempo Restante",
            value=f"**{days_left}d {hours_left}h**",
            inline=True
        )
        
        # Recompensa da liga
        reward_str = f"{league_info['season_reward_gold']:,}" if league_info['season_reward_gold'] > 0 else "Nenhuma"
        embed.add_field(
            name="💰 Recompensa da Liga",
            value=f"{reward_str} gold",
            inline=True
        )
        
        # Próxima liga
        if next_league:
            fame_needed = next_league['min_fame'] - guild_data['season_fame']
            embed.add_field(
                name=f"📈 Próxima Liga: {next_league['icon']} {next_league['league_name']}",
                value=f"Falta: **{self.format_number(fame_needed)}** fama",
                inline=False
            )
        else:
            embed.add_field(
                name="👑 Liga Máxima",
                value="Sua guilda alcançou a liga mais alta!",
                inline=False
            )
        
        # Top contribuidores
        if top_contributors:
            contrib_text = []
            for idx, contrib in enumerate(top_contributors, 1):
                user = self.bot.get_user(contrib['user_id'])
                name = user.display_name if user else f"ID:{contrib['user_id']}"
                fame = self.format_number(contrib['fame_contributed'])
                
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                contrib_text.append(f"{medal} **{name}** - {fame}")
            
            embed.add_field(
                name="⭐ Top 5 Contribuidores",
                value="\n".join(contrib_text),
                inline=False
            )
        
        embed.set_footer(text=f"💡 50% da sua fama pessoal vai para a guilda!")
        
        await interaction.followup.send(embed=embed)
    
    # =========================
    # COMANDO: /league history
    # =========================
    @league_group.command(name="history", description="📜 Ver histórico de temporadas da sua guilda")
    async def history(self, interaction: discord.Interaction):
        """Mostra o histórico de temporadas da guilda"""
        await interaction.response.defer()
        
        # Busca guilda do jogador
        guild_data = await self.bot.db.fetchrow(
            """
            SELECT g.id, g.name
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE gm.user_id = $1
            """,
            interaction.user.id
        )
        
        if not guild_data:
            return await interaction.followup.send(
                "🚫 Você não está em nenhuma guilda!",
                ephemeral=True
            )
        
        # Busca histórico de temporadas
        history = await self.bot.db.fetch(
            """
            SELECT gsr.season_id, gs.season_number, gsr.final_fame, 
                   gsr.final_league, gsr.final_rank, gsr.recorded_at
            FROM guild_season_rankings gsr
            JOIN guild_seasons gs ON gs.season_id = gsr.season_id
            WHERE gsr.guild_id = $1
            ORDER BY gs.season_number DESC
            LIMIT 10
            """,
            guild_data['id']
        )
        
        if not history:
            return await interaction.followup.send(
                "📜 Sua guilda ainda não possui histórico de temporadas.",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title=f"📜 Histórico de {guild_data['name']}",
            description="Últimas 10 temporadas",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        history_text = []
        for record in history:
            # Busca ícone da liga
            league_data = await self.bot.db.fetchrow(
                "SELECT icon FROM guild_leagues WHERE league_name = $1",
                record['final_league']
            )
            icon = league_data['icon'] if league_data else "🏆"
            
            fame_str = self.format_number(record['final_fame'])
            
            history_text.append(
                f"**Temporada {record['season_number']}** - Rank #{record['final_rank']}\n"
                f"{icon} {record['final_league']} | {fame_str} fama"
            )
        
        embed.add_field(
            name="🏆 Histórico",
            value="\n\n".join(history_text),
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
    
    # =========================
    # COMANDO: /league contribution
    # =========================
    @league_group.command(name="contribution", description="📊 Ver sua contribuição para a guilda")
    async def contribution(self, interaction: discord.Interaction):
        """Mostra a contribuição do jogador para a fama da guilda"""
        await interaction.response.defer()
        
        # Busca guilda do jogador
        guild_data = await self.bot.db.fetchrow(
            """
            SELECT g.id, g.name, g.season_fame
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE gm.user_id = $1
            """,
            interaction.user.id
        )
        
        if not guild_data:
            return await interaction.followup.send(
                "🚫 Você não está em nenhuma guilda!",
                ephemeral=True
            )
        
        # Busca temporada ativa
        season = await self.bot.db.fetchrow(
            "SELECT season_id, season_number FROM guild_seasons WHERE status = 'active'"
        )
        
        if not season:
            return await interaction.followup.send(
                "❌ Nenhuma temporada ativa no momento.",
                ephemeral=True
            )
        
        # Busca contribuição do jogador
        contribution = await self.bot.db.fetchrow(
            """
            SELECT fame_contributed, last_contribution
            FROM guild_fame_contributions
            WHERE guild_id = $1 AND user_id = $2 AND season_id = $3
            """,
            guild_data['id'], interaction.user.id, season['season_id']
        )
        
        if not contribution or contribution['fame_contributed'] == 0:
            return await interaction.followup.send(
                "📊 Você ainda não contribuiu com fama nesta temporada!\n"
                "💡 Ganhe fama pessoal através de atividades para contribuir com a guilda.",
                ephemeral=True
            )
        
        # Calcula porcentagem
        percentage = (contribution['fame_contributed'] / guild_data['season_fame'] * 100) if guild_data['season_fame'] > 0 else 0
        
        # Busca posição no ranking de contribuidores
        rank = await self.bot.db.fetchval(
            """
            SELECT COUNT(*) + 1
            FROM guild_fame_contributions
            WHERE guild_id = $1 AND season_id = $2 AND fame_contributed > $3
            """,
            guild_data['id'], season['season_id'], contribution['fame_contributed']
        )
        
        embed = discord.Embed(
            title=f"📊 Contribuição para {guild_data['name']}",
            description=f"Temporada {season['season_number']}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="🏆 Fama Contribuída",
            value=f"**{self.format_number(contribution['fame_contributed'])}** pontos",
            inline=True
        )
        
        embed.add_field(
            name="📈 Porcentagem",
            value=f"**{percentage:.1f}%** da fama total",
            inline=True
        )
        
        embed.add_field(
            name="🏅 Posição",
            value=f"**#{rank}** contribuidor",
            inline=True
        )
        
        # Última contribuição
        if contribution['last_contribution']:
            time_since = datetime.datetime.now() - contribution['last_contribution']
            if time_since.days > 0:
                time_str = f"{time_since.days}d atrás"
            elif time_since.seconds // 3600 > 0:
                time_str = f"{time_since.seconds // 3600}h atrás"
            else:
                time_str = "Recentemente"
            
            embed.add_field(
                name="⏰ Última Contribuição",
                value=time_str,
                inline=False
            )
        
        embed.set_footer(text="💡 Continue ativo para ajudar sua guilda a subir de liga!")
        
        await interaction.followup.send(embed=embed)
    
    # =========================
    # HELPER: FORMATAR NÚMEROS
    # =========================
    def format_number(self, num: int) -> str:
        """Formata números grandes"""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)

async def setup(bot):
    await bot.add_cog(GuildLeague(bot))
