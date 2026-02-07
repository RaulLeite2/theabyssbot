import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class CraftButton(discord.ui.Button):
    def __init__(self, recipe_id: int, item_name: str, tier: int, subtier: int):
        super().__init__(
            label=f"Craftar {item_name}",
            style=discord.ButtonStyle.green,
            custom_id=f"craft_{recipe_id}"
        )
        self.recipe_id = recipe_id
        self.item_name = item_name
        self.tier = tier
        self.subtier = subtier

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_id = interaction.user.id
        bot = interaction.client
        
        # Buscar receita e ingredientes
        recipe = await bot.db.fetchrow(
            "SELECT item_id, tier, subtier FROM recipes WHERE id = $1",
            self.recipe_id
        )
        
        if not recipe:
            return await interaction.followup.send("❌ Receita não encontrada.", ephemeral=True)
        
        ingredients = await bot.db.fetch(
            """
            SELECT ri.resource_id, ri.quantity, r.name, r.emoji
            FROM recipe_ingredients ri
            JOIN resources r ON r.id = ri.resource_id
            WHERE ri.recipe_id = $1
            """,
            self.recipe_id
        )
        
        # Verificar se tem todos os recursos
        missing = []
        for ing in ingredients:
            user_res = await bot.db.fetchval(
                "SELECT quantity FROM user_resources WHERE user_id = $1 AND resource_id = $2",
                user_id, ing["resource_id"]
            )
            if not user_res or user_res < ing["quantity"]:
                have = user_res or 0
                missing.append(f"{ing['emoji']} {ing['name']}: {have}/{ing['quantity']}")
        
        if missing:
            embed = discord.Embed(
                title="❌ Recursos Insuficientes",
                description="Você não tem todos os recursos necessários:\n" + "\n".join(missing),
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Consumir recursos
        for ing in ingredients:
            await bot.db.execute(
                """
                UPDATE user_resources 
                SET quantity = quantity - $1 
                WHERE user_id = $2 AND resource_id = $3
                """,
                ing["quantity"], user_id, ing["resource_id"]
            )
        
        # Adicionar item ao inventário
        await bot.db.execute(
            """
            INSERT INTO inventory (user_id, item_id, tier, quantity)
            VALUES ($1, $2, $3, 1)
            ON CONFLICT (user_id, item_id, tier)
            DO UPDATE SET quantity = inventory.quantity + 1
            """,
            user_id, recipe["item_id"], recipe["tier"]
        )
        
        # Adicionar Fama de Criação
        fame_amount = 10 + (recipe["tier"] * 5)  # Mais fama para tiers maiores
        rpg_cog = bot.get_cog("RPG")
        if rpg_cog and hasattr(rpg_cog, 'add_fame'):
            await rpg_cog.add_fame(
                user_id, 
                'crafting', 
                fame_amount, 
                f"Craftou {self.item_name} T{self.tier}.{self.subtier}"
            )
        
        # Mensagem de sucesso
        embed = discord.Embed(
            title="✅ Item Craftado!",
            description=f"Você craftou com sucesso: **{self.item_name}** `T{self.tier}.{self.subtier}`!",
            color=discord.Color.green()
        )
        
        resources_used = "\n".join([f"{ing['emoji']} {ing['quantity']}x {ing['name']}" for ing in ingredients])
        embed.add_field(name="📦 Recursos Consumidos", value=resources_used, inline=False)
        embed.add_field(name="🏆 Fama de Criação", value=f"+{fame_amount} pontos", inline=False)
        
        await interaction.followup.send(embed=embed)


class RecipeView(discord.ui.View):
    def __init__(self, recipes: list):
        super().__init__(timeout=180)
        for recipe in recipes[:5]:  # Máximo 5 botões
            self.add_item(CraftButton(
                recipe["id"], 
                recipe["name"], 
                recipe["tier"], 
                recipe["subtier"]
            ))


class RPGCraft(commands.Cog):
    """Sistema de crafting de itens usando recursos."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def craftable_items_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete que mostra apenas itens que o usuário pode craftar"""
        
        user_id = interaction.user.id
        
        # Busca todos os recursos do usuário
        user_resources = await self.bot.db.fetch(
            "SELECT resource_id, quantity FROM user_resources WHERE user_id = $1",
            user_id
        )
        
        if not user_resources:
            return []
        
        # Cria dicionário de recursos disponíveis
        available_resources = {res['resource_id']: res['quantity'] for res in user_resources}
        
        # Busca todas as receitas
        recipes = await self.bot.db.fetch(
            """
            SELECT r.id, i.name, r.tier, r.subtier
            FROM recipes r
            JOIN items i ON i.id = r.item_id
            ORDER BY r.tier ASC, r.subtier ASC
            """
        )
        
        craftable = []
        
        for recipe in recipes:
            # Busca ingredientes necessários
            ingredients = await self.bot.db.fetch(
                """
                SELECT resource_id, quantity
                FROM recipe_ingredients
                WHERE recipe_id = $1
                """,
                recipe['id']
            )
            
            # Verifica se tem todos os recursos
            can_craft = True
            for ing in ingredients:
                user_qty = available_resources.get(ing['resource_id'], 0)
                if user_qty < ing['quantity']:
                    can_craft = False
                    break
            
            if can_craft:
                item_display = f"{recipe['name']} T{recipe['tier']}.{recipe['subtier']}"
                # Filtra pelo texto digitado
                if current.lower() in item_display.lower():
                    craftable.append(app_commands.Choice(
                        name=item_display[:100],  # Limite do Discord
                        value=recipe['name']
                    ))
        
        # Retorna até 25 opções (limite do Discord)
        return craftable[:25]

    @app_commands.command(name="craft", description="Abrir interface de crafting")
    @app_commands.autocomplete(item_name=craftable_items_autocomplete)
    async def craft(self, interaction: discord.Interaction, item_name: Optional[str] = None):
        """Interface de crafting com botões."""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Verificar se jogador existe
        exists = await self.bot.db.fetchval("SELECT 1 FROM users WHERE discord_id = $1", user_id)
        if not exists:
            return await interaction.followup.send(
                "❌ Você ainda não começou sua jornada! Use `/start` primeiro.",
                ephemeral=True
            )
        
        # Buscar receitas (filtradas por nome se fornecido)
        if item_name:
            recipes = await self.bot.db.fetch(
                """
                SELECT r.id, i.name, r.tier, r.subtier, i.slot_id, i.basedamage, i.basedefense
                FROM recipes r
                JOIN items i ON i.id = r.item_id
                WHERE LOWER(i.name) LIKE LOWER($1)
                ORDER BY r.tier ASC, r.subtier ASC
                LIMIT 10
                """,
                f"%{item_name}%"
            )
        else:
            recipes = await self.bot.db.fetch(
                """
                SELECT r.id, i.name, r.tier, r.subtier, i.slot_id, i.basedamage, i.basedefense
                FROM recipes r
                JOIN items i ON i.id = r.item_id
                ORDER BY r.tier ASC, r.subtier ASC
                LIMIT 10
                """
            )
        
        if not recipes:
            return await interaction.followup.send(
                "❌ Nenhuma receita encontrada. Administradores precisam criar receitas com `/addcraft`.",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title="🔨 Oficina de Crafting",
            description="Selecione um item para craftar:",
            color=discord.Color.blue()
        )
        
        for recipe in recipes[:10]:
            # Buscar ingredientes
            ingredients = await self.bot.db.fetch(
                """
                SELECT ri.quantity, r.name, r.emoji
                FROM recipe_ingredients ri
                JOIN resources r ON r.id = ri.resource_id
                WHERE ri.recipe_id = $1
                """,
                recipe["id"]
            )
            
            ing_text = ", ".join([f"{ing['emoji']} {ing['quantity']}x {ing['name']}" for ing in ingredients])
            
            stats = ""
            if recipe["basedamage"]:
                stats = f"⚔️ Dano: {recipe['basedamage']}"
            if recipe["basedefense"]:
                stats = f"🛡️ Defesa: {recipe['basedefense']}"
            
            embed.add_field(
                name=f"**{recipe['name']}** `T{recipe['tier']}.{recipe['subtier']}`",
                value=f"{stats}\n📦 {ing_text}",
                inline=False
            )
        
        view = RecipeView(recipes)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="recipes", description="Ver todas as receitas disponíveis")
    async def recipes(self, interaction: discord.Interaction, tier: Optional[int] = None):
        """Lista todas as receitas de craft."""
        await interaction.response.defer()
        
        if tier:
            recipes = await self.bot.db.fetch(
                """
                SELECT r.id, i.name, r.tier, r.subtier, i.slot_id
                FROM recipes r
                JOIN items i ON i.id = r.item_id
                WHERE r.tier = $1
                ORDER BY r.subtier ASC
                """,
                tier
            )
        else:
            recipes = await self.bot.db.fetch(
                """
                SELECT r.id, i.name, r.tier, r.subtier, i.slot_id
                FROM recipes r
                JOIN items i ON i.id = r.item_id
                ORDER BY r.tier ASC, r.subtier ASC
                LIMIT 25
                """
            )
        
        if not recipes:
            return await interaction.followup.send("📜 Nenhuma receita disponível ainda.", ephemeral=True)
        
        embed = discord.Embed(
            title="📜 Livro de Receitas",
            description=f"Receitas disponíveis{f' (Tier {tier})' if tier else ''}:",
            color=discord.Color.gold()
        )
        
        for recipe in recipes:
            ingredients = await self.bot.db.fetch(
                """
                SELECT ri.quantity, r.name, r.emoji
                FROM recipe_ingredients ri
                JOIN resources r ON r.id = ri.resource_id
                WHERE ri.recipe_id = $1
                """,
                recipe["id"]
            )
            
            ing_text = ", ".join([f"{ing['emoji']} {ing['quantity']}x" for ing in ingredients])
            
            slot_names = {
                1: "Amuleto", 2: "Cabeça", 3: "Pernas", 4: "Mão Principal",
                5: "Torso", 6: "Mão Secundária", 7: "Costas", 8: "Pés"
            }
            slot_name = slot_names.get(recipe["slot_id"], "Desconhecido")
            
            embed.add_field(
                name=f"{recipe['name']} `T{recipe['tier']}.{recipe['subtier']}`",
                value=f"🎯 {slot_name} | {ing_text}",
                inline=True
            )
        
        embed.set_footer(text="Use /craft <nome> para craftar um item específico")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="myresources", description="Ver seus recursos de crafting")
    async def myresources(self, interaction: discord.Interaction):
        """Mostra os recursos do jogador."""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        resources = await self.bot.db.fetch(
            """
            SELECT r.name, r.emoji, ur.quantity
            FROM user_resources ur
            JOIN resources r ON r.id = ur.resource_id
            WHERE ur.user_id = $1 AND ur.quantity > 0
            ORDER BY r.name ASC
            """,
            user_id
        )
        
        if not resources:
            return await interaction.followup.send(
                "📦 Você não tem nenhum recurso ainda. Use `/explore` para coletar recursos!",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title="📦 Meus Recursos",
            description="Recursos disponíveis para crafting:",
            color=discord.Color.green()
        )
        
        for res in resources:
            embed.add_field(
                name=f"{res['emoji']} {res['name']}",
                value=f"**{res['quantity']}x**",
                inline=True
            )
        
        embed.set_footer(text="Use /craft para criar itens com seus recursos")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="craftable", description="Ver apenas receitas que você pode craftar agora")
    async def craftable(self, interaction: discord.Interaction):
        """Mostra apenas receitas que o usuário tem recursos para craftar."""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        # Busca recursos do usuário
        user_resources = await self.bot.db.fetch(
            "SELECT resource_id, quantity FROM user_resources WHERE user_id = $1",
            user_id
        )
        
        if not user_resources:
            return await interaction.followup.send(
                "📦 Você não tem recursos! Use `/explore` para coletar recursos primeiro.",
                ephemeral=True
            )
        
        # Cria dicionário de recursos disponíveis
        available_resources = {res['resource_id']: res['quantity'] for res in user_resources}
        
        # Busca todas as receitas
        all_recipes = await self.bot.db.fetch(
            """
            SELECT r.id, i.name, r.tier, r.subtier, i.slot_id, i.basedamage, i.basedefense
            FROM recipes r
            JOIN items i ON i.id = r.item_id
            ORDER BY r.tier ASC, r.subtier ASC
            """
        )
        
        if not all_recipes:
            return await interaction.followup.send(
                "❌ Nenhuma receita disponível no jogo.",
                ephemeral=True
            )
        
        craftable_recipes = []
        
        for recipe in all_recipes:
            # Busca ingredientes necessários
            ingredients = await self.bot.db.fetch(
                """
                SELECT ri.resource_id, ri.quantity, r.name, r.emoji
                FROM recipe_ingredients ri
                JOIN resources r ON r.id = ri.resource_id
                WHERE ri.recipe_id = $1
                """,
                recipe['id']
            )
            
            # Verifica se tem todos os recursos
            can_craft = True
            for ing in ingredients:
                user_qty = available_resources.get(ing['resource_id'], 0)
                if user_qty < ing['quantity']:
                    can_craft = False
                    break
            
            if can_craft:
                craftable_recipes.append({
                    'recipe': recipe,
                    'ingredients': ingredients
                })
        
        if not craftable_recipes:
            embed = discord.Embed(
                title="🔨 Receitas Craftáveis",
                description="❌ Você ainda não tem recursos suficientes para craftar nada.\n\n💡 Use `/explore` para coletar mais recursos!",
                color=discord.Color.orange()
            )
            return await interaction.followup.send(embed=embed)
        
        embed = discord.Embed(
            title="✅ Receitas Craftáveis",
            description=f"Você pode craftar **{len(craftable_recipes)}** itens agora!",
            color=discord.Color.green()
        )
        
        slot_names = {
            1: "🎒 Amuleto", 2: "🪖 Cabeça", 3: "👖 Pernas", 4: "⚔️ Mão Principal",
            5: "🛡️ Torso", 6: "🗡️ Mão Secundária", 7: "🧥 Costas", 8: "👢 Pés"
        }
        
        for data in craftable_recipes[:15]:  # Limita a 15 para não passar do limite
            recipe = data['recipe']
            ingredients = data['ingredients']
            
            ing_text = ", ".join([f"{ing['emoji']} {ing['quantity']}x" for ing in ingredients])
            
            slot_name = slot_names.get(recipe["slot_id"], "❓ Desconhecido")
            
            stats = []
            if recipe["basedamage"]:
                stats.append(f"⚔️ {recipe['basedamage']}")
            if recipe["basedefense"]:
                stats.append(f"🛡️ {recipe['basedefense']}")
            
            stats_text = " | ".join(stats) if stats else "📦 Item"
            
            embed.add_field(
                name=f"**{recipe['name']}** `T{recipe['tier']}.{recipe['subtier']}`",
                value=f"{slot_name}\n{stats_text}\n📦 {ing_text}",
                inline=False
            )
        
        if len(craftable_recipes) > 15:
            embed.set_footer(text=f"Mostrando 15 de {len(craftable_recipes)} receitas | Use /craft <nome> para craftar")
        else:
            embed.set_footer(text="Use /craft <nome> para craftar um item")
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(RPGCraft(bot))
