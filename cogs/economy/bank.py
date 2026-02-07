import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import random

class Bank(commands.Cog):
    """Sistema de banco com juros passivos"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.apply_interest.start()
    
    def cog_unload(self):
        self.apply_interest.cancel()
    
    # =========================
    # APLICAR JUROS (A CADA HORA)
    # =========================
    @tasks.loop(hours=1)
    async def apply_interest(self):
        """Aplica 1% de juros a cada hora em todas as contas"""
        try:
            # Atualiza o gold de todos os usuários com 1% de juros
            await self.bot.db.execute(
                """
                UPDATE economy
                SET gold = FLOOR(gold * 1.01)
                WHERE gold > 0
                """
            )
            print(f"✅ Juros de 1% aplicados às {datetime.datetime.now()}")
        except Exception as e:
            print(f"❌ Erro ao aplicar juros: {e}")
    
    @apply_interest.before_loop
    async def before_apply_interest(self):
        await self.bot.wait_until_ready()
    
    # =========================
    # COMANDO /BANK
    # =========================
    @app_commands.command(name="bank", description="🏦 Consulte seu saldo bancário e informações de juros")
    async def bank(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Verifica se o usuário está em um hub
        zone = await self.bot.db.fetchrow(
            """
            SELECT z.zone_id, z.nome, z.is_hub
            FROM users u
            JOIN zone z ON z.zone_id = u.zona_id
            WHERE u.discord_id = $1
            """,
            interaction.user.id
        )
        
        if not zone or not zone["is_hub"]:
            return await interaction.followup.send(
                "🏛️ Você precisa estar em um **Hub (Cidade)** para acessar o banco!\n\n"
                "💡 Use `/rpg hub` para ir para a cidade mais próxima.",
                ephemeral=True
            )
        
        # Busca dados econômicos do usuário
        economy = await self.bot.db.fetchrow(
            "SELECT gold FROM economy WHERE user_id = $1",
            interaction.user.id
        )
        
        if not economy:
            return await interaction.followup.send(
                "❌ Você ainda não possui uma conta no banco.",
                ephemeral=True
            )
        
        gold = economy["gold"]
        hourly_interest = int(gold * 0.01)  # 1% por hora
        daily_interest = int(gold * 0.01 * 24)  # 24 horas
        
        # Interação com NPC Martha (Estalajadeira/Banqueira)
        npc_cog = self.bot.get_cog("NPCSystem")
        greeting = "Bem-vindo ao banco, aventureiro!"
        
        if npc_cog:
            # Busca reputação com Martha
            rep_data = await npc_cog.get_reputation(interaction.user.id, "martha")
            
            greetings = [
                "Olá, querido! Seu dinheiro está seguro aqui. 💰",
                "Bem-vindo de volta! Que bom ver você prosperando!",
                "Suas economias estão crescendo bem! Continue assim!",
                "O banco sempre cuida do seu dinheiro com carinho!"
            ]
            greeting = random.choice(greetings)
        
        # Cria embed com informações do banco
        embed = discord.Embed(
            title="🏦 Banco de The Abyss",
            description=f"💬 **Martha:** *\"{greeting}\"*",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💰 Saldo Atual",
            value=f"`{gold:,}` Gold",
            inline=False
        )
        
        embed.add_field(
            name="📈 Juros por Hora (1%)",
            value=f"`+{hourly_interest:,}` Gold/hora",
            inline=True
        )
        
        embed.add_field(
            name="📊 Projeção Diária",
            value=f"`+{daily_interest:,}` Gold/dia",
            inline=True
        )
        
        embed.add_field(
            name="ℹ️ Informações",
            value=(
                "• O banco aplica **1% de juros** automaticamente a cada hora\n"
                "• Seus juros são calculados sobre o saldo total\n"
                "• Quanto mais gold você tem, mais você ganha!\n"
                "• Os juros são aplicados mesmo quando você está offline"
            ),
            inline=False
        )
        
        if npc_cog:
            rep_data = await npc_cog.get_reputation(interaction.user.id, "martha")
            embed.add_field(
                name="⭐ Reputação com Martha",
                value=f"`{rep_data['reputation']}` pontos - *{rep_data['title']}*",
                inline=False
            )
        
        embed.set_footer(text=f"Consultado em {zone['nome']}")
        embed.timestamp = datetime.datetime.now()
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Bank(bot))
