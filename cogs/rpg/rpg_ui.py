import discord
from discord import ui
from discord.ext import commands
import random
import asyncio
from typing import List, Dict, Optional

class BattleView(ui.View):
    def __init__(self, cog, user_id: int, player: dict, enemy: dict, reward: dict, event_id: int, is_worldboss: bool, zone_id: int, timeout: float = 300.0):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.user_id = user_id
        self.player = player
        self.enemy = enemy
        # Ensure enemy has max_hp
        if 'max_hp' not in self.enemy:
            self.enemy['max_hp'] = self.enemy['hp']
        self.reward = reward
        self.event_id = event_id
        self.is_worldboss = is_worldboss
        self.zone_id = zone_id
        
        # Truncate enemy name for initial log
        enemy_name = enemy['name']
        if len(enemy_name) > 50:
            enemy_name = enemy_name[:47] + "..."
        
        self.log = [f"⚔️ Combate iniciado contra {enemy_name}", f"❤️ HP Inicial: {player['hp']}/{player['max_hp']}"]
        self.turn = 1
        self.player_defending = False
        self.enemy_defending = False

    def make_embed(self):
        # Calculate HP percentages for visual bars
        player_hp_percent = (self.player['hp'] / self.player['max_hp']) * 100
        enemy_max_hp = self.enemy.get('max_hp', self.enemy['hp'])
        enemy_hp_percent = (self.enemy['hp'] / enemy_max_hp) * 100
        
        # HP bars
        player_bar = self._make_hp_bar(player_hp_percent)
        enemy_bar = self._make_hp_bar(enemy_hp_percent)
        
        # Truncate enemy name if too long
        enemy_name = self.enemy['name']
        if len(enemy_name) > 100:
            enemy_name = enemy_name[:97] + "..."
        
        embed = discord.Embed(
            title=f"⚔️ Batalha: {enemy_name}",
            description=f"**Turno {self.turn}**",
            color=discord.Color.red() if self.is_worldboss else discord.Color.blurple()
        )
        
        # Player field - ensure it's under 1024 chars
        player_value = f"{player_bar}\n❤️ **{self.player['hp']}/{self.player['max_hp']}** HP"
        if len(player_value) > 1020:
            player_value = player_value[:1017] + "..."
        
        embed.add_field(
            name="👤 Você",
            value=player_value,
            inline=True
        )
        
        # Enemy field - ensure it's under 1024 chars
        enemy_value = f"{enemy_bar}\n💔 **{self.enemy['hp']}/{enemy_max_hp}** HP"
        if len(enemy_value) > 1020:
            enemy_value = enemy_value[:1017] + "..."
        
        embed.add_field(
            name=f"{'💀 WorldBoss' if self.is_worldboss else '👹 Inimigo'}",
            value=enemy_value,
            inline=True
        )
        
        # Latest turn info - truncate if too long
        last_turn = self.log[-1] if self.log else "Aguardando ação..."
        if len(last_turn) > 1000:
            last_turn = last_turn[:997] + "..."
        embed.add_field(name="⚡ Último Turno", value=last_turn, inline=False)
        
        status = []
        if self.player_defending:
            status.append("🛡️ Defendendo")
        if self.enemy_defending:
            status.append("😈 Inimigo Defendendo")
        
        if status:
            status_value = ", ".join(status)
            if len(status_value) > 1020:
                status_value = status_value[:1017] + "..."
            embed.add_field(name="📊 Status", value=status_value, inline=False)
        
        return embed
    
    def _make_hp_bar(self, percent: float) -> str:
        """Creates a visual HP bar"""
        bars = 10
        filled = int((percent / 100) * bars)
        if percent > 70:
            emoji = "🟩"
        elif percent > 30:
            emoji = "🟨"
        else:
            emoji = "🟥"
        return emoji * filled + "⬛" * (bars - filled)

    async def enemy_action(self):
        choice = random.choices(["attack", "defend", "attack"], weights=[60,20,20])[0]
        
        # Truncate enemy name for log entries
        enemy_name = self.enemy['name']
        if len(enemy_name) > 50:
            enemy_name = enemy_name[:47] + "..."
        
        if choice == "defend":
            self.enemy_defending = True
            self.log.append(f"🛡️ Turno {self.turn}: {enemy_name} se prepara para defender.")
        else:
            dmg = max(self.enemy['atk'] - (self.player['defense'] + (10 if self.player_defending else 0)), 0)
            if self.enemy_defending:
                dmg = max(dmg - 5, 0)
            self.player['hp'] -= dmg
            self.log.append(f"🩸 Turno {self.turn}: {enemy_name} ataca! -`{dmg}` HP")
        self.player_defending = False
        self.enemy_defending = False
        
        # Keep log manageable - only last 50 entries
        if len(self.log) > 50:
            self.log = self.log[-50:]

    @ui.button(label="⚔️ Atacar", style=discord.ButtonStyle.primary, custom_id="rpg_attack")
    async def attack_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Isso não é seu combate.", ephemeral=True)
        
        # Player attack
        dmg = max(self.player['atk'] - (self.enemy['defense'] + (5 if self.enemy_defending else 0)), 0)
        crit = random.random() < 0.15  # 15% crit chance
        if crit:
            dmg = int(dmg * 1.5)
            self.log.append(f"💥 **CRÍTICO!** Turno {self.turn}: Você causa `{dmg}` de dano!")
        else:
            self.log.append(f"⚔️ Turno {self.turn}: Você ataca e causa `{dmg}` de dano.")
        
        # Keep log manageable
        if len(self.log) > 50:
            self.log = self.log[-50:]
        
        self.enemy['hp'] -= dmg
        
        # Update message with player action
        await interaction.response.edit_message(embed=self.make_embed(), view=self)
        
        # Check if enemy died
        if self.enemy['hp'] <= 0:
            await asyncio.sleep(0.5)  # Brief pause before victory
            await self.end_battle(interaction)
            return
        
        # Enemy turn
        await asyncio.sleep(1)  # Pause before enemy action
        self.turn += 1
        await self.enemy_action()
        
        # Check if player died
        if self.player['hp'] <= 0:
            await interaction.edit_original_response(embed=self.make_embed(), view=self)
            await asyncio.sleep(0.5)
            await self.end_battle(interaction)
            return
        
        # Update with enemy action
        await interaction.edit_original_response(embed=self.make_embed(), view=self)

    @ui.button(label="🛡️ Defender", style=discord.ButtonStyle.secondary, custom_id="rpg_defend")
    async def defend_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Isso não é seu combate.", ephemeral=True)
        self.player_defending = True
        self.log.append(f"🛡️ Turno {self.turn}: Você assume postura defensiva.")
        
        # Keep log manageable
        if len(self.log) > 50:
            self.log = self.log[-50:]
        
        # Update message
        await interaction.response.edit_message(embed=self.make_embed(), view=self)
        
        # Enemy turn
        await asyncio.sleep(1)
        self.turn += 1
        await self.enemy_action()
        
        if self.player['hp'] <= 0:
            await interaction.edit_original_response(embed=self.make_embed(), view=self)
            await asyncio.sleep(0.5)
            await self.end_battle(interaction)
            return
        
        await interaction.edit_original_response(embed=self.make_embed(), view=self)

    @ui.button(label="💚 Usar Poção", style=discord.ButtonStyle.success, custom_id="rpg_potion")
    async def potion_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Isso não é seu combate.", ephemeral=True)
        heal = min(100, self.player['max_hp'] - self.player['hp'])
        if heal <= 0:
            self.log.append(f"💤 Turno {self.turn}: Você já está com HP máximo.")
        else:
            self.player['hp'] += heal
            self.log.append(f"💚 Turno {self.turn}: Poção restaura `{heal}` HP!")
        
        # Update message
        await interaction.response.edit_message(embed=self.make_embed(), view=self)
        
        # Enemy turn
        await asyncio.sleep(1)
        self.turn += 1
        await self.enemy_action()
        
        if self.player['hp'] <= 0:
            await interaction.edit_original_response(embed=self.make_embed(), view=self)
            await asyncio.sleep(0.5)
            await self.end_battle(interaction)
            return
        
        await interaction.edit_original_response(embed=self.make_embed(), view=self)

    @ui.button(label="🔄 Fugir", style=discord.ButtonStyle.danger, custom_id="rpg_flee")
    async def flee_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Isso não é seu combate.", ephemeral=True)
        if random.random() < 0.6:
            self.log.append("🏃‍♂️ Você foge com sucesso!")
            embed = discord.Embed(title="🏃 Fuga Bem Sucedida", description="Você escapou do combate.")
            await interaction.response.edit_message(embed=embed, view=None)
            return
        else:
            self.log.append("❌ Fuga falhou!")
            self.turn += 1
            await self.enemy_action()
            if self.player['hp'] <= 0:
                await self.end_battle(interaction)
                return
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    async def end_battle(self, interaction: discord.Interaction):
        if self.player['hp'] <= 0:
            await self.cog.bot.db.execute("UPDATE users SET current_hp = 0 WHERE discord_id = $1", self.user_id)
            self.log.append("☠️ Você foi derrotado pelo Abismo...")
            embed = discord.Embed(
                title="☠️ Derrota",
                description="*As trevas te consomem...*\n\n" + "\n".join(self.log[-8:]),
                color=discord.Color.dark_red()
            )
            try:
                await interaction.edit_original_response(embed=embed, view=None)
            except:
                await interaction.response.edit_message(embed=embed, view=None)
            # send revive options separately
            revive_view = ReviveView(self.cog, self.user_id, self.player['max_hp'])
            await interaction.followup.send("Você pode tentar reviver usando uma poção:", view=revive_view, ephemeral=True)
            return
        
        # Victory - deactivate event and update player
        await self.cog.bot.db.execute("UPDATE events SET active = FALSE WHERE id = $1", self.event_id)
        await self.cog.bot.db.execute("UPDATE users SET current_hp = $1 WHERE discord_id = $2", self.player['hp'], self.user_id)
        
        gold = self.reward.get('gold', 0)
        xp = self.reward.get('xp', 0)
        
        if gold:
            await self.cog.bot.db.execute(
                "INSERT INTO economy (user_id, gold) VALUES ($1,$2) ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2",
                self.user_id, gold
            )
        if xp:
            await self.cog.give_exp(self.user_id, xp)
        
        # Generate loot based on zone tier for WorldBoss
        items = self.reward.get('items', [])
        if self.is_worldboss and not items:
            # Get zone tier
            zone_tier = await self.cog.bot.db.fetchval(
                "SELECT tier FROM zone WHERE zone_id = $1",
                self.zone_id
            )
            if zone_tier:
                items = await self._generate_worldboss_loot(zone_tier)
                self.reward['items'] = items
        
        embed = discord.Embed(
            title="🏆 Vitória Épica!" if self.is_worldboss else "🏆 Vitória!",
            description="*Você prevaleceu contra as trevas!*\n\n" + "\n".join(self.log[-8:]),
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Gold", value=f"**{gold:,}**", inline=True)
        embed.add_field(name="📜 XP", value=f"**{xp:,}**", inline=True)
        embed.add_field(name="❤️ HP Restante", value=f"**{self.player['hp']}/{self.player['max_hp']}**", inline=True)
        
        if items:
            rows = []
            try:
                rows = await self.cog.bot.db.fetch(
                    "SELECT id, name, tier, subtier FROM items WHERE id = ANY($1::int[])",
                    items
                )
            except Exception:
                rows = []
            item_list = "\n".join(f"• **{r['name']}** T{r['tier']}.{r['subtier']} `(ID {r['id']})`" for r in rows) if rows else "—"
            embed.add_field(name="🎁 Loot Obtido", value=item_list, inline=False)
        
        try:
            await interaction.edit_original_response(embed=embed, view=None)
        except:
            await interaction.response.edit_message(embed=embed, view=None)
        
        if items:
            loot_view = LootView(self.cog, self.user_id, items)
            await interaction.followup.send("🎁 Selecione como deseja recolher o saque:", view=loot_view, ephemeral=True)
    
    async def _generate_worldboss_loot(self, zone_tier: int) -> list:
        """Generate loot based on zone tier (e.g., T8 zone drops up to T8.4 items)"""
        try:
            # Number of items to drop (2-4 for worldboss)
            num_items = random.randint(2, 4)
            
            # Get random items up to zone_tier with subtier up to 4
            items = await self.cog.bot.db.fetch(
                """
                SELECT id FROM items
                WHERE tier <= $1 AND subtier <= 4
                ORDER BY RANDOM()
                LIMIT $2
                """,
                zone_tier, num_items
            )
            
            return [item['id'] for item in items]
        except Exception as e:
            print(f"Error generating worldboss loot: {e}")
            return []

__all__ = ["BattleView", "LootView", "ReviveView"]


class RPGUI(commands.Cog):
    """Cog que serve como ponto de entrada para as Views do RPG."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    cog = RPGUI(bot)
    await bot.add_cog(cog)

class LootView(ui.View):
    def __init__(self, cog, user_id: int, items: list):
        super().__init__(timeout=120.0)
        self.cog = cog
        self.user_id = user_id
        self.items = items
        options = [discord.SelectOption(label=f"Item {iid}", value=str(iid)) for iid in items]
        if options:
            self.add_item(ui.Select(placeholder="Escolher item...", min_values=1, max_values=1, options=options, custom_id="loot_select"))

    @ui.button(label="Pegar todos", style=discord.ButtonStyle.primary, custom_id="loot_take_all")
    async def take_all(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Esse saque não é seu.", ephemeral=True)
        for iid in self.items:
            await self.cog.bot.db.execute(
                "INSERT INTO inventory (user_id, item_id, tier, quantity) VALUES ($1,$2,1,1) ON CONFLICT (user_id,item_id,tier) DO UPDATE SET quantity = inventory.quantity + 1",
                self.user_id, iid
            )
        await interaction.response.edit_message(content="🎉 Você pegou todo o saque!", embed=None, view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @ui.select(custom_id="loot_select")
    async def select_item(self, interaction: discord.Interaction, select: ui.Select):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Esse saque não é seu.", ephemeral=True)
        iid = int(select.values[0])
        await self.cog.bot.db.execute(
            "INSERT INTO inventory (user_id, item_id, tier, quantity) VALUES ($1,$2,1,1) ON CONFLICT (user_id,item_id,tier) DO UPDATE SET quantity = inventory.quantity + 1",
            self.user_id, iid
        )
        self.items = [i for i in self.items if i != iid]
        await interaction.response.send_message(f"🧾 Você pegou o item `{iid}`.", ephemeral=True)
        if not self.items:
            await interaction.edit_original_response(content="Todos os itens foram pegos.", view=None)
        else:
            opts = [discord.SelectOption(label=f"Item {i}", value=str(i)) for i in self.items]
            for child in list(self.children):
                if isinstance(child, ui.Select):
                    child.options = opts
                    break

class ReviveView(ui.View):
    def __init__(self, cog, user_id: int, max_hp: int):
        super().__init__(timeout=60.0)
        self.cog = cog
        self.user_id = user_id
        self.max_hp = max_hp

    @ui.button(label="Sim", style=discord.ButtonStyle.success, custom_id="revive_yes")
    async def yes(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Isso não é para você.", ephemeral=True)
        new_hp = int(self.max_hp * random.uniform(0.5, 0.75))
        await self.cog.bot.db.execute("UPDATE users SET current_hp = $1 WHERE discord_id = $2", new_hp, self.user_id)
        await interaction.response.send_message(f"✨ Você reviveu com {new_hp} HP.", ephemeral=True)

    @ui.button(label="Não", style=discord.ButtonStyle.danger, custom_id="revive_no")
    async def no(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Isso não é para você.", ephemeral=True)
        await self.cog.bot.db.execute("UPDATE users SET current_hp = 0 WHERE discord_id = $1", self.user_id)
        await interaction.response.send_message("☠️ Morte definitiva.", ephemeral=True)
