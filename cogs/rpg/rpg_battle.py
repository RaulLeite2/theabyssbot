import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import json
try:
    from cogs.rpg.rpg_ui import BattleView
except Exception:
    BattleView = None

class RPGBattle(commands.Cog):
    """Combate e exploração do RPG (battle group)."""
    rpg_battle = app_commands.Group(name="battle", description="Comandos de combate do RPG")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # NOTE: `explore` foi movido para `cogs/rpg_explore.py` para separar responsabilidades.

    async def zone_name_autocomplete(self, interaction: discord.Interaction, current: str):
        # Return up to 25 matching zone names from the `zone` table (case-insensitive)
        try:
            rows = await self.bot.db.fetch(
                "SELECT nome FROM zone WHERE nome ILIKE $1 ORDER BY nome LIMIT 25",
                f"%{current}%"
            )
            return [app_commands.Choice(name=r['nome'], value=r['nome']) for r in rows]
        except Exception:
            return []

    @rpg_battle.command(name="engage", description="Entra em combate contra o evento ativo da zona")
    @app_commands.autocomplete(zone_name=zone_name_autocomplete)
    async def engage(self, interaction: discord.Interaction, zone_name: str):
        await interaction.response.defer()
        # resolve zone by name
        zone_row = await self.bot.db.fetchrow(
            "SELECT zone_id, permanent, nome FROM zone WHERE nome = $1",
            zone_name
        )
        if not zone_row:
            return await interaction.followup.send("🚫 Zona não encontrada.", ephemeral=True)

        zone_id = zone_row["zone_id"]

        player_zone = await self.bot.db.fetchval(
            "SELECT zona_id FROM users WHERE discord_id = $1",
            interaction.user.id
        )

        if player_zone != zone_id:
            return await interaction.followup.send("🚫 Você não está nessa zona.", ephemeral=True)

        event = await self.bot.db.fetchrow(
            "SELECT id, type, reward FROM events WHERE zone_id = $1 AND active = TRUE",
            zone_id
        )
        if not event:
            return await interaction.followup.send("🚫 Não há nada aqui digno do seu aço.", ephemeral=True)

        is_worldboss = event["type"] == 2
        reward = json.loads(event["reward"]) if event.get("reward") else {}

        # basic player stats fetch
        row = await self.bot.db.fetchrow(
            "SELECT level, base_hp, current_hp FROM users WHERE discord_id = $1", interaction.user.id
        )
        if not row:
            return await interaction.followup.send("🚫 Você não iniciou sua jornada.", ephemeral=True)

        max_hp = row["base_hp"] + row["level"] * 25
        # equipment bonuses
        eq_rows = await self.bot.db.fetch(
            """
            SELECT i.basedamage, i.basedefense
            FROM equipment e
            JOIN items i ON i.id = e.item_id
            WHERE e.user_id = $1
            """,
            interaction.user.id
        )
        bonus_atk = sum(r["basedamage"] or 0 for r in eq_rows)
        bonus_def = sum(r["basedefense"] or 0 for r in eq_rows)

        player = {
            "hp": row["current_hp"],
            "max_hp": max_hp,
            "atk": 50 + bonus_atk,
            "defense": 10 + bonus_def,
            "healing": 0
        }

        enemy = {
            "name": "Chefe Mundial" if is_worldboss else "Guardião da Dungeon",
            "hp": 1500 if is_worldboss else 500,
            "atk": 80 if is_worldboss else 45,
            "defense": 20 if is_worldboss else 10
        }

        # If interactive UI is available, hand off to BattleView
        if BattleView:
            main_rpg = self.bot.get_cog("RPG") or self
            view = BattleView(main_rpg, interaction.user.id, player, enemy, reward, event["id"], is_worldboss, zone_id)
            await interaction.followup.send(embed=view.make_embed(), view=view)
            return

        # fallback: synchronous simulated battle
        battle_log = [f"⚔️ Combate iniciado contra {enemy['name']}", f"❤️ HP Inicial: {player['hp']}/{player['max_hp']}"]
        turn = 1

        while player["hp"] > 0 and enemy["hp"] > 0:
            roll_player = random.randint(1, 6)
            roll_enemy = random.randint(1, 6)

            if player["healing"] > 0:
                heal = min(player["healing"], player["max_hp"] - player["hp"])
                if heal > 0:
                    player["hp"] += heal
                    battle_log.append(f"💚 Turno {turn}: Você regenera `{heal}` HP.")

            dmg_enemy = max(player["atk"] - enemy["defense"], 0)
            dmg_player = max(enemy["atk"] - player["defense"], 0)

            if roll_player >= roll_enemy:
                enemy["hp"] -= dmg_enemy
                battle_log.append(f"⚔️ Turno {turn}: Você causa `{dmg_enemy}` de dano.")
            else:
                player["hp"] -= dmg_player
                battle_log.append(f"🩸 Turno {turn}: Você sofre `{dmg_player}` de dano.")

            turn += 1

        # checagens pós-batalha
        if player["hp"] <= 0:
            await interaction.followup.send("☠️ **Derrota**\nO Abismo te engole sem piedade.")
            await self.bot.db.execute("UPDATE users SET current_hp = 0 WHERE discord_id = $1", interaction.user.id)
            return

        # vitória
        await self.bot.db.execute("UPDATE events SET active = FALSE WHERE id = $1", event["id"])
        await self.bot.db.execute("UPDATE users SET current_hp = $1 WHERE discord_id = $2", player["hp"], interaction.user.id)

        # Dar recompensas de gold e XP
        gold_reward = reward.get("gold", 100)
        xp_reward = reward.get("xp", 50)
        
        # Adicionar gold
        await self.bot.db.execute(
            """
            INSERT INTO economy (user_id, gold) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2
            """,
            interaction.user.id, gold_reward
        )
        
        # Adicionar XP
        rpg_cog = self.bot.get_cog("RPG")
        leveled = False
        if rpg_cog and hasattr(rpg_cog, 'give_exp'):
            leveled = await rpg_cog.give_exp(interaction.user.id, xp_reward)
        
        # Adicionar Fama de Combate
        fame_amount = 50 if not is_worldboss else 200  # World Boss dá mais fama
        if rpg_cog and hasattr(rpg_cog, 'add_fame'):
            await rpg_cog.add_fame(
                interaction.user.id, 
                'combat', 
                fame_amount, 
                f"Derrotou {enemy['name']} em {zone_row['nome']}"
            )

        embed = discord.Embed(title="🏆 Vitória!", description="\n".join(battle_log[-10:]), color=discord.Color.gold())
        embed.add_field(name="❤️ HP Restante", value=f"{player['hp']}/{player['max_hp']}")
        embed.add_field(name="💰 Gold Ganho", value=f"+{gold_reward} gold")
        embed.add_field(name="📜 XP Ganho", value=f"+{xp_reward} XP{' ⭐ LEVEL UP!' if leveled else ''}")
        embed.add_field(name="🏆 Fama de Combate", value=f"+{fame_amount} pontos", inline=False)

        await interaction.followup.send(embed=embed)

        # zona permanente check
        if is_worldboss:
            zone = await self.bot.db.fetchrow("SELECT permanent FROM zone WHERE zone_id = $1", zone_id)
            if zone and not zone["permanent"]:
                await interaction.channel.send("🌑 O WorldBoss caiu. 60s até o colapso.")
                asyncio.create_task(self.destroy_zone_after_worldboss(zone_id, interaction.channel))
            else:
                await interaction.channel.send("🌑 O WorldBoss caiu, mas a zona é permanente e não colapsará.")

    @rpg_battle.command(name="loot", description="Recolhe um item do saque (forneça item_id)")
    async def loot(self, interaction: discord.Interaction, item_id: int = None, take_all: bool = False):
        user_id = interaction.user.id
        if take_all:
            return await interaction.response.send_message("Use a interface interativa para pegar todo o saque.", ephemeral=True)

        if not item_id:
            return await interaction.response.send_message("📦 Especifique um `item_id` para recolher.", ephemeral=True)

        # give item to inventory
        try:
            await self.bot.db.execute(
                "INSERT INTO inventory (user_id, item_id, tier, quantity) VALUES ($1,$2,1,1) ON CONFLICT (user_id,item_id,tier) DO UPDATE SET quantity = inventory.quantity + 1",
                user_id, item_id
            )
            name = await self.bot.db.fetchval("SELECT name FROM items WHERE id = $1", item_id)
            return await interaction.response.send_message(f"🧾 Você pegou **{name or ('Item '+str(item_id))}**.", ephemeral=True)
        except Exception as e:
            print(f"Error giving loot: {e}")
            return await interaction.response.send_message("❌ Erro ao recolher o item.", ephemeral=True)

    @rpg_battle.command(name="revive", description="Tenta reviver usando uma poção de healing equipada ou no inventário")
    async def revive(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        # check equipment for healing buff
        eq = await self.bot.db.fetch(
            """
            SELECT i.id, i.name
            FROM equipment e
            JOIN items i ON i.id = e.item_id
            JOIN item_buffs ib ON ib.item_id = i.id
            WHERE e.user_id = $1 AND ib.tipo = 'healing'
            """,
            user_id
        )

        if eq:
            # use equipped healing
            row = await self.bot.db.fetchrow("SELECT base_hp, level FROM users WHERE discord_id = $1", user_id)
            max_hp = row["base_hp"] + row["level"] * 25
            new_hp = int(max_hp * 0.75)
            await self.bot.db.execute("UPDATE users SET current_hp = $1 WHERE discord_id = $2", new_hp, user_id)
            return await interaction.response.send_message(f"✨ Você reviveu usando {eq[0]['name']} e recebeu {new_hp} HP.", ephemeral=True)

        # check inventory for healing item
        inv = await self.bot.db.fetchrow(
            "SELECT inv.item_id, i.name FROM inventory inv JOIN items i ON i.id = inv.item_id JOIN item_buffs ib ON ib.item_id = i.id WHERE inv.user_id = $1 AND ib.tipo = 'healing' AND inv.quantity > 0",
            user_id
        )
        if inv:
            # consume one
            await self.bot.db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_id = $2", user_id, inv["item_id"])
            row = await self.bot.db.fetchrow("SELECT base_hp, level FROM users WHERE discord_id = $1", user_id)
            max_hp = row["base_hp"] + row["level"] * 25
            new_hp = int(max_hp * 0.75)
            await self.bot.db.execute("UPDATE users SET current_hp = $1 WHERE discord_id = $2", new_hp, user_id)
            return await interaction.response.send_message(f"✨ Você usou {inv['name']} e reviveu com {new_hp} HP.", ephemeral=True)

        return await interaction.response.send_message("❌ Você não possui poção de revive equipada nem no inventário.", ephemeral=True)

    @rpg_battle.command(name="zoneinfo", description="Mostra informações da zona e eventos ativos")
    @app_commands.autocomplete(zone_name=zone_name_autocomplete)
    async def zoneinfo(self, interaction: discord.Interaction, zone_name: str):
        await interaction.response.defer()
        zone = await self.bot.db.fetchrow(
            "SELECT zone_id, permanent, nome FROM zone WHERE nome = $1",
            zone_name
        )
        if not zone:
            return await interaction.followup.send("🚫 Zona não encontrada.", ephemeral=True)

        event = await self.bot.db.fetchrow(
            "SELECT id, type, reward FROM events WHERE zone_id = $1 AND active = TRUE",
            zone["zone_id"]
        )

        player_count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM users WHERE zona_id = $1",
            zone["zone_id"]
        )

        embed = discord.Embed(title=f"📍 Zona: {zone['nome']}", color=discord.Color.blurple())
        embed.add_field(name="🧑‍🤝‍🧑 Jogadores na zona", value=str(player_count), inline=True)
        embed.add_field(name="🔒 Permanente", value=str(bool(zone.get("permanent"))), inline=True)

        if event:
            reward = json.loads(event["reward"]) if event.get("reward") else {}
            is_worldboss = event["type"] == 2
            embed.add_field(name="⚠️ Evento ativo", value=("WorldBoss" if is_worldboss else "Normal"), inline=False)
            embed.add_field(name="🎁 Recompensas (preview)", value=f"Gold: {reward.get('gold',0)} • XP: {reward.get('xp',0)}", inline=False)
        else:
            embed.add_field(name="⚠️ Evento ativo", value="Nenhum evento ativo no momento", inline=False)

        await interaction.followup.send(embed=embed)

    async def destroy_zone_after_worldboss(self, zone_id: int, channel: discord.TextChannel):
        zone = await self.bot.db.fetchrow("SELECT permanent FROM zone WHERE zone_id = $1", zone_id)
        if zone and zone["permanent"]:
            await channel.send("🕳️ O WorldBoss caiu, mas a zona é permanente e não colapsará.")
            return

        await asyncio.sleep(60)
        await self.bot.db.execute("UPDATE users SET zona_id = $1 WHERE zona_id = $2", 0, zone_id)
        await self.bot.db.execute("DELETE FROM events WHERE zone_id = $1", zone_id)
        await channel.send("🕳️ **A zona colapsou.** Todos foram puxados para a capital.")

async def setup(bot: commands.Bot):
    cog = RPGBattle(bot)
    await bot.add_cog(cog)

    # Pega o cog principal RPG
    main = bot.get_cog("RPG")

    # Se o RPG cog existir e tiver o grupo 'rpg', adiciona battle como subgrupo
    if main and hasattr(main, 'rpg'):
        # remove possível registro top-level criado automaticamente durante add_cog
        try:
            bot.tree.remove_command(cog.rpg_battle.name)
        except Exception:
            pass

        try:
            main.rpg.add_command(cog.rpg_battle)
        except Exception:
            # fallback: registrar direto no tree caso a adição como subgrupo falhe
            try:
                bot.tree.add_command(cog.rpg_battle)
            except discord.app_commands.errors.CommandAlreadyRegistered:
                pass
    else:
        # Se não existir, adiciona diretamente no tree
        try:
            bot.tree.add_command(cog.rpg_battle)
        except discord.app_commands.errors.CommandAlreadyRegistered:
            pass
