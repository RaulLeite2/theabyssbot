import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import asyncio


class ArenaUI(commands.Cog):
    """Arena UI with buttons for accept/decline and auto-wager execution."""
    # Note: arena group is defined in arena_leaderboard cog

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Attach commands to the existing arena group
        try:
            main_arena_cog = bot.get_cog('ArenaLeaderboard')
            if main_arena_cog and hasattr(main_arena_cog, 'arena'):
                main_arena_cog.arena.add_command(self.ui_challenge_cmd())
        except Exception:
            pass

    class ChallengeView(View):
        def __init__(self, bot, challenger_id, challenged_id, wager):
            super().__init__(timeout=60)
            self.bot = bot
            self.challenger = challenger_id
            self.challenged = challenged_id
            self.wager = wager

        @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
        async def accept(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != self.challenged:
                return await interaction.response.send_message("🚫 Apenas o desafiado pode aceitar.", ephemeral=True)

            # attempt to lock wagers automatically if wager > 0
            if self.wager and self.wager > 0:
                aw = self.bot.get_cog('ArenaWager')
                if aw is None:
                    return await interaction.response.send_message("❌ Sistema de apostas indisponível.", ephemeral=True)
                ok1 = await aw.safe_transfer(self.challenger, self.wager)
                ok2 = await aw.safe_transfer(self.challenged, self.wager)
                if not (ok1 and ok2):
                    # refund any partial
                    if ok1:
                        await self.bot.db.execute("UPDATE users SET gold = gold + $1 WHERE discord_id = $2", self.wager, self.challenger)
                    if ok2:
                        await self.bot.db.execute("UPDATE users SET gold = gold + $1 WHERE discord_id = $2", self.wager, self.challenged)
                    return await interaction.response.send_message("🚫 Falha ao bloquear aposta (saldo insuficiente).", ephemeral=True)

            await interaction.response.send_message("✅ Desafio aceito. Iniciando duelo...")
            # Trigger duel by sending a message to a handler or directly simulate here
            # For simplicity, just announce start
            channel = interaction.channel
            await channel.send(f"🏟️ Duel start: <@{self.challenger}> vs <@{self.challenged}> (Wager: {self.wager})")
            self.stop()

        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
        async def decline(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != self.challenged:
                return await interaction.response.send_message("🚫 Apenas o desafiado pode recusar.", ephemeral=True)
            await interaction.response.send_message("❌ Desafio recusado.")
            self.stop()

    def ui_challenge_cmd(self):
        @app_commands.command(name="ui_challenge", description="Desafiar com UI (buttons) e aposta automática")
        async def ui_challenge(interaction: discord.Interaction, opponent: discord.User, wager: int = 0):
            await interaction.response.defer()
            view = ArenaUI.ChallengeView(self.bot, interaction.user.id, opponent.id, wager)
            await interaction.followup.send(f"{opponent.mention}, você foi desafiado por {interaction.user.mention} (Wager: {wager})", view=view)
        return ui_challenge


async def setup(bot: commands.Bot):
    # Temporarily disabled - conflicts with arena_leaderboard
    # TODO: Add commands to arena_leaderboard cog
    pass
