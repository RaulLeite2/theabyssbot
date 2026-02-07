import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord import ui
import datetime
import random

CAPITAL_ZONE_ID = 0  # Depth of Darkness

# =========================
# HELPERS
# =========================
async def get_user_zone(bot, user_id: int):
    return await bot.db.fetchrow(
        """
        SELECT z.zone_id, z.nome, z.is_hub, z.is_hideout,
               z.owner_guild, z.owner_alliance
        FROM users u
        JOIN zone z ON z.zone_id = u.zona_id
        WHERE u.discord_id = $1
        """,
        user_id
    )


async def require_capital(interaction: discord.Interaction, zone):
    if not zone:
        await interaction.followup.send(
            "❌ Você não está em nenhuma zona do mundo.",
            ephemeral=True
        )
        return False

    if not zone["is_hub"]:
        await interaction.followup.send(
            f"🏛️ Esse comando só pode ser usado em um **Hub (Cidade)**. Você está em **{zone['nome']}**."
            f"\n\n💡 Use `/rpg hub` para ir para a cidade mais próxima.",
            ephemeral=True
        )
        return False

    return True


# =========================
# SHOP VIEW
# =========================
class ShopView(ui.View):
    def __init__(self, bot, items):
        super().__init__(timeout=300)
        self.bot = bot
        for item in items:
            button = ui.Button(label=item['name'], custom_id=str(item['id']))
            button.callback = self.buy_callback
            self.add_item(button)

    async def buy_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        item_id = int(interaction.data['custom_id'])

        zone = await get_user_zone(self.bot, interaction.user.id)
        if not await require_capital(interaction, zone):
            return

        item = await self.bot.db.fetchrow(
            "SELECT price FROM shop WHERE item_id = $1",
            item_id
        )

        if not item:
            return await interaction.followup.send(
                "❌ Esse item não está à venda na Capital.",
                ephemeral=True
            )

        total_price = item["price"]

        gold = await self.bot.db.fetchval(
            "SELECT gold FROM economy WHERE user_id = $1",
            interaction.user.id
        )

        if gold is None or gold < total_price:
            return await interaction.followup.send(
                "💸 Ouro insuficiente.",
                ephemeral=True
            )

        item_name = await self.bot.db.fetchval(
            "SELECT name FROM items WHERE id = $1",
            item_id
        )

        await self.bot.db.execute(
            "UPDATE economy SET gold = gold - $1 WHERE user_id = $2",
            total_price,
            interaction.user.id
        )

        await self.bot.db.execute(
            """
            INSERT INTO inventory (user_id, item_id, tier, quantity)
            VALUES ($1, $2, $3, 1)
            ON CONFLICT (user_id, item_id, tier)
            DO UPDATE SET quantity = inventory.quantity + 1
            """,
            interaction.user.id,
            item_id,
            1
        )

        # Interação com NPC Lysandra (Mercadora)
        npc_cog = self.bot.get_cog("NPCSystem")
        if npc_cog:
            # Adiciona reputação
            rep_gain = max(1, total_price // 100)  # 1 ponto a cada 100 gold
            await npc_cog.add_reputation(interaction.user.id, "lysandra", rep_gain, total_price)
            
            # Busca reputação atual
            rep_data = await npc_cog.get_reputation(interaction.user.id, "lysandra")
            
            # Diálogo aleatório da Lysandra
            greeting = random.choice([
                "Prazer em fazer negócios com você! ✨",
                "Obrigada pela preferência, aventureiro!",
                "Excelente escolha! Volte sempre!",
                "Que a sorte esteja com você nas suas jornadas!"
            ])
            
            # Adicionar Fama Comercial
            fame_amount = max(1, total_price // 50)  # 1 ponto a cada 50 gold
            rpg_cog = self.bot.get_cog("RPG")
            if rpg_cog and hasattr(rpg_cog, 'add_fame'):
                await rpg_cog.add_fame(
                    interaction.user.id, 
                    'trading', 
                    fame_amount, 
                    f"Comprou {item_name} no shop"
                )
            
            await interaction.followup.send(
                f"🛒 Comprou **1x {item_name}** por 💰 `{total_price}`\n\n"
                f"💬 **Lysandra:** *\"{greeting}\"*\n"
                f"⭐ Reputação com Lysandra: **{rep_data['reputation']}** pontos (+{rep_gain})\n"
                f"🏆 Fama Comercial: +{fame_amount} pontos",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"🛒 Comprou **1x {item_name}** por 💰 `{total_price}`",
                ephemeral=True
            )


# =========================
# HOSHOP VIEW
# =========================
class HoShopView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        # Kit de Construção de Esconderijo - ID 2210
        button1 = ui.Button(label="Kit de Construção de Esconderijo", custom_id="2210")
        button1.callback = self.hobuy_callback
        self.add_item(button1)
        # Estrutura Básica de Hideout - ID 7812
        button2 = ui.Button(label="Estrutura Básica de Hideout", custom_id="7812")
        button2.callback = self.hobuy_callback
        self.add_item(button2)

    async def hobuy_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        item_id = int(interaction.data['custom_id'])

        zone = await get_user_zone(self.bot, interaction.user.id)
        if not await require_capital(interaction, zone):
            return

        member = await self.bot.db.fetchrow(
            "SELECT guild_id FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )
        if not member:
            return await interaction.followup.send(
                "🚫 Você não pertence a nenhuma guilda.",
                ephemeral=True
            )

        if item_id == 2210:
            price = 10_000_000
        elif item_id == 7812:
            price = 130_000
        else:
            return await interaction.followup.send(
                "❌ Esse item não é vendido no Hideout.",
                ephemeral=True
            )

        item = await self.bot.db.fetchrow(
            "SELECT id, name, tier FROM items WHERE id = $1",
            item_id
        )
        if not item:
            return await interaction.followup.send(
                "❌ Item não encontrado na base de dados.",
                ephemeral=True
            )

        total_price = price

        gold = await self.bot.db.fetchval(
            "SELECT gold FROM economy WHERE user_id = $1",
            interaction.user.id
        )
        if gold < total_price:
            return await interaction.followup.send(
                "💸 Ouro insuficiente.",
                ephemeral=True
            )

        await self.bot.db.execute(
            "UPDATE economy SET gold = gold - $1 WHERE user_id = $2",
            total_price,
            interaction.user.id
        )

        await self.bot.db.execute(
            """
            INSERT INTO inventory (user_id, item_id, tier, quantity)
            VALUES ($1, $2, $3, 1)
            ON CONFLICT (user_id, item_id, tier)
            DO UPDATE SET quantity = inventory.quantity + 1
            """,
            interaction.user.id,
            item_id,
            item["tier"]
        )

        # Interação com NPC Gorak (Ferreiro do Esconderijo)
        npc_cog = self.bot.get_cog("NPCSystem")
        if npc_cog:
            # Adiciona reputação
            rep_gain = max(5, total_price // 50000)  # Mais reputação por itens caros
            await npc_cog.add_reputation(interaction.user.id, "gorak", rep_gain, total_price)
            
            # Busca reputação atual
            rep_data = await npc_cog.get_reputation(interaction.user.id, "gorak")
            
            # Diálogo aleatório do Gorak
            greeting = random.choice([
                "HAHA! Uma ótima escolha, aventureiro! Forge bem! 🔨",
                "Isso vai te servir bem nas batalhas! Volte sempre!",
                "Minhas forjas nunca falham! Use com orgulho!",
                "Que suas armas nunca percam o gume! ⚔️"
            ])
            
            await interaction.followup.send(
                f"🏰 Comprou **1x {item['name']}** por 💰 `{total_price:,}` Gold\n\n"
                f"💬 **Gorak:** *\"{greeting}\"*\n"
                f"⭐ Reputação com Gorak: **{rep_data['reputation']}** pontos (+{rep_gain})",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"🏰 Comprou **1x {item['name']}** por 💰 `{total_price:,}` Gold",
                ephemeral=True
            )


# =========================
# SHOP COG
# =========================
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_shop.start()

    # =========================
    # RESET DO SHOP (1 HORA)
    # =========================
    @tasks.loop(hours=1)
    async def reset_shop(self):
        await self.bot.db.execute("DELETE FROM shop")

        items = await self.bot.db.fetch(
            """
            SELECT id, tier, subtier
            FROM items
            WHERE tier <= 5
            ORDER BY RANDOM()
            LIMIT 5
            """
        )

        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        for item in items:
            price = (item["tier"] * 1000) + (item["subtier"] * 500)

            await self.bot.db.execute(
                """
                INSERT INTO shop (item_id, price, expires_at)
                VALUES ($1, $2, $3)
                """,
                item["id"],
                price,
                expires
            )

    # =========================
    # /SHOP
    # =========================
    @app_commands.command(name="shop", description="Mostra os itens à venda na capital")
    async def shop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        zone = await get_user_zone(self.bot, interaction.user.id)
        if not await require_capital(interaction, zone):
            return

        rows = await self.bot.db.fetch(
            """
            SELECT i.id, i.name, i.tier, i.subtier, i.slot_id, s.price
            FROM shop s
            JOIN items i ON i.id = s.item_id
            ORDER BY i.tier DESC, i.subtier DESC
            """
        )

        if not rows:
            return await interaction.followup.send(
                "🛒 A capital está silenciosa… o shop reseta em breve.",
                ephemeral=True
            )

        desc = ""
        for r in rows:
            desc += (
                f"🧿 **{r['name']}**\n"
                f"T{r['tier']}.{r['subtier']} | Slot `{r['slot_id']}`\n"
                f"💰 {r['price']}\n\n"
            )

        embed = discord.Embed(
            title="🛒 Shop da Capital — Depth of Darkness",
            description=desc,
            color=0x2ecc71
        )

        view = ShopView(self.bot, rows)
        await interaction.followup.send(embed=embed, view=view)



    # =========================
    # /HOSHOP
    # =========================
    @app_commands.command(
        name="hoshop",
        description="Loja do Hideout (na Capital)"
    )
    async def hoshop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        zone = await get_user_zone(self.bot, interaction.user.id)
        if not await require_capital(interaction, zone):
            return

        member = await self.bot.db.fetchrow(
            "SELECT guild_id FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )
        if not member:
            return await interaction.followup.send(
                "🚫 Você não pertence a nenhuma guilda.",
                ephemeral=True
            )

        desc = (
            "🧱 **Kit de Construção de Esconderijo**\n"
            "ID: `2210`\n"
            "💰 10.000.000 Gold\n\n"
            "🏗️ **Estrutura Básica de Hideout**\n"
            "ID: `7812`\n"
            "💰 130.000 Gold\n"
        )

        embed = discord.Embed(
            title="🏰 Loja do Hideout — Capital",
            description=desc,
            color=0x9b59b6
        )

        view = HoShopView(self.bot)
        await interaction.followup.send(
            embed=embed,
            view=view,
            ephemeral=True
        )





async def setup(bot):
    await bot.add_cog(Shop(bot))
