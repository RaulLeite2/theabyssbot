"""
Party Arena Cog - Sistema de arenas para grupos/parties
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime
from db.db import Database


class PartyArena(commands.Cog):
    """Sistema de arenas para combate em grupo"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()
        self.active_arenas = {}  # guild_id: {party1_id: [...], party2_id: [...]}
    
    @app_commands.command(name="party_arena_info", description="Ver informações sobre arena de party")
    async def arena_info(self, interaction: discord.Interaction):
        """Mostra informações sobre o sistema de arena de party"""
        embed = discord.Embed(
            title="🏟️ Party Arena",
            description="Sistema de combate em grupo na arena",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="Como funciona",
            value="Forme uma party e desafie outras parties para combates épicos!",
            inline=False
        )
        embed.add_field(
            name="Recompensas",
            value="Ganhe XP, ouro e itens especiais ao vencer!",
            inline=False
        )
        embed.set_footer(text="Use /party_arena_challenge para desafiar!")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="party_arena_challenge", description="Desafiar outra party para arena")
    @app_commands.describe(party_leader="Líder da party que você quer desafiar")
    async def arena_challenge(self, interaction: discord.Interaction, party_leader: discord.Member):
        """Desafia outra party para um combate de arena"""
        
        if party_leader.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ Você não pode desafiar sua própria party!",
                ephemeral=True
            )
            return
        
        if party_leader.bot:
            await interaction.response.send_message(
                "❌ Você não pode desafiar bots!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="⚔️ Desafio de Arena!",
            description=f"{interaction.user.mention} desafiou a party de {party_leader.mention} para um combate de arena!",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Status",
            value="Aguardando aceitação...",
            inline=False
        )
        embed.set_footer(text="O líder da party desafiada deve aceitar o desafio")
        
        await interaction.response.send_message(embed=embed)
        await interaction.followup.send(
            f"{party_leader.mention}, você foi desafiado! Use `/party_arena_accept` para aceitar.",
            ephemeral=False
        )
    
    @app_commands.command(name="party_arena_leaderboard", description="Ver ranking de arenas de party")
    async def arena_leaderboard(self, interaction: discord.Interaction):
        """Mostra o ranking das parties na arena"""
        embed = discord.Embed(
            title="🏆 Ranking de Party Arena",
            description="Top parties na arena",
            color=discord.Color.purple()
        )
        
        # Placeholder para dados reais
        rankings = [
            {"name": "Party Alpha", "wins": 10, "losses": 2},
            {"name": "Party Beta", "wins": 8, "losses": 3},
            {"name": "Party Gamma", "wins": 6, "losses": 5},
        ]
        
        for idx, party in enumerate(rankings, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            embed.add_field(
                name=f"{medal} {party['name']}",
                value=f"Vitórias: {party['wins']} | Derrotas: {party['losses']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """Carrega o cog PartyArena"""
    await bot.add_cog(PartyArena(bot))
