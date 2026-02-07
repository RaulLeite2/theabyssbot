import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import asyncio
import random


class ArenaLeaderboard(commands.Cog):
    """Arena PvP system with leaderboard, wagers, UI, and challenges."""
    arena = app_commands.Group(name="arena", description="Comandos da arena PvP")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_table(self):
        try:
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS arena_stats (
                    user_id BIGINT PRIMARY KEY,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0
                )
                """
            )
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
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS arena_challenges (
                    id SERIAL PRIMARY KEY,
                    challenger BIGINT NOT NULL,
                    challenged BIGINT NOT NULL,
                    wager INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
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

    @arena.command(name="record", description="Mostra o record de um jogador na arena")
    async def record(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        await self.ensure_table()
        target = user or interaction.user
        row = await self.bot.db.fetchrow("SELECT wins,losses,draws FROM arena_stats WHERE user_id = $1", target.id)
        if not row:
            return await interaction.followup.send("Nenhum registro para esse jogador.", ephemeral=True)
        embed = discord.Embed(title=f"Arena Record: {target.display_name}")
        embed.add_field(name="Wins", value=str(row.get("wins",0)))
        embed.add_field(name="Losses", value=str(row.get("losses",0)))
        embed.add_field(name="Draws", value=str(row.get("draws",0)))
        await interaction.followup.send(embed=embed)

    @arena.command(name="top", description="Top jogadores da arena")
    async def top(self, interaction: discord.Interaction, limit: int = 10):
        await interaction.response.defer()
        await self.ensure_table()
        rows = await self.bot.db.fetch("SELECT user_id,wins FROM arena_stats ORDER BY wins DESC LIMIT $1", limit)
        desc = []
        for r in rows:
            try:
                u = await self.bot.fetch_user(r["user_id"])
                desc.append(f"{u.display_name} — {r['wins']} wins")
            except Exception:
                desc.append(f"{r['user_id']} — {r['wins']} wins")

        embed = discord.Embed(title="🏆 Arena Top")
        embed.description = "\n".join(desc) if desc else "Nenhum registro"
        await interaction.followup.send(embed=embed)

    @arena.command(name="wager", description="Bloqueia gold para uma aposta de arena")
    async def wager(self, interaction: discord.Interaction, amount: int):
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

    class ChallengeView(View):
        def __init__(self, bot, challenger_id, challenged_id, wager):
            super().__init__(timeout=60)
            self.bot = bot
            self.challenger = challenger_id
            self.challenged = challenged_id
            self.wager = wager

        @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
        async def accept_button(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != self.challenged:
                return await interaction.response.send_message("🚫 Apenas o desafiado pode aceitar.", ephemeral=True)

            # attempt to lock wagers automatically if wager > 0
            if self.wager and self.wager > 0:
                arena_cog = self.bot.get_cog('ArenaLeaderboard')
                if arena_cog is None:
                    return await interaction.response.send_message("❌ Sistema de apostas indisponível.", ephemeral=True)
                ok1 = await arena_cog.safe_transfer(self.challenger, self.wager)
                ok2 = await arena_cog.safe_transfer(self.challenged, self.wager)
                if not (ok1 and ok2):
                    # refund any partial
                    if ok1:
                        await self.bot.db.execute("UPDATE users SET gold = gold + $1 WHERE discord_id = $2", self.wager, self.challenger)
                    if ok2:
                        await self.bot.db.execute("UPDATE users SET gold = gold + $1 WHERE discord_id = $2", self.wager, self.challenged)
                    return await interaction.response.send_message("🚫 Falha ao bloquear aposta (saldo insuficiente).", ephemeral=True)

            await interaction.response.send_message("✅ Desafio aceito. Iniciando duelo...")
            channel = interaction.channel
            await channel.send(f"🏟️ Duel start: <@{self.challenger}> vs <@{self.challenged}> (Wager: {self.wager})")
            self.stop()

        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
        async def decline_button(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != self.challenged:
                return await interaction.response.send_message("🚫 Apenas o desafiado pode recusar.", ephemeral=True)
            await interaction.response.send_message("❌ Desafio recusado.")
            self.stop()

    @arena.command(name="ui_challenge", description="Desafiar com UI (buttons) e aposta automática")
    async def ui_challenge(self, interaction: discord.Interaction, opponent: discord.User, wager: int = 0):
        await interaction.response.defer()
        view = ArenaLeaderboard.ChallengeView(self.bot, interaction.user.id, opponent.id, wager)
        await interaction.followup.send(f"{opponent.mention}, você foi desafiado por {interaction.user.mention} (Wager: {wager})", view=view)

    @arena.command(name="challenge", description="Desafiar um jogador para duelo com combate simulado")
    async def challenge(self, interaction: discord.Interaction, opponent: discord.User, wager: int = 0):
        await interaction.response.defer()
        await self.ensure_table()
        try:
            row = await self.bot.db.fetchrow("INSERT INTO arena_challenges (challenger, challenged, wager) VALUES ($1,$2,$3) RETURNING id", interaction.user.id, opponent.id, wager)
        except Exception:
            return await interaction.followup.send("❌ Não foi possível criar desafio.", ephemeral=True)

        await interaction.followup.send(f"⚔️ Desafio enviado para {opponent.mention}. Wager: {wager}. Use `/arena duel {interaction.user.id}` para aceitar e duelar.")
        try:
            await opponent.send(f"Você foi desafiado por {interaction.user.display_name} para um duelo. Use `/arena duel {interaction.user.id}` para aceitar.")
        except Exception:
            pass

    @arena.command(name="duel", description="Aceitar desafio e iniciar combate simulado")
    async def duel(self, interaction: discord.Interaction, challenger_id: str):
        await interaction.response.defer()
        await self.ensure_table()
        try:
            cid = int(challenger_id)
        except Exception:
            return await interaction.followup.send("❌ ID inválido.", ephemeral=True)

        chal = await self.bot.db.fetchrow("SELECT id, challenger, challenged, wager, status FROM arena_challenges WHERE challenger = $1 AND challenged = $2 ORDER BY created_at DESC LIMIT 1", cid, interaction.user.id)
        if not chal or chal["status"] != 'pending':
            return await interaction.followup.send("🚫 Não há desafio pendente desse jogador.", ephemeral=True)

        # fetch basic stats for both players
        def get_stats(row):
            if not row:
                return None
            max_hp = (row["base_hp"] or 0) + (row.get("level") or 0) * 25
            return {
                "hp": row.get("current_hp") or max_hp,
                "max_hp": max_hp,
                "atk": 50,
                "defense": 10
            }

        a = await self.bot.db.fetchrow("SELECT level, base_hp, current_hp FROM users WHERE discord_id = $1", chal["challenger"])
        b = await self.bot.db.fetchrow("SELECT level, base_hp, current_hp FROM users WHERE discord_id = $1", chal["challenged"])

        if not a or not b:
            return await interaction.followup.send("🚫 Estatísticas de um dos jogadores não encontradas.", ephemeral=True)

        # equipment bonuses
        try:
            eq_a = await self.bot.db.fetch("SELECT i.basedamage, i.basedefense FROM equipment e JOIN items i ON i.id = e.item_id WHERE e.user_id = $1", chal["challenger"])
            eq_b = await self.bot.db.fetch("SELECT i.basedamage, i.basedefense FROM equipment e JOIN items i ON i.id = e.item_id WHERE e.user_id = $1", chal["challenged"])
            a_bonus_atk = sum(r["basedamage"] or 0 for r in eq_a)
            a_bonus_def = sum(r["basedefense"] or 0 for r in eq_a)
            b_bonus_atk = sum(r["basedamage"] or 0 for r in eq_b)
            b_bonus_def = sum(r["basedefense"] or 0 for r in eq_b)
        except Exception:
            a_bonus_atk = a_bonus_def = b_bonus_atk = b_bonus_def = 0

        stat_a = get_stats(a)
        stat_b = get_stats(b)
        stat_a["atk"] += a_bonus_atk
        stat_a["defense"] += a_bonus_def
        stat_b["atk"] += b_bonus_atk
        stat_b["defense"] += b_bonus_def

        # simple simulated duel
        log = [f"Duel start: <@{chal['challenger']}> vs <@{chal['challenged']}>"]
        turn = 1
        while stat_a["hp"] > 0 and stat_b["hp"] > 0 and turn < 200:
            ra = random.randint(1, 6)
            rb = random.randint(1, 6)
            dmg_a = max(stat_a["atk"] - stat_b["defense"], 0)
            dmg_b = max(stat_b["atk"] - stat_a["defense"], 0)
            if ra >= rb:
                stat_b["hp"] -= dmg_a
                log.append(f"Turn {turn}: <@{chal['challenger']}> hits {dmg_a} dmg")
            else:
                stat_a["hp"] -= dmg_b
                log.append(f"Turn {turn}: <@{chal['challenged']}> hits {dmg_b} dmg")
            turn += 1

        if stat_a["hp"] <= 0 and stat_b["hp"] <= 0:
            result = "Draw"
            winner = None
        elif stat_a["hp"] <= 0:
            result = f"Winner: <@{chal['challenged']}>"
            winner = chal['challenged']
        else:
            result = f"Winner: <@{chal['challenger']}>"
            winner = chal['challenger']

        # update arena stats
        if winner:
            loser = chal['challenger'] if winner == chal['challenged'] else chal['challenged']
            await self.bot.db.execute("INSERT INTO arena_stats (user_id, wins) VALUES ($1, 1) ON CONFLICT (user_id) DO UPDATE SET wins = arena_stats.wins + 1", winner)
            await self.bot.db.execute("INSERT INTO arena_stats (user_id, losses) VALUES ($1, 1) ON CONFLICT (user_id) DO UPDATE SET losses = arena_stats.losses + 1", loser)
            
            # Adicionar Fama de Arena para o vencedor
            fame_amount = 25  # Fama por vitória na arena
            rpg_cog = self.bot.get_cog("RPG")
            if rpg_cog and hasattr(rpg_cog, 'add_fame'):
                await rpg_cog.add_fame(
                    winner, 
                    'arena', 
                    fame_amount, 
                    f"Venceu duelo de arena"
                )
        else:
            await self.bot.db.execute("INSERT INTO arena_stats (user_id, draws) VALUES ($1, 1) ON CONFLICT (user_id) DO UPDATE SET draws = arena_stats.draws + 1", chal['challenger'])
            await self.bot.db.execute("INSERT INTO arena_stats (user_id, draws) VALUES ($1, 1) ON CONFLICT (user_id) DO UPDATE SET draws = arena_stats.draws + 1", chal['challenged'])

        # mark challenge completed
        await self.bot.db.execute("UPDATE arena_challenges SET status = 'completed' WHERE id = $1", chal["id"])

        embed = discord.Embed(title="🏟️ Arena Duel Result", description="\n".join(log[-8:]))
        embed.add_field(name="Resultado", value=result)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    cog = ArenaLeaderboard(bot)
    await bot.add_cog(cog)
