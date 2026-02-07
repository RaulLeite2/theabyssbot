import discord
from discord.ext import commands, tasks
from discord import app_commands, ui
import datetime
import asyncio
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


async def finalize_expired_auctions(bot):
    """Finalize auctions that have ended."""
    expired_auctions = await bot.db.fetch(
        "SELECT * FROM auction WHERE status = 'active' AND ends_at <= NOW()"
    )

    for auction in expired_auctions:
        async with bot.db.acquire() as conn:
            async with conn.transaction():
                if auction['highest_bidder_id']:
                    # Transfer item to winner
                    item = await conn.fetchrow("SELECT tier FROM items WHERE id = $1", auction['item_id'])
                    await conn.execute(
                        """
                        INSERT INTO inventory (user_id, item_id, tier, quantity)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (user_id, item_id, tier)
                        DO UPDATE SET quantity = inventory.quantity + $4
                        """,
                        auction['highest_bidder_id'],
                        auction['item_id'],
                        item['tier'],
                        auction['amount']
                    )

                    # Transfer gold to seller
                    await conn.execute(
                        "UPDATE economy SET gold = gold + $1 WHERE user_id = $2",
                        auction['price'],
                        auction['seller_id']
                    )

                # Mark auction as ended
                await conn.execute(
                    "UPDATE auction SET status = 'ended' WHERE auction_id = $1",
                    auction['auction_id']
                )


