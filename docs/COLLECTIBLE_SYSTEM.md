# 🌿 Sistema de Recursos Coletáveis - The Abyss

## 📋 Resumo das Alterações

### 1. Banco de Dados
- **Nova coluna**: `is_collectible` na tabela `items`
- **Tipo**: BOOLEAN (padrão: FALSE)
- **Propósito**: Identificar itens que são recursos coletáveis (madeira, pedra, etc)

### 2. Comando /genitem Atualizado

#### Novo Parâmetro
```
is_collectible: bool = False
```

#### Funcionalidade de Confirmação
Antes de criar os itens, o bot agora mostra um embed de confirmação com:
- ✅ Nome do item
- ⚔️ Dano base
- 🛡️ Defesa base
- 🎰 Slot ID
- 📊 Tier inicial e final
- 📦 Status de coletável
- 📈 Total de itens que serão criados

#### Botões de Ação
- **✅ Confirmar**: Cria os itens
- **❌ Cancelar**: Cancela a operação

## 📦 Recursos Coletáveis Disponíveis

### Recursos Básicos
| Emoji | Nome | Slot ID | Uso Principal |
|-------|------|---------|---------------|
| 🪵 | Madeira | 9 | Estruturas, arcos, cajados |
| 🪨 | Pedra | 9 | Base, fortalecimento |
| ⛏️ | Minério | 9 | Armas, armaduras metálicas |
| 🧵 | Fibra | 9 | Tecidos, roupas leves |
| 🦌 | Pelego | 9 | Couro, proteção |

### Recursos Especiais
| Emoji | Nome | Slot ID | Uso Principal |
|-------|------|---------|---------------|
| 💎 | Cristal | 9 | Encantamentos e itens raros |
| 🌿 | Ervas Medicinais | 9 | Poções e consumíveis |

## 🚀 Como Usar

### Criar um Recurso Coletável
```
/genitem nome:"Madeira" base_damage:0 base_defense:0 slot_id:9 start_tier:1 start_subtier:0 end_tier:1 end_subtier:0 is_collectible:true
```

### Criar um Item Normal (Arma/Armadura)
```
/genitem nome:"Espada de Ferro" base_damage:10 slot_id:4 start_tier:2 start_subtier:0 end_tier:3 end_subtier:4 is_collectible:false
```

### Criar Múltiplos Tiers de Uma Vez
```
/genitem nome:"Lâmina do Abismo" base_damage:25 slot_id:4 start_tier:4 start_subtier:0 end_tier:5 end_subtier:4
```
Isso criará automaticamente todos os tiers de T4.0 até T5.4 (10 itens).

## 📊 Fluxo de Confirmação

```
1. Admin executa /genitem
        ↓
2. Bot mostra embed com preview
        ↓
3. Admin escolhe:
   ✅ Confirmar → Itens criados
   ❌ Cancelar → Operação cancelada
        ↓
4. Bot cria itens e mostra resultado
```

## 🔧 Migration do Banco de Dados

Execute o arquivo `migration_add_collectible.sql` para adicionar a coluna em bancos existentes:

```sql
ALTER TABLE items 
ADD COLUMN IF NOT EXISTS is_collectible BOOLEAN DEFAULT FALSE;
```

## 📝 Convenções

### Slot IDs
- **1**: Amuleto
- **2**: Cabeça (Head)
- **3**: Pernas (Legs)
- **4**: Mão Principal (Main Hand) - ARMAS
- **5**: Torso (Chest)
- **6**: Mão Secundária (Off Hand)
- **7**: Costas (Back/Cape)
- **8**: Pés (Feet)
- **9**: Recursos Coletáveis (NÃO EQUIPÁVEL)

### Recursos Coletáveis
- Sempre use `slot_id:9`
- Sempre use `is_collectible:true`
- Dano e defesa devem ser 0
- Geralmente tier 1.0 (único tier)

### Itens Equipáveis
- Use slots 1-8 conforme o tipo
- `is_collectible:false` (padrão)
- Defina dano OU defesa (não ambos zero)
- Pode ter múltiplos tiers

## 🎯 Ordem de Criação Recomendada

1. **Recursos Coletáveis** (slot_id:9, is_collectible:true)
2. **Itens T1.0** de cada tipo
3. **Itens T2.0** intermediários
4. **Itens T4.0** avançados
5. **Itens T6.0+** lendários

## ⚠️ Notas Importantes

- O comando agora tem timeout de 30 segundos para confirmação
- Se não confirmar a tempo, a operação é cancelada automaticamente
- A confirmação impede criações acidentais de centenas de itens
- Recursos coletáveis NÃO devem ter dano ou defesa base
- Sempre verifique o preview antes de confirmar

## 🔍 Queries Úteis

### Ver todos os recursos coletáveis
```sql
SELECT * FROM items WHERE is_collectible = TRUE;
```

### Ver todos os itens normais
```sql
SELECT * FROM items WHERE is_collectible = FALSE;
```

### Contar por tipo
```sql
SELECT 
    is_collectible,
    COUNT(*) as total
FROM items
GROUP BY is_collectible;
```

## 📚 Arquivos Modificados

- `db/schema.sql` - Adicionado campo is_collectible
- `db/migration_add_collectible.sql` - Migration para bancos existentes
- `cogs/admin/adminrpg.py` - Comando /genitem atualizado com confirmação
- `starter_items.txt` - Comandos de recursos coletáveis adicionados

## 🐛 Troubleshooting

### "Armas precisam de dano base"
- Certifique-se de usar `is_collectible:true` para recursos
- Ou defina um dano base > 0 para armas

### "Armaduras precisam de defesa base"
- Use `is_collectible:true` para recursos
- Ou defina defesa base > 0 para armaduras

### Timeout na confirmação
- O bot espera 30 segundos por resposta
- Reexecute o comando se expirar

---
**Criado em**: 2026-01-09  
**Versão**: 1.0.0
