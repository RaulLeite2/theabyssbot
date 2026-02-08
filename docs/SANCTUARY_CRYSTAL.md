# 🏰 Sistema de Cristal de Fundação do Santuário

## 📋 Visão Geral

O **Cristal de Fundação do Santuário** é um item lendário consumível que permite às guildas criarem seu próprio Santuário (antigo Hideout) nas profundezas do Abismo.

## 🎯 Características do Item

- **Nome**: Cristal de Fundação do Santuário
- **Tipo**: Consumível Único
- **Qualidade**: Legendary (Depth 8)
- **Tradeable**: Não (bound)
- **Uso**: Permite criar um Santuário para sua guilda

## ⚙️ Como Implementar

### 1. Popular os Items no Banco

Execute os SQLs na ordem:

```bash
# Primeiro: Criar os materiais e o cristal
psql -U postgres -d theabyssbot -f db/seeds/populate_sanctuary_crystal.sql

# Segundo: Popular items de equipamento (se ainda não fez)
psql -U postgres -d theabyssbot -f db/seeds/populate_items_depth.sql
```

### 2. Configurar a Receita

Após popular os items, você precisa:

1. Encontrar os IDs dos materiais:
```sql
SELECT id, name FROM items WHERE name IN (
    'Fragmento de Fogo Primordial', 
    'Fragmento de Gelo Eterno', 
    'Fragmento de Trovão Arcano', 
    'Fragmento de Terra Antiga',
    'Essência do Abismo', 
    'Essência Celestial', 
    'Essência do Vazio',
    'Núcleo de Mana Concentrado', 
    'Cristal de Energia Pura', 
    'Coração de Dragão Ancião',
    'Minério de Mythril', 
    'Minério de Adamantium', 
    'Minério de Orichalcum',
    'Runa de Proteção Lv5', 
    'Pergaminho de Selamento', 
    'Grimório Ancestral',
    'Cristal de Fundação do Santuário'
);
```

2. Editar `db/seeds/populate_hideout_recipes.sql`:
   - Substituir `result_item_id = NULL` pelo ID do Cristal
   - Descomentar e ajustar os IDs na seção `hideout_recipe_materials`

3. Executar o SQL:
```bash
psql -U postgres -d theabyssbot -f db/seeds/populate_hideout_recipes.sql
```

## 🔨 Receita de Craft

### Requisitos
- **Hideout Nível**: 5 (alto)
- **Tempo de Craft**: 2 horas
- **Total de Materiais**: 1,812 items de 15 tipos diferentes

### Lista Completa de Materiais

#### Fragmentos Elementais (400 total)
- 100x Fragmento de Fogo Primordial (T6 Rare)
- 100x Fragmento de Gelo Eterno (T6 Rare)
- 100x Fragmento de Trovão Arcano (T6 Rare)
- 100x Fragmento de Terra Antiga (T6 Rare)

#### Essências Místicas (110 total)
- 50x Essência do Abismo (T7 Epic)
- 50x Essência Celestial (T7 Epic)
- 10x Essência do Vazio (T8 Legendary) ⭐

#### Núcleos de Poder (276 total)
- 200x Núcleo de Mana Concentrado (T5 Uncommon)
- 75x Cristal de Energia Pura (T6 Rare)
- 1x Coração de Dragão Ancião (T8 Mythic) ⭐⭐⭐

#### Minérios Místicos (950 total)
- 500x Minério de Mythril (T5 Rare)
- 300x Minério de Adamantium (T6 Epic)
- 150x Minério de Orichalcum (T7 Epic)

#### Runas e Pergaminhos (76 total)
- 50x Runa de Proteção Lv5 (T5 Rare)
- 25x Pergaminho de Selamento (T6 Epic)
- 1x Grimório Ancestral (T8 Legendary) ⭐⭐

## 💡 Design da Receita

### Dificuldade

A receita foi projetada para ser **extremamente desafiadora**:

1. **Quantidade massiva**: 1,812 items no total
2. **Variedade**: 15 tipos diferentes de materiais
3. **Raridade**: Inclui 2 items únicos (Coração de Dragão e Grimório)
4. **Tempo**: 2 horas de tempo de craft
5. **Progressão**: Requer Hideout nível 5

### Balanceamento

- **Materiais T5-T6**: Coletáveis em grande quantidade (farming)
- **Materiais T7-T8**: Raros, requerem exploração profunda
- **Items Únicos**: Drops de bosses ou conquistas especiais
- **Coordenação**: Incentiva trabalho em guilda para coletar tudo

## 🎮 Como Usar no Jogo

### Para Jogadores

1. Reunir todos os materiais (trabalho em guilda recomendado)
2. Ter um Hideout nível 5 ou superior
3. Iniciar o craft no Hideout
4. Aguardar 2 horas
5. Receber o Cristal de Fundação
6. Usar o cristal para criar o Santuário permanente

### Para Implementação no Bot

No cog do Hideout/Sanctuary:

```python
@app_commands.command(name="criar_santuario")
async def criar_santuario(self, interaction: discord.Interaction):
    """Usa o Cristal de Fundação para criar um Santuário"""
    
    # Verificar se player tem o cristal
    cristal = await self.bot.db.fetchrow(
        """
        SELECT item_id FROM inventory 
        WHERE user_id = $1 
        AND item_id = (SELECT id FROM items WHERE name = 'Cristal de Fundação do Santuário')
        """,
        interaction.user.id
    )
    
    if not cristal:
        return await interaction.response.send_message(
            "❌ Você não possui um Cristal de Fundação do Santuário!",
            ephemeral=True
        )
    
    # Verificar se é líder da guilda
    # ... (seu código existing)
    
    # Consumir o cristal e criar sanctuary
    # ... (seu código existing)
```

## 📊 Estatísticas

- **Items criados**: 16 (1 cristal + 15 materiais)
- **Receitas adicionadas**: 1
- **Tempo estimado para coletar todos os materiais**: 50-100 horas de jogo (em guilda)
- **Dificuldade**: ⭐⭐⭐⭐⭐ (Lendária)

## 🔄 Versão

- **Data de Criação**: 2026-02-08
- **Sistema Compatível**: Depth System (Profundidades 1-8)
- **Versão do Schema**: Pós-migração Tier→Depth

## ⚠️ Notas Importantes

1. Os IDs dos items nos SQLs são `NULL` ou exemplos - **DEVEM ser ajustados após popular o banco**
2. A seção de `hideout_recipe_materials` está comentada - **descomentar após ajustar IDs**
3. O sistema assume que você já tem a migração Tier→Depth completa
4. Os materiais podem ser obtidos via drops, craft, ou compra (design de economia fica a seu critério)

## 🎨 Customização

Sinta-se livre para ajustar:
- Quantidades de materiais
- Tempo de craft
- Nível mínimo de Hideout
- Raridade dos items
- Adicionar mais materiais ou remover alguns
