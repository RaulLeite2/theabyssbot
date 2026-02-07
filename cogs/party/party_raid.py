import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json


class PartyRaid(commands.Cog):
    """Party system with buffs sharing, invites, and raid ready/start flow."""
    party = app_commands.Group(name="party", description="Comandos de party")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_tables(self):
        try:
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS parties (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE,
                    leader BIGINT NOT NULL
                )
                """
            )
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS party_members (
                    party_id INTEGER REFERENCES parties(id) ON DELETE CASCADE,
                    user_id BIGINT NOT NULL,
                    joined_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(party_id,user_id)
                )
                """
            )
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS party_invites (
                    party_id INTEGER REFERENCES parties(id) ON DELETE CASCADE,
                    invited BIGINT NOT NULL,
                    inviter BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(party_id, invited)
                )
                """
            )
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS party_buffs (
                    party_id INTEGER PRIMARY KEY,
                    buff JSONB,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
                """
            )
            await self.bot.db.execute(
                """
                CREATE TABLE IF NOT EXISTS raid_ready (
                    party_id INTEGER PRIMARY KEY,
                    ready BOOLEAN DEFAULT FALSE,
                    started BOOLEAN DEFAULT FALSE,
                    started_at TIMESTAMP
                )
                """
            )
        except Exception:
            pass

    @party.command(name="create", description="Cria uma party (nome único)")
    async def create(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        await self.ensure_tables()
        try:
            row = await self.bot.db.fetchrow("INSERT INTO parties (name, leader) VALUES ($1,$2) RETURNING id", name, interaction.user.id)
        except Exception:
            return await interaction.followup.send("❌ Já existe uma party com esse nome.", ephemeral=True)

        await self.bot.db.execute("INSERT INTO party_members (party_id,user_id) VALUES ($1,$2)", row["id"], interaction.user.id)
        await interaction.followup.send(f"✅ Party **{name}** criada. Você é o líder.")

    @party.command(name="invite", description="Convida um jogador para sua party")
    async def invite(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        await self.ensure_tables()
        party = await self.bot.db.fetchrow("SELECT id, leader, name FROM parties WHERE leader = $1", interaction.user.id)
        if not party:
            return await interaction.followup.send("🚫 Você não lidera nenhuma party.", ephemeral=True)

        try:
            await self.bot.db.execute("INSERT INTO party_invites (party_id, invited, inviter) VALUES ($1,$2,$3)", party["id"], member.id, interaction.user.id)
        except Exception:
            return await interaction.followup.send("⚠️ Convite já pendente para esse jogador.", ephemeral=True)

        await interaction.followup.send(f"✉️ Convite enviado para {member.display_name}.", ephemeral=True)
        try:
            await member.send(f"Você foi convidado para a party **{party['name']}** por {interaction.user.display_name}. Use `/party accept {party['name']}` para entrar.")
        except Exception:
            pass

    @party.command(name="accept", description="Aceita um convite para entrar em uma party pelo nome")
    async def accept(self, interaction: discord.Interaction, party_name: str):
        await interaction.response.defer()
        await self.ensure_tables()
        party = await self.bot.db.fetchrow("SELECT id, name FROM parties WHERE name = $1", party_name)
        if not party:
            return await interaction.followup.send("🚫 Party não encontrada.", ephemeral=True)

        invite = await self.bot.db.fetchrow("SELECT party_id FROM party_invites WHERE party_id = $1 AND invited = $2", party["id"], interaction.user.id)
        if not invite:
            return await interaction.followup.send("🚫 Você não tem convite para essa party.", ephemeral=True)

        await self.bot.db.execute("DELETE FROM party_invites WHERE party_id = $1 AND invited = $2", party["id"], interaction.user.id)
        try:
            await self.bot.db.execute("INSERT INTO party_members (party_id,user_id) VALUES ($1,$2)", party["id"], interaction.user.id)
        except Exception:
            return await interaction.followup.send("⚠️ Você já está nessa party.", ephemeral=True)

        await interaction.followup.send(f"✅ Você entrou na party **{party['name']}**.")

    @party.command(name="leave", description="Sai da sua party atual")
    async def leave(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.ensure_tables()
        member = await self.bot.db.fetchrow("SELECT party_id FROM party_members WHERE user_id = $1", interaction.user.id)
        if not member:
            return await interaction.followup.send("🚫 Você não está em nenhuma party.", ephemeral=True)

        await self.bot.db.execute("DELETE FROM party_members WHERE party_id = $1 AND user_id = $2", member["party_id"], interaction.user.id)
        # if leader left, disband
        leader = await self.bot.db.fetchval("SELECT leader FROM parties WHERE id = $1", member["party_id"])
        if leader == interaction.user.id:
            await self.bot.db.execute("DELETE FROM parties WHERE id = $1", member["party_id"])
            await interaction.followup.send("🚪 Você deixou a party e ela foi desfeita (você era o líder).")
            return

        await interaction.followup.send("🚪 Você saiu da party.")

    @party.command(name="info", description="Mostra informações da party pelo nome")
    async def info(self, interaction: discord.Interaction, party_name: str):
        await interaction.response.defer()
        await self.ensure_tables()
        party = await self.bot.db.fetchrow("SELECT id, name, leader FROM parties WHERE name = $1", party_name)
        if not party:
            return await interaction.followup.send("🚫 Party não encontrada.", ephemeral=True)

        members = await self.bot.db.fetch("SELECT user_id FROM party_members WHERE party_id = $1", party["id"])
        member_mentions = []
        for m in members:
            try:
                user = await self.bot.fetch_user(m["user_id"])
                member_mentions.append(user.display_name)
            except Exception:
                member_mentions.append(str(m["user_id"]))

        embed = discord.Embed(title=f"Party: {party['name']}")
        embed.add_field(name="Líder", value=f"<@{party['leader']}>", inline=True)
        embed.add_field(name="Membros", value=(", ".join(member_mentions) or "Nenhum"), inline=False)
        await interaction.followup.send(embed=embed)

    @party.command(name="setbuff", description="Define um buff compartilhado para a party (JSON de buffs)")
    async def setbuff(self, interaction: discord.Interaction, party_name: str, buff_json: str):
        await interaction.response.defer()
        await self.ensure_tables()
        party = await self.bot.db.fetchrow("SELECT id, leader FROM parties WHERE name = $1", party_name)
        if not party:
            return await interaction.followup.send("🚫 Party não encontrada.", ephemeral=True)
        if party["leader"] != interaction.user.id:
            return await interaction.followup.send("🚫 Apenas o líder pode definir buffs.", ephemeral=True)

        try:
            data = json.loads(buff_json)
        except Exception:
            return await interaction.followup.send("❌ JSON inválido.", ephemeral=True)

        await self.bot.db.execute("INSERT INTO party_buffs (party_id,buff) VALUES ($1,$2) ON CONFLICT (party_id) DO UPDATE SET buff = $2, updated_at = NOW()", party["id"], json.dumps(data))
        await interaction.followup.send("✅ Buff da party atualizado.")

    @party.command(name="ready", description="Marca a party como pronta para raid (líder somente)")
    async def ready(self, interaction: discord.Interaction, party_name: str):
        await interaction.response.defer()
        await self.ensure_tables()
        party = await self.bot.db.fetchrow("SELECT id, leader FROM parties WHERE name = $1", party_name)
        if not party:
            return await interaction.followup.send("🚫 Party não encontrada.", ephemeral=True)
        if party["leader"] != interaction.user.id:
            return await interaction.followup.send("🚫 Apenas o líder pode marcar como ready.", ephemeral=True)

        await self.bot.db.execute("INSERT INTO raid_ready (party_id, ready, started) VALUES ($1, TRUE, FALSE) ON CONFLICT (party_id) DO UPDATE SET ready = TRUE", party["id"])
        await interaction.followup.send("✅ Party marcada como pronta. Use `/party startraid <party_name>` para iniciar.")

    @party.command(name="startraid", description="Inicia a raid se a party estiver pronta (líder)")
    async def startraid(self, interaction: discord.Interaction, party_name: str):
        await interaction.response.defer()
        await self.ensure_tables()
        party = await self.bot.db.fetchrow("SELECT id, leader FROM parties WHERE name = $1", party_name)
        if not party:
            return await interaction.followup.send("🚫 Party não encontrada.", ephemeral=True)
        if party["leader"] != interaction.user.id:
            return await interaction.followup.send("🚫 Apenas o líder pode iniciar a raid.", ephemeral=True)

        rr = await self.bot.db.fetchrow("SELECT ready, started FROM raid_ready WHERE party_id = $1", party["id"])
        if not rr or not rr.get("ready"):
            return await interaction.followup.send("🚫 A party não está pronta.", ephemeral=True)
        if rr.get("started"):
            return await interaction.followup.send("🚫 Raid já iniciada.", ephemeral=True)

        await self.bot.db.execute("UPDATE raid_ready SET started = TRUE, started_at = NOW() WHERE party_id = $1", party["id"])
        members = await self.bot.db.fetch("SELECT user_id FROM party_members WHERE party_id = $1", party["id"])
        names = []
        for m in members:
            try:
                u = await self.bot.fetch_user(m["user_id"])
                names.append(u.display_name)
            except Exception:
                names.append(str(m["user_id"]))

        await interaction.followup.send(f"🚀 Raid iniciada para party **{party_name}**. Membros: {', '.join(names)}")


async def setup(bot: commands.Bot):
    cog = PartyRaid(bot)
    await bot.add_cog(cog)
