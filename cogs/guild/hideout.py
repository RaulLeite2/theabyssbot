import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random
from utils.rank_system import depth_to_rank, depth_to_rank_emoji, depth_to_rank_abbr


class Hideout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._tasks = []
        # Inicia o loop de degradação de durabilidade
        self.bot.loop.create_task(self._start_durability_loop())

    async def _start_durability_loop(self):
        """Aguarda o bot estar pronto e inicia o loop."""
        await self.bot.wait_until_ready()
        self._tasks.append(self.bot.loop.create_task(self.durability_degradation_loop()))

    async def cog_unload(self):
        """Cancela tasks ao descarregar o cog."""
        for t in self._tasks:
            t.cancel()

    # =========================
    # HELPER: NOTIFICAÇÃO DE HIDEOUT
    # =========================
    
    async def check_hideout_in_zone(self, user_id: int, zone_id: int, previous_zone_id: int = None):
        """
        Verifica se há Hideout da guilda/aliança do player na zona atual
        Retorna um embed se encontrar E a zona mudou, None caso contrário
        
        Args:
            user_id: ID do usuário
            zone_id: Zona atual
            previous_zone_id: Zona anterior (None = sempre notifica)
        """
        # Se a zona não mudou, não notifica
        if previous_zone_id is not None and zone_id == previous_zone_id:
            return None
        
        # Verifica se o usuário está em uma guilda
        guild_member = await self.bot.db.fetchrow(
            "SELECT guild_id FROM guild_members WHERE user_id = $1",
            user_id
        )
        
        if not guild_member:
            return None
        
        guild_id = guild_member['guild_id']
        
        # Verifica se a guilda tem aliança
        alliance = await self.bot.db.fetchrow(
            "SELECT alliance_id FROM guild_alliances WHERE guild_id = $1",
            guild_id
        )
        
        # Procura Hideout da guilda ou da aliança nesta zona
        if alliance:
            hideout = await self.bot.db.fetchrow(
                """
                SELECT h.id, h.name, h.energy, g.name as guild_name, a.name as alliance_name
                FROM hideouts h
                LEFT JOIN guilds g ON h.guild_id = g.id
                LEFT JOIN alliances a ON h.alliance_id = a.id
                WHERE h.zone_id = $1 
                AND (h.guild_id = $2 OR h.alliance_id = $3)
                AND h.energy > 0
                """,
                zone_id, guild_id, alliance['alliance_id']
            )
        else:
            hideout = await self.bot.db.fetchrow(
                """
                SELECT h.id, h.name, h.energy, g.name as guild_name
                FROM hideouts h
                LEFT JOIN guilds g ON h.guild_id = g.id
                WHERE h.zone_id = $1 
                AND h.guild_id = $2
                AND h.energy > 0
                """,
                zone_id, guild_id
            )
        
        if hideout:
            embed = discord.Embed(
                title="🏠 Hideout Detectado!",
                description=f"Esta zona possui o Hideout **{hideout['name']}**!",
                color=discord.Color.blue()
            )
            
            if hideout.get('alliance_name'):
                embed.add_field(
                    name="🤝 Pertence à",
                    value=f"Aliança **{hideout['alliance_name']}**",
                    inline=True
                )
            elif hideout.get('guild_name'):
                embed.add_field(
                    name="⚔️ Pertence à",
                    value=f"Guilda **{hideout['guild_name']}**",
                    inline=True
                )
            
            embed.add_field(
                name="⚡ Energia",
                value=f"{hideout['energy']}%",
                inline=True
            )
            embed.add_field(
                name="💡 Dica",
                value="Use `/ho entrar` para acessar!",
                inline=False
            )
            
            return embed
        
        return None

    async def durability_degradation_loop(self):
        """Loop que verifica HOs sem energia e degrada durabilidade."""
        import asyncio
        while not self.bot.is_closed():
            try:
                # A cada 30 minutos, verifica HOs sem energia
                await asyncio.sleep(1800)  # 30 minutos
                
                # Busca todos os hideouts com energia 0
                hos_without_energy = await self.bot.db.fetch(
                    "SELECT id, guild_id, zone_id, name, durability FROM hideouts WHERE energy = 0"
                )
                
                for ho in hos_without_energy:
                    current_durability = ho["durability"] if ho.get("durability") is not None else 100
                    
                    # Reduz durabilidade em 10 pontos
                    new_durability = max(0, current_durability - 10)
                    
                    if new_durability <= 0:
                        # HO destruído! Deleta o hideout e a zona
                        try:
                            await self.bot.db.execute(
                                "DELETE FROM hideouts WHERE id = $1",
                                ho["id"]
                            )
                            await self.bot.db.execute(
                                "DELETE FROM zone WHERE zone_id = $1",
                                ho["zone_id"]
                            )
                            print(f"🏚️ Hideout '{ho['name']}' (ID: {ho['id']}) foi destruído por falta de energia.")
                        except Exception as e:
                            print(f"Erro ao deletar hideout {ho['id']}: {e}")
                    else:
                        # Atualiza a durabilidade
                        await self.bot.db.execute(
                            "UPDATE hideouts SET durability = $1 WHERE id = $2",
                            new_durability, ho["id"]
                        )
                        print(f"⚠️ Hideout '{ho['name']}' (ID: {ho['id']}) perdeu durabilidade: {current_durability} → {new_durability}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Erro no loop de durabilidade: {e}")
                await asyncio.sleep(300)  # Espera 5 min em caso de erro

    async def clone_zone_for_hideout(self, base_zone_id: int, guild_id: int):
        """
        Para zonas especiais de Zahuv: clona a zona
        Para zonas normais: torna a zona permanente sem clonar
        """
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                # Pega os dados da zona base
                base_zone = await conn.fetchrow(
                    "SELECT * FROM zone WHERE zone_id = $1",
                    base_zone_id
                )
                if not base_zone:
                    raise ValueError("Base zone not found")

                # Verifica se é zona de Zahuv (nome começa com prefixo especial)
                is_zahuv_zone = base_zone['nome'].startswith(("Ai'", "Et'", "Al'", "Jo'", "Ka'", "Lu'", "Xe'", "Ty'"))
                
                if is_zahuv_zone:
                    # === ZONAS DE ZAHUV: CLONA A ZONA ===
                    # Gera um novo zone_id único
                    attempts = 0
                    max_attempts = 100
                    new_zone_id = None
                    while attempts < max_attempts:
                        new_zone_id = random.randint(10_000_000, 99_999_999)
                        exists = await conn.fetchval(
                            "SELECT 1 FROM zone WHERE zone_id = $1", new_zone_id
                        )
                        if not exists:
                            break
                        attempts += 1
                    if attempts >= max_attempts:
                        raise ValueError("Failed to generate unique zone_id")

                    # Cria a nova zona clonada
                    zone_name = base_zone['nome']
                    
                    await conn.execute(
                        """
                        INSERT INTO zone (zone_id, nome, tier, is_hub, is_hideout, permanent, owner_guild)
                        VALUES ($1, $2, $3, $4, TRUE, TRUE, $5)
                        """,
                        new_zone_id,
                        zone_name,
                        base_zone["tier"],
                        base_zone["is_hub"],
                        guild_id
                    )

                    # Clona apenas eventos de Dungeon (type=1), exclui WorldBoss (type=2)
                    events = await conn.fetch(
                        "SELECT type, reward, active FROM events WHERE zone_id = $1 AND type = 1",
                        base_zone_id
                    )
                    for ev in events:
                        await conn.execute(
                            """
                            INSERT INTO events (type, zone_id, reward, active)
                            VALUES ($1, $2, $3, $4)
                            """,
                            ev["type"],
                            new_zone_id,
                            ev["reward"],
                            ev["active"]
                        )

                    return new_zone_id
                
                else:
                    # === ZONAS NORMAIS: APENAS TORNA PERMANENTE ===
                    # Atualiza a zona existente para ser permanente e hideout
                    await conn.execute(
                        """
                        UPDATE zone 
                        SET is_hideout = TRUE, 
                            permanent = TRUE, 
                            owner_guild = $1
                        WHERE zone_id = $2
                        """,
                        guild_id,
                        base_zone_id
                    )
                    
                    return base_zone_id


    # ======================================================
    # 🔧 FUNÇÕES UTILITÁRIAS
    # ======================================================
    async def get_hideout(self, guild_id: int):
        """Pega o hideout pelo guild_id."""
        return await self.bot.db.fetchrow(
            "SELECT * FROM hideouts WHERE guild_id = $1",
            guild_id
        )

    async def recharge_hideout(self, guild_id: int):
        """Recarrega energia do hideout."""
        try:
            hideout = await self.get_hideout(guild_id)
            if not hideout:
                return None, "❌ Hideout não encontrado."

            now = datetime.utcnow()
            last = hideout["last_recharge"]

            if last and now - last < timedelta(hours=1):
                restante = timedelta(hours=1) - (now - last)
                minutos = int(restante.total_seconds() // 60)
                return False, f"⏳ O Hideout ainda está recarregando.\nVolta em **{minutos} min**."

            await self.bot.db.execute(
                """
                UPDATE hideouts
                SET energy = max_energy,
                    last_recharge = $1
                WHERE guild_id = $2
                """,
                now, guild_id
            )
            return True, "⚡ **Hideout recarregado!** Energia no talo."
        except Exception as e:
            return None, f"❌ Erro ao recarregar hideout: {str(e)}"

    async def get_all_hideouts(self):
        """Retorna todos os hideouts cadastrados."""
        return await self.bot.db.fetch("SELECT * FROM hideouts")

    async def validate_guild_leader_and_hideout(self, user_id: int):
        """Valida se o usuário é líder de uma guilda e se a guilda tem hideout."""
        guild = await self.bot.db.fetchrow(
            "SELECT id FROM guilds WHERE leader_id = $1",
            user_id
        )
        if not guild:
            return None, None, "❌ Você não é líder de nenhuma guilda registrada."

        guild_id = guild["id"]
        hideout = await self.get_hideout(guild_id)
        if not hideout:
            return guild_id, None, "❌ Nenhum Hideout encontrado para sua guilda."

        return guild_id, hideout, None

    # ======================================================
    # 🏰 GRUPO /ho
    # ======================================================
    ho = app_commands.Group(
        name="ho",
        description="Comandos do Hideout"
    )

    # -------------------------------
    # /ho create
    # -------------------------------
    @ho.command(name="create", description="Cria o Hideout da guilda (máx 7 por guilda)")
    async def ho_create(self, interaction: discord.Interaction):
        import random
        import json

        # Load Zahuv map names
        with open("data/maps_zahuv.json", "r", encoding="utf-8") as f:
            zahuv_data = json.load(f)

        guild = await self.bot.db.fetchrow(
            "SELECT id, name FROM guilds WHERE leader_id = $1",
            interaction.user.id
        )
        if not guild:
            return await interaction.response.send_message(
                "❌ Você não é líder de nenhuma guilda registrada.",
                ephemeral=True
            )

        guild_id = guild["id"]
        guild_name = guild["name"]

        # Check if guild already has 7 hideouts
        hideout_count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM hideouts WHERE guild_id = $1",
            guild_id
        )
        if hideout_count >= 7:
            return await interaction.response.send_message(
                "⚠️ Sua guilda já possui 7 Hideouts (limite máximo).",
                ephemeral=True
            )

        base_zone_id = await self.bot.db.fetchval(
            "SELECT zona_id FROM users WHERE discord_id = $1",
            interaction.user.id
        )
        if not base_zone_id:
            return await interaction.response.send_message(
                "❌ Não foi possível determinar a zona atual do líder.",
                ephemeral=True
            )

        base_zone = await self.bot.db.fetchrow(
            "SELECT nome FROM zone WHERE zone_id = $1",
            base_zone_id
        )
        if not base_zone:
            return await interaction.response.send_message(
                "❌ Zona base não encontrada.",
                ephemeral=True
            )

        # Verifica o tier da zona atual
        base_zone_tier = await self.bot.db.fetchval(
            "SELECT tier FROM zone WHERE zone_id = $1",
            base_zone_id
        )
        
        fictional_zone_name = None
        
        # Se for zona de Zahuv (special_initial), verifica limite de 5 HOs nessa zona
        if base_zone["nome"].startswith(("Ai'", "Et'", "Al'", "Jo'", "Ka'", "Lu'", "Xe'", "Ty'")):
            # É uma zona de Zahuv com special_initial
            # Verifica quantos HOs já existem nessa zona (apenas contando zonas clonadas)
            # Zonas de Zahuv são clonadas, então verificamos quantos hideouts têm zona_id diferente mas nome similar
            existing_hos = await self.bot.db.fetchval(
                """
                SELECT COUNT(DISTINCT h.zone_id)
                FROM hideouts h
                JOIN zone z ON z.zone_id = h.zone_id
                WHERE z.nome = $1 AND z.zone_id != $2
                """,
                base_zone["nome"],
                base_zone_id
            )
            
            if existing_hos >= 5:
                return await interaction.response.send_message(
                    "⚠️ Esta zona de Zahuv já possui 5 Hideouts clonados (limite máximo).",
                    ephemeral=True
                )
            
            # Escolhe um nome aleatório de Zahuv
            special_maps = [m for m in zahuv_data["maps"] if m.get("special_initial")]
            if special_maps:
                chosen_map = random.choice(special_maps)
                fictional_zone_name = chosen_map["name"]
        else:
            # Para zonas normais, verifica se já tem hideout
            existing_ho = await self.bot.db.fetchval(
                "SELECT 1 FROM hideouts WHERE zone_id = $1",
                base_zone_id
            )
            
            if existing_ho:
                return await interaction.response.send_message(
                    "⚠️ Esta zona já possui um Hideout instalado!",
                    ephemeral=True
                )

        try:
            zone_id = await self.clone_zone_for_hideout(base_zone_id, guild_id)
        except Exception:
            return await interaction.response.send_message(
                "❌ Falha ao clonar a zona do Hideout.",
                ephemeral=True
            )

        alliance_id = await self.bot.db.fetchval(
            "SELECT alliance_id FROM guild_alliances WHERE guild_id = $1",
            guild_id
        )

        # Se não tem nome especial de Zahuv, pega o nome da zona
        if not fictional_zone_name:
            zone_info = await self.bot.db.fetchrow(
                "SELECT nome FROM zone WHERE zone_id = $1",
                zone_id
            )
            fictional_zone_name = zone_info["nome"] if zone_info else "Hideout"
        
        try:
            await self.bot.db.execute(
                """
                INSERT INTO hideouts (guild_id, zone_id, name, alliance_id, energy, max_energy, level, durability, max_durability)
                VALUES ($1, $2, $3, $4, 100, 100, 1, 100, 100)
                """,
                guild_id, zone_id, fictional_zone_name, alliance_id
            )
        except Exception:
            await self.bot.db.execute(
                "DELETE FROM zone WHERE zone_id = $1",
                zone_id
            )
            return await interaction.response.send_message(
                "❌ Falha ao criar o Hideout. Zona clonada foi removida.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"🏰 **Hideout criado!** A base da guilda **{guild_name}** agora existe na zona **{fictional_zone_name}** ({hideout_count + 1}/7)."
        )


    # -------------------------------
    # /ho info
    # -------------------------------
    @ho.command(name="info", description="Mostra informações do Hideout")
    async def ho_info(self, interaction: discord.Interaction):
        guild_id, hideout, error_msg = await self.validate_guild_leader_and_hideout(interaction.user.id)
        if error_msg:
            return await interaction.response.send_message(error_msg, ephemeral=True)

        embed = discord.Embed(
            title=f"🏰 Hideout: {hideout['name']}",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name="🔼 Nível", value=hideout["level"], inline=False)
        embed.add_field(
            name="⚡ Energia",
            value=f"{hideout['energy']} / {hideout['max_energy']}",
            inline=False
        )
        
        # Mostra durabilidade se existir
        if hideout.get("durability") is not None:
            durability_bar = "█" * (hideout["durability"] // 10) + "░" * (10 - hideout["durability"] // 10)
            durability_status = "🟢 Ótimo" if hideout["durability"] > 70 else "🟡 Desgastado" if hideout["durability"] > 30 else "🔴 Crítico"
            embed.add_field(
                name="🛡️ Durabilidade",
                value=f"{durability_bar}\n{hideout['durability']}/100 | {durability_status}",
                inline=False
            )
            if hideout["energy"] == 0:
                embed.add_field(
                    name="⚠️ Aviso",
                    value="**Sem energia!** O Hideout está perdendo durabilidade. Recarregue-o urgentemente!",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)

    # -------------------------------
    # /ho recharge
    # -------------------------------
    @ho.command(name="recharge", description="Recarrega o Hideout")
    async def ho_recharge(self, interaction: discord.Interaction):
        guild_id, hideout, error_msg = await self.validate_guild_leader_and_hideout(interaction.user.id)
        if error_msg:
            return await interaction.response.send_message(error_msg, ephemeral=True)

        success, msg = await self.recharge_hideout(guild_id)
        await interaction.response.send_message(msg)

    # -------------------------------
    # /ho upgrade
    # -------------------------------
    @ho.command(name="upgrade", description="Evolui o Hideout")
    async def ho_upgrade(self, interaction: discord.Interaction):
        guild_id = await self.bot.db.fetchval(
            "SELECT id FROM guilds WHERE leader_id = $1",
            interaction.user.id
        )
        if not guild_id:
            return await interaction.response.send_message(
                "❌ Você não lidera nenhuma guilda registrada.",
                ephemeral=True
            )

        hideout = await self.get_hideout(guild_id)
        new_level = hideout["level"] + 1
        new_max_energy = 100 + new_level * 50

        await self.bot.db.execute(
            """
            UPDATE hideouts
            SET level = $1,
                max_energy = $2
            WHERE guild_id = $3
            """,
            new_level,
            new_max_energy,
            guild_id
        )

        await interaction.response.send_message(
            f"🚀 **Hideout evoluído!**\n"
            f"Nível: **{hideout['level']} → {new_level}**\n"
            f"Energia Máxima: **{new_max_energy}**"
        )

    @ho.command(name="zone", description="Mostra a zona do Hideout")
    async def ho_zone(self, interaction: discord.Interaction):
        guild_id, hideout, error_msg = await self.validate_guild_leader_and_hideout(interaction.user.id)
        if error_msg:
            return await interaction.response.send_message(error_msg, ephemeral=True)

        # Pega a zona associada
        zone = await self.bot.db.fetchrow(
            "SELECT * FROM zone WHERE zone_id = $1",
            hideout["zone_id"]
        )
        if not zone:
            return await interaction.response.send_message(
                "❌ Zona do Hideout não encontrada.",
                ephemeral=True
            )

        # Monta embed
        embed = discord.Embed(
            title=f"🗺️ Zona do Hideout: {zone['nome']}",
            color=discord.Color.green()
        )
        rank_emoji = depth_to_rank_emoji(zone["tier"])
        rank_name = depth_to_rank(zone["tier"])
        embed.add_field(name="Rank", value=f"{rank_emoji} {rank_name}")
        embed.add_field(name="Hideout Permanente?", value="✅" if zone["permanent"] else "❌")
        embed.add_field(name="É Hideout?", value="✅" if zone["is_hideout"] else "❌")

        await interaction.response.send_message(embed=embed)

    @ho.command(name="list", description="Lista todos os hideouts da sua guilda")
    async def ho_list(self, interaction: discord.Interaction):
        guild = await self.bot.db.fetchrow(
            "SELECT id, name FROM guilds WHERE leader_id = $1",
            interaction.user.id
        )
        if not guild:
            return await interaction.response.send_message(
                "❌ Você não é líder de nenhuma guilda registrada.",
                ephemeral=True
            )

        guild_id = guild["id"]
        
        # Lista todos os hideouts da guilda
        hideouts = await self.bot.db.fetch(
            """
            SELECT h.id, h.zone_id, h.name, h.level, h.energy, h.max_energy,
                   z.nome as zone_name, z.zone_id as zone_exists
            FROM hideouts h
            LEFT JOIN zone z ON z.zone_id = h.zone_id
            WHERE h.guild_id = $1
            ORDER BY h.id
            """,
            guild_id
        )
        
        if not hideouts:
            return await interaction.response.send_message(
                "📦 Sua guilda não possui hideouts ainda.\n\nUse `/ho create` para criar um!",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title=f"🏰 Hideouts de {guild['name']}",
            description=f"Total: **{len(hideouts)}/7** hideouts",
            color=discord.Color.dark_gold()
        )
        
        for ho in hideouts:
            # Verifica se a zona ainda existe
            if ho["zone_exists"] is None:
                status = "❌ **ZONA ÓRFÃ** (zona não existe mais)"
                zone_info = f"ID: `{ho['zone_id']}` (deletada)"
            else:
                status = "✅ Ativo"
                zone_info = f"**{ho['zone_name']}** (ID: `{ho['zone_id']}`)"
            
            durability_info = ""
            if ho.get("durability") is not None:
                durability_emoji = "🟢" if ho["durability"] > 70 else "🟡" if ho["durability"] > 30 else "🔴"
                durability_info = f" | {durability_emoji} Durabilidade: {ho['durability']}/100"
            
            embed.add_field(
                name=f"#{ho['id']} - {ho['name']}",
                value=(
                    f"{status}\n"
                    f"🗺️ Zona: {zone_info}\n"
                    f"⚡ Energia: {ho['energy']}/{ho['max_energy']} | 🔼 Nível: {ho['level']}{durability_info}"
                ),
                inline=False
            )
        
        embed.set_footer(text="Use /ho cleanup para remover hideouts órfãos")
        await interaction.response.send_message(embed=embed)

    @ho.command(name="cleanup", description="Remove hideouts com zonas que não existem mais")
    async def ho_cleanup(self, interaction: discord.Interaction):
        guild = await self.bot.db.fetchrow(
            "SELECT id, name FROM guilds WHERE leader_id = $1",
            interaction.user.id
        )
        if not guild:
            return await interaction.response.send_message(
                "❌ Você não é líder de nenhuma guilda registrada.",
                ephemeral=True
            )

        guild_id = guild["id"]
        
        # Encontra hideouts órfãos (zona não existe mais)
        orphaned = await self.bot.db.fetch(
            """
            SELECT h.id, h.name, h.zone_id
            FROM hideouts h
            WHERE h.guild_id = $1
            AND NOT EXISTS (SELECT 1 FROM zone z WHERE z.zone_id = h.zone_id)
            """,
            guild_id
        )
        
        if not orphaned:
            return await interaction.response.send_message(
                "✅ Todos os hideouts da sua guilda estão OK!\n\nNenhuma zona órfã encontrada.",
                ephemeral=True
            )
        
        # Remove os hideouts órfãos
        deleted_count = 0
        deleted_names = []
        for ho in orphaned:
            await self.bot.db.execute(
                "DELETE FROM hideouts WHERE id = $1",
                ho["id"]
            )
            deleted_count += 1
            deleted_names.append(f"• **{ho['name']}** (zona ID: `{ho['zone_id']}`)")
        
        embed = discord.Embed(
            title="🧹 Cleanup Concluído!",
            description=f"Removidos **{deleted_count}** hideout(s) órfão(s):",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Hideouts Removidos",
            value="\n".join(deleted_names),
            inline=False
        )
        embed.set_footer(text="Você pode criar novos hideouts com /ho create")
        
        await interaction.response.send_message(embed=embed)

    @ho.command(name="delete", description="Deleta um hideout específico pelo ID")
    @app_commands.describe(hideout_id="ID do hideout para deletar")
    async def ho_delete(self, interaction: discord.Interaction, hideout_id: int):
        guild = await self.bot.db.fetchrow(
            "SELECT id, name FROM guilds WHERE leader_id = $1",
            interaction.user.id
        )
        if not guild:
            return await interaction.response.send_message(
                "❌ Você não é líder de nenhuma guilda registrada.",
                ephemeral=True
            )

        guild_id = guild["id"]
        
        # Verifica se o hideout existe e pertence à guilda
        hideout = await self.bot.db.fetchrow(
            "SELECT id, name, zone_id FROM hideouts WHERE id = $1 AND guild_id = $2",
            hideout_id, guild_id
        )
        
        if not hideout:
            return await interaction.response.send_message(
                f"❌ Hideout ID `{hideout_id}` não encontrado ou não pertence à sua guilda.",
                ephemeral=True
            )
        
        # Deleta o hideout
        await self.bot.db.execute(
            "DELETE FROM hideouts WHERE id = $1",
            hideout_id
        )
        
        # Tenta deletar a zona também (se ainda existir)
        zone_deleted = False
        try:
            zone_exists = await self.bot.db.fetchval(
                "SELECT 1 FROM zone WHERE zone_id = $1",
                hideout["zone_id"]
            )
            if zone_exists:
                await self.bot.db.execute(
                    "DELETE FROM zone WHERE zone_id = $1",
                    hideout["zone_id"]
                )
                zone_deleted = True
        except Exception:
            pass
        
        embed = discord.Embed(
            title="🗑️ Hideout Deletado!",
            description=f"**{hideout['name']}** (ID: `{hideout_id}`) foi removido.",
            color=discord.Color.red()
        )
        if zone_deleted:
            embed.add_field(
                name="Zona",
                value=f"✅ Zona `{hideout['zone_id']}` também foi deletada",
                inline=False
            )
        else:
            embed.add_field(
                name="Zona",
                value=f"⚠️ Zona `{hideout['zone_id']}` não foi encontrada (já estava deletada)",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    # =========================
    # POWER SCORE SYSTEM
    # =========================
    
    async def calculate_power_score(self, user_id: int) -> int:
        """Calcula o Power Score do jogador baseado em arma e armadura equipadas"""
        user = await self.bot.db.fetchrow(
            """
            SELECT equipped_weapon, equipped_armor 
            FROM users 
            WHERE discord_id = $1
            """,
            user_id
        )
        
        if not user:
            return 0
        
        power_score = 0
        
        # Arma equipada
        if user['equipped_weapon']:
            weapon = await self.bot.db.fetchrow(
                "SELECT basedamage, tier FROM items WHERE id = $1",
                user['equipped_weapon']
            )
            if weapon:
                # Power = (basedamage * 2) + (tier * 50)
                power_score += (weapon['basedamage'] or 0) * 2 + weapon['tier'] * 50
        
        # Armadura equipada
        if user['equipped_armor']:
            armor = await self.bot.db.fetchrow(
                "SELECT basedefense, tier FROM items WHERE id = $1",
                user['equipped_armor']
            )
            if armor:
                # Power = (basedefense * 2) + (tier * 50)
                power_score += (armor['basedefense'] or 0) * 2 + armor['tier'] * 50
        
        return power_score

    # =========================
    # ENTRADA/SAÍDA DO HIDEOUT
    # =========================
    
    @ho.command(name="entrar", description="Entra no Hideout da sua guilda/aliança na zona atual")
    async def ho_entrar(self, interaction: discord.Interaction):
        # Verifica se o usuário está em uma guilda
        guild_member = await self.bot.db.fetchrow(
            "SELECT guild_id FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )
        
        if not guild_member:
            return await interaction.response.send_message(
                "❌ Você precisa estar em uma guilda para entrar em um Hideout!",
                ephemeral=True
            )
        
        # Pega a zona atual do usuário
        user = await self.bot.db.fetchrow(
            "SELECT zona_id, in_hideout_id FROM users WHERE discord_id = $1",
            interaction.user.id
        )
        
        if not user or not user['zona_id']:
            return await interaction.response.send_message(
                "❌ Você não está em nenhuma zona!",
                ephemeral=True
            )
        
        if user['in_hideout_id']:
            return await interaction.response.send_message(
                "❌ Você já está dentro de um Hideout! Use `/ho sair` primeiro.",
                ephemeral=True
            )
        
        current_zone_id = user['zona_id']
        guild_id = guild_member['guild_id']
        
        # Verifica se a guilda tem aliança
        alliance = await self.bot.db.fetchrow(
            "SELECT alliance_id FROM guild_alliances WHERE guild_id = $1",
            guild_id
        )
        
        # Procura Hideout da guilda ou da aliança nesta zona
        if alliance:
            hideout = await self.bot.db.fetchrow(
                """
                SELECT h.id, h.name, h.energy, h.has_crafting_station, h.has_dungeon_portal
                FROM hideouts h
                JOIN zone z ON h.zone_id = z.zone_id
                WHERE z.zone_id = $1 
                AND (h.guild_id = $2 OR h.alliance_id = $3)
                AND h.energy > 0
                """,
                current_zone_id, guild_id, alliance['alliance_id']
            )
        else:
            hideout = await self.bot.db.fetchrow(
                """
                SELECT h.id, h.name, h.energy, h.has_crafting_station, h.has_dungeon_portal
                FROM hideouts h
                JOIN zone z ON h.zone_id = z.zone_id
                WHERE z.zone_id = $1 
                AND h.guild_id = $2
                AND h.energy > 0
                """,
                current_zone_id, guild_id
            )
        
        if not hideout:
            return await interaction.response.send_message(
                "❌ Não há Hideout da sua guilda ou aliança nesta zona!",
                ephemeral=True
            )
        
        # Entra no hideout
        await self.bot.db.execute(
            """
            UPDATE users 
            SET in_hideout_id = $1, previous_zone_id = $2
            WHERE discord_id = $3
            """,
            hideout['id'], current_zone_id, interaction.user.id
        )
        
        # Calcula power score do usuário
        power_score = await self.calculate_power_score(interaction.user.id)
        
        embed = discord.Embed(
            title=f"🏠 Bem-vindo ao {hideout['name']}!",
            description="Você entrou no Hideout da sua guilda/aliança.",
            color=discord.Color.green()
        )
        embed.add_field(name="⚡ Energia", value=f"{hideout['energy']}%", inline=True)
        embed.add_field(name="💪 Seu Power Score", value=f"`{power_score}`", inline=True)
        
        facilities = []
        if hideout['has_crafting_station']:
            facilities.append("🔨 Estação de Crafting")
        if hideout['has_dungeon_portal']:
            facilities.append("🌀 Portal da Dungeon")
        
        if facilities:
            embed.add_field(
                name="🏗️ Instalações",
                value="\n".join(facilities),
                inline=False
            )
        
        embed.set_footer(text="Use /ho sair para retornar à zona anterior")
        
        await interaction.response.send_message(embed=embed)
    
    @ho.command(name="sair", description="Sai do Hideout e retorna à zona anterior")
    async def ho_sair(self, interaction: discord.Interaction):
        user = await self.bot.db.fetchrow(
            "SELECT in_hideout_id, previous_zone_id FROM users WHERE discord_id = $1",
            interaction.user.id
        )
        
        if not user or not user['in_hideout_id']:
            return await interaction.response.send_message(
                "❌ Você não está em nenhum Hideout!",
                ephemeral=True
            )
        
        previous_zone = user['previous_zone_id']
        
        # Remove do hideout
        await self.bot.db.execute(
            """
            UPDATE users 
            SET in_hideout_id = NULL, previous_zone_id = NULL
            WHERE discord_id = $1
            """,
            interaction.user.id
        )
        
        zone_name = "a zona anterior"
        if previous_zone:
            zone_data = await self.bot.db.fetchrow(
                "SELECT nome FROM zone WHERE zone_id = $1",
                previous_zone
            )
            if zone_data:
                zone_name = zone_data['nome']
        
        embed = discord.Embed(
            title="👋 Saindo do Hideout",
            description=f"Você voltou para **{zone_name}**.",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)

    # =========================
    # CRAFTING SYSTEM
    # =========================
    
    @ho.command(name="craft", description="Crafta um item especial no Hideout")
    @app_commands.describe(recipe_id="ID da receita para craftar")
    async def ho_craft(self, interaction: discord.Interaction, recipe_id: int):
        # Verifica se está no hideout
        user = await self.bot.db.fetchrow(
            "SELECT in_hideout_id FROM users WHERE discord_id = $1",
            interaction.user.id
        )
        
        if not user or not user['in_hideout_id']:
            return await interaction.response.send_message(
                "❌ Você precisa estar dentro de um Hideout para craftar!",
                ephemeral=True
            )
        
        hideout_id = user['in_hideout_id']
        
        # Verifica se o hideout tem estação de crafting
        hideout = await self.bot.db.fetchrow(
            "SELECT has_crafting_station, level FROM hideouts WHERE id = $1",
            hideout_id
        )
        
        if not hideout['has_crafting_station']:
            return await interaction.response.send_message(
                "❌ Este Hideout não possui uma Estação de Crafting!",
                ephemeral=True
            )
        
        # Busca a receita
        recipe = await self.bot.db.fetchrow(
            """
            SELECT r.*, i.name as result_name
            FROM hideout_recipes r
            JOIN items i ON r.result_item_id = i.id
            WHERE r.id = $1
            """,
            recipe_id
        )
        
        if not recipe:
            return await interaction.response.send_message(
                "❌ Receita não encontrada!",
                ephemeral=True
            )
        
        if recipe['min_hideout_level'] > hideout['level']:
            return await interaction.response.send_message(
                f"❌ Este Hideout precisa estar no nível {recipe['min_hideout_level']} para esta receita!",
                ephemeral=True
            )
        
        # Verifica materiais necessários
        materials = await self.bot.db.fetch(
            """
            SELECT rm.item_id, rm.quantity, i.name
            FROM hideout_recipe_materials rm
            JOIN items i ON rm.item_id = i.id
            WHERE rm.recipe_id = $1
            """,
            recipe_id
        )
        
        # Verifica se o player tem os materiais
        missing_materials = []
        for mat in materials:
            player_qty = await self.bot.db.fetchval(
                "SELECT quantidade FROM inventario WHERE user_id = $1 AND item_id = $2",
                interaction.user.id, mat['item_id']
            ) or 0
            
            if player_qty < mat['quantity']:
                missing_materials.append(f"{mat['name']} ({player_qty}/{mat['quantity']})")
        
        if missing_materials:
            return await interaction.response.send_message(
                f"❌ Materiais insuficientes:\n" + "\n".join(missing_materials),
                ephemeral=True
            )
        
        # Remove materiais
        for mat in materials:
            await self.bot.db.execute(
                """
                UPDATE inventario 
                SET quantidade = quantidade - $1
                WHERE user_id = $2 AND item_id = $3
                """,
                mat['quantity'], interaction.user.id, mat['item_id']
            )
        
        # Adiciona à fila de crafting
        finish_time = datetime.now() + timedelta(seconds=recipe['craft_time_seconds'])
        await self.bot.db.execute(
            """
            INSERT INTO hideout_crafting_queue 
            (hideout_id, user_id, recipe_id, finishes_at)
            VALUES ($1, $2, $3, $4)
            """,
            hideout_id, interaction.user.id, recipe_id, finish_time
        )
        
        embed = discord.Embed(
            title="🔨 Crafting Iniciado!",
            description=f"Craftando **{recipe['result_name']}** x{recipe['result_quantity']}",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="⏳ Tempo",
            value=f"{recipe['craft_time_seconds']} segundos",
            inline=True
        )
        embed.add_field(
            name="✅ Pronto em",
            value=f"<t:{int(finish_time.timestamp())}:R>",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @ho.command(name="recipes", description="Lista receitas de crafting disponíveis")
    async def ho_recipes(self, interaction: discord.Interaction):
        recipes = await self.bot.db.fetch(
            """
            SELECT r.id, r.name, r.description, r.min_hideout_level, 
                   i.name as result_name, r.result_quantity
            FROM hideout_recipes r
            JOIN items i ON r.result_item_id = i.id
            ORDER BY r.min_hideout_level, r.id
            """
        )
        
        if not recipes:
            return await interaction.response.send_message(
                "❌ Nenhuma receita disponível no momento.",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title="📜 Receitas de Crafting do Hideout",
            description="Use `/ho craft <recipe_id>` para craftar",
            color=discord.Color.purple()
        )
        
        for recipe in recipes[:25]:  # Limite de fields
            materials = await self.bot.db.fetch(
                """
                SELECT i.name, rm.quantity
                FROM hideout_recipe_materials rm
                JOIN items i ON rm.item_id = i.id
                WHERE rm.recipe_id = $1
                """,
                recipe['id']
            )
            
            mat_text = ", ".join([f"{m['name']} x{m['quantity']}" for m in materials])
            
            embed.add_field(
                name=f"[{recipe['id']}] {recipe['name']} (Nv.{recipe['min_hideout_level']}+)",
                value=f"🎁 **{recipe['result_name']}** x{recipe['result_quantity']}\n"
                      f"📦 {mat_text or 'Sem materiais'}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    # =========================
    # HIDEOUT DUNGEON SYSTEM
    # =========================
    
    @ho.command(name="dungeon", description="Inicia a Dungeon especial do Hideout (requer 5 pessoas e 1500 power)")
    async def ho_dungeon(self, interaction: discord.Interaction):
        # Verifica se está no hideout
        user = await self.bot.db.fetchrow(
            "SELECT in_hideout_id FROM users WHERE discord_id = $1",
            interaction.user.id
        )
        
        if not user or not user['in_hideout_id']:
            return await interaction.response.send_message(
                "❌ Você precisa estar dentro de um Hideout!",
                ephemeral=True
            )
        
        hideout_id = user['in_hideout_id']
        
        # Verifica se o hideout tem portal de dungeon
        hideout = await self.bot.db.fetchrow(
            """
            SELECT has_dungeon_portal, dungeon_cooldown, level, name
            FROM hideouts WHERE id = $1
            """,
            hideout_id
        )
        
        if not hideout['has_dungeon_portal']:
            return await interaction.response.send_message(
                "❌ Este Hideout não possui Portal de Dungeon!",
                ephemeral=True
            )
        
        # Verifica cooldown
        if hideout['dungeon_cooldown'] and hideout['dungeon_cooldown'] > datetime.now():
            cooldown_end = int(hideout['dungeon_cooldown'].timestamp())
            return await interaction.response.send_message(
                f"❌ A Dungeon está em cooldown! Disponível <t:{cooldown_end}:R>",
                ephemeral=True
            )
        
        # Verifica se o usuário tem party ativa (você precisa importar do party_raid)
        from ..party.party_raid import party_manager
        
        party = party_manager.get_party(interaction.user.id)
        if not party:
            return await interaction.response.send_message(
                "❌ Você precisa estar em uma party! Use `/party_create` primeiro.",
                ephemeral=True
            )
        
        # Verifica se todos os membros estão no hideout
        members_in_ho = []
        members_not_in_ho = []
        total_power = 0
        
        for member_id in party.members:
            member_data = await self.bot.db.fetchrow(
                "SELECT in_hideout_id FROM users WHERE discord_id = $1",
                member_id
            )
            
            if member_data and member_data['in_hideout_id'] == hideout_id:
                power = await self.calculate_power_score(member_id)
                members_in_ho.append((member_id, power))
                total_power += power
            else:
                members_not_in_ho.append(f"<@{member_id}>")
        
        if len(members_in_ho) < 5:
            msg = f"❌ A Dungeon requer 5 pessoas no Hideout! ({len(members_in_ho)}/5)"
            if members_not_in_ho:
                msg += f"\n\nMembros fora do HO: {', '.join(members_not_in_ho)}"
            return await interaction.response.send_message(msg, ephemeral=True)
        
        if total_power < 1500:
            return await interaction.response.send_message(
                f"❌ Power Score insuficiente! A party precisa de 1500+ de poder total.\n"
                f"**Poder Atual:** {total_power}/1500",
                ephemeral=True
            )
        
        # Cria a dungeon run
        difficulty_tier = hideout['level']  # Dificuldade baseada no nível do HO
        
        run_id = await self.bot.db.fetchval(
            """
            INSERT INTO hideout_dungeon_runs 
            (hideout_id, party_leader_id, total_power_score, difficulty_tier)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            hideout_id, interaction.user.id, total_power, difficulty_tier
        )
        
        # Adiciona membros da party
        for member_id, power in members_in_ho:
            await self.bot.db.execute(
                """
                INSERT INTO hideout_dungeon_party (run_id, user_id, power_score)
                VALUES ($1, $2, $3)
                """,
                run_id, member_id, power
            )
        
        # Define cooldown (1 hora)
        cooldown_time = datetime.now() + timedelta(hours=1)
        await self.bot.db.execute(
            "UPDATE hideouts SET dungeon_cooldown = $1 WHERE id = $2",
            cooldown_time, hideout_id
        )
        
        embed = discord.Embed(
            title=f"🌀 Dungeon Iniciada: {hideout['name']}",
            description=f"A party entrou na dungeon especial!",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="👥 Membros", value=str(len(members_in_ho)), inline=True)
        embed.add_field(name="💪 Power Total", value=f"{total_power}", inline=True)
        rank_emoji = depth_to_rank_emoji(difficulty_tier)
        rank_name = depth_to_rank_abbr(difficulty_tier)
        embed.add_field(name="🔥 Dificuldade", value=f"{rank_emoji} {rank_name}-Rank", inline=True)
        
        member_list = "\n".join([f"<@{mid}>: `{pwr}` power" for mid, pwr in members_in_ho])
        embed.add_field(name="Party", value=member_list, inline=False)
        
        embed.set_footer(text=f"Run ID: {run_id} | Cooldown: 1 hora")
        
        await interaction.response.send_message(embed=embed)
        
        # Simula batalha (você pode expandir isso)
        await self._simulate_dungeon_battle(interaction, run_id, members_in_ho, difficulty_tier)
    
    async def _simulate_dungeon_battle(self, interaction, run_id, members, difficulty_tier):
        """Simula a batalha da dungeon e distribui recompensas"""
        import asyncio
        await asyncio.sleep(3)
        
        # Chance de sucesso baseada no poder total vs dificuldade
        success = random.random() < 0.7  # 70% de chance base
        
        # Atualiza a run
        await self.bot.db.execute(
            """
            UPDATE hideout_dungeon_runs 
            SET completed_at = NOW(), success = $1
            WHERE id = $2
            """,
            success, run_id
        )
        
        if success:
            # Gera recompensas
            for member_id, power in members:
                # Recompensa proporcional ao poder
                gold_reward = difficulty_tier * 10000 + (power * 100)
                
                await self.bot.db.execute(
                    """
                    INSERT INTO hideout_dungeon_rewards 
                    (run_id, user_id, gold_reward)
                    VALUES ($1, $2, $3)
                    """,
                    run_id, member_id, gold_reward
                )
                
                # Adiciona gold ao player
                await self.bot.db.execute(
                    "UPDATE users SET gold = gold + $1 WHERE discord_id = $2",
                    gold_reward, member_id
                )
            
            embed = discord.Embed(
                title="✅ Dungeon Completa!",
                description="A party derrotou todos os inimigos!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🏆 Recompensas",
                value=f"Cada membro recebeu gold baseado em seu poder!",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Dungeon Falhou",
                description="A party foi derrotada...",
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed)
    
    @ho.command(name="facility", description="Adiciona instalações ao Hideout (Crafting/Dungeon)")
    @app_commands.describe(
        upgrade_type="Tipo de instalação: crafting, dungeon"
    )
    @app_commands.choices(upgrade_type=[
        app_commands.Choice(name="Estação de Crafting", value="crafting"),
        app_commands.Choice(name="Portal da Dungeon", value="dungeon")
    ])
    async def ho_facility(self, interaction: discord.Interaction, upgrade_type: str):
        # Verifica se é líder da guilda
        guild = await self.bot.db.fetchrow(
            "SELECT id, name, gold FROM guilds WHERE leader_id = $1",
            interaction.user.id
        )
        
        if not guild:
            return await interaction.response.send_message(
                "❌ Você não é líder de nenhuma guilda!",
                ephemeral=True
            )
        
        # Lista hideouts da guilda
        hideouts = await self.bot.db.fetch(
            """
            SELECT id, name, has_crafting_station, has_dungeon_portal, level
            FROM hideouts WHERE guild_id = $1
            """,
            guild['id']
        )
        
        if not hideouts:
            return await interaction.response.send_message(
                "❌ Sua guilda não possui Hideouts!",
                ephemeral=True
            )
        
        # Para simplificar, pega o primeiro hideout
        hideout = hideouts[0]
        
        cost = 500000  # 500k gold
        
        if upgrade_type == "crafting":
            if hideout['has_crafting_station']:
                return await interaction.response.send_message(
                    "❌ Este Hideout já possui Estação de Crafting!",
                    ephemeral=True
                )
            
            if guild['gold'] < cost:
                return await interaction.response.send_message(
                    f"❌ Gold insuficiente! Custo: {cost:,} gold",
                    ephemeral=True
                )
            
            await self.bot.db.execute(
                "UPDATE hideouts SET has_crafting_station = TRUE WHERE id = $1",
                hideout['id']
            )
            await self.bot.db.execute(
                "UPDATE guilds SET gold = gold - $1 WHERE id = $2",
                cost, guild['id']
            )
            
            embed = discord.Embed(
                title="🔨 Estação de Crafting Construída!",
                description=f"**{hideout['name']}** agora possui uma estação de crafting!",
                color=discord.Color.gold()
            )
        
        else:  # dungeon
            if hideout['has_dungeon_portal']:
                return await interaction.response.send_message(
                    "❌ Este Hideout já possui Portal da Dungeon!",
                    ephemeral=True
                )
            
            if guild['gold'] < cost:
                return await interaction.response.send_message(
                    f"❌ Gold insuficiente! Custo: {cost:,} gold",
                    ephemeral=True
                )
            
            await self.bot.db.execute(
                "UPDATE hideouts SET has_dungeon_portal = TRUE WHERE id = $1",
                hideout['id']
            )
            await self.bot.db.execute(
                "UPDATE guilds SET gold = gold - $1 WHERE id = $2",
                cost, guild['id']
            )
            
            embed = discord.Embed(
                title="🌀 Portal da Dungeon Ativado!",
                description=f"**{hideout['name']}** agora possui acesso à dungeon especial!",
                color=discord.Color.purple()
            )
        
        embed.add_field(name="💰 Custo", value=f"{cost:,} gold", inline=True)
        embed.add_field(name="💳 Gold Restante", value=f"{guild['gold'] - cost:,}", inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Hideout(bot))
