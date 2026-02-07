import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class Economy(commands.Cog):
    """Comandos básicos de economia e gold."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Ver seu saldo de gold")
    async def balance(self, interaction: discord.Interaction, player: Optional[discord.Member] = None):
        """Mostra o saldo de gold do jogador."""
        target = player or interaction.user
        
        gold = await self.bot.db.fetchval(
            "SELECT gold FROM economy WHERE user_id = $1",
            target.id
        )
        
        if gold is None:
            # Criar entrada na economia se não existir
            await self.bot.db.execute(
                "INSERT INTO economy (user_id, gold) VALUES ($1, 0) ON CONFLICT DO NOTHING",
                target.id
            )
            gold = 0
        
        embed = discord.Embed(
            title=f"💰 {'Seu Saldo' if target == interaction.user else f'Saldo de {target.display_name}'}",
            description=f"**{gold:,} gold**",
            color=discord.Color.gold()
        )
        
        if target == interaction.user:
            embed.set_footer(text="Use /explore e /battle engage para ganhar mais gold!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pay", description="Transferir gold para outro jogador")
    @app_commands.describe(player="Jogador que receberá o gold", amount="Quantidade de gold")
    async def pay(self, interaction: discord.Interaction, player: discord.Member, amount: int):
        """Transfere gold entre jogadores."""
        if player.id == interaction.user.id:
            return await interaction.response.send_message("❌ Você não pode transferir gold para si mesmo!", ephemeral=True)
        
        if amount <= 0:
            return await interaction.response.send_message("❌ A quantidade deve ser maior que 0!", ephemeral=True)
        
        if player.bot:
            return await interaction.response.send_message("❌ Você não pode transferir gold para bots!", ephemeral=True)
        
        # Verificar se o jogador tem gold suficiente
        sender_gold = await self.bot.db.fetchval(
            "SELECT gold FROM economy WHERE user_id = $1",
            interaction.user.id
        )
        
        if not sender_gold or sender_gold < amount:
            return await interaction.response.send_message(
                f"❌ Você não tem gold suficiente! Saldo atual: {sender_gold or 0} gold",
                ephemeral=True
            )
        
        # Realizar transferência
        await self.bot.db.execute(
            """
            UPDATE economy SET gold = gold - $1 WHERE user_id = $2
            """,
            amount, interaction.user.id
        )
        
        await self.bot.db.execute(
            """
            INSERT INTO economy (user_id, gold) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2
            """,
            player.id, amount
        )
        
        embed = discord.Embed(
            title="💸 Transferência Realizada",
            description=f"{interaction.user.mention} transferiu **{amount:,} gold** para {player.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Ver ranking de jogadores")
    @app_commands.describe(category="Categoria do ranking")
    @app_commands.choices(category=[
        app_commands.Choice(name="💰 Gold", value="gold"),
        app_commands.Choice(name="⭐ Level", value="level"),
        app_commands.Choice(name="🏆 Fama Total", value="fame_total"),
        app_commands.Choice(name="⚔️ Fama Arena", value="fame_arena"),
        app_commands.Choice(name="💀 Fama Combate", value="fame_combat"),
        app_commands.Choice(name="🔨 Fama Criação", value="fame_crafting"),
        app_commands.Choice(name="🗺️ Fama Exploração", value="fame_exploration"),
        app_commands.Choice(name="💎 Fama Comércio", value="fame_trading"),
    ])
    async def leaderboard(self, interaction: discord.Interaction, category: str = "gold"):
        """Mostra o leaderboard de gold ou level."""
        await interaction.response.defer()
        
        if category == "gold":
            rows = await self.bot.db.fetch(
                """
                SELECT e.user_id, e.gold
                FROM economy e
                ORDER BY e.gold DESC
                LIMIT 10
                """
            )
            
            if not rows:
                return await interaction.followup.send("📊 Nenhum jogador com gold ainda.", ephemeral=True)
            
            embed = discord.Embed(
                title="💰 Top 10 - Gold",
                color=discord.Color.gold()
            )
            
            description = []
            for idx, row in enumerate(rows, 1):
                user = self.bot.get_user(row["user_id"])
                name = user.display_name if user else f"User#{row['user_id']}"
                
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"`{idx}.`"
                description.append(f"{medal} **{name}** - {row['gold']:,} gold")
            
            embed.description = "\n".join(description)
            
        elif category == "level":
            rows = await self.bot.db.fetch(
                """
                SELECT discord_id, level
                FROM users
                ORDER BY level DESC
                LIMIT 10
                """
            )
            
            if not rows:
                return await interaction.followup.send("📊 Nenhum jogador registrado ainda.", ephemeral=True)
            
            embed = discord.Embed(
                title="⭐ Top 10 - Level",
                color=discord.Color.blue()
            )
            
            description = []
            for idx, row in enumerate(rows, 1):
                user = self.bot.get_user(row["discord_id"])
                name = user.display_name if user else f"User#{row['discord_id']}"
                
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"`{idx}.`"
                description.append(f"{medal} **{name}** - Level {row['level']}")
            
            embed.description = "\n".join(description)
        
        elif category == "fame_total":
            rows = await self.bot.db.fetch(
                """
                SELECT discord_id, 
                       (COALESCE(fame_arena, 0) + COALESCE(fame_combat, 0) + 
                        COALESCE(fame_crafting, 0) + COALESCE(fame_exploration, 0) + 
                        COALESCE(fame_trading, 0)) as total_fame
                FROM users
                ORDER BY total_fame DESC
                LIMIT 10
                """
            )
            
            if not rows:
                return await interaction.followup.send("📊 Nenhum jogador com fama ainda.", ephemeral=True)
            
            embed = discord.Embed(
                title="🏆 Top 10 - Fama Total",
                color=discord.Color.purple()
            )
            
            description = []
            for idx, row in enumerate(rows, 1):
                user = self.bot.get_user(row["discord_id"])
                name = user.display_name if user else f"User#{row['discord_id']}"
                
                fame = row['total_fame']
                fame_str = f"{fame / 1_000_000:.1f}M" if fame >= 1_000_000 else f"{fame / 1_000:.1f}K" if fame >= 1_000 else str(fame)
                
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"`{idx}.`"
                description.append(f"{medal} **{name}** - {fame_str} pontos")
            
            embed.description = "\n".join(description)
        
        elif category in ["fame_arena", "fame_combat", "fame_crafting", "fame_exploration", "fame_trading"]:
            icons = {
                "fame_arena": "⚔️",
                "fame_combat": "💀",
                "fame_crafting": "🔨",
                "fame_exploration": "🗺️",
                "fame_trading": "💎"
            }
            titles = {
                "fame_arena": "Arena",
                "fame_combat": "Combate",
                "fame_crafting": "Criação",
                "fame_exploration": "Exploração",
                "fame_trading": "Comércio"
            }
            
            rows = await self.bot.db.fetch(
                f"""
                SELECT discord_id, COALESCE({category}, 0) as fame
                FROM users
                ORDER BY fame DESC
                LIMIT 10
                """
            )
            
            if not rows:
                return await interaction.followup.send("📊 Nenhum jogador com essa fama ainda.", ephemeral=True)
            
            embed = discord.Embed(
                title=f"{icons[category]} Top 10 - Fama de {titles[category]}",
                color=discord.Color.purple()
            )
            
            description = []
            for idx, row in enumerate(rows, 1):
                user = self.bot.get_user(row["discord_id"])
                name = user.display_name if user else f"User#{row['discord_id']}"
                
                fame = row['fame']
                fame_str = f"{fame / 1_000_000:.1f}M" if fame >= 1_000_000 else f"{fame / 1_000:.1f}K" if fame >= 1_000 else str(fame)
                
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"`{idx}.`"
                description.append(f"{medal} **{name}** - {fame_str} pontos")
            
            embed.description = "\n".join(description)
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
