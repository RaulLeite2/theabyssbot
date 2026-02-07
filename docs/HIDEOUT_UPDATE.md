# 🏠 Hideout System Update - Sistema Completo

## 📋 Visão Geral

Este update transforma os Hideouts em bases funcionais onde guilds podem:
- **Entrar e sair** dinamicamente do Hideout
- **Craftar itens especiais** exclusivos
- **Participar de dungeons de 5 jogadores** com recompensas épicas
- **Sistema de Power Score** baseado em equipamentos

---

## 🗺️ Sistema de Notificação

### Como Funciona
Quando um jogador **explora uma zona** ou **atravessa um portal**, o sistema verifica automaticamente se há um Hideout da sua guilda ou aliança na zona.

### Notificação
Se encontrado, o jogador recebe uma notificação privada com:
- Nome do Hideout
- Pertence à guilda ou aliança
- Nível de energia atual
- Dica para usar `/ho entrar`

---

## 🚪 Entrada e Saída do Hideout

### Comandos

#### `/ho entrar`
- **Requisitos:**
  - Estar em uma guilda
  - Estar em uma zona com Hideout da sua guilda/aliança
  - Hideout deve ter energia > 0

- **Efeito:**
  - Move o jogador para dentro do Hideout
  - Salva a zona anterior
  - Mostra instalações disponíveis
  - Exibe seu Power Score atual

#### `/ho sair`
- **Efeito:**
  - Retorna o jogador à zona anterior
  - Remove do Hideout

---

## 💪 Sistema de Power Score

### Cálculo
O Power Score é calculado automaticamente baseado nos itens equipados:

```
Power Score = (Weapon Power) + (Armor Power)

Weapon Power = (basedamage × 2) + (tier × 50)
Armor Power = (basedefense × 2) + (tier × 50)
```

### Exemplo
- **Arma:** Tier 7, 150 damage → Power = (150×2) + (7×50) = 650
- **Armadura:** Tier 6, 100 defense → Power = (100×2) + (6×50) = 500
- **Total:** 1150 Power Score

### Uso
- Requerido para entrar em dungeons do Hideout
- Mostrado ao entrar no Hideout
- Calculado em tempo real

---

## 🔨 Sistema de Crafting

### Pré-requisitos
- Hideout precisa ter **Estação de Crafting** (500k gold)
- Jogador deve estar **dentro do Hideout**
- Hideout deve ter nível mínimo da receita

### Comandos

#### `/ho recipes`
Lista todas as receitas de crafting disponíveis com:
- ID da receita
- Nome do item resultante
- Materiais necessários
- Nível mínimo do Hideout

#### `/ho craft <recipe_id>`
Inicia o crafting de um item:
1. Verifica materiais no inventário
2. Consome materiais
3. Adiciona à fila de crafting
4. Aguarda tempo de craft
5. Item é entregue quando pronto

### Estrutura das Receitas

```sql
hideout_recipes:
- id
- name
- description
- result_item_id (item craftado)
- result_quantity
- min_hideout_level
- craft_time_seconds

hideout_recipe_materials:
- recipe_id
- item_id (material necessário)
- quantity
```

---

## 🌀 Dungeon Especial do Hideout

### Requisitos

#### Para o Hideout
- Deve ter **Portal da Dungeon** ativo (500k gold)
- Sem cooldown ativo (1 hora após cada run)

#### Para a Party
- **5 jogadores** na party
- Todos dentro do **mesmo Hideout**
- **1500+ Power Score total** entre todos

### Como Funciona

#### 1. Formação da Party
```
/party_create (líder cria a party)
/party_invite @player (convida membros)
```

#### 2. Preparação
- Todos entram no Hideout (`/ho entrar`)
- Líder verifica Power Score total
- Sistema calcula se atendem os 1500 pontos

#### 3. Início da Dungeon
```
/ho dungeon
```

Sistema verifica:
- ✅ 5 pessoas presentes
- ✅ Todos no mesmo Hideout  
- ✅ 1500+ Power total
- ✅ Sem cooldown

#### 4. Batalha
- Dungeon processa automaticamente
- Dificuldade baseada no **nível do Hideout**
- 70% chance base de sucesso
- 3 segundos de duração

#### 5. Recompensas
**Se sucesso:**
- Gold para cada membro (proporcional ao poder individual)
- Itens raros (implementação futura)
- XP da dungeon (implementação futura)

**Fórmula de Gold:**
```
Gold = (difficulty_tier × 10,000) + (player_power × 100)
```

Exemplo com Hideout Tier 3:
- Player com 300 power: 30,000 + 30,000 = 60,000 gold
- Player com 500 power: 30,000 + 50,000 = 80,000 gold

#### 6. Cooldown
- 1 hora após cada tentativa
- Aplica-se ao Hideout, não aos jogadores

