import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import json

CAPITAL_ZONE_ID = 0

class RPG(commands.Cog):
    """Cog mínimo para registrar o grupo `/rpg` e comandos básicos."""
    rpg = app_commands.Group(name="rpg", description="Comandos principais do RPG")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @rpg.command(name="start", description="Inicia sua jornada no Abismo")
    async def start(self, interaction: discord.Interaction):
        try:
            if not hasattr(self.bot, 'db'):
                return await interaction.response.send_message("❌ Database não disponível.", ephemeral=True)
            
            # Check if user already exists
            existing = await self.bot.db.fetchval("SELECT 1 FROM users WHERE discord_id = $1", interaction.user.id)
            if existing:
                return await interaction.response.send_message("⚠️ Você já iniciou sua jornada no Abismo!", ephemeral=True)
            
            # Create user
            await self.bot.db.execute("INSERT INTO users (discord_id) VALUES ($1)", interaction.user.id)
            
            # Get starter items from database - lowest tier items for each slot
            # Slot IDs: 2=Head, 3=Legs, 4=Main Hand, 5=Torso, 6=Off Hand, 8=Feet
            slot_ids = [4, 5, 2, 3, 8, 6]  # Main Hand, Torso, Head, Legs, Feet, Off Hand
            starter_items = []
            
            for slot_id in slot_ids:
                item = await self.bot.db.fetchrow(
                    """
                    SELECT id, tier FROM items 
                    WHERE slot_id = $1 
                    ORDER BY tier ASC, subtier ASC 
                    LIMIT 1
                    """,
                    slot_id
                )
                if item:
                    starter_items.append((item['id'], slot_id, item['tier']))
            
            # If no items found, give basic message
            if not starter_items:
                await interaction.response.send_message(
                    "⚠️ Nenhum item inicial disponível. Por favor, contate um administrador para criar os itens iniciais usando `/genitem`.",
                    ephemeral=True
                )
                return
            
            # Add items to inventory and equip them
            for item_id, slot_id, tier in starter_items:
                # Add to inventory
                await self.bot.db.execute(
                    """
                    INSERT INTO inventory (user_id, item_id, tier, exp, quantity)
                    VALUES ($1, $2, $3, 0, 1)
                    ON CONFLICT (user_id, item_id, tier) DO NOTHING
                    """,
                    interaction.user.id, item_id, tier
                )
                
                # Auto-equip
                await self.bot.db.execute(
                    """
                    INSERT INTO equipment (user_id, slot_id, item_id, tier)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, slot_id) DO UPDATE SET item_id = $3, tier = $4
                    """,
                    interaction.user.id, slot_id, item_id, tier
                )
            
            embed = discord.Embed(
                title="🕳️ Bem-vindo ao Abismo",
                description="*As trevas te abraçam... sua jornada começa agora.*",
                color=0x2C2F33
            )
            embed.add_field(
                name="⚔️ Kit Inicial Recebido",
                value=(
                    "• **Espada Enferrujada** (Arma)\n"
                    "• **Armadura de Couro Gasto** (Torso)\n"
                    "• **Elmo Rachado** (Cabeça)\n"
                    "• **Calças de Pano** (Pernas)\n"
                    "• **Botas Desgastadas** (Pés)\n"
                    "• **Anel do Iniciante** (Acessório)"
                ),
                inline=False
            )
            embed.add_field(
                name="📊 Status Inicial",
                value="**HP**: 100 | **Level**: 1 | **Dano Total**: +18 | **Defesa Total**: +50",
                inline=False
            )
            embed.add_field(
                name="🗺️ Próximos Passos",
                value="Use `/rpg stats` para ver seu status completo e `/help` para ver todos os comandos disponíveis!",
                inline=False
            )
            embed.set_footer(text="Que a sorte esteja com você nas trevas...")
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error starting RPG: {e}")
            await interaction.response.send_message("❌ Erro ao iniciar jornada. Tente novamente.", ephemeral=True)

    @rpg.command(name="ping", description="Checa se o cog está ativo")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong — RPG cog ativo.")

    async def give_exp(self, user_id: int, amount: int):
        # minimal implementation used by other cogs; safe no-op if DB missing
        try:
            if hasattr(self.bot, 'db'):
                row = await self.bot.db.fetchrow("SELECT level, exp FROM users WHERE discord_id = $1", user_id)
                if not row:
                    return False
                level = row['level']
                exp = row['exp'] + amount
                leveled_up = False
                while exp >= level * 100:
                    exp -= level * 100
                    level += 1
                    leveled_up = True
                await self.bot.db.execute("UPDATE users SET level=$1, exp=$2 WHERE discord_id=$3", level, exp, user_id)
                return leveled_up
        except Exception:
            return False
        return False
    
    # =========================
    # FAME SYSTEM
    # =========================
    async def add_fame(self, user_id: int, fame_type: str, amount: int, reason: str = None):
        """
        Adiciona fama de um tipo específico ao usuário
        fame_type: 'arena', 'combat', 'crafting', 'exploration', 'trading'
        """
        try:
            if not hasattr(self.bot, 'db'):
                return False
            
            # Mapeia o tipo de fama para a coluna correta
            fame_columns = {
                'arena': 'fame_arena',
                'combat': 'fame_combat',
                'crafting': 'fame_crafting',
                'exploration': 'fame_exploration',
                'trading': 'fame_trading'
            }
            
            if fame_type not in fame_columns:
                return False
            
            column = fame_columns[fame_type]
            
            # Atualiza a fama
            await self.bot.db.execute(
                f"UPDATE users SET {column} = COALESCE({column}, 0) + $1 WHERE discord_id = $2",
                amount, user_id
            )
            
            # Registra no histórico
            await self.bot.db.execute(
                """
                INSERT INTO fame_history (user_id, fame_type, amount, reason)
                VALUES ($1, $2, $3, $4)
                """,
                user_id, fame_type, amount, reason
            )
            
            # Adiciona fama para a guilda do jogador
            guild_data = await self.bot.db.fetchrow(
                "SELECT guild_id FROM guild_members WHERE user_id = $1",
                user_id
            )
            
            if guild_data:
                # 50% da fama pessoal vai para a guilda
                guild_fame = amount // 2
                await self.bot.db.execute(
                    "SELECT add_guild_fame($1, $2, $3)",
                    guild_data['guild_id'], user_id, guild_fame
                )
            
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar fama: {e}")
            return False

    @rpg.command(name="zones", description="Zonas com atividade")
    async def zones(self, interaction: discord.Interaction):
        rows = await self.bot.db.fetch(
            """
            SELECT z.zone_id, z.nome, z.tier
            FROM zone z
            JOIN events e ON e.zone_id = z.zone_id
            WHERE e.active = TRUE
            AND (
                z.is_hideout = FALSE
                OR EXISTS (SELECT 1 FROM hideouts h WHERE h.zone_id = z.zone_id)
            )
            ORDER BY z.tier DESC
            """
        )

        if not rows:
            return await interaction.response.send_message(
                "🌫️ Nenhuma zona ativa no momento.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🌍 Zonas Ativas",
            color=discord.Color.dark_teal()
        )

        for z in rows:
            embed.add_field(
                name=z["nome"],
                value=f"Tier ⭐ {z['tier']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


    @rpg.command(name="goto", description="Muda sua zona pelo nome")
    @app_commands.describe(zone_name="Nome da zona (ou parte do nome)")
    async def goto(self, interaction: discord.Interaction, zone_name: str):
        user_id = interaction.user.id
        
        # Busca zona anterior
        old_zone_id = await self.bot.db.fetchval(
            "SELECT zona_id FROM users WHERE discord_id = $1",
            user_id
        )

        # procura zona por nome (case-insensitive, partial match), preferindo tiers mais altos
        zone = await self.bot.db.fetchrow(
            """
            SELECT zone_id, nome, tier
            FROM zone
            WHERE nome ILIKE $1
            ORDER BY tier DESC
            LIMIT 1
            """,
            f"%{zone_name}%"
        )

        if not zone:
            return await interaction.response.send_message("❌ Zona não encontrada.", ephemeral=True)

        # garante que o usuário exista e atualiza a zona (upsert)
        await self.bot.db.execute(
            """
            INSERT INTO users (discord_id, zona_id)
            VALUES ($1, $2)
            ON CONFLICT (discord_id) DO UPDATE SET zona_id = EXCLUDED.zona_id
            """,
            user_id, zone["zone_id"]
        )

        await interaction.response.send_message(
            f"🧭 Você foi para **{zone['nome']}** (Tier {zone['tier']}).",
            ephemeral=True
        )
        
        # Verifica se há Hideout na zona (notifica apenas se mudou de zona)
        hideout_cog = self.bot.get_cog("Hideout")
        if hideout_cog:
            hideout_embed = await hideout_cog.check_hideout_in_zone(user_id, zone["zone_id"], old_zone_id)
            if hideout_embed:
                await interaction.followup.send(embed=hideout_embed, ephemeral=True)

    @rpg.command(name="hub", description="Viaja diretamente para o Hub mais próximo")
    async def hub(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        # Busca zona anterior
        old_zone_id = await self.bot.db.fetchval(
            "SELECT zona_id FROM users WHERE discord_id = $1",
            user_id
        )

        # busca o primeiro hub disponível (is_hub = true)
        hub_zone = await self.bot.db.fetchrow(
            """
            SELECT zone_id, nome, tier
            FROM zone
            WHERE is_hub = TRUE
            ORDER BY tier ASC
            LIMIT 1
            """
        )

        if not hub_zone:
            return await interaction.response.send_message(
                "❌ Nenhum Hub disponível no momento.",
                ephemeral=True
            )

        # garante que o usuário exista e atualiza a zona para o hub
        await self.bot.db.execute(
            """
            INSERT INTO users (discord_id, zona_id)
            VALUES ($1, $2)
            ON CONFLICT (discord_id) DO UPDATE SET zona_id = EXCLUDED.zona_id
            """,
            user_id, hub_zone["zone_id"]
        )

        embed = discord.Embed(
            title="🏛️ Chegada ao Hub",
            description=f"Você chegou ao **{hub_zone['nome']}**!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📍 Localização",
            value=f"**Tier:** ⭐ `T{hub_zone['tier']}`\n**Tipo:** 🏛️ Hub (Cidade Segura)",
            inline=False
        )
        embed.add_field(
            name="ℹ️ Sobre Hubs",
            value=(
                "Hubs são cidades seguras onde você pode:\n"
                "• Comercializar itens no **Mercado**\n"
                "• Descansar e recuperar HP\n"
                "• Interagir com NPCs e comerciantes\n"
                "• Aceitar missões especiais"
            ),
            inline=False
        )
        embed.set_footer(text="Use /rpg zoneinfo para mais detalhes sobre esta zona")

        await interaction.response.send_message(embed=embed)
        
        # Verifica se há Hideout na zona (notifica apenas se mudou de zona)
        hideout_cog = self.bot.get_cog("Hideout")
        if hideout_cog:
            hideout_embed = await hideout_cog.check_hideout_in_zone(user_id, hub_zone["zone_id"], old_zone_id)
            if hideout_embed:
                await interaction.followup.send(embed=hideout_embed, ephemeral=True)

    # =========================
    # HP & LEVEL
    # =========================
    def hp_from_level(self, level: int) -> int:
        return level * 25

    async def get_equipment_stats(self, user_id: int):
        rows = await self.bot.db.fetch(
            """
            SELECT i.basedamage, i.basedefense
            FROM equipment e
            JOIN items i ON i.id = e.item_id
            WHERE e.user_id = $1::bigint
            """,
            user_id
        )

        hp_bonus = 0
        defense = 0
        for r in rows:
            if r["basedefense"]:
                defense += r["basedefense"]
        return hp_bonus, defense

    async def calculate_max_hp(self, user_id: int) -> int:
        row = await self.bot.db.fetchrow(
            "SELECT base_hp, level FROM users WHERE discord_id = $1::bigint",
            user_id
        )
        if not row:
            return 0
        return row["base_hp"] + self.hp_from_level(row["level"])

    async def give_exp(self, user_id: int, amount: int):
        user = await self.bot.db.fetchrow(
            "SELECT level, exp FROM users WHERE discord_id = $1::bigint",
            user_id
        )
        if not user:
            return False

        level = user["level"]
        exp = user["exp"] + amount
        leveled_up = False
        while exp >= level * 100:
            exp -= level * 100
            level += 1
            leveled_up = True

        await self.bot.db.execute(
            "UPDATE users SET level=$1, exp=$2 WHERE discord_id=$3::bigint",
            level, exp, user_id
        )
        return leveled_up

    # =========================
    # /rpg stats
    # =========================
    @rpg.command(name="stats", description="Veja seus status")
    async def stats(self, interaction: discord.Interaction):
        user_id = interaction.user.id
    
        # Puxa stats do usuário
        user = await self.bot.db.fetchrow(
            "SELECT level, base_hp, current_hp, exp FROM users WHERE discord_id=$1::bigint",
            user_id
        )
        if not user:
            return await interaction.response.send_message(
                "⚠️ Você ainda não iniciou sua jornada.", ephemeral=True
            )
    
        # Puxa economia do usuário
        economy = await self.bot.db.fetchrow(
            "SELECT gold FROM economy WHERE user_id=$1::bigint",
            user_id
        )
        gold = economy["gold"] if economy else 0  # caso não exista registro, assume 0

        max_hp = await self.calculate_max_hp(user_id)
        _, defense = await self.get_equipment_stats(user_id)

        embed = discord.Embed(
            title="📊 Status do Personagem",
            description="O Abismo observa…",
            color=0x8B0000
        )
        embed.add_field(name="⭐ Level", value=user["level"], inline=True)
        embed.add_field(name="🧪 EXP", value=f'{user["exp"]}/{user["level"]*100}', inline=True)
        embed.add_field(name="🩸 HP", value=f'{user["current_hp"]}/{max_hp}', inline=False)
        embed.add_field(name="🛡️ Defesa", value=defense, inline=True)
        embed.add_field(name="💰 Gold", value=f'{gold:,}', inline=True)  # formata com vírgula
        await interaction.response.send_message(embed=embed)


    # =========================
    # /rpg inventory
    # =========================
    @rpg.command(name="inventory", description="Veja todos os itens que você possui")
    async def inventory(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        rows = await self.bot.db.fetch(
            """
            SELECT i.id AS item_id, i.name, inv.tier, inv.quantity, i.slot_id
            FROM inventory inv
            JOIN items i ON i.id = inv.item_id
            WHERE inv.user_id=$1::bigint
            ORDER BY i.slot_id, i.name
            """,
            user_id
        )
        
        # Buscar recursos
        resources = await self.bot.db.fetch(
            """
            SELECT r.name, r.emoji, ur.quantity
            FROM user_resources ur
            JOIN resources r ON r.id = ur.resource_id
            WHERE ur.user_id = $1 AND ur.quantity > 0
            ORDER BY r.name
            """,
            user_id
        )

        if not rows and not resources:
            return await interaction.response.send_message("🎒 Sua mochila tá vazia…", ephemeral=True)

        slot_names = {1:"🎒 Mochila",2:"🪖 Cabeça",3:"🧥 Capa",4:"⚔️ Mão Principal",5:"🛡️ Torso",6:"🗡️ Mão Secundária",7:"🧪 Poção",8:"👢 Pés",9:"🍖 Comida"}
        embed = discord.Embed(title="🎒 Inventário", color=0x2F4F4F)

        current_slot = None
        text = ""
        for item in rows:
            slot = slot_names.get(item["slot_id"], "❓")
            line = f"• **{item['name']}** `T{item['tier']}` x{item['quantity']}\n"
            if slot != current_slot:
                if text:
                    embed.add_field(name=current_slot, value=text, inline=False)
                current_slot = slot
                text = line
            else:
                text += line
        if text:
            embed.add_field(name=current_slot, value=text, inline=False)
        
        # Adicionar recursos
        if resources:
            resource_text = ""
            for res in resources:
                # Tenta buscar tier se a coluna existir
                tier_display = ""
                try:
                    tier = await self.bot.db.fetchval(
                        "SELECT tier FROM resources WHERE name = $1",
                        res['name']
                    )
                    if tier:
                        tier_display = f" `T{tier}`"
                except:
                    pass
                
                resource_text += f"{res['emoji']} **{res['name']}**{tier_display} x{res['quantity']}\n"
            embed.add_field(name="📦 Recursos", value=resource_text, inline=False)

        await interaction.response.send_message(embed=embed)

    # =========================
    # /rpg equipment
    # =========================
    @rpg.command(name="equipment", description="Veja os equipamentos que você está usando")
    async def equipment(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        rows = await self.bot.db.fetch(
            """
            SELECT e.slot_id, i.id AS item_id, i.name, e.tier, i.basedamage, i.basedefense
            FROM equipment e
            JOIN items i ON i.id = e.item_id
            WHERE e.user_id=$1::bigint
            ORDER BY e.slot_id
            """,
            user_id
        )

        slot_names = {1:"🎒 Mochila",2:"🪖 Cabeça",3:"🧥 Capa",4:"⚔️ Mão Principal",5:"🛡️ Torso",6:"🗡️ Mão Secundária",7:"🧪 Poção",8:"👢 Pés",9:"🍖 Comida"}
        embed = discord.Embed(title="🧙 Equipamentos", color=0x8B0000)

        if not rows:
            embed.add_field(name="Nada equipado", value="Você enfrenta o mundo nu e corajoso.", inline=False)
        else:
                for item in rows:
                    stats = []
                    if item["basedamage"]:
                        stats.append(f"+{item['basedamage']} ATK")
                    if item["basedefense"]:
                        stats.append(f"+{item['basedefense']} DEF")
                    embed.add_field(
                        name=slot_names.get(item["slot_id"], "❓"),
                        value=f"**{item['name']}** `T{item['tier']}`\n{' | '.join(stats) if stats else 'Sem bônus'}",
                        inline=False
                    )

        await interaction.response.send_message(embed=embed)

    # =========================
    # /rpg equip
    # =========================
    @rpg.command(name="equip", description="Equipa um item do seu inventário (por nome)")
    @app_commands.describe(item_name="Nome do item (ou parte do nome)", tier="(opcional) Tier do item")
    async def equip(self, interaction: discord.Interaction, item_name: str, tier: int | None = None):
        user_id = interaction.user.id
        # busca item no inventário pelo nome (case-insensitive); se tier fornecido, filtra por tier
        if tier is not None:
            item = await self.bot.db.fetchrow(
                """
                SELECT i.id, i.name, i.slot_id, inv.tier
                FROM inventory inv
                JOIN items i ON i.id = inv.item_id
                WHERE inv.user_id=$1 AND i.name ILIKE $2 AND inv.tier=$3 AND inv.quantity>0
                LIMIT 1
                """,
                user_id, f"%{item_name}%", tier
            )
        else:
            item = await self.bot.db.fetchrow(
                """
                SELECT i.id, i.name, i.slot_id, inv.tier
                FROM inventory inv
                JOIN items i ON i.id = inv.item_id
                WHERE inv.user_id=$1 AND i.name ILIKE $2 AND inv.quantity>0
                ORDER BY inv.tier DESC
                LIMIT 1
                """,
                user_id, f"%{item_name}%"
            )

        if not item:
            return await interaction.response.send_message("❌ Você não tem esse item no inventário.", ephemeral=True)

        slot_id = item["slot_id"]
        item_id = item["id"]
        item_tier = item["tier"]

        # remove do inventário
        await self.bot.db.execute(
            "UPDATE inventory SET quantity=quantity-1 WHERE user_id=$1 AND item_id=$2 AND tier=$3",
            user_id, item_id, item_tier
        )

        # remove do equipamento antigo e equipa
        await self.bot.db.execute("DELETE FROM equipment WHERE user_id=$1 AND slot_id=$2", user_id, slot_id)
        await self.bot.db.execute(
            "INSERT INTO equipment (user_id, slot_id, item_id, tier) VALUES ($1,$2,$3,$4)",
            user_id, slot_id, item_id, item_tier
        )

        await interaction.response.send_message(f"🧙‍♂️ **{item['name']}** `T{item_tier}` equipado com sucesso.", ephemeral=True)

    # =========================
    # /rpg unequip
    # =========================
    @rpg.command(name="unequip", description="Desequipa um item")
    @app_commands.describe(slot_id="Slot do equipamento")
    async def unequip(self, interaction: discord.Interaction, slot_id: int):
        user_id = interaction.user.id
        item = await self.bot.db.fetchrow(
            """
            SELECT e.item_id, e.tier, i.name
            FROM equipment e
            JOIN items i ON i.id = e.item_id
            WHERE e.user_id=$1 AND e.slot_id=$2
            """,
            user_id, slot_id
        )
        if not item:
            return await interaction.response.send_message("❌ Não tem nada equipado nesse slot.", ephemeral=True)

        # remove do equipamento
        await self.bot.db.execute("DELETE FROM equipment WHERE user_id=$1 AND slot_id=$2", user_id, slot_id)

        # devolve pro inventário
        await self.bot.db.execute(
            """
            INSERT INTO inventory (user_id, item_id, tier, quantity)
            VALUES ($1,$2,$3,1)
            ON CONFLICT (user_id,item_id,tier)
            DO UPDATE SET quantity=inventory.quantity+1
            """,
            user_id, item["item_id"], item["tier"]
        )

        await interaction.response.send_message(f"🧳 **{item['name']}** voltou pra mochila.", ephemeral=True)

    # =========================
    # /rpg zoneinfo
    # =========================
    @rpg.command(name="zoneinfo", description="Mostra informações detalhadas da zona atual")
    async def zoneinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Busca a zona atual do usuário
        user_data = await self.bot.db.fetchrow(
            "SELECT zona_id FROM users WHERE discord_id = $1",
            user_id
        )
        
        if not user_data or not user_data["zona_id"]:
            return await interaction.followup.send(
                "❌ Você não está em nenhuma zona. Use `/rpg goto` para explorar!",
                ephemeral=True
            )
        
        zone_id = user_data["zona_id"]
        
        # Busca informações da zona
        zone = await self.bot.db.fetchrow(
            """
            SELECT z.zone_id, z.nome, z.tier, z.is_hub, z.is_hideout, z.owner_guild, z.created_at,
                   h.name as hideout_name, h.level as hideout_level, h.guild_id as hideout_guild_id
            FROM zone z
            LEFT JOIN hideouts h ON h.zone_id = z.zone_id
            WHERE z.zone_id = $1
            """,
            zone_id
        )
        
        if not zone:
            return await interaction.followup.send(
                "❌ Zona não encontrada.",
                ephemeral=True
            )
        
        # Monta o embed
        embed = discord.Embed(
            title=f"🗺️ {zone['nome']}",
            color=discord.Color.blue() if not zone["is_hideout"] else discord.Color.gold()
        )
        
        # Informações básicas
        tier_stars = "⭐" * zone["tier"]
        zone_type = "🏛️ Hub" if zone["is_hub"] else "🏰 Hideout" if zone["is_hideout"] else "🌍 Zona Normal"
        
        # Detecta se é zona de Zahuv
        is_zahuv = zone["nome"].startswith(("Ai'", "Et'", "Al'", "Jo'", "Ka'", "Lu'", "Xe'", "Ty'"))
        if is_zahuv:
            zone_type += " | 🌀 **Zahuv**"
        
        embed.add_field(
            name="📍 Informações",
            value=f"**Tipo:** {zone_type}\n**Tier:** {tier_stars} `T{zone['tier']}`\n**ID:** `{zone['zone_id']}`",
            inline=False
        )
        
        # Se for Hideout
        if zone["is_hideout"] and zone["hideout_guild_id"]:
            guild_name = await self.bot.db.fetchval(
                "SELECT name FROM guilds WHERE id = $1",
                zone["hideout_guild_id"]
            )
            embed.add_field(
                name="🏰 Hideout",
                value=f"**Nome:** {zone['hideout_name']}\n**Guilda:** {guild_name or 'Desconhecida'}\n**Nível:** {zone['hideout_level']}",
                inline=False
            )
        
        # Busca eventos ativos na zona
        events = await self.bot.db.fetch(
            """
            SELECT id, type, reward, active, created_at
            FROM events
            WHERE zone_id = $1 AND active = TRUE
            ORDER BY type, created_at DESC
            """,
            zone_id
        )
        
        if events:
            event_descriptions = []
            for event in events:
                event_type = event["type"]
                
                if event_type == 1:
                    event_descriptions.append("⚔️ **Dungeon Ativa** - Explore para batalhas!")
                elif event_type == 2:
                    event_descriptions.append("🐉 **World Boss** - Chefe poderoso disponível!")
                elif event_type == 3:
                    event_descriptions.append("🌀 **Portal de Zahuv** - Use `/explore_portal` para entrar!")
                else:
                    event_descriptions.append(f"❓ Evento desconhecido (Tipo {event_type})")
            
            embed.add_field(
                name="🎯 Eventos Ativos",
                value="\n".join(event_descriptions),
                inline=False
            )
        else:
            embed.add_field(
                name="🎯 Eventos Ativos",
                value="🌫️ Nenhum evento ativo no momento.\nUse `/explore` para procurar segredos!",
                inline=False
            )
        
        # Conta players na zona
        player_count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM users WHERE zona_id = $1",
            zone_id
        )
        
        embed.add_field(
            name="👥 Jogadores",
            value=f"**{player_count}** jogador(es) nesta zona",
            inline=False
        )
        
        # Informações especiais de Zahuv
        if is_zahuv:
            embed.add_field(
                name="🌀 Terras Distantes de Zahuv",
                value=(
                    "Esta é uma zona misteriosa de Zahuv!\n"
                    "• Tiers podem variar aleatoriamente\n"
                    "• Eventos raros podem aparecer\n"
                    "• Portais podem conectar zonas distantes"
                ),
                inline=False
            )
        
        # Footer com dica
        embed.set_footer(text="Use /rpg goto para viajar para outras zonas | /explore para procurar segredos")
        
        await interaction.followup.send(embed=embed)

    # Battle commands are implemented in cogs/rpg_battle.py

async def setup(bot):
    cog = RPG(bot)
    await bot.add_cog(cog)

    # adiciona os grupos no tree
    try:
        bot.tree.add_command(cog.rpg)          # grupo principal
    except app_commands.errors.CommandAlreadyRegistered:
        pass
    # NOTE: subgrupos (ex: battle) são registrados pelos seus próprios cogs
    # para evitar dupla-registracão/colisão de nomes.

