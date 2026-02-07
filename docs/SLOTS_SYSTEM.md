# 🎰 Sistema de Slots - The Abyss

## 📋 Visão Geral

O sistema de slots define onde cada item pode ser equipado no personagem. Cada slot tem um ID único e uma função específica.

## 🗂️ Lista Completa de Slots

| Slot ID | Nome | Emoji | Tipo | Descrição |
|---------|------|-------|------|-----------|
| **1** | Amuleto | 📿 | Acessório | Amuletos mágicos e talismãs |
| **2** | Cabeça | 🪖 | Armadura | Elmos, capacetes, capuzes |
| **3** | Pernas | 👖 | Armadura | Calças, grevas, proteção de pernas |
| **4** | Mão Principal | ⚔️ | Arma | Armas principais (espadas, machados, cajados, arcos) |
| **5** | Torso | 🎽 | Armadura | Peitorais, armaduras, túnicas |
| **6** | Mão Secundária | 🛡️ | Acessório | Escudos, anéis, braceletes |
| **7** | Costas | 🧥 | Acessório | Capas, mantos (não implementado) |
| **8** | Pés | 👢 | Armadura | Botas, sapatos, sandálias |
| **9** | Recursos | 📦 | Especial | Itens coletáveis NÃO equipáveis |

## 📦 Slot Especial: Recursos (ID 9)

O Slot ID 9 é reservado exclusivamente para **recursos coletáveis**:

### Características
- ❌ **NÃO equipável** no personagem
- ✅ **Coletável** através de `/explore`
- 🔨 Usado em **crafting** e **construção**
- 📊 Geralmente tem apenas **Tier 1.0** (único tier)
- ⚔️ Dano e defesa sempre **0**

### Recursos Disponíveis
- 🪵 **Madeira** - Estruturas, arcos, cajados
- 🪨 **Pedra** - Fundações, fortalecimento
- ⛏️ **Minério** - Armas metálicas, armaduras
- 🧵 **Fibra** - Tecidos, roupas leves
- 🦌 **Pelego** - Couro, proteção
- 💎 **Cristal** - Encantamentos (raro)
- 🌿 **Ervas Medicinais** - Poções

## ⚔️ Slots de Combate (IDs 1-8)

### Armas (Slot 4)
- **Tipos**: Espadas, Adagas, Machados, Cajados, Arcos
- **Atributo Principal**: `basedamage` (dano)
- **Basedefense**: 0 ou NULL

### Armaduras (Slots 2, 3, 5, 8)
- **Tipos**: Elmos, Torsos, Pernas, Botas
- **Atributo Principal**: `basedefense` (defesa)
- **Basedamage**: 0 ou NULL

### Acessórios (Slots 1, 6, 7)
- **Tipos**: Amuletos, Anéis, Escudos, Capas
- **Atributos**: Variam (podem ter defesa ou efeitos especiais)

## 🎯 Ordem de Equipamento Recomendada

Para jogadores iniciantes, esta é a prioridade de equipamento:

1. **Mão Principal (4)** - Arma para causar dano
2. **Torso (5)** - Maior proteção
3. **Cabeça (2)** - Proteção vital
4. **Pernas (3)** - Mobilidade e defesa
5. **Pés (8)** - Velocidade e agilidade
6. **Mão Secundária (6)** - Defesa extra ou efeitos

## 💻 Uso no Código

### Verificar Tipo de Slot
```python
# Verificar se é arma
if slot_id == 4:
    # É uma arma, deve ter basedamage

# Verificar se é recurso
if slot_id == 9:
    # É recurso, não equipável
    # Deve ter is_collectible = True
```

### Criar Item por Slot
```discord
# Arma (Slot 4)
/genitem nome:"Espada" base_damage:10 slot_id:4 ...

# Armadura (Slot 5)
/genitem nome:"Peitoral" base_defense:15 slot_id:5 ...

# Recurso (Slot 9)
/genitem nome:"Madeira" base_damage:0 base_defense:0 slot_id:9 is_collectible:true ...
```

## 🔍 Referência Rápida no Código

### Arquivo: `rpg.py`
```python
# Slot IDs: 2=Head, 3=Legs, 4=Main Hand, 5=Torso, 6=Off Hand, 8=Feet
slot_ids = [4, 5, 2, 3, 8, 6]  # Ordem de equipamento inicial
```

### Arquivo: `starter_items.txt`
```
1 = Amuleto
2 = Cabeça (Head)
3 = Pernas (Legs)
4 = Mão Principal (Main Hand) - ARMAS
5 = Torso (Chest)
6 = Mão Secundária (Off Hand)
7 = Costas (Back/Cape)
8 = Pés (Feet)
9 = Recursos Coletáveis (NÃO EQUIPÁVEL)
```

## ⚠️ Regras Importantes

### Para Criação de Itens
1. **Armas (Slot 4)**:
   - SEMPRE `basedamage > 0`
   - `basedefense = 0` ou NULL
   - `is_collectible = false`

2. **Armaduras (Slots 2, 3, 5, 8)**:
   - SEMPRE `basedefense > 0`
   - `basedamage = 0` ou NULL
   - `is_collectible = false`

3. **Recursos (Slot 9)**:
   - SEMPRE `basedamage = 0`
   - SEMPRE `basedefense = 0`
   - SEMPRE `is_collectible = true`
   - Geralmente `tier = 1`, `subtier = 0`

### Para Equipamento
- Um jogador só pode equipar **1 item por slot** (exceto slot 9)
- Slot 9 é para **inventário**, não para equipamento
- Equipamentos têm múltiplos tiers (T1.0 até T8.4)
- Recursos têm apenas 1 tier (T1.0)

## 📊 Distribuição de Itens por Slot

| Slot | Quantidade Aproximada | Variação de Tier |
|------|----------------------|------------------|
| 1 | Baixa | T1-T8 |
| 2 | Média | T1-T8 |
| 3 | Média | T1-T8 |
| 4 | Alta | T1-T8 |
| 5 | Média | T1-T8 |
| 6 | Média | T1-T8 |
| 7 | Baixa | T1-T8 |
| 8 | Média | T1-T8 |
| 9 | Baixa | T1 apenas |

## 🎮 Comandos Relacionados

- `/equip` - Equipar item em um slot
- `/unequip` - Desequipar item de um slot
- `/profile` - Ver todos os slots equipados
- `/explore` - Coletar recursos (slot 9)
- `/craft` - Usar recursos para criar itens

## 🔗 Ver Também

- [COLLECTIBLE_SYSTEM.md](COLLECTIBLE_SYSTEM.md) - Sistema de coletáveis
- [NPC_SYSTEM.md](NPC_SYSTEM.md) - Sistema de NPCs e recompensas
- `starter_items.txt` - Lista completa de itens por slot
- `schema.sql` - Estrutura do banco de dados
