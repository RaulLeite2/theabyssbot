import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio


class Trade(commands.Cog):
    """Sistema de comércio entre jogadores"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_trades = {}  # {user_id: trade_data}
    
    trade = app_commands.Group(name="trade", description="Comandos de comércio entre jogadores")
    
    @trade.command(name="offer", description="Oferece um trade para outro jogador")
    @app_commands.describe(
        player="Jogador com quem você quer negociar",
        your_gold="Quantidade de gold que você está oferecendo (deixe 0 se não quiser oferecer)",
        your_item="Nome do item que você está oferecendo (deixe vazio se não quiser oferecer)",
        request_gold="Quantidade de gold que você está pedindo",
        request_item="Nome do item que você está pedindo (deixe vazio se não quiser pedir)"
    )
    async def trade_offer(
        self, 
        interaction: discord.Interaction, 
        player: discord.Member,
        your_gold: int = 0,
        your_item: str = None,
        request_gold: int = 0,
        request_item: str = None
    ):
        """Cria uma oferta de trade para outro jogador"""
        
        if player.id == interaction.user.id:
            return await interaction.response.send_message(
                "❌ Você não pode negociar consigo mesmo!",
                ephemeral=True
            )
        
        if player.bot:
            return await interaction.response.send_message(
                "❌ Você não pode negociar com bots!",
                ephemeral=True
            )
        
        # Verifica se algum dos jogadores já tem trade ativo
        if interaction.user.id in self.active_trades:
            return await interaction.response.send_message(
                "❌ Você já tem um trade ativo! Cancele-o com `/trade cancel` primeiro.",
                ephemeral=True
            )
        
        if player.id in self.active_trades:
            return await interaction.response.send_message(
                f"❌ {player.mention} já tem um trade ativo!",
                ephemeral=True
            )
        
        # Validações
        if your_gold < 0 or request_gold < 0:
            return await interaction.response.send_message(
                "❌ Valores de gold não podem ser negativos!",
                ephemeral=True
            )
        
        if your_gold == 0 and not your_item and request_gold == 0 and not request_item:
            return await interaction.response.send_message(
                "❌ Você precisa oferecer ou pedir algo!",
                ephemeral=True
            )
        
        # Verifica se o usuário tem o gold oferecido
        if your_gold > 0:
            user_gold = await self.bot.db.fetchval(
                "SELECT gold FROM economy WHERE user_id = $1",
                interaction.user.id
            ) or 0
            
            if user_gold < your_gold:
                return await interaction.response.send_message(
                    f"❌ Você não tem {your_gold:,} gold! Você tem: {user_gold:,}",
                    ephemeral=True
                )
        
        # Verifica se o usuário tem o item oferecido
        your_item_id = None
        your_item_tier = None
        if your_item:
            item_data = await self.bot.db.fetchrow(
                """
                SELECT i.id, i.name, inv.tier, inv.quantity
                FROM inventory inv
                JOIN items i ON i.id = inv.item_id
                WHERE inv.user_id = $1 AND LOWER(i.name) = LOWER($2)
                """,
                interaction.user.id, your_item
            )
            
            if not item_data:
                return await interaction.response.send_message(
                    f"❌ Você não possui o item **{your_item}**!",
                    ephemeral=True
                )
            
            if item_data['quantity'] < 1:
                return await interaction.response.send_message(
                    f"❌ Você não tem quantidade suficiente de **{your_item}**!",
                    ephemeral=True
                )
            
            your_item_id = item_data['id']
            your_item_tier = item_data['tier']
            your_item = item_data['name']  # Nome correto do item
        
        # Verifica se o item pedido existe
        request_item_id = None
        if request_item:
            item_exists = await self.bot.db.fetchrow(
                "SELECT id, name FROM items WHERE LOWER(name) = LOWER($1)",
                request_item
            )
            
            if not item_exists:
                return await interaction.response.send_message(
                    f"❌ Item **{request_item}** não existe no jogo!",
                    ephemeral=True
                )
            
            request_item_id = item_exists['id']
            request_item = item_exists['name']  # Nome correto
        
        # Cria o trade
        trade_id = f"{interaction.user.id}_{player.id}_{int(datetime.now().timestamp())}"
        trade_data = {
            'id': trade_id,
            'offerer_id': interaction.user.id,
            'offerer_name': interaction.user.display_name,
            'receiver_id': player.id,
            'receiver_name': player.display_name,
            'offer_gold': your_gold,
            'offer_item_id': your_item_id,
            'offer_item_name': your_item,
            'offer_item_tier': your_item_tier,
            'request_gold': request_gold,
            'request_item_id': request_item_id,
            'request_item_name': request_item,
            'created_at': datetime.now(),
            'offerer_accepted': False,
            'receiver_accepted': False
        }
        
        self.active_trades[interaction.user.id] = trade_data
        self.active_trades[player.id] = trade_data
        
        # Cria embed da oferta
        embed = discord.Embed(
            title="🤝 Proposta de Trade",
            description=f"{interaction.user.mention} quer negociar com {player.mention}!",
            color=discord.Color.gold()
        )
        
        # O que está sendo oferecido
        offer_text = []
        if your_gold > 0:
            offer_text.append(f"💰 **{your_gold:,}** gold")
        if your_item:
            tier_text = f" `T{your_item_tier}`" if your_item_tier else ""
            offer_text.append(f"📦 **{your_item}**{tier_text}")
        
        embed.add_field(
            name=f"📤 {interaction.user.display_name} oferece:",
            value="\n".join(offer_text) if offer_text else "Nada",
            inline=True
        )
        
        # O que está sendo pedido
        request_text = []
        if request_gold > 0:
            request_text.append(f"💰 **{request_gold:,}** gold")
        if request_item:
            request_text.append(f"📦 **{request_item}**")
        
        embed.add_field(
            name=f"📥 {interaction.user.display_name} pede:",
            value="\n".join(request_text) if request_text else "Nada",
            inline=True
        )
        
        embed.set_footer(text=f"Trade ID: {trade_id[:16]}... | Use /trade accept ou /trade decline")
        
        await interaction.response.send_message(embed=embed)
        
        # Notifica o outro jogador
        try:
            await player.send(
                f"🤝 {interaction.user.mention} criou uma proposta de trade com você no servidor **{interaction.guild.name}**!\n"
                f"Use `/trade accept` ou `/trade decline` no servidor para responder."
            )
        except:
            pass
        
        # Auto-cancela após 5 minutos
        await asyncio.sleep(300)
        if trade_id in [t.get('id') for t in self.active_trades.values()]:
            await self._cancel_trade(trade_id, "⏰ Trade expirou após 5 minutos.")
    
    @trade.command(name="accept", description="Aceita o trade proposto")
    async def trade_accept(self, interaction: discord.Interaction):
        """Aceita um trade ativo"""
        
        if interaction.user.id not in self.active_trades:
            return await interaction.response.send_message(
                "❌ Você não tem nenhum trade ativo!",
                ephemeral=True
            )
        
        trade = self.active_trades[interaction.user.id]
        
        # Marca que o usuário aceitou
        if interaction.user.id == trade['offerer_id']:
            trade['offerer_accepted'] = True
            await interaction.response.send_message(
                "✅ Você aceitou o trade! Aguardando o outro jogador aceitar...",
                ephemeral=True
            )
        elif interaction.user.id == trade['receiver_id']:
            trade['receiver_accepted'] = True
            await interaction.response.send_message(
                "✅ Você aceitou o trade! Aguardando o outro jogador aceitar...",
                ephemeral=True
            )
        
        # Se ambos aceitaram, executa o trade
        if trade['offerer_accepted'] and trade['receiver_accepted']:
            await self._execute_trade(interaction, trade)
    
    async def _execute_trade(self, interaction: discord.Interaction, trade: dict):
        """Executa a troca entre os jogadores"""
        
        offerer_id = trade['offerer_id']
        receiver_id = trade['receiver_id']
        
        try:
            async with self.bot.db.acquire() as conn:
                async with conn.transaction():
                    # Verifica novamente se ambos têm os recursos
                    
                    # Gold do offerer
                    if trade['offer_gold'] > 0:
                        offerer_gold = await conn.fetchval(
                            "SELECT gold FROM economy WHERE user_id = $1",
                            offerer_id
                        ) or 0
                        
                        if offerer_gold < trade['offer_gold']:
                            raise ValueError(f"{trade['offerer_name']} não tem gold suficiente!")
                    
                    # Item do offerer
                    if trade['offer_item_id']:
                        offerer_item = await conn.fetchval(
                            "SELECT quantity FROM inventory WHERE user_id = $1 AND item_id = $2",
                            offerer_id, trade['offer_item_id']
                        ) or 0
                        
                        if offerer_item < 1:
                            raise ValueError(f"{trade['offerer_name']} não tem o item oferecido!")
                    
                    # Gold do receiver
                    if trade['request_gold'] > 0:
                        receiver_gold = await conn.fetchval(
                            "SELECT gold FROM economy WHERE user_id = $1",
                            receiver_id
                        ) or 0
                        
                        if receiver_gold < trade['request_gold']:
                            raise ValueError(f"{trade['receiver_name']} não tem gold suficiente!")
                    
                    # Item do receiver
                    if trade['request_item_id']:
                        receiver_item = await conn.fetchval(
                            "SELECT quantity FROM inventory WHERE user_id = $1 AND item_id = $2",
                            receiver_id, trade['request_item_id']
                        ) or 0
                        
                        if receiver_item < 1:
                            raise ValueError(f"{trade['receiver_name']} não tem o item pedido!")
                    
                    # EXECUTA AS TRANSFERÊNCIAS
                    
                    # Transfer gold: offerer -> receiver
                    if trade['offer_gold'] > 0:
                        await conn.execute(
                            "UPDATE economy SET gold = gold - $1 WHERE user_id = $2",
                            trade['offer_gold'], offerer_id
                        )
                        await conn.execute(
                            """
                            INSERT INTO economy (user_id, gold) VALUES ($1, $2)
                            ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2
                            """,
                            receiver_id, trade['offer_gold']
                        )
                    
                    # Transfer gold: receiver -> offerer
                    if trade['request_gold'] > 0:
                        await conn.execute(
                            "UPDATE economy SET gold = gold - $1 WHERE user_id = $2",
                            trade['request_gold'], receiver_id
                        )
                        await conn.execute(
                            """
                            INSERT INTO economy (user_id, gold) VALUES ($1, $2)
                            ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2
                            """,
                            offerer_id, trade['request_gold']
                        )
                    
                    # Transfer item: offerer -> receiver
                    if trade['offer_item_id']:
                        # Remove do offerer
                        await conn.execute(
                            "UPDATE inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_id = $2",
                            offerer_id, trade['offer_item_id']
                        )
                        await conn.execute(
                            "DELETE FROM inventory WHERE user_id = $1 AND quantity <= 0",
                            offerer_id
                        )
                        
                        # Adiciona ao receiver
                        await conn.execute(
                            """
                            INSERT INTO inventory (user_id, item_id, tier, quantity)
                            VALUES ($1, $2, $3, 1)
                            ON CONFLICT (user_id, item_id, tier)
                            DO UPDATE SET quantity = inventory.quantity + 1
                            """,
                            receiver_id, trade['offer_item_id'], trade['offer_item_tier']
                        )
                    
                    # Transfer item: receiver -> offerer
                    if trade['request_item_id']:
                        # Busca o tier do item do receiver
                        receiver_item_tier = await conn.fetchval(
                            "SELECT tier FROM inventory WHERE user_id = $1 AND item_id = $2",
                            receiver_id, trade['request_item_id']
                        )
                        
                        # Remove do receiver
                        await conn.execute(
                            "UPDATE inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_id = $2",
                            receiver_id, trade['request_item_id']
                        )
                        await conn.execute(
                            "DELETE FROM inventory WHERE user_id = $1 AND quantity <= 0",
                            receiver_id
                        )
                        
                        # Adiciona ao offerer
                        await conn.execute(
                            """
                            INSERT INTO inventory (user_id, item_id, tier, quantity)
                            VALUES ($1, $2, $3, 1)
                            ON CONFLICT (user_id, item_id, tier)
                            DO UPDATE SET quantity = inventory.quantity + 1
                            """,
                            offerer_id, trade['request_item_id'], receiver_item_tier
                        )
            
            # Trade concluído com sucesso!
            embed = discord.Embed(
                title="✅ Trade Completo!",
                description=f"Trade entre {trade['offerer_name']} e {trade['receiver_name']} foi concluído!",
                color=discord.Color.green()
            )
            
            # Resumo das transferências
            transfers = []
            
            if trade['offer_gold'] > 0:
                transfers.append(f"💰 **{trade['offerer_name']}** enviou **{trade['offer_gold']:,}** gold")
            if trade['offer_item_name']:
                transfers.append(f"📦 **{trade['offerer_name']}** enviou **{trade['offer_item_name']}**")
            if trade['request_gold'] > 0:
                transfers.append(f"💰 **{trade['receiver_name']}** enviou **{trade['request_gold']:,}** gold")
            if trade['request_item_name']:
                transfers.append(f"📦 **{trade['receiver_name']}** enviou **{trade['request_item_name']}**")
            
            embed.add_field(
                name="📋 Transferências",
                value="\n".join(transfers),
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
            # Remove o trade
            del self.active_trades[offerer_id]
            del self.active_trades[receiver_id]
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Erro ao executar o trade: {str(e)}",
                ephemeral=True
            )
            # Remove o trade em caso de erro
            if offerer_id in self.active_trades:
                del self.active_trades[offerer_id]
            if receiver_id in self.active_trades:
                del self.active_trades[receiver_id]
    
    @trade.command(name="decline", description="Recusa o trade proposto")
    async def trade_decline(self, interaction: discord.Interaction):
        """Recusa um trade ativo"""
        
        if interaction.user.id not in self.active_trades:
            return await interaction.response.send_message(
                "❌ Você não tem nenhum trade ativo!",
                ephemeral=True
            )
        
        trade = self.active_trades[interaction.user.id]
        await self._cancel_trade(trade['id'], f"❌ {interaction.user.display_name} recusou o trade.")
        await interaction.response.send_message("❌ Trade cancelado.", ephemeral=True)
    
    @trade.command(name="cancel", description="Cancela o trade que você criou")
    async def trade_cancel(self, interaction: discord.Interaction):
        """Cancela um trade ativo"""
        
        if interaction.user.id not in self.active_trades:
            return await interaction.response.send_message(
                "❌ Você não tem nenhum trade ativo!",
                ephemeral=True
            )
        
        trade = self.active_trades[interaction.user.id]
        
        if trade['offerer_id'] != interaction.user.id:
            return await interaction.response.send_message(
                "❌ Apenas quem criou o trade pode cancelá-lo! Use `/trade decline` para recusar.",
                ephemeral=True
            )
        
        await self._cancel_trade(trade['id'], f"❌ {interaction.user.display_name} cancelou o trade.")
        await interaction.response.send_message("❌ Trade cancelado.", ephemeral=True)
    
    async def _cancel_trade(self, trade_id: str, reason: str):
        """Cancela um trade ativo"""
        # Encontra e remove o trade
        to_remove = []
        for user_id, trade in self.active_trades.items():
            if trade['id'] == trade_id:
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.active_trades[user_id]
    
    @trade.command(name="status", description="Verifica o status do seu trade ativo")
    async def trade_status(self, interaction: discord.Interaction):
        """Mostra informações sobre o trade ativo"""
        
        if interaction.user.id not in self.active_trades:
            return await interaction.response.send_message(
                "❌ Você não tem nenhum trade ativo!",
                ephemeral=True
            )
        
        trade = self.active_trades[interaction.user.id]
        
        embed = discord.Embed(
            title="📊 Status do Trade",
            color=discord.Color.blue()
        )
        
        # Participantes
        embed.add_field(
            name="👥 Participantes",
            value=f"**Criador:** {trade['offerer_name']}\n**Receptor:** {trade['receiver_name']}",
            inline=False
        )
        
        # Ofertas
        offer_text = []
        if trade['offer_gold'] > 0:
            offer_text.append(f"💰 {trade['offer_gold']:,} gold")
        if trade['offer_item_name']:
            offer_text.append(f"📦 {trade['offer_item_name']}")
        
        request_text = []
        if trade['request_gold'] > 0:
            request_text.append(f"💰 {trade['request_gold']:,} gold")
        if trade['request_item_name']:
            request_text.append(f"📦 {trade['request_item_name']}")
        
        embed.add_field(
            name=f"📤 {trade['offerer_name']} oferece:",
            value="\n".join(offer_text) if offer_text else "Nada",
            inline=True
        )
        
        embed.add_field(
            name=f"📥 {trade['offerer_name']} pede:",
            value="\n".join(request_text) if request_text else "Nada",
            inline=True
        )
        
        # Status de aceitação
        status_text = []
        status_text.append(f"✅ {trade['offerer_name']}" if trade['offerer_accepted'] else f"⏳ {trade['offerer_name']}")
        status_text.append(f"✅ {trade['receiver_name']}" if trade['receiver_accepted'] else f"⏳ {trade['receiver_name']}")
        
        embed.add_field(
            name="📝 Aceitação",
            value="\n".join(status_text),
            inline=False
        )
        
        # Tempo restante
        elapsed = (datetime.now() - trade['created_at']).total_seconds()
        remaining = 300 - elapsed
        if remaining > 0:
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            embed.set_footer(text=f"⏰ Expira em {mins}m {secs}s")
        else:
            embed.set_footer(text="⏰ Trade expirado")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Trade(bot))
