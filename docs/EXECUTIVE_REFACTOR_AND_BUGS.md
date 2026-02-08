# 🔧 EXECUTIVO: REFATORAÇÃO COMPLETA + BUG FIXES

## 📊 STATUS GERAL

**Data**: 2026-02-08  
**Escopo**: Tier → Depth + Hideout → Sanctuary + Bug fixes  
**Tempo Estimado**: 3-4 horas (refactoring) + 2-3 horas (testes)  

---

## ✅ FASE 1: INFRAESTRUTURA (COMPLETADA)

- [x] `utils/depth_system.py` - Sistema Depth base (274 linhas)
- [x] `utils/cog_version_system.py` - Gerenciador de versões
- [x] `db/migrations/001_tier_to_depth_migration.sql` - SQL migration
- [x] `db/migrations/001_tier_to_depth_migration_rollback.sql` - Rollback script
- [x] `scripts/migrate_to_depth.py` - Migration automation
- [x] `scripts/validate_depth_migration.py` - Validador de dados
- [x] `cogs/rpg/rpg_refactored.py` - RPG refatorado para Depth

### Como usar:
```bash
# 1. Backup antes
# 2. Executar migração
python scripts/migrate_to_depth.py

# 3. Validar
python scripts/validate_depth_migration.py

# 4. Se erro: rollback
python scripts/migrate_to_depth.py --rollback
```

---

## 🐛 FASE 2: BUGS IDENTIFICADOS

### 2.1 CRITICAL - Logging deficiente
**Arquivos**: `cogs/guild/guild.py`, `cogs/guild/ally.py`, `cogs/rpg/rpg_battle.py` + 8+
**Problema**: Uso de `print()` em produção ao invés de `logging`  
**Impacto**: Erros não rastreáveis em logs persistentes  
**Solução**:
```python
# ❌ ANTES
except Exception as e:
    print(f"Error: {e}")

# ✅ DEPOIS
import logging
logger = logging.getLogger(__name__)
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
```

**Arquivos Afetados**:
- `cogs/guild/guild.py` (linha 47)
- `cogs/guild/ally.py` (linhas 108, 176, 256, 359, 418, 503, 604, 709) - 8 instâncias
- `cogs/rpg/rpg_battle.py` (linha 207)
- `cogs/rpg/rpg.py` (linha 110)
- Potencialmente mais em: `cogs/rpg/*`, `cogs/economy/*`

### 2.2 MEDIUM - Exception handling genérico
**Problema**: `except asyncio.CancelledError: pass` sem logging  
**Arquivos**: `cogs/guild/hideout.py` (linha 163), `cogs/special/zahuv.py` (4 linhas)  
**Impacto**: Background tasks podem falhar silenciosamente  
**Solução**: Logar cancelamentos para debugging

### 2.3 MEDIUM - Tier system hardcoded
**Problema**: T1-T8 em strings de UI, validações hardcoded  
**Arquivos**: Todos `cogs/rpg/*`, `cogs/arena/*`, `cogs/economy/*`  
**Impacto**: UI mostra "Tier 1-8" em vez de "Depth 1-8" após migração  
**Solução**: Usar `utils/depth_system.Quality` enum e formatadores

### 2.4 MEDIUM - Validações de slot_id faltando
**Problema**: Algumas queries não validam `slot_id`  
**Arquivo**: `cogs/rpg/rpg_ui.py`, `cogs/arena/arena_ui.py`  
**Impacto**: Potencial crash ao equipar items inválidos  
**Solução**: Adicionar validação de 1-9 range

### 2.5 LOW - Strings SQL sem prepared statements em alguns pontos
**Arquivos**: `cogs/rpg/rpg_npc.py`, `cogs/guild/hideout.py`  
**Impacto**: Potencial SQL injection (baixo risco - parâmetros internos)  
**Solução**: Converter para parameterized queries

---

## 🔄 FASE 3: REFATORAÇÃO DE COGS

### Prioridade 1 (Crítico - afeta todos os usuários)

#### 3.1 Atualizar `cogs/rpg/rpg.py`
- [ ] Usar `rpg_refactored.py` como base
- [ ] Manter compatibilidade com dados antigos (tier)
- [ ] Atualizar UI para mostrar Depth ao invés de Tier
- [ ] Adicionar logging.logger para erros
- **Tempo**: 45 min

#### 3.2 Atualizar `cogs/rpg/rpg_profile.py`
- [ ] Mostra Depth em vez de Tier no perfil
- [ ] Calcular power_value() usando novo sistema
- [ ] Mostrar Quality badges
- **Tempo**: 30 min

#### 3.3 Atualizar `cogs/rpg/rpg_ui.py`
- [ ] Equipment view usa depth_new em vez de tier
- [ ] Validar slot_id (1-9)
- [ ] Formatação de qualidade com cores Discord
- **Tempo**: 45 min

### Prioridade 2 (Alto - sistemas secundários)

#### 3.4 Atualizar `cogs/guild/hideout.py`
- [ ] Renomear tabelas (hideout → sanctuary) ✅ SQL pronto
- [ ] Adicionar energy_decay() task
- [ ] Logs com logger instead of print()
- **Tempo**: 1h

#### 3.5 Atualizar `cogs/economy/shop.py`
- [ ] Atualizar preços baseado em Depth + Quality
- [ ] Usar fórmula: base_price × depth_multiplier × quality_multiplier
- **Tempo**: 30 min

