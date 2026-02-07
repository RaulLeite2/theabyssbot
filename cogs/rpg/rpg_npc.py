import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import random
from datetime import datetime, timedelta

class NPCSystem(commands.Cog):
    """Sistema de NPCs com personalidades e reputação"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.npcs_data = self.load_npcs()
        self.check_merchant_spawn.start()
    
    def load_npcs(self):
        """Carrega dados dos NPCs do arquivo JSON"""
        try:
            with open('data/npcs.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar NPCs: {e}")
            return {"npcs": {}, "reputation_titles": {}}
    
    def cog_unload(self):
        self.check_merchant_spawn.cancel()
    
    # =========================
    # SISTEMA DE REPUTAÇÃO
    # =========================
    
    async def get_reputation(self, user_id: int, npc_id: str):
        """Busca a reputação do usuário com um NPC"""
        rep = await self.bot.db.fetchrow(
            """
            SELECT reputation, title, total_purchases, total_gold_spent
            FROM npc_reputation
            WHERE user_id = $1 AND npc_id = $2
            """,
            user_id, npc_id
        )
        
        if not rep:
            # Cria entrada inicial
            await self.bot.db.execute(
                """
                INSERT INTO npc_reputation (user_id, npc_id, reputation, title)
                VALUES ($1, $2, 0, 'Desconhecido')
                ON CONFLICT (user_id, npc_id) DO NOTHING
                """,
                user_id, npc_id
            )
            return {'reputation': 0, 'title': 'Desconhecido', 'total_purchases': 0, 'total_gold_spent': 0}
        
        return dict(rep)
    
    async def add_reputation(self, user_id: int, npc_id: str, amount: int, gold_spent: int = 0):
        """Adiciona reputação com um NPC"""
        await self.bot.db.execute(
            """
            INSERT INTO npc_reputation (user_id, npc_id, reputation, total_purchases, total_gold_spent, last_interaction)
            VALUES ($1, $2, $3, 1, $4, NOW())
            ON CONFLICT (user_id, npc_id)
            DO UPDATE SET 
                reputation = npc_reputation.reputation + $3,
                total_purchases = npc_reputation.total_purchases + 1,
                total_gold_spent = npc_reputation.total_gold_spent + $4,
                last_interaction = NOW()
            """,
            user_id, npc_id, amount, gold_spent
        )
    
    def get_discount(self, reputation: int) -> float:
        """Calcula desconto baseado na reputação"""
        if reputation >= 5000:
            return 0.15  # 15% desconto
        elif reputation >= 2500:
            return 0.10  # 10% desconto
        elif reputation >= 1000:
            return 0.08  # 8% desconto
        elif reputation >= 500:
            return 0.05  # 5% desconto
        return 0.0
    
    # =========================
    # SISTEMA DE DIÁLOGOS
    # =========================
    
    async def get_npc_dialogue(self, npc_id: str, dialogue_type: str, user_id: int = None):
        """Retorna um diálogo aleatório do NPC"""
        npc = self.npcs_data['npcs'].get(npc_id)
        if not npc:
            return "..."
        
        dialogues = npc.get(dialogue_type, [])
        if not dialogues:
            return "..."
        
        message = random.choice(dialogues)
        
        # Salva no histórico se tiver user_id
        if user_id:
            await self.bot.db.execute(
                """
                INSERT INTO npc_dialogues (user_id, npc_id, dialogue_type, message)
                VALUES ($1, $2, $3, $4)
                """,
                user_id, npc_id, dialogue_type, message
            )
        
        return message
    
    # =========================
    # MERCADOR VIAJANTE (SISTEMA SURPRESA)
    # =========================
    
    @tasks.loop(minutes=15)
    async def check_merchant_spawn(self):
        """Verifica e spawna o Mercador Viajante aleatoriamente"""
        try:
            # Verifica se já existe um merchant ativo
            active = await self.bot.db.fetchval(
                "SELECT COUNT(*) FROM traveling_merchant WHERE is_active = TRUE AND despawn_at > NOW()"
            )
            
            if active > 0:
                return
            
            # 5% de chance de spawn a cada 15 minutos
            if random.random() < 0.05:
                await self.spawn_traveling_merchant()
        except Exception as e:
            print(f"❌ Erro no check_merchant_spawn: {e}")
    
    @check_merchant_spawn.before_loop
    async def before_check_merchant(self):
        await self.bot.wait_until_ready()
    
    async def spawn_traveling_merchant(self):
        """Spawna o Mercador Viajante em um hub aleatório"""
        # Busca todos os hubs
        hubs = await self.bot.db.fetch(
            "SELECT zone_id, nome FROM zone WHERE is_hub = TRUE"
        )
        
        if not hubs:
            return
        
        # Escolhe hub aleatório
        hub = random.choice(hubs)
        despawn_time = datetime.now() + timedelta(minutes=30)
        
        # Cria spawn
        spawn_id = await self.bot.db.fetchval(
            """
            INSERT INTO traveling_merchant (zone_id, despawn_at, is_active)
            VALUES ($1, $2, TRUE)
            RETURNING spawn_id
            """,
            hub['zone_id'], despawn_time
        )
        
        # Gera inventário lendário
        await self.generate_merchant_inventory(spawn_id)
        
        # Anuncia no canal (se configurado)
        print(f"🌪️ Mercador Viajante apareceu em {hub['nome']}!")
        
        # Aqui você pode adicionar notificação em canal específico se quiser
        # channel = self.bot.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
        # if channel:
        #     await channel.send(f"🌪️ **Zephyr, o Mercador do Vento** apareceu em **{hub['nome']}**! Ele partirá em 30 minutos!")
    
    async def generate_merchant_inventory(self, spawn_id: int):
        """Gera inventário raro para o Mercador Viajante"""
        # Busca itens de tiers altos
        legendary_items = await self.bot.db.fetch(
            """
            SELECT id, tier 
            FROM items 
            WHERE tier >= 6 AND is_collectible = FALSE
            ORDER BY RANDOM()
            LIMIT 10
            """
        )
        
        for item in legendary_items:
            # Preços altíssimos para itens lendários
            base_price = item['tier'] * 50000
            price = base_price + random.randint(-10000, 50000)
            
            await self.bot.db.execute(
                """
                INSERT INTO traveling_merchant_inventory (spawn_id, item_id, tier, price, quantity)
                VALUES ($1, $2, $3, $4, 1)
                """,
                spawn_id, item['id'], item['tier'], price
            )
    
    # =========================
    # COMANDOS
    # =========================
    
    @app_commands.command(name="npcs", description="Lista todos os NPCs disponíveis nos hubs")
    async def list_npcs(self, interaction: discord.Interaction):
        """Lista NPCs e suas localizações"""
        embed = discord.Embed(
            title="👥 NPCs do The Abyss",
            description="Interaja com NPCs para ganhar reputação e desbloquear recompensas!",
            color=discord.Color.gold()
        )
        
        for npc_key, npc in self.npcs_data['npcs'].items():
            if npc_key == "traveling_merchant":
                continue  # Mercador viajante é especial
            
            # Busca reputação do usuário
            rep = await self.get_reputation(interaction.user.id, npc['id'])
            discount = self.get_discount(rep['reputation'])
            
            value = f"**{npc['title']}** - {npc['race']}\n"
            value += f"*{npc['description'][:100]}...*\n"
            value += f"📍 Localização: `{npc['location']}`\n"
            value += f"🏆 Sua Reputação: **{rep['reputation']}** ({rep['title']})\n"
            
            if discount > 0:
                value += f"💰 Desconto Atual: **{int(discount*100)}%**\n"
            
            embed.add_field(
                name=f"{npc['name']}",
                value=value,
                inline=False
            )
        
        # Info sobre Mercador Viajante
        embed.add_field(
            name="🌪️ Zephyr, o Mercador do Vento (RARO)",
            value=(
                "**Comerciante Dimensional** - Genasi do Ar\n"
                "*Aparece aleatoriamente em hubs com itens lendários!*\n"
                "📍 Localização: Aleatória\n"
                "⏰ Aparece por apenas 30 minutos!\n"
                "💎 Vende itens **LENDÁRIOS** exclusivos"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use /talk <npc_name> para interagir com um NPC")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="talk", description="Conversa com um NPC")
    @app_commands.describe(npc_name="Nome do NPC (ex: Gorak, Lysandra, Martha)")
    async def talk_to_npc(self, interaction: discord.Interaction, npc_name: str):
        """Interage com um NPC"""
        # Procura NPC pelo nome
        npc_found = None
        npc_id = None
        
        for key, npc in self.npcs_data['npcs'].items():
            if npc_name.lower() in npc['name'].lower():
                npc_found = npc
                npc_id = npc['id']
                break
        
        if not npc_found:
            return await interaction.response.send_message(
                f"❌ NPC '{npc_name}' não encontrado. Use `/npcs` para ver a lista!",
                ephemeral=True
            )
        
        # Busca reputação
        rep = await self.get_reputation(interaction.user.id, npc_id)
        
        # Pega diálogo de saudação
        greeting = await self.get_npc_dialogue(npc_id, 'greeting', interaction.user.id)
        
        # Monta embed de interação
        embed = discord.Embed(
            title=f"💬 {npc_found['name']}",
            description=f"*{npc_found['title']}*",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📜 Diálogo",
            value=f'"{greeting}"',
            inline=False
        )
        
        embed.add_field(
            name="🏆 Sua Reputação",
            value=f"**{rep['reputation']}** pontos | Status: **{rep['title']}**",
            inline=True
        )
        
        discount = self.get_discount(rep['reputation'])
        if discount > 0:
            embed.add_field(
                name="💰 Desconto Ativo",
                value=f"**{int(discount*100)}%** de desconto em compras!",
                inline=True
            )
        
        # Mostra perks desbloqueados
        perks_unlocked = []
        for threshold, perk in npc_found.get('reputation_perks', {}).items():
            if rep['reputation'] >= int(threshold):
                perks_unlocked.append(f"✅ {perk}")
        
        if perks_unlocked:
            embed.add_field(
                name="🎁 Benefícios Desbloqueados",
                value="\n".join(perks_unlocked),
                inline=False
            )
        
        # Mostra próximo perk
        next_perk = None
        for threshold, perk in sorted(npc_found.get('reputation_perks', {}).items(), key=lambda x: int(x[0])):
            if rep['reputation'] < int(threshold):
                next_perk = (threshold, perk)
                break
        
        if next_perk:
            embed.add_field(
                name="🎯 Próximo Benefício",
                value=f"**{next_perk[0]}** pontos: {next_perk[1]}",
                inline=False
            )
        
        embed.set_footer(text=f"Compre itens deste NPC para ganhar reputação!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="merchant", description="Verifica se o Mercador Viajante está em algum hub")
    async def check_merchant(self, interaction: discord.Interaction):
        """Verifica localização do Mercador Viajante"""
        merchant = await self.bot.db.fetchrow(
            """
            SELECT tm.spawn_id, tm.zone_id, tm.despawn_at, z.nome
            FROM traveling_merchant tm
            JOIN zone z ON z.zone_id = tm.zone_id
            WHERE tm.is_active = TRUE AND tm.despawn_at > NOW()
            ORDER BY tm.spawned_at DESC
            LIMIT 1
            """
        )
        
        if not merchant:
            embed = discord.Embed(
                title="🌪️ Zephyr, o Mercador do Vento",
                description="*Os ventos estão calmos... Zephyr não está em nenhum hub no momento.*",
                color=discord.Color.greyple()
            )
            embed.add_field(
                name="ℹ️ Sobre o Mercador",
                value=(
                    "Zephyr é um comerciante dimensional raro que aparece aleatoriamente nos hubs!\n\n"
                    "🌟 **Vende itens lendários e únicos**\n"
                    "⏰ **Fica apenas 30 minutos quando aparece**\n"
                    "💎 **Preços altíssimos mas vale cada moeda!**"
                ),
                inline=False
            )
            return await interaction.response.send_message(embed=embed)
        
        # Calcula tempo restante
        time_left = merchant['despawn_at'] - datetime.now()
        minutes_left = int(time_left.total_seconds() / 60)
        
        embed = discord.Embed(
            title="🌪️ Zephyr, o Mercador do Vento",
            description=f"*O mercador dimensional foi avistado!*",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📍 Localização Atual",
            value=f"**{merchant['nome']}**",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Tempo Restante",
            value=f"**{minutes_left} minutos**",
            inline=True
        )
        
        embed.add_field(
            name="💬 Mensagem",
            value='"Os ventos me trouxeram tesouros de terras distantes... Venha, enquanto ainda estou aqui."',
            inline=False
        )
        
        embed.add_field(
            name="🛍️ Como Comprar",
            value=f"Use `/rpg goto {merchant['nome']}` para ir até lá!\nDepois use `/merchant_shop` para ver os itens!",
            inline=False
        )
        
        embed.set_footer(text="Corra! Ele desaparecerá em breve!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(NPCSystem(bot))