---

## 🏗️ Melhorias do Hideout

### `/ho facility <tipo>`

#### Estação de Crafting
- **Custo:** 500,000 gold
- **Efeito:** Desbloqueia sistema de crafting
- **Pago por:** Cofre da guilda

#### Portal da Dungeon  
- **Custo:** 500,000 gold
- **Efeito:** Habilita dungeon especial
- **Pago por:** Cofre da guilda

### Requisitos
- Apenas **líder da guilda** pode comprar
- Gold vem do **cofre da guilda**
- Permanente (não precisa recomprar)

---

## 📊 Banco de Dados

### Novas Colunas em `users`
```sql
- in_hideout_id: INT (NULL se não estiver em HO)
- previous_zone_id: BIGINT (zona antes de entrar)
- equipped_weapon: BIGINT (arma equipada)
- equipped_armor: BIGINT (armadura equipada)
```

### Novas Colunas em `hideouts`
```sql
- has_crafting_station: BOOLEAN
- has_dungeon_portal: BOOLEAN
- dungeon_cooldown: TIMESTAMP
```

### Novas Tabelas

#### `hideout_recipes`
Receitas de crafting disponíveis

#### `hideout_recipe_materials`
Materiais necessários para cada receita

#### `hideout_crafting_queue`
Fila de itens sendo craftados

#### `hideout_dungeon_runs`
Histórico de dungeons realizadas

#### `hideout_dungeon_party`
Membros que participaram de cada run

#### `hideout_dungeon_rewards`
Recompensas distribuídas por run

---

## 🚀 Instalação

### 1. Aplicar Migration
```bash
psql -U username -d database_name -f db/migration_hideout_update.sql
```

### 2. Reiniciar Bot
O bot carregará automaticamente os novos comandos.

### 3. Testar Funcionalidades
```
/ho entrar
/ho recipes
/ho upgrade crafting
/ho craft 1
/ho dungeon
```

---

## 🎮 Fluxo de Jogo Completo

### Exemplo de Sessão

1. **Jogador explora zona**
   ```
   /explore
   ```
   *"🏠 Hideout Detectado! Esta zona possui o Hideout Fortaleza do Vento!"*

2. **Entra no Hideout**
   ```
   /ho entrar
   ```
   *Power Score: 850 | Energia: 95%*

3. **Verifica receitas**
   ```
   /ho recipes
   ```
   *Lista 10 receitas de crafting*

4. **Inicia crafting**
   ```
   /ho craft 3
   ```
   *Craftando Espada Lendária... 5 minutos*

5. **Líder compra Portal**
   ```
   /ho facility dungeon
   ```
   *Portal da Dungeon ativado! -500k gold*

6. **Forma party de 5**
   ```
   /party_create
   /party_invite @player2 @player3 @player4 @player5
   ```

7. **Todos entram no HO**
   ```
   (Cada um) /ho entrar
   ```

8. **Inicia dungeon**
   ```
   /ho dungeon
   ```
   *Party: 5 membros | Power: 1650/1500 ✅*

9. **Batalha processa**
   *3 segundos depois...*
   
10. **Recompensas**
    *✅ Dungeon Completa! Cada membro recebeu 60k-80k gold*

---

## ⚠️ Limitações e Futuras Melhorias

### Atual
- Dungeon é simulada (não tem batalha real)
- Recompensas apenas em gold
- Receitas precisam ser populadas manualmente
- Power Score não considera outros equipamentos

### Planejado
- Sistema de batalha por turnos na dungeon
- Boss final com mecânicas especiais
- Loot table específica com itens únicos
- Power Score incluindo botas, luvas, acessórios
- Sistema de melhorias progressivas do Hideout
- Defesas automáticas do Hideout contra invasões
- Ranking de dungeons completadas

---

## 🔧 Comandos Administrativos

### Popular Receitas (Exemplo SQL)
```sql
-- Receita exemplo: Espada Épica
INSERT INTO hideout_recipes (name, description, result_item_id, result_quantity, min_hideout_level, craft_time_seconds)
VALUES ('Espada do Abismo', 'Espada forjada nas profundezas', 101, 1, 3, 600);

-- Materiais necessários
INSERT INTO hideout_recipe_materials (recipe_id, item_id, quantity)
VALUES 
  (1, 50, 10),  -- 10x Minério Obscuro
  (1, 51, 5),   -- 5x Fragmento de Cristal
  (1, 52, 1);   -- 1x Essência do Abismo
```

---

## 📞 Suporte

Para issues ou sugestões:
- Verifique logs do bot: `print()` statements incluídos
- Teste com SQL queries diretamente
- Use `/ho info` para debug de estado do Hideout

---

**Versão:** 2.0  
**Data:** Janeiro 2026  
**Autor:** Sistema The Abyss