#### 3.6 Atualizar `cogs/arena/arena_ui.py`
- [ ] Mostrar powerscores em Depth system
- [ ] Novo cálculo: (depth × 15) × quality.multiplier()
- **Tempo**: 30 min

### Prioridade 3 (Médio - refactor cosmético)

#### 3.7 Atualizar Wiki cog
- [ ] Já estava refatorada ✅
- [ ] Verificar compatibilidade com depth_new/quality_new
- **Tempo**: 10 min

---

## 🛠️ FASE 4: CORREÇÃO DE BUGS

### Step 1: Converter todos os `print()` para `logger.error()`
```bash
# Arquivo: scripts/fix_logging.py
python scripts/fix_logging.py
```
**Afeta**: 15+ arquivos

### Step 2: Adicionar validações de safety
- Validar slot_id em equipment
- Validar depth range (1-8)
- Validar quality enum
- **Arquivo**: `utils/validators.py` (criar novo)

### Step 3: Atualizar queries SQL
- Usar parameterized queries em 100% dos casos
- Adicionar índices para performance
- **Tempo**: 1h

### Step 4: Testes de coexistência
```python
# Teste: Tier compatibilidade
old_item = await db.fetchrow("SELECT tier FROM items WHERE id = 1")
tier = old_item['tier']  # "T3.2"

# Deve converter automático
converted = TierMigrator.convert_tier_to_depth(tier)
assert converted.depth == 3
assert converted.quality == Quality.RARE
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Pre-Migration
- [ ] Criar backup do banco (automático em `migrate_to_depth.py`)
- [ ] Testar script de migration em ambiente de staging
- [ ] Verificar lista de playeres (para notificação)

### Durante Migration
- [ ] Executar `python scripts/migrate_to_depth.py`
- [ ] Monitorar erro (tempo ~30-60 seg)
- [ ] Validar com `python scripts/validate_depth_migration.py`

### Pós-Migration
- [ ] [ ] Atualizar `main.py` para carregar cogs refatorados
- [ ] [ ] Testar `/rpg start` - deve dar items Depth 1
- [ ] [ ] Testar `/rpg profile` - deve mostrar Depth
- [ ] [ ] Testar `/wiki` - deve buscar items func

### Cogs a testar
- [ ] `/rpg start`
- [ ] `/rpg profile`
- [ ] `/rpg stats`
- [ ] `/ho list` (sanctuary, não hideout)
- [ ] `/wiki buscar`
- [ ] `/shop comprar`
- [ ] `/arena stats`

---

## 🚨 ROLLBACK PROCEDURE

Se algo der errado:

```bash
# 1. Parar o bot
# 2. Restaurar último backup antigo (se disponível)
# 3. Ou executar rollback
python scripts/migrate_to_depth.py --rollback

# 4. Reiniciar bot
python main.py
```

---

## 📈 PRÓXIMOS PASSOS (Pós-Migração)

### Curto Prazo (1-2 dias)
- Monitorar logs para novos bugs
- Feedback de usuários
- Pequenas correções

### Médio Prazo (1 semana)
- Implementar Energy system (Phase X do REFACTORING_PLAN)
- Balanceamento de power scores
- Novas features baseadas em Depth

### Longo Prazo
- Remover completamente suporte a Tier system (1-2 semanas pós-migração)
- Otimização de dados (limpar campos antigos)

---

## 📞 STATUS CALLS

Cada cog refatorado deve ligar para seu refactor em paralelo:

```bash
# Tempo total: 3-4 horas se feito sequencial
# OTIMZADO: 1.5-2 horas se paralelo (aguardar cogs independentes)

Prioridade 1: rpg.py + rpg_profile.py + rpg_ui.py (em paralelo)
    ↓
Prioridade 2: hideout.py + shop.py + arena_ui.py (em paralelo)
    ↓
Prioridade 3: Testes
    ↓
Deploy
```

---

## 🔐 SAFETY RAILS

```python
# Sempre em transação
async with db.pool.acquire() as conn:
    async with conn.transaction():
        # Duas não podem acontecer simultaneamente
        
# Sempre com rollback
await db.execute("ROLLBACK") if error else None

# Sempre validar
validator = MigrationValidator(db)
if not await validator.run_all_checks():
    raise Exception("Validation failed")
```

---

## 📁 ARQUIVOS CRIADOS NESTA SESSION

```
✅ utils/depth_system.py (274 linhas)
✅ utils/cog_version_system.py (120 linhas)
✅ db/migrations/001_tier_to_depth_migration.sql
✅ db/migrations/001_tier_to_depth_migration_rollback.sql
✅ scripts/migrate_to_depth.py (300+ linhas)
✅ scripts/validate_depth_migration.py (350+ linhas)
✅ cogs/rpg/rpg_refactored.py (400+ linhas)
🔄 docs/EXECUTIVE_REFACTOR_AND_BUGS.md (THIS FILE)
```

**Total**: ~2000 linhas de código novo + 8 arquivos de infra

---

## ⏱️ ESTIMATIVA FINAL

Se implementar TODAS as soluções acima:

| Fase | Tempo | Status |
|------|-------|--------|
| 1. Infra | ✅ DONE | 0h (já feito) |
| 2. Fix Logging | 1h | Not started |
| 3. Refactor Cogs | 2.5h | Not started |
| 4. Bug Fixes | 1h | Not started |
| 5. Tests | 1-2h | Not started |
| **TOTAL** | **5.5-6.5h** | 0% |

**Se apenas Tier→Depth (sem bug fixes)**:  
→ **2-3 horas**

---

Gerado: 08/02/2026 | Autor: Copilot