# =========================
# MODALS
# =========================
class BidModal(ui.Modal, title="Dar Lance no Leilão"):
    bid_amount = ui.TextInput(label="Valor do Lance", placeholder="Digite o valor do lance (inteiro positivo)", required=True)

    def __init__(self, auction_id):
        super().__init__()
        self.auction_id = auction_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bid_amount = int(self.bid_amount.value)
            if bid_amount <= 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError:
            return await interaction.response.send_message(
                "❌ Valor do lance deve ser um inteiro positivo.",
                ephemeral=True
            )

        async with interaction.client.db.acquire() as conn:
            async with conn.transaction():
                # Check if auction exists and is active
                auction = await conn.fetchrow(
                    "SELECT seller_id, item_id, price, highest_bidder_id, ends_at, status FROM auction WHERE auction_id = $1",
                    self.auction_id
                )

                if not auction or auction['status'] != 'active':
                    return await interaction.response.send_message(
                        "❌ Leilão não encontrado ou inativo.",
                        ephemeral=True
                    )

                if auction['ends_at'] <= datetime.datetime.utcnow():
                    return await interaction.response.send_message(
                        "❌ Este leilão já expirou.",
                        ephemeral=True
                    )

                if bid_amount <= auction['price']:
                    return await interaction.response.send_message(
                        f"❌ Lance deve ser maior que o preço atual: 💰 {auction['price']}.",
                        ephemeral=True
                    )

                if interaction.user.id == auction['seller_id']:
                    return await interaction.response.send_message(
                        "❌ Você não pode dar lance no seu próprio leilão.",
                        ephemeral=True
                    )

                # Check if user has enough gold
                gold = await conn.fetchval(
                    "SELECT gold FROM economy WHERE user_id = $1",
                    interaction.user.id
                )

                if gold is None or gold < bid_amount:
                    return await interaction.response.send_message(
                        "💸 Ouro insuficiente.",
                        ephemeral=True
                    )

                # Debit new bidder
                await conn.execute(
                    "UPDATE economy SET gold = gold - $1 WHERE user_id = $2",
                    bid_amount,
                    interaction.user.id
                )

                # Refund previous bidder if exists
                if auction['highest_bidder_id']:
                    await conn.execute(
                        "UPDATE economy SET gold = gold + $1 WHERE user_id = $2",
                        auction['price'],
                        auction['highest_bidder_id']
                    )

                # Update auction
                await conn.execute(
                    "UPDATE auction SET price = $1, highest_bidder_id = $2 WHERE auction_id = $3",
                    bid_amount,
                    interaction.user.id,
                    self.auction_id
                )

        # Interação com NPC Raven (Mercado Negro/Leilões)
        npc_cog = interaction.client.get_cog("NPCSystem")
        if npc_cog:
            # Adiciona reputação
            rep_gain = max(1, bid_amount // 1000)  # 1 ponto a cada 1000 gold
            await npc_cog.add_reputation(interaction.user.id, "raven", rep_gain, bid_amount)
            
            # Busca reputação atual
            rep_data = await npc_cog.get_reputation(interaction.user.id, "raven")
            
            # Diálogo aleatório da Raven
            greeting = random.choice([
                "Hehe... Gosto de pessoas que sabem o valor das coisas... 😏",
                "Um lance ousado! Interessante...",
                "Sempre é bom fazer negócios com alguém que entende... 🌙",
                "As sombras protegem quem sabe negociar bem..."
            ])
            
            # Adicionar Fama Comercial
            fame_amount = max(1, bid_amount // 500)  # 1 ponto a cada 500 gold
            rpg_cog = interaction.client.get_cog("RPG")
            if rpg_cog and hasattr(rpg_cog, 'add_fame'):
                await rpg_cog.add_fame(
                    interaction.user.id, 
                    'trading', 
                    fame_amount, 
                    f"Lance de {bid_amount} no leilão"
                )
            
            await interaction.response.send_message(
                f"🏺 Lance dado no leilão `{self.auction_id}` por 💰 `{bid_amount}`\n\n"
                f"💬 **Raven:** *\"{greeting}\"*\n"
                f"⭐ Reputação com Raven: **{rep_data['reputation']}** pontos (+{rep_gain})\n"
                f"🏆 Fama Comercial: +{fame_amount} pontos",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"🏺 Lance dado no leilão `{self.auction_id}` por 💰 `{bid_amount}`",
                ephemeral=True
            )


class SearchModal(ui.Modal, title="Procurar Leilão"):
    search_term = ui.TextInput(label="Nome do Item", placeholder="Digite o nome do item para buscar", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        search_term = self.search_term.value.strip()

        # Search by item name only
        auction = await interaction.client.db.fetchrow(
            """
            SELECT a.auction_id, i.name, i.tier, a.amount, a.price, a.ends_at, a.status, a.seller_id
            FROM auction a
            JOIN items i ON i.id = a.item_id
            WHERE LOWER(i.name) LIKE LOWER($1) AND a.status = 'active'
            ORDER BY a.price DESC
            LIMIT 1
            """,
            f"%{search_term}%"
        )

        if not auction:
            return await interaction.response.send_message(
                "❌ Nenhum leilão ativo encontrado com esse nome de item.",
                ephemeral=True
            )

        # Check if auction is still active
        if auction['ends_at'] <= datetime.datetime.utcnow():
            return await interaction.response.send_message(
                "❌ Este leilão já expirou.",
                ephemeral=True
            )

        # Display the found auction
        time_left = auction['ends_at'] - datetime.datetime.utcnow()
        hours, remainder = divmod(int(time_left.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{hours}h {minutes}m" if time_left.total_seconds() > 0 else "Expirado"

        embed = discord.Embed(
            title=f"🏺 Leilão Encontrado — {auction['name']} (T{auction['tier']})",
            color=0xf1c40f
        )

        embed.add_field(
            name="Detalhes",
            value=f"Quantidade: {auction['amount']}\nPreço Atual: 💰 {auction['price']}\nTempo Restante: ⏰ {time_str}",
            inline=False
        )

        view = ui.View()
        view.add_item(BidButton(auction['auction_id'], "Dar Lance"))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class SellModal(ui.Modal, title="Vender Item no Leilão"):
    item_name = ui.TextInput(label="Nome do Item", placeholder="Digite o nome do item", required=True)
    amount = ui.TextInput(label="Quantidade", placeholder="Digite a quantidade (inteiro positivo)", required=True)
    starting_price = ui.TextInput(label="Preço Inicial", placeholder="Digite o preço inicial (inteiro positivo)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            item_name = self.item_name.value.strip()
            amount = int(self.amount.value)
            starting_price = int(self.starting_price.value)
            if amount <= 0 or starting_price <= 0:
                raise ValueError("Valores devem ser positivos")
        except ValueError:
            return await interaction.response.send_message(
                "❌ Quantidade e preço devem ser inteiros positivos.",
                ephemeral=True
            )

        zone = await get_user_zone(interaction.client, interaction.user.id)
        if not await require_capital(interaction, zone):
            return

        # Resolve item name to ID
        item = await interaction.client.db.fetchrow("SELECT id, tier FROM items WHERE LOWER(name) = LOWER($1)", item_name)
        if not item:
            return await interaction.response.send_message(
                "❌ Item não encontrado.",
                ephemeral=True
            )

        item_id = item['id']

        # Check if user has the item
        inventory = await interaction.client.db.fetchrow(
            "SELECT quantity FROM inventory WHERE user_id = $1 AND item_id = $2 AND tier = $3",
            interaction.user.id,
            item_id,
            item['tier']
        )

        if not inventory or inventory["quantity"] < amount:
            return await interaction.response.send_message(
                "❌ Você não possui essa quantidade do item.",
                ephemeral=True
            )

        # Remove item from inventory
        await interaction.client.db.execute(
            "UPDATE inventory SET quantity = quantity - $1 WHERE user_id = $2 AND item_id = $3 AND tier = $4",
            amount,
            interaction.user.id,
            item_id,
            item['tier']
        )

        # Add to auction (24 hours duration)
        ends_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        await interaction.client.db.execute(
            """
            INSERT INTO auction (seller_id, item_id, amount, price, ends_at)
            VALUES ($1, $2, $3, $4, $5)
            """,
            interaction.user.id,
            item_id,
            amount,
            starting_price,
            ends_at
        )

        await interaction.response.send_message(
            f"🏺 Item '{item_name}' colocado no leilão com preço inicial 💰 `{starting_price}`. Expira em 24 horas.",
            ephemeral=True
        )


# =========================
# VIEWS
# =========================
class AuctionView(ui.View):
    def __init__(self, auctions):
        super().__init__(timeout=300)
        self.auctions = auctions

        # Add bid buttons for each auction (max 5)
        for i, auction in enumerate(auctions[:5]):
            self.add_item(BidButton(auction['auction_id'], f"Dar Lance #{i+1}"))

        # Add search button
        self.add_item(SearchButton())


class BidButton(ui.Button):
    def __init__(self, auction_id, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.auction_id = auction_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BidModal(self.auction_id))


class SearchButton(ui.Button):
    def __init__(self):
        super().__init__(label="🔍 Procurar Leilão", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchModal())


# =========================
# AUCTION COG
# =========================
class Auction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.finalize_auctions.start()

    @tasks.loop(minutes=5)
    async def finalize_auctions(self):
        await finalize_expired_auctions(self.bot)

    # =========================
    # AUCTION GROUP
    # =========================
    auction_group = app_commands.Group(name="auction", description="Comandos relacionados ao leilão da capital")

    # =========================
    # /AUCTION LIST
    # =========================
    @auction_group.command(name="list", description="Mostra os itens no leilão da capital")
    async def auction_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        zone = await get_user_zone(self.bot, interaction.user.id)
        if not await require_capital(interaction, zone):
            return

        rows = await self.bot.db.fetch(
            """
            SELECT a.auction_id, i.name, i.tier, a.amount, a.price, a.ends_at, a.status
            FROM auction a
            JOIN items i ON i.id = a.item_id
            WHERE a.status = 'active'
            ORDER BY a.price DESC
            LIMIT 5
            """
        )

        if not rows:
            return await interaction.followup.send(
                "🏺 O leilão da Capital está vazio.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🏺 Leilão da Capital — Top 5 Leilões Ativos",
            description="Mostrando os leilões com os maiores lances atuais. Use '🔍 Procurar Leilão' para encontrar outros itens.",
            color=0xf1c40f
        )

        for i, r in enumerate(rows):
            time_left = r['ends_at'] - datetime.datetime.utcnow()
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            time_str = f"{hours}h {minutes}m" if time_left.total_seconds() > 0 else "Expirado"

            embed.add_field(
                name=f"#{i+1}: {r['name']} (T{r['tier']})",
                value=f"Qtd {r['amount']} | 💰 {r['price']} | ⏰ {time_str}",
                inline=False
            )

        view = AuctionView(rows)
        await interaction.followup.send(embed=embed, view=view)

    # =========================
    # /AUCTION SELL
    # =========================
    @auction_group.command(name="sell", description="Coloca um item à venda no leilão")
    async def auction_sell(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SellModal())

    # =========================
    # /AUCTION FINALIZE
    # =========================
    @auction_group.command(name="finalize", description="Finaliza leilões expirados (admin)")
    @commands.has_permissions(administrator=True)
    async def auction_finalize(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        await finalize_expired_auctions(self.bot)

        await interaction.followup.send(
            "🏺 Leilões expirados finalizados.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Auction(bot))
