import discord
from discord.ext import commands
from discord import app_commands


class ArenaWager(commands.Cog):
    """Secure wager transfer and checking for arena duels."""
    # Note: arena group is defined in arena_leaderboard cog

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Attach commands to the existing arena group
        try:
            main_arena_cog = bot.get_cog('ArenaLeaderboard')
            if main_arena_cog and hasattr(main_arena_cog, 'arena'):
                main_arena_cog.arena.add_command(self.wager_cmd())
        except Exception:
            pass

    async def ensure_table(self):
        try:
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS wagers (
                    id SERIAL PRIMARY KEY,
                    challenge_id INTEGER,
                    amount INTEGER NOT NULL,
                    payer BIGINT NOT NULL,
                    paid BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )
        except Exception:
            pass

    async def safe_transfer(self, user_id: int, amount: int) -> bool:
        """Attempt to deduct `amount` from user's gold atomically. Returns True on success."""
        if amount <= 0:
            return False
        # naive implementation: check and update
        try:
            balance = await self.bot.db.fetchval("SELECT gold FROM users WHERE discord_id = $1", user_id)
            if balance is None:
                return False
            if balance < amount:
                return False
            await self.bot.db.execute("UPDATE users SET gold = gold - $1 WHERE discord_id = $2", amount, user_id)
            return True
        except Exception:
            return False

    def wager_cmd(self):
        @app_commands.command(name="wager", description="Check or lock gold for an arena wager")
        async def wager(interaction: discord.Interaction, amount: int):
            await interaction.response.defer()
            await self.ensure_table()
            if amount <= 0:
                return await interaction.followup.send("❌ Valor inválido.", ephemeral=True)

            ok = await self.safe_transfer(interaction.user.id, amount)
            if not ok:
                return await interaction.followup.send("🚫 Saldo insuficiente.", ephemeral=True)

            # store wager record
            try:
                await self.bot.db.execute("INSERT INTO wagers (amount, payer, paid) VALUES ($1,$2,TRUE)", amount, interaction.user.id)
            except Exception:
                # refund on error
                await self.bot.db.execute("UPDATE users SET gold = gold + $1 WHERE discord_id = $2", amount, interaction.user.id)
                return await interaction.followup.send("❌ Erro ao registrar aposta. Valor reembolsado.", ephemeral=True)

            await interaction.followup.send(f"✅ Aposta de {amount} gold bloqueada com sucesso.", ephemeral=True)
        return wager


async def setup(bot: commands.Bot):
    # Temporarily disabled - conflicts with arena_leaderboard
    # TODO: Add commands to arena_leaderboard cog
    pass
