import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys
from utils.rank_system import depth_to_rank, depth_to_rank_emoji, depth_to_rank_abbr

load_dotenv()

MY_ID = 947849382278094880


class AddCraftConfirmView(discord.ui.View):
    """View para confirmar criação de receitas em massa."""
    def __init__(self, bot, item_name: str, base_resources: dict, all_items: list):
        super().__init__(timeout=60)
        self.bot = bot
        self.item_name = item_name
        self.base_resources = base_resources
        self.all_items = all_items
        self.confirmed = False
    
    @discord.ui.button(label="✅ Apenas Este Item", style=discord.ButtonStyle.green)
    async def single_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="🔥 Criar Para Todos os Tiers", style=discord.ButtonStyle.blurple)
    async def all_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = None
        self.stop()
        await interaction.response.edit_message(content="❌ Operação cancelada.", embed=None, view=None)

MIN_TIER = 1
MAX_TIER = 8
MIN_SUB = 0
MAX_SUB = 4
WEAPON_SLOT = 4


class AdminRPG(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =========================
    # HELPERS
    # =========================
    def is_admin(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == MY_ID

    async def deny(self, interaction: discord.Interaction, msg: str):
        await interaction.response.send_message(msg, ephemeral=True)

    def validate_tier_range(self, st, ss, et, es):
        if not (MIN_TIER <= st <= MAX_TIER):
            return False
        if not (MIN_TIER <= et <= MAX_TIER):
            return False
        if not (MIN_SUB <= ss <= MAX_SUB):
            return False
        if not (MIN_SUB <= es <= MAX_SUB):
            return False
        if (st, ss) > (et, es):
            return False
        return True

    async def search_items(self, query: str):
        return await self.bot.db.fetch(
            """
            SELECT i.id, i.name, i.tier, i.subtier, ib.tipo
            FROM items i
            LEFT JOIN item_buffs ib ON ib.item_id = i.id
            WHERE i.name ILIKE $1 OR ib.tipo ILIKE $1
            ORDER BY i.tier DESC, i.subtier DESC
            LIMIT 25
            """,
            f"%{query}%"
        )

    # =========================
    # GEN ITEM (Desacoplamento Total - v2.0)
    # =========================
    @app_commands.command(name="genitem", description="Gera itens de 1.0 até 8.4 (busca atributos de Itens.enc)")
    async def genitem(
        self,
        interaction: discord.Interaction,
        nome: str,
        item_identifier: str,
        slot_id: int = 4,
        start_tier: int = 1,
        start_subtier: int = 0,
        end_tier: int = 8,
        end_subtier: int = 4,
        is_collectible: bool = False
    ):
        """
        🔐 FILOSOFIA DE DESACOPLAMENTO TOTAL:
        - Este comando apenas AUTORIZA a criação do item
        - Os atributos reais (damage, defense, buffs) vêm do arquivo Itens.enc
        - O usuário NUNCA define poder aqui, apenas nome, slot e tier
        """
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Nem tenta, isso aqui é coisa dos deuses.")
        
        # Importa o resolvedor de itens
        from services.item_resolver import item_resolver
        
        # Verifica se o item existe no arquivo criptografado
        item_attrs = item_resolver.resolve_item(slot_id, item_identifier)
        
        if item_attrs is None:
            return await interaction.response.send_message(
                f"❌ Item '{item_identifier}' não encontrado no slot {slot_id}\n"
                f"💡 Verifique o arquivo Itens.enc e os identificadores disponíveis",
                ephemeral=True
            )
        
        # Extrai atributos base do arquivo
        base_damage = item_attrs.get("base_damage", 0)
        base_defense = item_attrs.get("base_defense", 0)
        
        # Informações sobre o item resolvido
        has_buffs = len(item_attrs.get("buffs", [])) > 0
        is_legendary = item_attrs.get("flags", {}).get("legendary", False)

        # Criar embed de confirmação
        embed = discord.Embed(
            title="📦 Confirmar Criação de Item",
            color=discord.Color.gold() if is_legendary else discord.Color.blue()
        )
        embed.add_field(name="📝 Nome Público", value=nome, inline=False)
        embed.add_field(name="🔐 Identificador (Itens.enc)", value=f"`{item_identifier}`", inline=False)
        embed.add_field(name="⚔️ Dano Base (Itens.enc)", value=base_damage, inline=True)
        embed.add_field(name="🛡️ Defesa Base (Itens.enc)", value=base_defense, inline=True)
        embed.add_field(name="🎰 Slot ID", value=slot_id, inline=True)
        embed.add_field(name="📊 Tier Inicial", value=f"{start_tier}.{start_subtier}", inline=True)
        embed.add_field(name="📊 Tier Final", value=f"{end_tier}.{end_subtier}", inline=True)
        embed.add_field(name="📦 Coletável", value="✅ Sim" if is_collectible else "❌ Não", inline=True)
        
        if is_legendary:
            embed.add_field(name="⭐ Lendário", value="✅ Sim", inline=True)
        if has_buffs:
            buffs_preview = ", ".join(b.get("type", "?") for b in item_attrs.get("buffs", [])[:3])
            embed.add_field(name="✨ Buffs", value=buffs_preview, inline=True)
        
        total_items = 0
        for tier in range(start_tier, end_tier + 1):
            sub_start = start_subtier if tier == start_tier else MIN_SUB
            sub_end = end_subtier if tier == end_tier else MAX_SUB
            total_items += (sub_end - sub_start + 1)
        
        embed.add_field(name="📈 Total de Itens", value=f"{total_items} itens serão criados", inline=False)
        embed.set_footer(text="🔒 Atributos resolvidos do arquivo criptografado Itens.enc")
        
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None
            
            @discord.ui.button(label="✅ Confirmar", style=discord.ButtonStyle.green)
            async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                self.value = True
                self.stop()
            
            @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.red)
            async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                self.value = False
                self.stop()
        
        view = ConfirmView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        
        if not view.value:
            return await interaction.edit_original_response(
                content="❌ Criação de item cancelada.",
                embed=None,
                view=None
            )
        
        if not self.validate_tier_range(start_tier, start_subtier, end_tier, end_subtier):
            return await interaction.edit_original_response(
                content="⚠️ Intervalo inválido. Use de 1.0 até 8.4.",
                embed=None,
                view=None
            )

        itens = []

        for tier in range(start_tier, end_tier + 1):
            sub_start = start_subtier if tier == start_tier else MIN_SUB
            sub_end = end_subtier if tier == end_tier else MAX_SUB

            for subtier in range(sub_start, sub_end + 1):
                # DESACOPLAMENTO TOTAL: Valores vêm do arquivo, não de fórmulas!
                if slot_id == WEAPON_SLOT:
                    value = base_damage + (tier - 1) * 5 + subtier * 2
                    damage, defense = value, 0
                else:
                    value = base_defense + (tier - 1) * 4 + subtier * 2
                    damage, defense = 0, value

                row = await self.bot.db.fetchrow(
                    """
                    INSERT INTO items (name, basedamage, basedefense, tier, subtier, slot_id, is_collectible)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id
                    """,
                    nome, damage, defense, tier, subtier, slot_id, is_collectible
                )

                itens.append(
                    f"🧾 **{nome}** T{tier}.{subtier} | "
                    f"{'⚔️ Dano' if slot_id == WEAPON_SLOT else '🛡️ Defesa'} `{value}` | "
                    f"ID `{row['id']}`"
                )

        embed = discord.Embed(
            title="📦 Itens Gerados" + (" 🌿 (Coletáveis)" if is_collectible else ""),
            description="\n".join(itens[:25]),
            color=discord.Color.gold() if is_legendary else discord.Color.green()
        )
        if len(itens) > 25:
            embed.set_footer(text=f"E mais {len(itens) - 25} itens...")
        else:
            embed.set_footer(text=f"🔐 Atributos de: {item_identifier}")
        
        await interaction.edit_original_response(content=None, embed=embed, view=None)

    # =========================
    # GET ITEM
    # =========================
    @app_commands.command(name="getitem", description="Busca itens por nome ou buff")
    async def getitem(self, interaction: discord.Interaction, atributo: str):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Sem permissão.")

        rows = await self.search_items(atributo)
        if not rows:
            return await interaction.response.send_message("⚠️ Nada encontrado.", ephemeral=True)

        msg = "\n".join(
            f"🆔 {r['id']} | {r['name']} T{r['tier']}.{r['subtier']} ({r['tipo'] or 'nenhum'})"
            for r in rows
        )

        await interaction.response.send_message(f"📜 Resultados:\n{msg}", ephemeral=True)

    # =========================
    # AUTOCOMPLETE
    # =========================
    @getitem.autocomplete("atributo")
    async def atributo_autocomplete(self, interaction: discord.Interaction, current: str):
        rows = await self.search_items(current)
        return [
            app_commands.Choice(
                name=f"{r['name']} T{r['tier']}.{r['subtier']} ({r['tipo'] or 'nenhum'})",
                value=r["name"]
            )
            for r in rows
        ]

    # =========================
    # DELETE ITEM (PREP)
    # =========================
    @app_commands.command(name="delitem", description="Deleta item(s) por ID ou nome")
    async def delitem(self, interaction: discord.Interaction, filtro: str):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Tu não apaga a realidade.")

        await interaction.response.defer(ephemeral=True)

        if filtro.isdigit():
            result = await self.bot.db.execute("DELETE FROM items WHERE id=$1", int(filtro))
        else:
            result = await self.bot.db.execute("DELETE FROM items WHERE name ILIKE $1", f"%{filtro}%")

        deleted = int(result.split()[-1]) if result else 0

        await interaction.followup.send(
            f"🗑️ {deleted} item(s) removidos do multiverso.",
            ephemeral=True
        )

    # =========================
    # GIVE ITEM
    # =========================
    @app_commands.command(name="giveitem", description="Concede item ao inventário")
    async def giveitem(self, interaction: discord.Interaction, item_id: int, quantity: int = 1):
        if not interaction.user.guild_permissions.administrator:
            return await self.deny(interaction, "❌ Permissão insuficiente.")

        item = await self.bot.db.fetchrow(
            "SELECT id, name, tier, subtier FROM items WHERE id=$1",
            item_id
        )
        if not item:
            return await interaction.response.send_message("⚠️ Item inexistente.", ephemeral=True)

        await self.bot.db.execute(
            """
            INSERT INTO inventory (user_id, item_id, tier, quantity)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, item_id, tier)
            DO UPDATE SET quantity = inventory.quantity + $4
            """,
            interaction.user.id, item_id, item["tier"], quantity
        )

        await interaction.response.send_message(
            f"✨ {item['name']} T{item['tier']}.{item['subtier']} x{quantity} adicionado.",
            ephemeral=True
        )

    # =========================
    # ADD GOLD
    # =========================
    @app_commands.command(name="addgold", description="Adiciona gold (ADM)")
    async def addgold(self, interaction: discord.Interaction, amount: int):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não é ADM.")

        if amount <= 0:
            return await interaction.response.send_message("💀 Gold inválido.", ephemeral=True)

        await self.bot.db.execute(
            """
            INSERT INTO economy (user_id, gold)
            VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET gold = economy.gold + $2
            """,
            interaction.user.id, amount
        )

        await interaction.response.send_message(
            f"💰 +{amount} gold adicionados.",
            ephemeral=True
        )

    # =========================
    # ADD BUFF
    # =========================
    @app_commands.command(name="addbuff", description="Adiciona buff a um item")
    async def addbuff(self, interaction: discord.Interaction, item_id: int, tipo: str, valor: int, duracao: int = 0):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        exists = await self.bot.db.fetchrow("SELECT 1 FROM items WHERE id=$1", item_id)
        if not exists:
            return await interaction.response.send_message("❌ Item não encontrado.", ephemeral=True)

        await self.bot.db.execute(
            """
            INSERT INTO item_buffs (item_id, tipo, valor, duracao)
            VALUES ($1, $2, $3, $4)
            """,
            item_id, tipo, valor, duracao
        )

        await interaction.response.send_message(
            f"✨ Buff `{tipo}` aplicado no item `{item_id}`.",
            ephemeral=True
        )

    @app_commands.command(name="createzone", description="Cria uma zona customizada (ADM)")
    @app_commands.describe(
        nome="Nome da zona (deixe vazio para gerar aleatório)",
        tier="Tier da zona (1-8) - Depth System",
        is_hub="Se é uma cidade/capital",
        is_hideout="Se é uma zona de hideout",
        permanent="Se a zona é permanente"
    )
    async def createzone(
        self, 
        interaction: discord.Interaction, 
        nome: str = None, 
        tier: int = 1,
        is_hub: bool = False,
        is_hideout: bool = False,
        permanent: bool = True
    ):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        # Valida tier (Depth System: 1-8)
        if tier < 1 or tier > 8:
            return await interaction.response.send_message(
                "❌ Tier deve estar entre 1 e 8 (Depth System).",
                ephemeral=True
            )

        # Se não forneceu nome, gera aleatoriamente
        if not nome:
            import random
            adjectives = ["Sombrio", "Velho", "Desolado", "Brumoso", "Silente", "Quebrado", "Aurora", 
                          "Eterno", "Perdido", "Gelado", "Ardente", "Místico", "Profundo", "Árido",
                          "Nebuloso", "Antigo", "Esquecido", "Sagrado", "Maldito", "Oculto"]
            nouns = ["Pântano", "Cume", "Abismo", "Vale", "Ruína", "Fenda", "Bosque", 
                     "Deserto", "Floresta", "Caverna", "Templo", "Fortaleza", "Porto", "Montanha",
                     "Colina", "Planície", "Rochedo", "Santuário", "Túmulo", "Castelo"]
            
            ho_prefixes = ["Ai'rathel", "Et'morun", "Al'therion", "Jo'valdris", "Ka'velmir", 
                           "Lu'rathis", "Xe'morven", "Ty'drakkar", "Ba'korath", "Vi'therax"]
            
            # Se for hideout, usa 3 palavras, senão 2
            if is_hideout:
                prefix = random.choice(ho_prefixes)
                nome = f"{prefix} {random.choice(adjectives)} {random.choice(nouns)}"
            else:
                nome = f"{random.choice(adjectives)} {random.choice(nouns)}"
        
        # Verifica se já existe uma zona com esse nome
        exists = await self.bot.db.fetchrow(
            "SELECT 1 FROM zone WHERE nome = $1",
            nome
        )
        if exists:
            return await interaction.response.send_message(
                f"❌ Já existe uma zona chamada **{nome}**.",
                ephemeral=True
            )

        # Cria a zona
        zone = await self.bot.db.fetchrow(
            """
            INSERT INTO zone (nome, tier, is_hub, is_hideout, permanent)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING zone_id, nome, tier
            """,
            nome, tier, is_hub, is_hideout, permanent
        )

        embed = discord.Embed(
            title="🗺️ Zona Criada",
            description=f"Nova zona adicionada ao mundo!",
            color=discord.Color.green()
        )
        embed.add_field(name="Nome", value=zone["nome"], inline=True)
        rank_emoji = depth_to_rank_emoji(zone['tier'])
        rank_name = depth_to_rank_abbr(zone['tier'])
        embed.add_field(name="Rank", value=f"{rank_emoji} {rank_name}-Rank", inline=True)
        embed.add_field(name="Zone ID", value=zone["zone_id"], inline=True)
        embed.add_field(name="Hub", value="✅" if is_hub else "❌", inline=True)
        embed.add_field(name="Hideout", value="✅" if is_hideout else "❌", inline=True)
        embed.add_field(name="Permanente", value="✅" if permanent else "❌", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="teleport", description="Teleporta para uma zona ou jogador (ADM)")
    @app_commands.describe(
        zone_name="Nome da zona (deixe vazio para listar)",
        player="Jogador para teleportar até ele"
    )
    async def teleport(
        self,
        interaction: discord.Interaction,
        zone_name: str = None,
        player: discord.User = None
    ):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        # Teleport para jogador
        if player:
            player_zone = await self.bot.db.fetchval(
                "SELECT zona_id FROM users WHERE discord_id = $1",
                player.id
            )
            if not player_zone:
                return await interaction.response.send_message(
                    f"❌ {player.mention} não está em nenhuma zona.",
                    ephemeral=True
                )
            
            zone = await self.bot.db.fetchrow(
                "SELECT zone_id, nome, tier FROM zone WHERE zone_id = $1",
                player_zone
            )
            
            await self.bot.db.execute(
                "UPDATE users SET zona_id = $1 WHERE discord_id = $2",
                player_zone, interaction.user.id
            )
            
            return await interaction.response.send_message(
                f"🌀 Teleportado para **{zone['nome']}** (onde {player.mention} está)!",
                ephemeral=True
            )

        # Listar zonas se não especificou
        if not zone_name:
            zones = await self.bot.db.fetch(
                "SELECT zone_id, nome, tier FROM zone ORDER BY tier DESC, nome LIMIT 25"
            )
            if not zones:
                return await interaction.response.send_message("❌ Nenhuma zona encontrada.", ephemeral=True)
            
            embed = discord.Embed(title="🗺️ Zonas Disponíveis", color=discord.Color.blue())
            zones_text = "\n".join([f"`{z['zone_id']}` - **{z['nome']}** (T{z['tier']})" for z in zones])
            embed.description = zones_text
            embed.set_footer(text="Use /teleport zone_name:<nome> para teleportar")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Teleport para zona
        zone = await self.bot.db.fetchrow(
            "SELECT zone_id, nome, tier FROM zone WHERE nome ILIKE $1 LIMIT 1",
            f"%{zone_name}%"
        )
        
        if not zone:
            return await interaction.response.send_message(
                f"❌ Zona **{zone_name}** não encontrada.",
                ephemeral=True
            )
        
        await self.bot.db.execute(
            "UPDATE users SET zona_id = $1 WHERE discord_id = $2",
            zone["zone_id"], interaction.user.id
        )
        
        await interaction.response.send_message(
            f"🌀 Teleportado para **{zone['nome']}** (Tier {zone['tier']})!",
            ephemeral=True
        )

    @app_commands.command(name="spawnevent", description="Cria um evento em uma zona (ADM)")
    @app_commands.describe(
        zone_name="Nome da zona",
        event_type="Tipo: 1=Dungeon, 2=WorldBoss, 3=Portal",
        gold_reward="Gold de recompensa",
        xp_reward="XP de recompensa"
    )
    async def spawnevent(
        self,
        interaction: discord.Interaction,
        zone_name: str,
        event_type: int = 1,
        gold_reward: int = 100,
        xp_reward: int = 50
    ):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        if event_type not in [1, 2, 3]:
            return await interaction.response.send_message(
                "❌ Tipo de evento deve ser 1 (Dungeon), 2 (WorldBoss) ou 3 (Portal).",
                ephemeral=True
            )

        zone = await self.bot.db.fetchrow(
            "SELECT zone_id, nome FROM zone WHERE nome ILIKE $1 LIMIT 1",
            f"%{zone_name}%"
        )
        
        if not zone:
            return await interaction.response.send_message(
                f"❌ Zona **{zone_name}** não encontrada.",
                ephemeral=True
            )

        import json
        if event_type == 3:
            reward = {"portal": True}
        else:
            reward = {"gold": gold_reward, "xp": xp_reward}

        await self.bot.db.execute(
            "INSERT INTO events (type, zone_id, reward, active) VALUES ($1, $2, $3, TRUE)",
            event_type, zone["zone_id"], json.dumps(reward)
        )

        event_names = {1: "🗡️ Dungeon", 2: "👹 WorldBoss", 3: "🌀 Portal"}
        
        await interaction.response.send_message(
            f"✨ Evento **{event_names[event_type]}** criado em **{zone['nome']}**!\n"
            f"💰 Recompensa: {gold_reward} gold | {xp_reward} XP",
            ephemeral=True
        )

    @app_commands.command(name="setlevel", description="Define o level de um jogador (ADM)")
    @app_commands.describe(player="Jogador alvo", level="Novo level")
    async def setlevel(self, interaction: discord.Interaction, player: discord.User, level: int):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        if level < 1 or level > 999:
            return await interaction.response.send_message("❌ Level deve estar entre 1 e 999.", ephemeral=True)

        await self.bot.db.execute(
            "UPDATE users SET level = $1, exp = 0 WHERE discord_id = $2",
            level, player.id
        )

        await interaction.response.send_message(
            f"⭐ {player.mention} agora é level **{level}**!",
            ephemeral=True
        )

    @app_commands.command(name="healall", description="Cura todos os jogadores na zona atual (ADM)")
    async def healall(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        admin_zone = await self.bot.db.fetchval(
            "SELECT zona_id FROM users WHERE discord_id = $1",
            interaction.user.id
        )

        if not admin_zone:
            return await interaction.response.send_message(
                "❌ Você não está em nenhuma zona.",
                ephemeral=True
            )

        # Cura todos na mesma zona
        result = await self.bot.db.execute(
            """
            UPDATE users 
            SET current_hp = base_hp + (level * 25)
            WHERE zona_id = $1
            """,
            admin_zone
        )

        healed = int(result.split()[-1]) if result else 0

        zone = await self.bot.db.fetchrow(
            "SELECT nome FROM zone WHERE zone_id = $1",
            admin_zone
        )

        await interaction.response.send_message(
            f"💚 **{healed}** jogadores curados em **{zone['nome']}**!",
            ephemeral=True
        )

    @app_commands.command(name="broadcast", description="Envia mensagem global (ADM)")
    @app_commands.describe(message="Mensagem para enviar")
    async def broadcast(self, interaction: discord.Interaction, message: str):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        embed = discord.Embed(
            title="📢 Anúncio Global",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Enviado por {interaction.user.name}")

        # Envia no canal atual
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Broadcast enviado!", ephemeral=True)

    @app_commands.command(name="playerstats", description="Ver stats de qualquer jogador (ADM)")
    @app_commands.describe(player="Jogador para ver stats")
    async def playerstats(self, interaction: discord.Interaction, player: discord.User):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        user = await self.bot.db.fetchrow(
            "SELECT level, base_hp, current_hp, exp, zona_id FROM users WHERE discord_id = $1",
            player.id
        )
        
        if not user:
            return await interaction.response.send_message(
                f"❌ {player.mention} não está registrado.",
                ephemeral=True
            )

        economy = await self.bot.db.fetchrow(
            "SELECT gold FROM economy WHERE user_id = $1",
            player.id
        )
        gold = economy["gold"] if economy else 0

        zone = await self.bot.db.fetchrow(
            "SELECT nome FROM zone WHERE zone_id = $1",
            user["zona_id"]
        ) if user["zona_id"] else None

        max_hp = user["base_hp"] + user["level"] * 25

        embed = discord.Embed(
            title=f"📊 Stats - {player.display_name}",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=player.display_avatar.url)
        embed.add_field(name="⭐ Level", value=user["level"], inline=True)
        embed.add_field(name="🧪 EXP", value=f'{user["exp"]}/{user["level"]*100}', inline=True)
        embed.add_field(name="💰 Gold", value=f'{gold:,}', inline=True)
        embed.add_field(name="🩸 HP", value=f'{user["current_hp"]}/{max_hp}', inline=True)
        embed.add_field(name="🗺️ Zona", value=zone["nome"] if zone else "Nenhuma", inline=True)
        embed.add_field(name="🆔 ID", value=player.id, inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clearinventory", description="Limpa inventário de um jogador (ADM)")
    @app_commands.describe(player="Jogador alvo")
    async def clearinventory(self, interaction: discord.Interaction, player: discord.User):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Não autorizado.")

        result = await self.bot.db.execute(
            "DELETE FROM inventory WHERE user_id = $1",
            player.id
        )

        deleted = int(result.split()[-1]) if result else 0

        await interaction.response.send_message(
            f"🗑️ Inventário de {player.mention} limpo! ({deleted} itens removidos)",
            ephemeral=True
        )

    @app_commands.command(name="addcraft", description="Adiciona receita de craft (ADM)")
    @app_commands.describe(
        item_id="ID do item que será craftado",
        madeira="Quantidade de Madeira",
        pedra="Quantidade de Pedra",
        minerio="Quantidade de Minério",
        fibra="Quantidade de Fibra",
        pelego="Quantidade de Pelego"
    )
    async def addcraft(
        self,
        interaction: discord.Interaction,
        item_id: int,
        madeira: int = 0,
        pedra: int = 0,
        minerio: int = 0,
        fibra: int = 0,
        pelego: int = 0
    ):
        if not self.is_admin(interaction):
            return await self.deny(interaction, "🚫 Apenas administradores podem criar receitas.")
        
        await interaction.response.defer(ephemeral=True)
        
        # Verificar se o item existe
        item = await self.bot.db.fetchrow(
            "SELECT id, name, tier, subtier FROM items WHERE id = $1",
            item_id
        )
        
        if not item:
            return await interaction.followup.send("❌ Item não encontrado.", ephemeral=True)
        
        # Verificar se já existe receita para este item/tier
        existing = await self.bot.db.fetchval(
            "SELECT 1 FROM recipes WHERE item_id = $1 AND tier = $2 AND subtier = $3",
            item["id"], item["tier"], item["subtier"]
        )
        
        if existing:
            return await interaction.followup.send(
                f"⚠️ Já existe uma receita para **{item['name']}** T{item['tier']}.{item['subtier']}",
                ephemeral=True
            )
        
        # Mapear recursos base
        base_resources = {
            "Madeira": madeira,
            "Pedra": pedra,
            "Minério": minerio,
            "Fibra": fibra,
            "Pelego": pelego
        }
        
        # Verificar se há recursos válidos
        if not any(base_resources.values()):
            return await interaction.followup.send(
                "❌ Você precisa adicionar pelo menos um recurso!",
                ephemeral=True
            )
        
        # Buscar todos os itens com o mesmo nome
        all_items = await self.bot.db.fetch(
            """
            SELECT id, name, tier, subtier FROM items 
            WHERE name = $1 AND id != $2
            ORDER BY tier ASC, subtier ASC
            """,
            item["name"], item["id"]
        )
        
        # Se houver outros itens com o mesmo nome, perguntar se quer criar para todos
        if all_items:
            # Calcular preview dos custos
            preview_items = []
            current_tier = item["tier"] + (item["subtier"] * 0.1)
            
            for other_item in all_items[:5]:  # Mostrar até 5 exemplos
                other_tier = other_item["tier"] + (other_item["subtier"] * 0.1)
                multiplier = other_tier / current_tier
                
                resources_preview = []
                for res_name, base_qty in base_resources.items():
                    if base_qty > 0:
                        scaled_qty = int(base_qty * multiplier)
                        resource = await self.bot.db.fetchrow(
                            "SELECT emoji FROM resources WHERE name = $1", res_name
                        )
                        if resource:
                            resources_preview.append(f"{resource['emoji']}{scaled_qty}")
                
                preview_items.append(
                    f"`T{other_item['tier']}.{other_item['subtier']}` → {' '.join(resources_preview)}"
                )
            
            embed = discord.Embed(
                title="🔨 Criar Receitas em Massa?",
                description=f"Encontrei **{len(all_items) + 1} itens** com o nome **{item['name']}**.\n\n"
                           f"Deseja criar receitas para todos os tiers com custos escalonados?",
                color=discord.Color.orange()
            )
            
            # Mostrar receita atual
            current_resources = []
            for res_name, qty in base_resources.items():
                if qty > 0:
                    resource = await self.bot.db.fetchrow(
                        "SELECT emoji FROM resources WHERE name = $1", res_name
                    )
                    if resource:
                        current_resources.append(f"{resource['emoji']} {qty}x {res_name}")
            
            embed.add_field(
                name=f"📦 Item Selecionado: T{item['tier']}.{item['subtier']}",
                value="\n".join(current_resources),
                inline=False
            )
            
            if preview_items:
                embed.add_field(
                    name="📊 Preview de Outros Tiers (custos escalonados)",
                    value="\n".join(preview_items) + (f"\n... e mais {len(all_items) - 5}" if len(all_items) > 5 else ""),
                    inline=False
                )
            
            embed.set_footer(text="Os custos serão multiplicados proporcionalmente ao tier")
            
            # Criar view com botões
            view = AddCraftConfirmView(self.bot, item["name"], base_resources, [item] + all_items)
            msg = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
            # Aguardar resposta
            await view.wait()
            
            if view.confirmed is None:
                return  # Cancelado
            
            if view.confirmed:
                # Criar receitas para todos
                await self._create_recipes_batch(
                    interaction, 
                    [item] + all_items, 
                    base_resources,
                    item["tier"] + (item["subtier"] * 0.1)
                )
                return
            # Se não confirmou criar em massa, continua para criar apenas o item atual
        
        # Criar receita apenas para o item especificado
        await self._create_single_recipe(interaction, item, base_resources)
    
    async def _create_single_recipe(self, interaction, item, base_resources):
        """Cria uma única receita."""
        recipe_id = await self.bot.db.fetchval(
            """
            INSERT INTO recipes (item_id, tier, subtier)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            item["id"], item["tier"], item["subtier"]
        )
        
        # Adicionar ingredientes
        ingredients_added = []
        for resource_name, quantity in base_resources.items():
            if quantity > 0:
                resource = await self.bot.db.fetchrow(
                    "SELECT id, emoji FROM resources WHERE name = $1",
                    resource_name
                )
                
                if resource:
                    await self.bot.db.execute(
                        """
                        INSERT INTO recipe_ingredients (recipe_id, resource_id, quantity)
                        VALUES ($1, $2, $3)
                        """,
                        recipe_id, resource["id"], quantity
                    )
                    ingredients_added.append(f"{resource['emoji']} {quantity}x {resource_name}")
        
        embed = discord.Embed(
            title="✅ Receita Criada!",
            description=f"Receita adicionada para **{item['name']}** `T{item['tier']}.{item['subtier']}`",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📦 Ingredientes",
            value="\n".join(ingredients_added),
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def _create_recipes_batch(self, interaction, items, base_resources, base_tier):
        """Cria múltiplas receitas com custos escalonados."""
        created = []
        skipped = []
        
        for item in items:
            # Verificar se já existe
            existing = await self.bot.db.fetchval(
                "SELECT 1 FROM recipes WHERE item_id = $1 AND tier = $2 AND subtier = $3",
                item["id"], item["tier"], item["subtier"]
            )
            
            if existing:
                skipped.append(f"`T{item['tier']}.{item['subtier']}`")
                continue
            
            # Calcular multiplicador baseado no tier
            item_tier = item["tier"] + (item["subtier"] * 0.1)
            multiplier = item_tier / base_tier
            
            # Criar receita
            recipe_id = await self.bot.db.fetchval(
                """
                INSERT INTO recipes (item_id, tier, subtier)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                item["id"], item["tier"], item["subtier"]
            )
            
            # Adicionar ingredientes escalados
            ingredients_added = []
            for resource_name, base_qty in base_resources.items():
                if base_qty > 0:
                    scaled_qty = max(1, int(base_qty * multiplier))
                    
                    resource = await self.bot.db.fetchrow(
                        "SELECT id, emoji FROM resources WHERE name = $1",
                        resource_name
                    )
                    
                    if resource:
                        await self.bot.db.execute(
                            """
                            INSERT INTO recipe_ingredients (recipe_id, resource_id, quantity)
                            VALUES ($1, $2, $3)
                            """,
                            recipe_id, resource["id"], scaled_qty
                        )
                        ingredients_added.append(f"{resource['emoji']}{scaled_qty}")
            
            created.append(f"`T{item['tier']}.{item['subtier']}` → {' '.join(ingredients_added)}")
        
        embed = discord.Embed(
            title="✅ Receitas Criadas em Massa!",
            description=f"**{len(created)}** receitas criadas para **{items[0]['name']}**",
            color=discord.Color.green()
        )
        
        if created:
            # Dividir em chunks se houver muitos
            chunk_size = 10
            for i in range(0, len(created), chunk_size):
                chunk = created[i:i+chunk_size]
                embed.add_field(
                    name=f"📦 Receitas Criadas ({i+1}-{min(i+chunk_size, len(created))})",
                    value="\n".join(chunk),
                    inline=False
                )
        
        if skipped:
            embed.add_field(
                name="⚠️ Ignorados (já existiam)",
                value=", ".join(skipped),
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="giveadminitem", description="Dá um item de admin (stats absurdas)")
    @app_commands.choices(item=[
        app_commands.Choice(name="⚔️ Espada do Desenvolvedor (100k DMG)", value="espada_do_desenvolvedor"),
        app_commands.Choice(name="🛡️ Armadura do Admin (200k DEF)", value="armadura_do_admin"),
        app_commands.Choice(name="👑 Elmo Omnisciente (150k DEF)", value="elmo_omnisciente"),
        app_commands.Choice(name="👖 Calças do Debugger (120k DEF)", value="calcas_do_debugger"),
        app_commands.Choice(name="👢 Botas do Hotfix (80k DEF)", value="botas_do_hotfix"),
        app_commands.Choice(name="📿 Amuleto do Sysadmin (50k DMG/DEF)", value="amuleto_do_sysadmin"),
        app_commands.Choice(name="💍 Anel do Commit (25k DMG/DEF)", value="anel_do_commit"),
        app_commands.Choice(name="🛡️ Escudo do Rollback (500k DEF)", value="escudo_do_rollback"),
        app_commands.Choice(name="🪄 Cajado do Refactor (250k DMG)", value="cajado_do_refactor"),
        app_commands.Choice(name="🧪 Poção de Godmode", value="pocao_de_godmode"),
        app_commands.Choice(name="🩹 Kit de Emergência", value="kit_de_emergencia"),
        app_commands.Choice(name="📜 Pergaminho do Fix", value="pergaminho_do_fix"),
    ])
    async def giveadminitem(
        self, 
        interaction: discord.Interaction, 
        item: str,
        user: discord.Member = None,
        quantity: int = 1
    ):
        """Dá um item de admin para um jogador"""
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Apenas o desenvolvedor pode usar este comando.", ephemeral=True)
        
        target = user or interaction.user
        
        # Buscar item de admin no banco
        item_data = await self.bot.db.fetchrow(
            "SELECT id, name, base_damage, base_defense, depth_new, quality_new FROM items WHERE name=$1",
            item
        )
        
        if not item_data:
            return await interaction.response.send_message(
                f"⚠️ Item '{item}' não encontrado no banco!\nExecute primeiro: `psql $DATABASE_URL < db/seeds/populate_admin_items.sql`",
                ephemeral=True
            )
        
        # Adicionar ao inventário
        await self.bot.db.execute(
            """
            INSERT INTO inventory (user_id, item_id, quantity)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, item_id)
            DO UPDATE SET quantity = inventory.quantity + $3
            """,
            target.id, item_data["id"], quantity
        )
        
        display_name = item.replace("_", " ").title()
        await interaction.response.send_message(
            f"✨ **{display_name}** x{quantity} dado para {target.mention}\n"
            f"⚔️ DMG: `{item_data['base_damage']:,}` | 🛡️ DEF: `{item_data['base_defense']:,}`\n"
            f"🏅 Qualidade: **{item_data['quality_new']}** (Depth {item_data['depth_new']})",
            ephemeral=True
        )

    @app_commands.command(name="giveadminkit", description="Dá um kit completo de itens de admin")
    async def giveadminkit(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member = None
    ):
        """Dá um set completo de equipamento admin para um jogador"""
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Apenas o desenvolvedor pode usar este comando.", ephemeral=True)
        
        target = user or interaction.user
        await interaction.response.defer(ephemeral=True)
        
        # Lista de itens do kit completo
        admin_kit = [
            "espada_do_desenvolvedor",  # Weapon
            "armadura_do_admin",        # Chest
            "elmo_omnisciente",         # Head
            "calcas_do_debugger",       # Legs
            "botas_do_hotfix",          # Feet
            "amuleto_do_sysadmin",      # Amulet
            "anel_do_commit",           # Ring
            "escudo_do_rollback",       # Shield
            "pocao_de_godmode",         # Consumable
            "kit_de_emergencia",        # Consumable
            "pergaminho_do_fix"         # Consumable
        ]
        
        given_items = []
        missing_items = []
        
        for item_name in admin_kit:
            item_data = await self.bot.db.fetchrow(
                "SELECT id, name, base_damage, base_defense FROM items WHERE name=$1",
                item_name
            )
            
            if not item_data:
                missing_items.append(item_name)
                continue
            
            # Adicionar ao inventário
            await self.bot.db.execute(
                """
                INSERT INTO inventory (user_id, item_id, quantity)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, item_id)
                DO UPDATE SET quantity = inventory.quantity + $3
                """,
                target.id, item_data["id"], 1
            )
            
            given_items.append(item_data["name"])
        
        embed = discord.Embed(
            title="🎁 Kit de Admin Entregue",
            description=f"Set completo de equipamento admin dado para {target.mention}",
            color=discord.Color.purple()
        )
        
        if given_items:
            items_list = "\n".join([f"✓ {item.replace('_', ' ').title()}" for item in given_items])
            embed.add_field(
                name=f"✨ Itens Entregues ({len(given_items)})",
                value=items_list,
                inline=False
            )
        
        if missing_items:
            missing_list = "\n".join([f"✗ {item.replace('_', ' ').title()}" for item in missing_items])
            embed.add_field(
                name=f"⚠️ Itens Não Encontrados ({len(missing_items)})",
                value=missing_list,
                inline=False
            )
            embed.add_field(
                name="📋 Como Corrigir",
                value="Execute: `psql $DATABASE_URL < db/seeds/populate_admin_items.sql`",
                inline=False
            )
        
        embed.set_footer(text="⚠️ Use com responsabilidade! Estes itens têm stats absurdas.")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="restart", description="Reinicia o bot (apenas admin)")

    async def restart(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Você não tem permissão para fazer isso.", ephemeral=True)

        await interaction.response.send_message("🔄 Reiniciando o bot...", ephemeral=True)
        await self.bot.close()
        os.execv(sys.executable, ['python'] + sys.argv)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminRPG(bot))
