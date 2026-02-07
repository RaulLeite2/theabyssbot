import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, List, Tuple

class CommandGroupSelect(discord.ui.Select):
    def __init__(self, owner_id: int, groups: Dict[str, List[Tuple[str, str]]]):
        options = [discord.SelectOption(label=name, description=(f"{len(cmds)} comandos" if cmds else ""))
                   for name, cmds in groups.items()]
        super().__init__(placeholder="Selecione um grupo de comandos…", min_values=1, max_values=1, options=options)
        self.owner_id = owner_id
        self.groups = groups

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Este menu não é seu.", ephemeral=True)

        selected = self.values[0]
        cmds = self.groups.get(selected, [])

        if not cmds:
            embed = discord.Embed(title=f"{selected} — Nenhum comando", description="Nenhum comando encontrado.", color=discord.Color.blurple())
        else:
            embed = discord.Embed(title=f"Comandos — {selected}", color=discord.Color.blurple())
            text = ""
            for name, desc in cmds:
                text += f"• **{name}** — {desc or 'Sem descrição.'}\n"
            embed.description = text

        await interaction.response.edit_message(embed=embed, view=self.view)

class RPGHelpView(discord.ui.View):
    def __init__(self, owner_id: int, groups: Dict[str, List[Tuple[str, str]]], timeout: float = 120.0):
        super().__init__(timeout=timeout)
        self.owner_id = owner_id
        self.select = CommandGroupSelect(owner_id, groups)
        self.add_item(self.select)

    async def on_timeout(self):
        # disable children when timing out
        for item in self.children:
            item.disabled = True
        try:
            # edit original message to disable UI
            await self.message.edit(view=self)
        except Exception:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ Este menu não é seu.", ephemeral=True)
            return False
        return True

