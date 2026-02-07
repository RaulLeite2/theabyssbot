import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random


class Achievements(commands.Cog):
    """Sistema de conquistas, daily quests e sorte"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # =========================
    # CONQUISTAS (ACHIEVEMENTS)
    # =========================
    
    @app_commands.command(name="achievements", description="Veja suas conquistas e progresso")
    async def achievements(self, interaction: discord.Interaction):
        """Mostra conquistas do jogador"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Busca todas as conquistas e progresso do usuário
        achievements = await self.bot.db.fetch(
            """
            SELECT 
                a.id, a.name, a.description, a.icon, a.category,
                a.requirement_amount, a.reward_gold, a.reward_fame,
                COALESCE(ua.progress, 0) as progress,
                COALESCE(ua.completed, FALSE) as completed,
                ua.completed_at
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = $1
            WHERE a.is_hidden = FALSE OR ua.completed = TRUE
            ORDER BY a.category, completed DESC, a.requirement_amount
            """,
            user_id
        )
        
        if not achievements:
            return await interaction.followup.send(
                "❌ Nenhuma conquista disponível no momento.",
                ephemeral=True
            )
        
        # Separa por categoria
        categories = {}
        completed_count = 0
        
        for ach in achievements:
            if ach['completed']:
                completed_count += 1
            
            cat = ach['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ach)
        
        # Emojis por categoria
        cat_icons = {
            'combat': '⚔️ Combate',
            'exploration': '🗺️ Exploração',
            'crafting': '🔨 Criação',
            'social': '🤝 Social',
            'special': '⭐ Especial'
        }
        
        embed = discord.Embed(
            title="🏆 Suas Conquistas",
            description=f"**{completed_count}/{len(achievements)}** conquistas completadas",
            color=discord.Color.gold()
        )
        
        for cat, achs in categories.items():
            cat_name = cat_icons.get(cat, cat.title())
            ach_text = []
            
            for ach in achs[:5]:  # Limite por categoria
                status = "✅" if ach['completed'] else "⏳"
                progress_bar = self._progress_bar(ach['progress'], ach['requirement_amount'])
                
                if ach['completed']:
                    ach_text.append(f"{status} **{ach['name']}** {ach['icon']}")
                else:
                    ach_text.append(
                        f"{status} **{ach['name']}** {ach['icon']}\n"
                        f"   {progress_bar} `{ach['progress']}/{ach['requirement_amount']}`"
                    )
            
            if ach_text:
                embed.add_field(
                    name=cat_name,
                    value="\n".join(ach_text),
                    inline=False
                )
        
        embed.set_footer(text="Complete conquistas para ganhar recompensas!")
        await interaction.followup.send(embed=embed)
    
    def _progress_bar(self, current: int, total: int, length: int = 10) -> str:
        """Cria uma barra de progresso visual"""
        if total == 0:
            return "░" * length
        
        filled = int((current / total) * length)
        filled = min(filled, length)
        bar = "█" * filled + "░" * (length - filled)
        return bar
    
    async def update_achievement_progress(self, user_id: int, requirement_type: str, amount: int = 1):
        """Atualiza progresso de conquistas e verifica conclusões"""
        # Busca conquistas desse tipo que o usuário ainda não completou
        achievements = await self.bot.db.fetch(
            """
            SELECT a.id, a.name, a.requirement_amount, a.reward_gold, a.reward_fame, a.icon
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = $1
            WHERE a.requirement_type = $2 
            AND (ua.completed IS NULL OR ua.completed = FALSE)
            """,
            user_id, requirement_type
        )
        
        completed_achievements = []
        
        for ach in achievements:
            # Atualiza ou insere progresso
            new_progress = await self.bot.db.fetchval(
                """
                INSERT INTO user_achievements (user_id, achievement_id, progress)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, achievement_id)
                DO UPDATE SET progress = user_achievements.progress + $3
                RETURNING progress
                """,
                user_id, ach['id'], amount
            )
            
            # Verifica se completou
            if new_progress >= ach['requirement_amount']:
                await self.bot.db.execute(
                    """
                    UPDATE user_achievements
                    SET completed = TRUE, completed_at = NOW()
                    WHERE user_id = $1 AND achievement_id = $2
                    """,
                    user_id, ach['id']
                )
                
                # Dá recompensas
                if ach['reward_gold'] > 0:
                    await self.bot.db.execute(
                        """
                        INSERT INTO economy (user_id, gold) VALUES ($1, $2)
                        ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2
                        """,
                        user_id, ach['reward_gold']
                    )
                
                if ach['reward_fame'] > 0:
                    rpg_cog = self.bot.get_cog("RPG")
                    if rpg_cog and hasattr(rpg_cog, 'add_fame'):
                        await rpg_cog.add_fame(user_id, 'achievement', ach['reward_fame'], f"Completou {ach['name']}")
                
                completed_achievements.append(ach)
        
        return completed_achievements
    
    # =========================
    # DAILY QUESTS
    # =========================
    
    @app_commands.command(name="daily", description="Veja suas missões diárias")
    async def daily(self, interaction: discord.Interaction):
        """Mostra daily quests do jogador"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Remove quests expiradas
        await self.bot.db.execute(
            "DELETE FROM user_daily_quests WHERE expires_at < NOW()"
        )
        
        # Verifica se tem quests ativas
        active_quests = await self.bot.db.fetch(
            """
            SELECT 
                dq.description, dq.icon, dq.requirement_amount, dq.difficulty,
                dq.reward_gold, dq.reward_exp, dq.reward_fame,
                udq.progress, udq.completed, udq.expires_at
            FROM user_daily_quests udq
            JOIN daily_quests dq ON dq.id = udq.quest_id
            WHERE udq.user_id = $1 AND udq.expires_at > NOW()
            ORDER BY udq.completed, dq.difficulty
            """,
            user_id
        )
        
        # Se não tem quests, gera novas
        if not active_quests:
            await self._generate_daily_quests(user_id)
            active_quests = await self.bot.db.fetch(
                """
                SELECT 
                    dq.description, dq.icon, dq.requirement_amount, dq.difficulty,
                    dq.reward_gold, dq.reward_exp, dq.reward_fame,
                    udq.progress, udq.completed, udq.expires_at
                FROM user_daily_quests udq
                JOIN daily_quests dq ON dq.id = udq.quest_id
                WHERE udq.user_id = $1
                ORDER BY udq.completed, dq.difficulty
                """,
                user_id
            )
        
        if not active_quests:
            return await interaction.followup.send(
                "❌ Erro ao gerar daily quests. Tente novamente.",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title="📜 Missões Diárias",
            description="Complete suas missões antes que expirem!",
            color=discord.Color.blue()
        )
        
        completed = sum(1 for q in active_quests if q['completed'])
        embed.add_field(
            name="📊 Progresso",
            value=f"**{completed}/{len(active_quests)}** missões completas",
            inline=False
        )
        
        difficulty_colors = {
            'easy': '🟢',
            'medium': '🟡',
            'hard': '🔴'
        }
        
        for quest in active_quests:
            status = "✅" if quest['completed'] else "⏳"
            diff_icon = difficulty_colors.get(quest['difficulty'], '⚪')
            progress_bar = self._progress_bar(quest['progress'], quest['requirement_amount'])
            
            rewards = []
            if quest['reward_gold'] > 0:
                rewards.append(f"💰 {quest['reward_gold']:,}")
            if quest['reward_exp'] > 0:
                rewards.append(f"⭐ {quest['reward_exp']} XP")
            if quest['reward_fame'] > 0:
                rewards.append(f"🏆 {quest['reward_fame']} fama")
            
            value_text = f"{progress_bar} `{quest['progress']}/{quest['requirement_amount']}`\n"
            value_text += f"🎁 {' | '.join(rewards)}"
            
            if not quest['completed']:
                embed.add_field(
                    name=f"{status} {diff_icon} {quest['icon']} {quest['description']}",
                    value=value_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{status} {quest['icon']} {quest['description']} (Completa)",
                    value="✨ Recompensas coletadas!",
                    inline=False
                )
        
        # Tempo restante
        expires_at = active_quests[0]['expires_at']
        time_left = expires_at - datetime.now()
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        
        embed.set_footer(text=f"⏰ Renova em {hours}h {minutes}m")
        await interaction.followup.send(embed=embed)
    
    async def _generate_daily_quests(self, user_id: int):
        """Gera 3 daily quests aleatórias para o usuário"""
        # Seleciona 3 quests aleatórias (1 easy, 1 medium, 1 hard)
        quests = []
        
        for difficulty in ['easy', 'medium', 'hard']:
            quest = await self.bot.db.fetchrow(
                """
                SELECT id FROM daily_quests 
                WHERE difficulty = $1
                ORDER BY RANDOM()
                LIMIT 1
                """,
                difficulty
            )
            if quest:
                quests.append(quest['id'])
        
        # Expira em 24 horas
        expires_at = datetime.now() + timedelta(hours=24)
        
        # Insere as quests
        for quest_id in quests:
            await self.bot.db.execute(
                """
                INSERT INTO user_daily_quests (user_id, quest_id, expires_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, quest_id) DO NOTHING
                """,
                user_id, quest_id, expires_at
            )
    
    async def update_daily_quest_progress(self, user_id: int, quest_type: str, amount: int = 1):
        """Atualiza progresso de daily quests"""
        # Busca quests ativas desse tipo
        quests = await self.bot.db.fetch(
            """
            SELECT udq.quest_id, dq.requirement_amount, dq.reward_gold, dq.reward_exp, dq.reward_fame
            FROM user_daily_quests udq
            JOIN daily_quests dq ON dq.id = udq.quest_id
            WHERE udq.user_id = $1 
            AND dq.quest_type = $2
            AND udq.completed = FALSE
            AND udq.expires_at > NOW()
            """,
            user_id, quest_type
        )
        
        for quest in quests:
            # Atualiza progresso
            new_progress = await self.bot.db.fetchval(
                """
                UPDATE user_daily_quests
                SET progress = progress + $1
                WHERE user_id = $2 AND quest_id = $3
                RETURNING progress
                """,
                amount, user_id, quest['quest_id']
            )
            
            # Se completou, dá recompensas
            if new_progress >= quest['requirement_amount']:
                await self.bot.db.execute(
                    """
                    UPDATE user_daily_quests
                    SET completed = TRUE
                    WHERE user_id = $1 AND quest_id = $2
                    """,
                    user_id, quest['quest_id']
                )
                
                # Recompensas
                if quest['reward_gold'] > 0:
                    await self.bot.db.execute(
                        """
                        INSERT INTO economy (user_id, gold) VALUES ($1, $2)
                        ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2
                        """,
                        user_id, quest['reward_gold']
                    )
                
                if quest['reward_exp'] > 0:
                    await self.bot.db.execute(
                        "UPDATE users SET exp = exp + $1 WHERE discord_id = $2",
                        quest['reward_exp'], user_id
                    )
                
                if quest['reward_fame'] > 0:
                    rpg_cog = self.bot.get_cog("RPG")
                    if rpg_cog and hasattr(rpg_cog, 'add_fame'):
                        await rpg_cog.add_fame(user_id, 'daily_quest', quest['reward_fame'], "Completou daily quest")
    
    # =========================
    # SISTEMA DE SORTE (FORTUNE)
    # =========================
    
    @app_commands.command(name="fortune", description="Consulte a Vidente Mística (1x por dia)")
    async def fortune(self, interaction: discord.Interaction):
        """Sistema de sorte com buffs/debuffs temporários"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Verifica última consulta
        last_fortune = await self.bot.db.fetchrow(
            "SELECT last_fortune_at, fortune_type, buff_type, buff_amount, expires_at FROM user_fortune WHERE user_id = $1",
            user_id
        )
        
        now = datetime.now()
        
        if last_fortune and last_fortune['last_fortune_at']:
            time_since = now - last_fortune['last_fortune_at']
            if time_since.total_seconds() < 86400:  # 24 horas
                # Mostra fortuna atual
                remaining = timedelta(seconds=86400) - time_since
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                
                if last_fortune['expires_at'] and last_fortune['expires_at'] > now:
                    fortune_names = {
                        'lucky': '🍀 Sortudo',
                        'unlucky': '💀 Azarado',
                        'blessed': '✨ Abençoado',
                        'cursed': '👿 Amaldiçoado',
                        'neutral': '😐 Neutro'
                    }
                    
                    buff_names = {
                        'gold_bonus': 'Bônus de Gold',
                        'exp_bonus': 'Bônus de XP',
                        'damage_bonus': 'Bônus de Dano',
                        'defense_bonus': 'Bônus de Defesa',
                        'loot_bonus': 'Bônus de Loot'
                    }
                    
                    buff_value = int((last_fortune['buff_amount'] - 1.0) * 100)
                    sign = "+" if buff_value > 0 else ""
                    
                    embed = discord.Embed(
                        title="🔮 Sua Fortuna Atual",
                        description=f"**{fortune_names.get(last_fortune['fortune_type'], 'Desconhecida')}**",
                        color=discord.Color.purple()
                    )
                    embed.add_field(
                        name="✨ Efeito Ativo",
                        value=f"{buff_names.get(last_fortune['buff_type'], 'Desconhecido')}: **{sign}{buff_value}%**",
                        inline=False
                    )
                    
                    buff_remaining = last_fortune['expires_at'] - now
                    buff_hours = int(buff_remaining.total_seconds() // 3600)
                    buff_minutes = int((buff_remaining.total_seconds() % 3600) // 60)
                    
                    embed.add_field(
                        name="⏳ Tempo Restante",
                        value=f"{buff_hours}h {buff_minutes}m",
                        inline=True
                    )
                    
                    embed.set_footer(text=f"Nova consulta disponível em {hours}h {minutes}m")
                    return await interaction.followup.send(embed=embed)
                
                return await interaction.followup.send(
                    f"⏰ Você já consultou a Vidente hoje!\nNova consulta em **{hours}h {minutes}m**.",
                    ephemeral=True
                )
        
        # Gera nova fortuna
        fortunes = [
            ('lucky', 'gold_bonus', 1.5, '🍀 **A Sorte Sorri Para Você!**\n+50% de Gold por 2 horas!'),
            ('lucky', 'exp_bonus', 1.3, '🍀 **Conhecimento Flui Como Água!**\n+30% de XP por 2 horas!'),
            ('blessed', 'damage_bonus', 1.25, '✨ **Força Divina Te Abençoa!**\n+25% de Dano por 2 horas!'),
            ('blessed', 'defense_bonus', 1.25, '✨ **Proteção Celestial Te Envolve!**\n+25% de Defesa por 2 horas!'),
            ('blessed', 'loot_bonus', 1.4, '✨ **Tesouros Te Aguardam!**\n+40% de Loot por 2 horas!'),
            ('unlucky', 'gold_bonus', 0.8, '💀 **O Azar Te Persegue...**\n-20% de Gold por 1 hora...'),
            ('cursed', 'damage_bonus', 0.85, '👿 **Maldição de Fraqueza!**\n-15% de Dano por 1 hora...'),
            ('neutral', 'gold_bonus', 1.0, '😐 **Um Dia Como Qualquer Outro.**\nSem efeitos especiais.'),
        ]
        
        fortune_type, buff_type, buff_amount, message = random.choice(fortunes)
        
        # Duração: buffs bons = 2h, debuffs = 1h, neutro = 0
        if fortune_type in ['lucky', 'blessed']:
            duration_hours = 2
        elif fortune_type in ['unlucky', 'cursed']:
            duration_hours = 1
        else:
            duration_hours = 0
        
        expires_at = now + timedelta(hours=duration_hours) if duration_hours > 0 else now
        
        # Salva fortuna
        await self.bot.db.execute(
            """
            INSERT INTO user_fortune (user_id, fortune_type, buff_type, buff_amount, expires_at, last_fortune_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id)
            DO UPDATE SET 
                fortune_type = $2,
                buff_type = $3,
                buff_amount = $4,
                expires_at = $5,
                last_fortune_at = $6
            """,
            user_id, fortune_type, buff_type, buff_amount, expires_at, now
        )
        
        embed = discord.Embed(
            title="🔮 A Vidente Mística Revela...",
            description=message,
            color=discord.Color.purple()
        )
        
        if duration_hours > 0:
            embed.add_field(
                name="⏰ Duração",
                value=f"{duration_hours} hora{'s' if duration_hours > 1 else ''}",
                inline=True
            )
        
        embed.set_footer(text="Volte amanhã para uma nova previsão!")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="stats", description="Veja suas estatísticas completas")
    async def stats(self, interaction: discord.Interaction):
        """Mostra estatísticas detalhadas do jogador"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Busca stats
        stats = await self.bot.db.fetchrow(
            "SELECT * FROM user_stats WHERE user_id = $1",
            user_id
        )
        
        if not stats:
            # Cria registro de stats
            await self.bot.db.execute(
                "INSERT INTO user_stats (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
                user_id
            )
            stats = await self.bot.db.fetchrow(
                "SELECT * FROM user_stats WHERE user_id = $1",
                user_id
            )
        
        # Busca dados básicos do usuário
        user = await self.bot.db.fetchrow(
            "SELECT level, exp FROM users WHERE discord_id = $1",
            user_id
        )
        
        gold = await self.bot.db.fetchval(
            "SELECT gold FROM economy WHERE user_id = $1",
            user_id
        ) or 0
        
        embed = discord.Embed(
            title=f"📊 Estatísticas de {interaction.user.display_name}",
            color=discord.Color.blue()
        )
        
        # Informações básicas
        embed.add_field(
            name="⭐ Perfil",
            value=f"**Nível:** {user['level']}\n**XP:** {user['exp']}\n**Gold:** {gold:,}",
            inline=True
        )
        
        # Combate
        kd_ratio = stats['total_kills'] / max(stats['total_deaths'], 1)
        embed.add_field(
            name="⚔️ Combate",
            value=f"**Kills:** {stats['total_kills']}\n**Deaths:** {stats['total_deaths']}\n**K/D:** {kd_ratio:.2f}",
            inline=True
        )
        
        # Conquistas
        achievements_count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM user_achievements WHERE user_id = $1 AND completed = TRUE",
            user_id
        ) or 0
        
        embed.add_field(
            name="🏆 Conquistas",
            value=f"**Desbloqueadas:** {achievements_count}",
            inline=True
        )
        
        # Exploração
        embed.add_field(
            name="🗺️ Exploração",
            value=f"**Zonas:** {stats['total_zones_explored']}\n**Recursos:** {stats['total_resources_collected']}",
            inline=True
        )
        
        # Economia
        embed.add_field(
            name="💰 Economia",
            value=f"**Gold Total Ganho:** {stats['total_gold_earned']:,}\n**Trades:** {stats['total_trades']}",
            inline=True
        )
        
        # Crafting
        embed.add_field(
            name="🔨 Criação",
            value=f"**Itens Craftados:** {stats['total_items_crafted']}",
            inline=True
        )
        
        # Recordes
        if stats['strongest_enemy_defeated'] or stats['rarest_item_found']:
            records = []
            if stats['strongest_enemy_defeated']:
                records.append(f"💀 **Inimigo mais forte:** {stats['strongest_enemy_defeated']}")
            if stats['rarest_item_found']:
                records.append(f"💎 **Item mais raro:** {stats['rarest_item_found']}")
            
            embed.add_field(
                name="🌟 Recordes",
                value="\n".join(records),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Achievements(bot))
