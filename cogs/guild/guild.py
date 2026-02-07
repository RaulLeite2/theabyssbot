import discord
from discord import app_commands
from discord.ext import commands

class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    guild = app_commands.Group(name="guild", description="Comandos de guildas")

    # =========================
    # GUILD CREATE
    # =========================
    @guild.command(name="create", description="Cria uma guilda")
    async def create(self, interaction: discord.Interaction, name: str):
        # Check if user is already in a guild
        exists = await self.bot.db.fetchrow("SELECT 1 FROM guild_members WHERE user_id = $1", interaction.user.id)
        if exists:
            return await interaction.response.send_message("🚫 Você já faz parte de uma guilda.", ephemeral=True)

        # Check if guild name already exists
        name_exists = await self.bot.db.fetchrow("SELECT 1 FROM guilds WHERE name = $1", name)
        if name_exists:
            return await interaction.response.send_message("🚫 Já existe uma guilda com esse nome.", ephemeral=True)

        try:
            guild_id = await self.bot.db.fetchval(
                "INSERT INTO guilds (name, leader_id) VALUES ($1, $2) RETURNING id",
                name, interaction.user.id
            )
            await self.bot.db.execute(
                "INSERT INTO guild_members (user_id, guild_id, role) VALUES ($1, $2, 'leader')",
                interaction.user.id, guild_id
            )
            await self.bot.db.execute(
                """
                INSERT INTO guild_logs (guild_id, user_id, action)
                VALUES ($1, $2, $3)
                """,
                guild_id,
                interaction.user.id,
                f"Guilda criada por {interaction.user.display_name}"
            )
            await interaction.response.send_message(f"🏰 **Guilda criada!**\nO estandarte de **{name}** foi erguido.\n👑 Líder: {interaction.user.mention}")
        except Exception as e:
            # Log error and respond
            print(f"Error creating guild: {e}")
            await interaction.response.send_message("🚫 Erro ao criar guilda. Tente novamente.", ephemeral=True)


    # =========================
    # GUILD INVITE
    # =========================
    @guild.command(name="invite", description="Convida alguém para a guilda")
    async def invite(self, interaction: discord.Interaction, member: discord.Member):

        data = await self.bot.db.fetchrow(
            """
            SELECT g.id AS guild_id, g.name, gm.role
            FROM guild_members gm
            JOIN guilds g ON g.id = gm.guild_id
            WHERE gm.user_id = $1
            """,
            interaction.user.id
        )

        if not data or data["role"] not in ("leader", "officer"):
            return await interaction.response.send_message(
                "🚫 Só o líder ou oficiais podem convidar.",
                ephemeral=True
            )

        target = await self.bot.db.fetchrow(
            "SELECT 1 FROM guild_members WHERE user_id = $1",
            member.id
        )
        if target:
            return await interaction.response.send_message(
                "🚫 Esse jogador já pertence a uma guilda.",
                ephemeral=True
            )

        class InviteView(discord.ui.View):
            def __init__(self, bot):
                super().__init__(timeout=60)
                self.bot = bot

            @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.green)
            async def accept(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                if interaction_btn.user.id != member.id:
                    return await interaction_btn.response.send_message(
                        "🚫 Esse convite não é pra você.",
                        ephemeral=True
                    )

                exists = await self.bot.db.fetchrow(
                    "SELECT 1 FROM guild_members WHERE user_id = $1",
                    member.id
                )
                if exists:
                    return await interaction_btn.response.send_message(
                        "🚫 Você já está em uma guilda.",
                        ephemeral=True
                    )

                await self.bot.db.execute(
                    """
                    INSERT INTO guild_members (user_id, guild_id, role)
                    VALUES ($1, $2, 'member')
                    """,
                    member.id,
                    data["guild_id"]
                )

                await interaction_btn.response.send_message(
                    f"✅ Você entrou na guilda **{data['name']}**!"
                )
                await self.bot.db.execute(
                    """
                    INSERT INTO guild_logs (guild_id, user_id, action)
                    VALUES ($1, $2, $3)
                    """,
                    data["guild_id"],
                    member.id,
                    f"{member.display_name} entrou na guilda"
                )
                self.stop()


            @discord.ui.button(label="Recusar", style=discord.ButtonStyle.red)
            async def decline(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                if interaction_btn.user.id != member.id:
                    return await interaction_btn.response.send_message(
                        "🚫 Esse convite não é pra você.",
                        ephemeral=True
                    )

                await interaction_btn.response.send_message(
                    "❌ Convite recusado."
                )
                self.stop()

        try:
            await member.send(
                f"📜 **Convite de Guilda**\n\n"
                f"Você foi convidado para entrar na guilda **{data['name']}**.\n"
                f"Deseja aceitar?",
                view=InviteView(self.bot)
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "🚫 Não consegui mandar DM para esse jogador.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"📨 Convite enviado para {member.mention}.",
            ephemeral=True
        )

    # =========================
    # GUILD LEAVE
    # =========================
    @guild.command(name="leave", description="Sai da guilda")
    async def leave(self, interaction: discord.Interaction):
        data = await self.bot.db.fetchrow("SELECT role FROM guild_members WHERE user_id = $1", interaction.user.id)
        if not data:
            return await interaction.response.send_message("🚫 Você não faz parte de nenhuma guilda.", ephemeral=True)

        if data["role"] == "leader":
            return await interaction.response.send_message("🚫 O líder não pode abandonar a própria guilda.", ephemeral=True)

        await self.bot.db.execute("DELETE FROM guild_members WHERE user_id = $1", interaction.user.id)
        await interaction.response.send_message("🚪 Você deixou a guilda. O Abismo segue.")
        await self.bot.db.execute(
            """
            INSERT INTO guild_logs (guild_id, user_id, action)
            VALUES ($1, $2, $3)
            """,
            data["guild_id"],
            interaction.user.id,
            f"{interaction.user.display_name} saiu da guilda"
        )

    # =========================
    # GUILD KICK
    # =========================
    @guild.command(name="kick", description="Expulsa um membro da guilda")
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        actor = await self.bot.db.fetchrow("SELECT guild_id, role FROM guild_members WHERE user_id = $1", interaction.user.id)
        target = await self.bot.db.fetchrow("SELECT guild_id, role FROM guild_members WHERE user_id = $1", member.id)

        if not actor or actor["role"] not in ("leader", "officer"):
            return await interaction.response.send_message("🚫 Você não manda aqui.", ephemeral=True)
        if not target or target["guild_id"] != actor["guild_id"]:
            return await interaction.response.send_message("🚫 Esse jogador não pertence à sua guilda.", ephemeral=True)
        if target["role"] == "leader":
            return await interaction.response.send_message("🚫 Não se chuta o líder.", ephemeral=True)
        if actor["role"] == "officer" and target["role"] == "officer":
            return await interaction.response.send_message("🚫 Oficiais não expulsam oficiais.", ephemeral=True)

        await self.bot.db.execute("DELETE FROM guild_members WHERE user_id = $1", member.id)
        await interaction.response.send_message(f"🪓 {member.mention} foi expulso da guilda.")
        await self.bot.db.execute(
            """
            INSERT INTO guild_logs (guild_id, user_id, action)
            VALUES ($1, $2, $3)
            """,
            actor["guild_id"],
            interaction.user.id,
            f"{member.display_name} foi expulso da guilda"
        )

    # =========================
    # GUILD PROMOTE
    # =========================
    @guild.command(name="promote", description="Promove um membro a oficial")
    async def promote(self, interaction: discord.Interaction, member: discord.Member):
        actor = await self.bot.db.fetchrow("SELECT guild_id, role FROM guild_members WHERE user_id = $1", interaction.user.id)
        if not actor or actor["role"] != "leader":
            return await interaction.response.send_message("🚫 Só o líder concede poder.", ephemeral=True)

        if member.id == interaction.user.id:
            return await interaction.response.send_message("🚫 Você não pode promover a si mesmo.", ephemeral=True)

        target = await self.bot.db.fetchrow("SELECT role FROM guild_members WHERE user_id = $1 AND guild_id = $2", member.id, actor["guild_id"])
        if not target:
            return await interaction.response.send_message("🚫 Esse membro não pertence à sua guilda.", ephemeral=True)
        if target["role"] == "officer":
            return await interaction.response.send_message("🚫 Esse membro já é oficial.", ephemeral=True)
        if target["role"] == "leader":
            return await interaction.response.send_message("🚫 O líder não pode ser promovido.", ephemeral=True)

        await self.bot.db.execute("UPDATE guild_members SET role = 'officer' WHERE user_id = $1 AND guild_id = $2", member.id, actor["guild_id"])
        await interaction.response.send_message(f"⚔️ {member.mention} agora é **Oficial**.")
        await self.bot.db.execute(
            """
            INSERT INTO guild_logs (guild_id, user_id, action)
            VALUES ($1, $2, $3)
            """,
            actor["guild_id"],
            interaction.user.id,
            f"{member.display_name} foi promovido a officer"
        )

    # =========================
    # GUILD INFO
    # =========================
    @guild.command(name="info", description="Mostra informações da guilda")
    async def info(self, interaction: discord.Interaction):
        data = await self.bot.db.fetchrow(
            """
            SELECT g.id, g.name, g.created_at, u.discord_id,
                   g.season_fame, g.total_fame, g.current_league, g.league_icon
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            JOIN users u ON u.discord_id = g.leader_id
            WHERE gm.user_id = $1
            """,
            interaction.user.id
        )
        if not data:
            return await interaction.response.send_message("🚫 Você não pertence a nenhuma guilda.", ephemeral=True)

        members = await self.bot.db.fetchval("SELECT COUNT(*) FROM guild_members WHERE guild_id = $1", data["id"])
        
        # Busca posição no ranking
        rank = await self.bot.db.fetchval(
            "SELECT COUNT(*) + 1 FROM guilds WHERE season_fame > $1",
            data['season_fame']
        )
        
        embed = discord.Embed(title=f"🏰 {data['name']}", color=discord.Color.dark_gold())
        embed.add_field(name="👥 Membros", value=members, inline=True)
        embed.add_field(name="📅 Fundação", value=data["created_at"].strftime("%d/%m/%Y"), inline=True)
        
        # Liga e ranking
        fame_str = f"{data['season_fame'] / 1_000_000:.1f}M" if data['season_fame'] >= 1_000_000 else f"{data['season_fame'] / 1_000:.1f}K" if data['season_fame'] >= 1_000 else str(data['season_fame'])
        embed.add_field(
            name=f"{data['league_icon']} Liga {data['current_league']}",
            value=f"Rank #{rank} | {fame_str} fama",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    # =========================
    # GUILD MEMBERS
    # =========================
    @guild.command(name="members", description="Lista os membros da guilda")
    async def members(self, interaction: discord.Interaction):

        data = await self.bot.db.fetchrow(
            "SELECT guild_id FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )
        if not data:
            return await interaction.response.send_message("🚫 Você não está em uma guilda.", ephemeral=True)

        rows = await self.bot.db.fetch(
            """
            SELECT user_id, role
            FROM guild_members
            WHERE guild_id = $1
            ORDER BY role DESC
            """,
            data["guild_id"]
        )

        desc = ""
        for r in rows:
            member = interaction.guild.get_member(r["user_id"])
            name = member.display_name if member else f"ID <@{r['user_id']}>"
            desc += f"• **{name}** — `{r['role']}`\n"

        await interaction.response.send_message(
            f"👥 **Membros da Guilda**\n\n{desc}"
        )

    # =========================
    # GUILD DEMOTE
    # =========================
    @guild.command(name="demote", description="Rebaixa um membro")
    async def demote(self, interaction: discord.Interaction, member: discord.Member):

        data = await self.bot.db.fetchrow(
            "SELECT guild_id, role FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )

        if not data or data["role"] != "leader":
            return await interaction.response.send_message("🚫 Só o líder pode rebaixar.", ephemeral=True)

        if member.id == interaction.user.id:
            return await interaction.response.send_message("🚫 Você não pode rebaixar a si mesmo.", ephemeral=True)

        target = await self.bot.db.fetchrow(
            "SELECT role FROM guild_members WHERE user_id = $1 AND guild_id = $2",
            member.id, data["guild_id"]
        )

        if not target:
            return await interaction.response.send_message("🚫 Esse membro não pertence à sua guilda.", ephemeral=True)
        if target["role"] != "officer":
            return await interaction.response.send_message("🚫 Esse membro não é officer.", ephemeral=True)

        await self.bot.db.execute(
            "UPDATE guild_members SET role = 'member' WHERE user_id = $1",
            member.id
        )

        await interaction.response.send_message(
            f"⬇️ {member.mention} foi rebaixado para **member**."
        )
        await self.bot.db.execute(
            """
            INSERT INTO guild_logs (guild_id, user_id, action)
            VALUES ($1, $2, $3)
            """,
            data["guild_id"],
            interaction.user.id,
            f"{member.display_name} foi rebaixado para member"
        )


    # =========================
    # GUILD TRANSFER
    # =========================
    @guild.command(name="transfer", description="Transfere a liderança da guilda")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member):

        data = await self.bot.db.fetchrow(
            "SELECT guild_id, role FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )

        if not data or data["role"] != "leader":
            return await interaction.response.send_message("🚫 Só o líder pode transferir.", ephemeral=True)

        if member.id == interaction.user.id:
            return await interaction.response.send_message("🚫 Você não pode transferir liderança para si mesmo.", ephemeral=True)

        target = await self.bot.db.fetchrow(
            "SELECT role FROM guild_members WHERE user_id = $1 AND guild_id = $2",
            member.id, data["guild_id"]
        )
        if not target:
            return await interaction.response.send_message("🚫 Esse usuário não está na guilda.", ephemeral=True)
        if target["role"] == "leader":
            return await interaction.response.send_message("🚫 Esse usuário já é o líder.", ephemeral=True)

        await self.bot.db.execute(
            "UPDATE guild_members SET role = 'leader' WHERE user_id = $1",
            member.id
        )
        await self.bot.db.execute(
            "UPDATE guild_members SET role = 'member' WHERE user_id = $1",
            interaction.user.id
        )

        await interaction.response.send_message(
            f"👑 {member.mention} agora é o novo **líder da guilda**."
        )
        await self.bot.db.execute(
            """
            INSERT INTO guild_logs (guild_id, user_id, action)
            VALUES ($1, $2, $3)
            """,
            data["guild_id"],
            interaction.user.id,
            f"Liderança transferida para {member.display_name}"
        )

    # =========================
    # GUILD DISBAND
    # =========================
    @guild.command(name="disband", description="Dissolve a guilda")
    async def disband(self, interaction: discord.Interaction):

        data = await self.bot.db.fetchrow(
            "SELECT guild_id, role FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )

        if not data or data["role"] != "leader":
            return await interaction.response.send_message("🚫 Só o líder pode dissolver a guilda.", ephemeral=True)

        # Check if there are other members
        member_count = await self.bot.db.fetchval("SELECT COUNT(*) FROM guild_members WHERE guild_id = $1", data["guild_id"])
        if member_count > 1:
            return await interaction.response.send_message("🚫 Você não pode dissolver a guilda enquanto houver outros membros.", ephemeral=True)

        # Clean up all references before deleting guild
        # 1. Remove hideouts and their zones
        hideout_zones = await self.bot.db.fetch(
            "SELECT zone_id FROM hideouts WHERE guild_id = $1",
            data["guild_id"]
        )
        for hz in hideout_zones:
            await self.bot.db.execute("DELETE FROM events WHERE zone_id = $1", hz["zone_id"])
            await self.bot.db.execute("DELETE FROM zone WHERE zone_id = $1", hz["zone_id"])
        
        await self.bot.db.execute("DELETE FROM hideouts WHERE guild_id = $1", data["guild_id"])
        
        # 2. Remove guild ownership from zones
        await self.bot.db.execute("UPDATE zone SET owner_guild = NULL WHERE owner_guild = $1", data["guild_id"])
        
        # 3. Leave alliance if in one
        await self.bot.db.execute("DELETE FROM guild_alliances WHERE guild_id = $1", data["guild_id"])
        
        # 4. Delete guild logs
        await self.bot.db.execute("DELETE FROM guild_logs WHERE guild_id = $1", data["guild_id"])
        
        # 5. Delete guild members
        await self.bot.db.execute(
            "DELETE FROM guild_members WHERE guild_id = $1",
            data["guild_id"]
        )
        
        # 6. Finally, delete the guild
        await self.bot.db.execute(
            "DELETE FROM guilds WHERE id = $1",
            data["guild_id"]
        )

        await interaction.response.send_message(
            "💥 A guilda foi dissolvida. Fim de uma era."
        )
        # Note: Logging after deletion might not be possible, but since disband is final, we skip logging here

    # =========================
    # GUILD LOGS
    # =========================
    @guild.command(name="logs", description="Mostra o histórico da guilda")
    async def logs(self, interaction: discord.Interaction):

        data = await self.bot.db.fetchrow(
            "SELECT guild_id FROM guild_members WHERE user_id = $1",
            interaction.user.id
        )
        if not data:
            return await interaction.response.send_message(
                "🚫 Você não pertence a nenhuma guilda.",
                ephemeral=True
            )

        rows = await self.bot.db.fetch(
            """
            SELECT action, created_at
            FROM guild_logs
            WHERE guild_id = $1
            ORDER BY created_at DESC
            LIMIT 10
            """,
            data["guild_id"]
        )

        if not rows:
            return await interaction.response.send_message(
                "📜 Nenhum registro encontrado."
            )

        desc = ""
        for r in rows:
            date = r["created_at"].strftime("%d/%m %H:%M")
            desc += f"• `{date}` — {r['action']}\n"

        embed = discord.Embed(
            title="📜 Histórico da Guilda",
            description=desc,
            color=discord.Color.dark_grey()
        )

        await interaction.response.send_message(embed=embed)


# =========================
# SETUP
# =========================
async def setup(bot: commands.Bot):
    await bot.add_cog(Guild(bot))