class RPGHelp(commands.Cog):
    """Interactive help for RPG commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Ajuda interativa do RPG")
    async def help(self, interaction: discord.Interaction):
        # gather the `/rpg` group from the command tree
        rpg_cmd = None
        for cmd in self.bot.tree.get_commands():
            if getattr(cmd, 'name', None) == 'rpg':
                rpg_cmd = cmd
                break

        groups: Dict[str, List[Tuple[str, str]]] = {}

        # RPG Core Commands
        groups['RPG'] = [
            ("/rpg start", "Inicia sua jornada no Abismo"),
            ("/rpg ping", "Checa se o cog está ativo"),
            ("/rpg zones", "Zonas com atividade"),
            ("/rpg goto", "Muda sua zona pelo nome"),
            ("/rpg stats", "Veja seus status"),
            ("/rpg inventory", "Veja todos os itens que você possui"),
            ("/rpg equipment", "Veja os equipamentos que você está usando"),
            ("/rpg equip", "Equipa um item do seu inventário"),
            ("/rpg unequip", "Desequipa um item"),
            ("/rpg explore", "Explore a região atual em busca de segredos"),
            ("/rpg explore_portal", "Entre no portal de Zahuv descoberto"),
        ]
        
        # Battle Commands
        groups['Battle'] = [
            ("/rpg battle engage", "Entra em combate contra o evento ativo da zona"),
            ("/rpg battle loot", "Recolhe um item do saque"),
            ("/rpg battle revive", "Tenta reviver usando uma poção de healing"),
            ("/rpg battle zoneinfo", "Mostra informações da zona e eventos ativos"),
        ]
        
        # Arena PvP Commands
        groups['Arena'] = [
            ("/arena record", "Mostra o record de um jogador na arena"),
            ("/arena top", "Top jogadores da arena"),
            ("/arena wager", "Bloqueia gold para uma aposta de arena"),
            ("/arena ui_challenge", "Desafiar com UI (buttons) e aposta automática"),
            ("/arena challenge", "Desafiar um jogador para duelo"),
            ("/arena duel", "Aceitar desafio e iniciar combate simulado"),
        ]
        
        # Party System Commands
        groups['Party'] = [
            ("/party create", "Cria uma party (nome único)"),
            ("/party invite", "Convida um jogador para sua party"),
            ("/party accept", "Aceita um convite para entrar em uma party"),
            ("/party leave", "Sai da sua party atual"),
            ("/party info", "Mostra informações da party pelo nome"),
            ("/party setbuff", "Define um buff compartilhado para a party"),
            ("/party ready", "Marca a party como pronta para raid"),
            ("/party startraid", "Inicia a raid se a party estiver pronta"),
        ]
        
        # Party Arena Commands
        groups['Party Arena'] = [
            ("/party_arena_info", "Ver informações sobre arena de party"),
            ("/party_arena_challenge", "Desafiar outra party para arena"),
            ("/party_arena_leaderboard", "Ver ranking de arenas de party"),
        ]
        
        # Guild Commands
        groups['Guild'] = [
            ("/guild create", "Cria uma guilda"),
            ("/guild invite", "Convida alguém para a guilda"),
            ("/guild leave", "Sai da guilda"),
            ("/guild kick", "Expulsa um membro da guilda"),
            ("/guild promote", "Promove um membro a oficial"),
            ("/guild demote", "Rebaixa um membro"),
            ("/guild transfer", "Transfere a liderança da guilda"),
            ("/guild disband", "Dissolve a guilda"),
            ("/guild info", "Mostra informações da guilda"),
            ("/guild members", "Lista os membros da guilda"),
            ("/guild logs", "Mostra o histórico da guilda"),
        ]
        
        # Hideout Commands
        groups['Hideout'] = [
            ("/ho create", "🏰 Cria o Hideout da guilda (máx 7 por guilda)"),
            ("/ho info", "📊 Mostra informações do Hideout"),
            ("/ho recharge", "⚡ Recarrega o Hideout"),
            ("/ho upgrade", "🚀 Evolui o Hideout"),
            ("/ho zone", "🗺️ Mostra a zona do Hideout"),
            ("/ho list", "📜 Lista todos os hideouts da guilda"),
            ("/ho cleanup", "🧹 Remove hideouts com zonas deletadas"),
            ("/ho delete", "🗑️ Deleta um hideout específico"),
        ]
        
        # Alliance Commands
        groups['Alliance'] = [
            ("/ally create", "💎 Cria uma aliança (custa 7M de gold)"),
            ("/ally join", "🤝 Entra em uma aliança existente"),
            ("/ally leave", "💔 Sai da aliança atual"),
            ("/ally info", "📋 Informações detalhadas da sua aliança"),
            ("/ally list", "📜 Lista todas as alianças disponíveis"),
            ("/ally members", "👥 Lista todas as guildas membros"),
            ("/ally kick", "⚔️ Expulsa uma guilda (apenas fundador)"),
            ("/ally transfer", "👑 Transfere liderança da aliança (apenas fundador)"),
        ]
        
        # Auction Commands
        groups['Auction'] = [
            ("/auction list", "Mostra os itens no leilão da capital"),
            ("/auction sell", "Coloca um item à venda no leilão"),
            ("/auction finalize", "Finaliza leilões expirados (admin)"),
        ]
        
        # Shop Commands
        groups['Shop'] = [
            ("/shop", "Mostra os itens à venda na capital"),
        ]
        
        # Admin Commands
        groups['Admin'] = [
            ("/genitem", "Gera itens de 1.0 até 8.4"),
            ("/getitem", "Busca itens por nome ou buff"),
            ("/delitem", "Deleta item(s) por ID ou nome"),
            ("/giveitem", "Concede item ao inventário"),
            ("/addgold", "Adiciona gold (ADM)"),
            ("/addbuff", "Adiciona buff a um item"),
            ("/createzone", "Cria uma zona customizada"),
            ("/teleport", "Teleporta para zona ou jogador"),
            ("/spawnevent", "Cria evento em uma zona"),
            ("/setlevel", "Define level de um jogador"),
            ("/healall", "Cura todos na zona atual"),
            ("/broadcast", "Envia mensagem global"),
            ("/playerstats", "Ver stats de qualquer jogador"),
            ("/clearinventory", "Limpa inventário de um jogador"),
            ("/restart", "Reinicia o bot (apenas admin)"),
        ]

        if rpg_cmd:
            for child in getattr(rpg_cmd, 'commands', []):
                # if the child is a Group (has .commands), list its subcommands
                name = child.name
                desc = getattr(child, 'description', '') or ''
                if getattr(child, 'commands', None):
                    subcmds = []
                    for sub in child.commands:
                        subname = sub.name
                        subdesc = getattr(sub, 'description', '') or ''
                        subcmds.append((f"/rpg {name} {subname}", subdesc))
                    groups[name] = subcmds
                else:
                    # top-level command under /rpg
                    groups.setdefault('Overview', []).append((f"/rpg {name}", desc))

        embed = discord.Embed(
            title="Ajuda — The Abys RPG",
            description=("Bem-vindo ao help interativo do RPG. Use o menu abaixo para selecionar "
                         "um grupo de comandos e ver os comandos disponíveis."),
            color=discord.Color.blurple()
        )

        view = RPGHelpView(interaction.user.id, groups)
        # send ephemeral message so it's private and safe for multiple users
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        # attach message reference to the view for timeout editing
        try:
            # fetch the message we just sent
            message = await interaction.original_response()
            view.message = message
        except Exception:
            view.message = None

async def setup(bot: commands.Bot):
    await bot.add_cog(RPGHelp(bot))
