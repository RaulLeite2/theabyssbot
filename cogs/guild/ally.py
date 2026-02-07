import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import datetime

ALLY_COST = 7_000_000
ALLY_COLORS = {
    "default": 0x9B59B6,  # Purple
    "strong": 0xE74C3C,   # Red
    "legendary": 0xF1C40F  # Gold
}

class Alliance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    ally_group = app_commands.Group(name="ally", description="🤝 Sistema de Alianças - Una forças no Abismo")

    # =========================
    # CREATE ALLIANCE
    # =========================
    @ally_group.command(name="create", description="🏛️ Cria uma aliança poderosa (custa 7M de gold)")
    @app_commands.describe(
        name="Nome épico da aliança",
        tag="Tag de 3 letras (ex: VME, ABY, WRK)"
    )
    async def create(self, interaction: discord.Interaction, name: str, tag: str):
        try:
            # Validate tag is 3 letters
            if len(tag) != 3:
                embed = discord.Embed(
                    title="❌ Tag Inválida",
                    description="A tag da aliança deve ter exatamente **3 letras**.\n\n📝 Exemplos: `VME`, `ABY`, `WRK`",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            tag = tag.upper()
            
            guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_members gm ON gm.guild_id = g.id
                WHERE gm.user_id = $1 AND gm.role IN ('leader', 'officer')
                """,
                interaction.user.id
            )
            if not guild:
                embed = discord.Embed(
                    title="🚫 Acesso Negado",
                    description="Apenas **líderes** ou **oficiais** de guilda podem criar alianças.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            already = await self.bot.db.fetchrow(
                "SELECT 1 FROM guild_alliances WHERE guild_id = $1",
                guild["id"]
            )
            if already:
                embed = discord.Embed(
                    title="⚠️ Já Aliado",
                    description="Sua guilda já faz parte de uma aliança.\nUse `/ally leave` para sair primeiro.",
                    color=0xE67E22
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            gold = await self.bot.db.fetchval(
                "SELECT gold FROM economy WHERE user_id = $1",
                interaction.user.id
            )
            if not gold or gold < ALLY_COST:
                embed = discord.Embed(
                    title="💰 Fundos Insuficientes",
                    description=f"Criar uma aliança custa **7.000.000 gold**.\n\n💳 Seu saldo: `{gold:,}` gold",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            alliance_id = await self.bot.db.fetchval(
                "INSERT INTO alliances (name, tag, founder_guild_id) VALUES ($1, $2, $3) RETURNING id",
                name, tag, guild["id"]
            )

            await self.bot.db.execute("UPDATE economy SET gold = gold - $1 WHERE user_id = $2", ALLY_COST, interaction.user.id)
            await self.bot.db.execute("INSERT INTO guild_alliances (guild_id, alliance_id) VALUES ($1, $2)", guild["id"], alliance_id)

            embed = discord.Embed(
                title="🏛️ Aliança Fundada!",
                description=f"**[{tag}] {name}** foi forjada no fogo do Abismo!",
                color=ALLY_COLORS["legendary"]
            )
            embed.add_field(name="🏰 Guilda Fundadora", value=guild["name"], inline=True)
            embed.add_field(name="💰 Investimento", value=f"{ALLY_COST:,} gold", inline=True)
            embed.add_field(name="🆔 ID", value=f"`{alliance_id}`", inline=True)
            embed.add_field(
                name="📜 Próximos Passos",
                value="• Use `/ally invite` para convidar outras guildas\n• Fortaleça seus laços com `/ally info`\n• Dominem o Abismo juntos!",
                inline=False
            )
            embed.set_footer(text=f"Criada por {interaction.user.name}")
            embed.timestamp = datetime.utcnow()
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error creating alliance: {e}")
            await interaction.response.send_message("🚫 Erro ao criar aliança. Tag pode já estar em uso.", ephemeral=True)

    # =========================
    # JOIN ALLIANCE
    # =========================
    @ally_group.command(name="join", description="🤝 Junta-se a uma aliança existente")
    @app_commands.describe(alliance_name="Nome da aliança")
    async def join(self, interaction: discord.Interaction, alliance_name: str):
        try:
            guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_members gm ON gm.guild_id = g.id
                WHERE gm.user_id = $1 AND gm.role IN ('leader', 'officer')
                """,
                interaction.user.id
            )
            if not guild:
                embed = discord.Embed(
                    title="🚫 Acesso Negado",
                    description="Apenas **líderes** ou **oficiais** podem firmar alianças.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            already = await self.bot.db.fetchrow("SELECT 1 FROM guild_alliances WHERE guild_id = $1", guild["id"])
            if already:
                embed = discord.Embed(
                    title="⚠️ Já Aliado",
                    description="Sua guilda já está em uma aliança.",
                    color=0xE67E22
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            alliance = await self.bot.db.fetchrow(
                "SELECT id, name, tag FROM alliances WHERE name ILIKE $1",
                f"%{alliance_name}%"
            )
            if not alliance:
                embed = discord.Embed(
                    title="❌ Aliança Não Encontrada",
                    description=f"Nenhuma aliança encontrada com o nome **{alliance_name}**.\n\nUse `/ally list` para ver alianças disponíveis.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            await self.bot.db.execute("INSERT INTO guild_alliances (guild_id, alliance_id) VALUES ($1, $2)", guild["id"], alliance["id"])
            
            # Get tag safely
            try:
                tag = alliance["tag"] if alliance.get("tag") else "???"
            except:
                tag = "???"
            
            embed = discord.Embed(
                title="🤝 Aliança Selada!",
                description=f"**{guild['name']}** agora faz parte de **[{tag}] {alliance['name']}**!",
                color=ALLY_COLORS["strong"]
            )
            embed.add_field(name="🏰 Guilda", value=guild["name"], inline=True)
            embed.add_field(name="🤝 Aliança", value=f"[{tag}] {alliance['name']}", inline=True)
            embed.set_footer(text=f"Selado por {interaction.user.name}")
            embed.timestamp = datetime.utcnow()
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error joining alliance: {e}")
            await interaction.response.send_message("🚫 Erro ao entrar na aliança. Tente novamente.", ephemeral=True)

    # =========================
    # LEAVE ALLIANCE
    # =========================
    @ally_group.command(name="leave", description="💔 Rompe o pacto e sai da aliança")
    async def leave(self, interaction: discord.Interaction):
        try:
            guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_members gm ON gm.guild_id = g.id
                WHERE gm.user_id = $1 AND gm.role IN ('leader', 'officer')
                """,
                interaction.user.id
            )
            if not guild:
                embed = discord.Embed(
                    title="🚫 Acesso Negado",
                    description="Apenas **líderes** ou **oficiais** podem romper pactos.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            alliance_data = await self.bot.db.fetchrow(
                """
                SELECT ga.alliance_id, a.name, a.tag
                FROM guild_alliances ga
                JOIN alliances a ON a.id = ga.alliance_id
                WHERE ga.guild_id = $1
                """,
                guild["id"]
            )
            if not alliance_data:
                embed = discord.Embed(
                    title="⚠️ Sem Aliança",
                    description="Sua guilda não pertence a nenhuma aliança.",
                    color=0xE67E22
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            alliance_id = alliance_data["alliance_id"]
            alliance_name = alliance_data["name"]
            try:
                tag = alliance_data["tag"] if alliance_data.get("tag") else "???"
            except:
                tag = "???"

            # Check if this is the last guild in the alliance
            member_count = await self.bot.db.fetchval("SELECT COUNT(*) FROM guild_alliances WHERE alliance_id = $1", alliance_id)
            
            if member_count == 1:
                # Last guild leaving, destroy the alliance
                # First, set hideouts alliance_id to NULL
                await self.bot.db.execute("UPDATE hideouts SET alliance_id = NULL WHERE alliance_id = $1", alliance_id)
                await self.bot.db.execute("DELETE FROM guild_alliances WHERE alliance_id = $1", alliance_id)
                await self.bot.db.execute("DELETE FROM alliances WHERE id = $1", alliance_id)
                
                embed = discord.Embed(
                    title="💥 Aliança Destruída!",
                    description=f"**[{tag}] {alliance_name}** foi dissolvida no vazio.\n\n**{guild['name']}** era o último membro.",
                    color=0x95A5A6
                )
                embed.set_footer(text="O Abismo reclama seus pactos...")
            else:
                # Just leave the alliance
                await self.bot.db.execute("DELETE FROM guild_alliances WHERE guild_id = $1", guild["id"])
                
                embed = discord.Embed(
                    title="💔 Pacto Rompido",
                    description=f"**{guild['name']}** deixou **[{tag}] {alliance_name}**.\n\nCada um por si no Abismo.",
                    color=0xE74C3C
                )
                embed.set_footer(text=f"Rompido por {interaction.user.name}")
            
            embed.timestamp = datetime.utcnow()
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error leaving alliance: {e}")
            await interaction.response.send_message("🚫 Erro ao sair da aliança. Tente novamente.", ephemeral=True)

    # =========================
    # ALLY INFO
    # =========================
    @ally_group.command(name="info", description="📋 Informações detalhadas da sua aliança")
    async def info(self, interaction: discord.Interaction):
        try:
            guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_members gm ON gm.guild_id = g.id
                WHERE gm.user_id = $1
                """,
                interaction.user.id
            )
            if not guild:
                embed = discord.Embed(
                    title="🚫 Sem Guilda",
                    description="Você precisa estar em uma guilda para ver informações de aliança.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            alliance_data = await self.bot.db.fetchrow(
                """
                SELECT a.id, a.name, a.tag, a.created_at, a.founder_guild_id
                FROM alliances a
                JOIN guild_alliances ga ON ga.alliance_id = a.id
                WHERE ga.guild_id = $1
                """,
                guild["id"]
            )
            if not alliance_data:
                embed = discord.Embed(
                    title="⚠️ Sem Aliança",
                    description=f"**{guild['name']}** ainda não pertence a nenhuma aliança.\n\nUse `/ally create` para criar uma ou `/ally join` para entrar.",
                    color=0xE67E22
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            try:
                tag = alliance_data["tag"] if alliance_data.get("tag") else "???"
            except:
                tag = "???"

            # Fetch founder guild name
            founder_guild = await self.bot.db.fetchval("SELECT name FROM guilds WHERE id = $1", alliance_data["founder_guild_id"])

            # Fetch all guilds in the alliance
            member_guilds = await self.bot.db.fetch(
                """
                SELECT g.name, ga.joined_at
                FROM guilds g
                JOIN guild_alliances ga ON ga.guild_id = g.id
                WHERE ga.alliance_id = $1
                ORDER BY ga.joined_at ASC
                """,
                alliance_data["id"]
            )
            
            guild_list = []
            for i, g in enumerate(member_guilds, 1):
                founder_mark = " 👑" if g['name'] == founder_guild else ""
                guild_list.append(f"`{i}.` {g['name']}{founder_mark}")
            
            embed = discord.Embed(
                title=f"⚔️ [{tag}] {alliance_data['name']}",
                description=f"*Unidos no Abismo, mais fortes contra o caos*",
                color=ALLY_COLORS["default"]
            )
            embed.add_field(
                name="📜 Tag da Aliança",
                value=f"`{tag}`",
                inline=True
            )
            embed.add_field(
                name="👥 Total de Guildas",
                value=f"**{len(member_guilds)}**",
                inline=True
            )
            embed.add_field(
                name="📅 Criada",
                value=f"<t:{int(alliance_data['created_at'].timestamp())}:R>",
                inline=True
            )
            embed.add_field(
                name="🏰 Guildas Membros",
                value="\n".join(guild_list) if guild_list else "*Nenhuma*",
                inline=False
            )
            embed.add_field(
                name="👑 Fundador",
                value=f"**{founder_guild}**",
                inline=True
            )
            embed.set_footer(text=f"Sua guilda: {guild['name']}")
            embed.timestamp = datetime.utcnow()
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error fetching alliance info: {e}")
            await interaction.response.send_message("🚫 Erro ao buscar informações. Tente novamente.", ephemeral=True)

    # =========================
    # LIST ALLIANCES
    # =========================
    @ally_group.command(name="list", description="📜 Lista todas as alianças disponíveis")
    async def list_alliances(self, interaction: discord.Interaction):
        try:
            alliances = await self.bot.db.fetch(
                """
                SELECT a.id, a.name, a.tag, a.created_at,
                       COUNT(ga.guild_id) as member_count
                FROM alliances a
                LEFT JOIN guild_alliances ga ON ga.alliance_id = a.id
                GROUP BY a.id, a.name, a.tag, a.created_at
                ORDER BY member_count DESC, a.created_at ASC
                """
            )
            
            if not alliances:
                embed = discord.Embed(
                    title="📜 Alianças do Abismo",
                    description="Nenhuma aliança ainda foi formada.\n\nSeja o primeiro! Use `/ally create` para fundar uma.",
                    color=0x95A5A6
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            embed = discord.Embed(
                title="⚔️ Alianças do Abismo",
                description=f"*{len(alliances)} alianças forjadas nas trevas*",
                color=ALLY_COLORS["default"]
            )
            
            for i, alliance in enumerate(alliances[:15], 1):  # Limit to 15
                try:
                    tag = alliance["tag"] if alliance.get("tag") else "???"
                except:
                    tag = "???"
                
                member_count = alliance["member_count"] or 0
                created_timestamp = int(alliance["created_at"].timestamp())
                
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`{i}.`"
                
                embed.add_field(
                    name=f"{rank_emoji} [{tag}] {alliance['name']}",
                    value=f"👥 **{member_count}** guildas • 📅 <t:{created_timestamp}:R>",
                    inline=False
                )
            
            if len(alliances) > 15:
                embed.set_footer(text=f"Mostrando 15 de {len(alliances)} alianças")
            else:
                embed.set_footer(text=f"Total: {len(alliances)} alianças")
            
            embed.timestamp = datetime.utcnow()
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error listing alliances: {e}")
            await interaction.response.send_message("🚫 Erro ao listar alianças. Tente novamente.", ephemeral=True)

    # =========================
    # MEMBERS OF ALLIANCE
    # =========================
    @ally_group.command(name="members", description="👥 Lista todas as guildas membros da sua aliança")
    async def members(self, interaction: discord.Interaction):
        try:
            guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_members gm ON gm.guild_id = g.id
                WHERE gm.user_id = $1
                """,
                interaction.user.id
            )
            if not guild:
                embed = discord.Embed(
                    title="🚫 Sem Guilda",
                    description="Você precisa estar em uma guilda.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            alliance_data = await self.bot.db.fetchrow(
                """
                SELECT a.id, a.name, a.tag, a.founder_guild_id
                FROM alliances a
                JOIN guild_alliances ga ON ga.alliance_id = a.id
                WHERE ga.guild_id = $1
                """,
                guild["id"]
            )
            if not alliance_data:
                embed = discord.Embed(
                    title="⚠️ Sem Aliança",
                    description="Sua guilda não pertence a nenhuma aliança.",
                    color=0xE67E22
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            try:
                tag = alliance_data["tag"] if alliance_data.get("tag") else "???"
            except:
                tag = "???"

            # Fetch all guild members with details
            member_guilds = await self.bot.db.fetch(
                """
                SELECT g.id, g.name, g.level, g.gold, ga.joined_at
                FROM guilds g
                JOIN guild_alliances ga ON ga.guild_id = g.id
                WHERE ga.alliance_id = $1
                ORDER BY ga.joined_at ASC
                """,
                alliance_data["id"]
            )
            
            embed = discord.Embed(
                title=f"👥 Membros de [{tag}] {alliance_data['name']}",
                description=f"*{len(member_guilds)} guildas unidas no pacto*",
                color=ALLY_COLORS["default"]
            )
            
            for i, g in enumerate(member_guilds, 1):
                is_founder = g['id'] == alliance_data['founder_guild_id']
                founder_mark = " 👑" if is_founder else ""
                is_your_guild = g['id'] == guild['id']
                your_mark = " ⭐" if is_your_guild else ""
                
                joined_timestamp = int(g['joined_at'].timestamp())
                
                embed.add_field(
                    name=f"`{i}.` {g['name']}{founder_mark}{your_mark}",
                    value=f"⚡ Nv. **{g['level']}** • 💰 **{g['gold']:,}** gold • 📅 <t:{joined_timestamp}:R>",
                    inline=False
                )
            
            embed.set_footer(text="👑 = Fundador • ⭐ = Sua guilda")
            embed.timestamp = datetime.utcnow()
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error fetching alliance members: {e}")
            await interaction.response.send_message("🚫 Erro ao buscar membros. Tente novamente.", ephemeral=True)

    # =========================
    # KICK FROM ALLIANCE
    # =========================
    @ally_group.command(name="kick", description="⚔️ Expulsa uma guilda da aliança (apenas fundador)")
    async def kick(self, interaction: discord.Interaction, guild_name: str):
        try:
            # Check if user is in a guild and is leader
            user_guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_members gm ON gm.guild_id = g.id
                WHERE gm.user_id = $1 AND gm.role = 'leader'
                """,
                interaction.user.id
            )
            if not user_guild:
                embed = discord.Embed(
                    title="🚫 Acesso Negado",
                    description="Apenas **líderes de guilda** podem expulsar membros.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Get alliance and check if user is founder
            alliance_data = await self.bot.db.fetchrow(
                """
                SELECT a.id, a.name, a.tag, a.founder_guild_id
                FROM alliances a
                JOIN guild_alliances ga ON ga.alliance_id = a.id
                WHERE ga.guild_id = $1
                """,
                user_guild["id"]
            )
            if not alliance_data:
                embed = discord.Embed(
                    title="⚠️ Sem Aliança",
                    description="Sua guilda não pertence a nenhuma aliança.",
                    color=0xE67E22
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            if alliance_data["founder_guild_id"] != user_guild["id"]:
                embed = discord.Embed(
                    title="🚫 Permissão Negada",
                    description="Apenas a **guilda fundadora** 👑 pode expulsar membros.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Find the target guild
            target_guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_alliances ga ON ga.guild_id = g.id
                WHERE ga.alliance_id = $1 AND g.name ILIKE $2
                """,
                alliance_data["id"],
                f"%{guild_name}%"
            )
            if not target_guild:
                embed = discord.Embed(
                    title="❌ Guilda Não Encontrada",
                    description=f"Nenhuma guilda com o nome **{guild_name}** encontrada na aliança.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Can't kick yourself (founder)
            if target_guild["id"] == user_guild["id"]:
                embed = discord.Embed(
                    title="🚫 Impossível",
                    description="Você não pode expulsar sua própria guilda!\n\nUse `/ally leave` se quiser dissolver a aliança.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Kick the guild
            await self.bot.db.execute("DELETE FROM guild_alliances WHERE guild_id = $1", target_guild["id"])
            
            try:
                tag = alliance_data["tag"] if alliance_data.get("tag") else "???"
            except:
                tag = "???"
            
            embed = discord.Embed(
                title="⚔️ Guilda Expulsa!",
                description=f"**{target_guild['name']}** foi removida de **[{tag}] {alliance_data['name']}**.",
                color=0xE74C3C
            )
            embed.add_field(name="👑 Fundador", value=user_guild['name'], inline=True)
            embed.add_field(name="💥 Expulsa", value=target_guild['name'], inline=True)
            embed.set_footer(text=f"Ação executada por {interaction.user.name}")
            embed.timestamp = datetime.utcnow()
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error kicking guild: {e}")
            await interaction.response.send_message("🚫 Erro ao expulsar guilda. Tente novamente.", ephemeral=True)

    # =========================
    # TRANSFER LEADERSHIP
    # =========================
    @ally_group.command(name="transfer", description="👑 Transfere liderança da aliança (apenas fundador)")
    async def transfer(self, interaction: discord.Interaction, guild_name: str):
        try:
            # Check if user is in a guild and is leader
            user_guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_members gm ON gm.guild_id = g.id
                WHERE gm.user_id = $1 AND gm.role = 'leader'
                """,
                interaction.user.id
            )
            if not user_guild:
                embed = discord.Embed(
                    title="🚫 Acesso Negado",
                    description="Apenas **líderes de guilda** podem transferir liderança.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Get alliance and check if user is founder
            alliance_data = await self.bot.db.fetchrow(
                """
                SELECT a.id, a.name, a.tag, a.founder_guild_id
                FROM alliances a
                JOIN guild_alliances ga ON ga.alliance_id = a.id
                WHERE ga.guild_id = $1
                """,
                user_guild["id"]
            )
            if not alliance_data:
                embed = discord.Embed(
                    title="⚠️ Sem Aliança",
                    description="Sua guilda não pertence a nenhuma aliança.",
                    color=0xE67E22
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            if alliance_data["founder_guild_id"] != user_guild["id"]:
                embed = discord.Embed(
                    title="🚫 Permissão Negada",
                    description="Apenas a **guilda fundadora** 👑 pode transferir liderança.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Find the target guild
            target_guild = await self.bot.db.fetchrow(
                """
                SELECT g.id, g.name
                FROM guilds g
                JOIN guild_alliances ga ON ga.guild_id = g.id
                WHERE ga.alliance_id = $1 AND g.name ILIKE $2
                """,
                alliance_data["id"],
                f"%{guild_name}%"
            )
            if not target_guild:
                embed = discord.Embed(
                    title="❌ Guilda Não Encontrada",
                    description=f"Nenhuma guilda com o nome **{guild_name}** encontrada na aliança.",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Can't transfer to yourself
            if target_guild["id"] == user_guild["id"]:
                embed = discord.Embed(
                    title="🚫 Impossível",
                    description="Você já é o fundador da aliança!",
                    color=0xE74C3C
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Transfer leadership
            await self.bot.db.execute(
                "UPDATE alliances SET founder_guild_id = $1 WHERE id = $2",
                target_guild["id"],
                alliance_data["id"]
            )
            
            try:
                tag = alliance_data["tag"] if alliance_data.get("tag") else "???"
            except:
                tag = "???"
            
            embed = discord.Embed(
                title="👑 Liderança Transferida!",
                description=f"A coroa de **[{tag}] {alliance_data['name']}** agora pertence a **{target_guild['name']}**!",
                color=ALLY_COLORS["legendary"]
            )
            embed.add_field(name="👑 Antigo Fundador", value=user_guild['name'], inline=True)
            embed.add_field(name="👑 Novo Fundador", value=target_guild['name'], inline=True)
            embed.set_footer(text=f"Transferido por {interaction.user.name}")
            embed.timestamp = datetime.utcnow()
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error transferring leadership: {e}")
            await interaction.response.send_message("🚫 Erro ao transferir liderança. Tente novamente.", ephemeral=True)

async def setup(bot):
    cog = Alliance(bot)
    bot.tree.add_command(cog.ally_group)  # adiciona o grupo globalmente

