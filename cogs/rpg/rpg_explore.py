import discord
from discord.ext import commands
from discord import app_commands
import random
import json


class RPGExplore(commands.Cog):
    """Comandos de exploração para descobrir segredos, portais e tesouros."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="explore", description="Explore a região atual em busca de segredos")
    async def explore(self, interaction: discord.Interaction):
        """Explora a zona atual, com chance de encontrar portais, tesouros ou perigos."""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Verifica se o usuário existe e pega sua zona
        user_data = await self.bot.db.fetchrow(
            "SELECT zona_id, level, current_hp FROM users WHERE discord_id = $1",
            user_id
        )
        
        if not user_data or not user_data["zona_id"]:
            return await interaction.followup.send(
                "❌ Você precisa estar em uma zona para explorar. Use `/rpg goto` primeiro.",
                ephemeral=True
            )
        
        if user_data["current_hp"] <= 0:
            return await interaction.followup.send(
                "💀 Você está morto! Use `/rpg battle revive` primeiro.",
                ephemeral=True
            )
        
        zona_id = user_data["zona_id"]
        
        # Busca informações da zona
        zone = await self.bot.db.fetchrow(
            "SELECT nome, tier, is_hub FROM zone WHERE zone_id = $1",
            zona_id
        )
        
        if not zone:
            return await interaction.followup.send(
                "❌ Zona não encontrada.",
                ephemeral=True
            )
        
        # Verifica se há um portal ativo na zona (evento tipo 3)
        portal = await self.bot.db.fetchrow(
            """
            SELECT id, reward FROM events 
            WHERE zone_id = $1 AND type = 3 AND active = TRUE
            """,
            zona_id
        )
        
        if portal:
            # PORTAL ENCONTRADO!
            embed = discord.Embed(
                title="🌀 Portal Descoberto!",
                description=f"Explorando **{zone['nome']}**, você encontra um portal dimensional pulsante!",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="🚪 Portal de Zahuv",
                value="Uma passagem instável que leva às Terras Distantes de Zahuv...",
                inline=False
            )
            embed.add_field(
                name="⚠️ Aviso",
                value="Portais são perigosos e podem levar você a lugares desconhecidos!",
                inline=False
            )
            embed.set_footer(text="Use /explore_portal para entrar (ou aguarde para explorar mais)")
            
            return await interaction.followup.send(embed=embed)
        
        # Sem portal - exploração normal com recompensas aleatórias
        embed = discord.Embed(
            title=f"🔍 Explorando {zone['nome']}",
            color=discord.Color.blue()
        )
        
        # Sistema de eventos aleatórios durante exploração
        roll = random.random()
        
        # SEMPRE dropa recursos (quantidade baseada no tier da zona)
        # Recursos podem ser coletados em qualquer zona, incluindo hubs
        resources = await self.bot.db.fetch("SELECT id, name, emoji FROM resources")
        if resources:
            # Escolhe 1-3 recursos aleatórios
            num_resources = random.randint(1, 3)
            selected_resources = random.sample(resources, min(num_resources, len(resources)))
            
            resource_text = []
            for res in selected_resources:
                # Quantidade baseada no tier (5-15 * tier) - mínimo 5 em hubs
                quantity = random.randint(5, 15) * max(1, zone["tier"])
                await self.bot.db.execute(
                    """
                    INSERT INTO user_resources (user_id, resource_id, quantity)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, resource_id)
                    DO UPDATE SET quantity = user_resources.quantity + $3
                    """,
                    user_id, res["id"], quantity
                )
                
                # Tenta buscar tier (se a coluna existir)
                try:
                    resource_tier = await self.bot.db.fetchval(
                        "SELECT tier FROM resources WHERE id = $1",
                        res["id"]
                    )
                    tier_text = f" `T{resource_tier}`" if resource_tier else ""
                except:
                    tier_text = ""
                
                resource_text.append(f"{res['emoji']} **{quantity}x {res['name']}**{tier_text}")
        
        if roll < 0.15:  # 15% - Encontra gold
            gold_found = random.randint(10, 100) * zone["tier"]
            await self.bot.db.execute(
                """
                INSERT INTO economy (user_id, gold) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET gold = economy.gold + $2
                """,
                user_id, gold_found
            )
            embed.description = f"💰 Você encontrou um baú escondido com **{gold_found} gold**!"
            if resource_text:
                embed.description += f"\n\n📦 **Recursos coletados:**\n" + "\n".join(resource_text)
            embed.color = discord.Color.gold()
            
        elif roll < 0.25:  # 10% - Encontra XP
            xp_found = random.randint(20, 80) * zone["tier"]
            rpg_cog = self.bot.get_cog("RPG")
            if rpg_cog:
                leveled = await rpg_cog.give_exp(user_id, xp_found)
                if leveled:
                    embed.description = f"📚 Você decifrou runas antigas e ganhou **{xp_found} XP**!\n⭐ **LEVEL UP!**"
                else:
                    embed.description = f"📚 Você decifrou runas antigas e ganhou **{xp_found} XP**!"
            else:
                embed.description = f"📚 Você decifrou runas antigas e ganhou **{xp_found} XP**!"
            if resource_text:
                embed.description += f"\n\n📦 **Recursos coletados:**\n" + "\n".join(resource_text)
            embed.color = discord.Color.blue()
            
        elif roll < 0.30:  # 5% - Toma dano (perigo)
            damage = random.randint(5, 20) * zone["tier"]
            new_hp = max(0, user_data["current_hp"] - damage)
            await self.bot.db.execute(
                "UPDATE users SET current_hp = $1 WHERE discord_id = $2",
                new_hp, user_id
            )
            if new_hp <= 0:
                embed.description = f"💀 Você caiu em uma armadilha e perdeu **{damage} HP**!\n**Você morreu!** Use `/rpg battle revive`."
                embed.color = discord.Color.dark_red()
            else:
                embed.description = f"⚠️ Você caiu em uma armadilha e perdeu **{damage} HP**! (HP restante: {new_hp})"
                embed.color = discord.Color.orange()
            if resource_text:
                embed.description += f"\n\n📦 **Recursos coletados:**\n" + "\n".join(resource_text)
                
        elif roll < 0.35:  # 5% - Encontra item comum
            # Busca um item aleatório de tier próximo à zona
            item = await self.bot.db.fetchrow(
                """
                SELECT id, name, tier FROM items 
                WHERE tier BETWEEN $1 AND $2
                ORDER BY RANDOM()
                LIMIT 1
                """,
                max(1, zone["tier"] - 1), zone["tier"] + 1
            )
            
            if item:
                await self.bot.db.execute(
                    """
                    INSERT INTO inventory (user_id, item_id, tier, quantity)
                    VALUES ($1, $2, $3, 1)
                    ON CONFLICT (user_id, item_id, tier)
                    DO UPDATE SET quantity = inventory.quantity + 1
                    """,
                    user_id, item["id"], item["tier"]
                )
                embed.description = f"✨ Você encontrou um item: **{item['name']}** `T{item['tier']}`!"
                embed.color = discord.Color.green()
            else:
                embed.description = "🌫️ A neblina está densa... você não encontrou nada desta vez."
                embed.color = discord.Color.light_grey()
            if resource_text:
                embed.description += f"\n\n📦 **Recursos coletados:**\n" + "\n".join(resource_text)
                
        else:  # 65% - Nada encontrado
            messages = [
                "🌫️ Você explorou a área mas não encontrou nada de especial.",
                "👣 Você seguiu alguns rastros, mas eles desapareceram no horizonte.",
                "🪨 Você examinou algumas ruínas, mas estavam vazias.",
                "🌿 A vegetação está densa, dificultando a exploração.",
                "🌙 A área está estranhamente silenciosa...",
                "💨 O vento carrega sussurros de aventuras passadas.",
            ]
            embed.description = random.choice(messages)
            if resource_text:
                embed.description += f"\n\n📦 **Recursos coletados:**\n" + "\n".join(resource_text)
            embed.color = discord.Color.dark_grey()
        
        # Adicionar Fama de Exploração (sempre ganha, mesmo sem encontrar nada)
        fame_amount = 5 + (zone["tier"] * 2)  # Mais fama em zonas de tier maior
        rpg_cog = self.bot.get_cog("RPG")
        if rpg_cog and hasattr(rpg_cog, 'add_fame'):
            await rpg_cog.add_fame(
                user_id, 
                'exploration', 
                fame_amount, 
                f"Explorou {zone['nome']}"
            )
            embed.add_field(name="🏆 Fama de Exploração", value=f"+{fame_amount} pontos", inline=False)
        
        # Atualiza conquistas e daily quests
        achievements_cog = self.bot.get_cog("Achievements")
        if achievements_cog:
            # Daily quest de exploração
            await achievements_cog.update_daily_quest_progress(user_id, 'explore', 1)
            # Conquista de zonas exploradas (atualiza stats)
            await self.bot.db.execute(
                """
                INSERT INTO user_stats (user_id, total_zones_explored, total_resources_collected)
                VALUES ($1, 1, 0)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    total_zones_explored = user_stats.total_zones_explored + 1,
                    updated_at = NOW()
                """,
                user_id
            )
        
        embed.set_footer(text=f"Zona: {zone['nome']} (Tier {zone['tier']}) | Continue explorando!")
        await interaction.followup.send(embed=embed)
        
        # NÃO verifica hideout no explore (mesma zona)
        # Notificação só aparece quando mudar de zona

    @app_commands.command(name="explore_portal", description="Entre no portal de Zahuv descoberto")
    async def explore_portal(self, interaction: discord.Interaction):
        """Entra em um portal de Zahuv e é transportado para uma zona aleatória."""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Verifica zona atual do usuário
        user_data = await self.bot.db.fetchrow(
            "SELECT zona_id FROM users WHERE discord_id = $1",
            user_id
        )
        
        if not user_data or not user_data["zona_id"]:
            return await interaction.followup.send(
                "❌ Você não está em nenhuma zona.",
                ephemeral=True
            )
        
        zona_id = user_data["zona_id"]
        
        # Verifica se há portal ativo
        portal = await self.bot.db.fetchrow(
            """
            SELECT id FROM events 
            WHERE zone_id = $1 AND type = 3 AND active = TRUE
            """,
            zona_id
        )
        
        if not portal:
            return await interaction.followup.send(
                "❌ Não há nenhum portal ativo nesta zona. Use `/explore` para procurar um.",
                ephemeral=True
            )
        
        # Desativa o portal (foi usado)
        await self.bot.db.execute(
            "UPDATE events SET active = FALSE WHERE id = $1",
            portal["id"]
        )
        
        # Busca uma zona aleatória de Zahuv (não-hub, não-hideout sem HO)
        new_zone = await self.bot.db.fetchrow(
            """
            SELECT zone_id, nome, tier FROM zone
            WHERE is_hub = FALSE 
            AND (
                is_hideout = FALSE 
                OR EXISTS (SELECT 1 FROM hideouts h WHERE h.zone_id = zone.zone_id)
            )
            AND zone_id != $1
            ORDER BY RANDOM()
            LIMIT 1
            """,
            zona_id
        )
        
        if not new_zone:
            return await interaction.followup.send(
                "❌ O portal falhou! Nenhuma zona de destino disponível.",
                ephemeral=True
            )
        
        # Teleporta o jogador
        await self.bot.db.execute(
            "UPDATE users SET zona_id = $1 WHERE discord_id = $2",
            new_zone["zone_id"], user_id
        )
        
        embed = discord.Embed(
            title="🌀 Portal Atravessado!",
            description=f"Você mergulha no portal dimensional e é transportado através do vazio...",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="🗺️ Nova Localização",
            value=f"**{new_zone['nome']}** (Tier ⭐ {new_zone['tier']})",
            inline=False
        )
        embed.add_field(
            name="✨ Status",
            value="Você chegou em segurança às Terras Distantes de Zahuv!",
            inline=False
        )
        embed.set_footer(text="Use /rpg battle zoneinfo para ver mais detalhes")
        
        await interaction.followup.send(embed=embed)
        
        # Verifica se há Hideout na zona (sempre mostra no portal pois mudou de zona)
        hideout_cog = self.bot.get_cog("Hideout")
        if hideout_cog:
            hideout_embed = await hideout_cog.check_hideout_in_zone(user_id, new_zone["zone_id"], previous_zone_id=None)
            if hideout_embed:
                await interaction.followup.send(embed=hideout_embed, ephemeral=True)


async def setup(bot: commands.Bot):
    cog = RPGExplore(bot)
    await bot.add_cog(cog)
    
    # Tenta adicionar os comandos ao tree principal
    main_rpg = bot.get_cog("RPG")
    if main_rpg and hasattr(main_rpg, 'rpg'):
        try:
            main_rpg.rpg.add_command(cog.explore)
            main_rpg.rpg.add_command(cog.explore_portal)
        except Exception:
            pass