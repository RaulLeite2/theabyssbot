# 🔐 Sistema de Geração de Itens - Implementação

## Visão Geral

O sistema de itens foi totalmente reformulado para **desacoplamento total** entre autorização e definição de poder.

### Antes (v1.0) ❌
```python
# Admin define poder AQUI no comando
/genitem nome:"Espada X" base_damage:500 base_defense:0 slot_id:4
```
**Problema**: Qualquer um que roubar o código vê a fórmula de power scaling

### Agora (v2.0) ✅
```python
# Admin apenas AUTORIZA a criação
/genitem nome:"Espada X" item_identifier:"espada_lendaria" slot_id:4

# Attributes vêm do arquivo criptografado data/Itens.enc
# Usuário NUNCA consegue ver os valores reais
```

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│  /genitem (Discord Command)                                 │
│  └─ nome: "Espada X"                                         │
│  └─ item_identifier: "espada_lendaria"                       │
│  └─ slot_id: 4                                               │
│  └─ tier_range: 1.0 até 8.4                                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                    Busca no arquivo
                             │
┌────────────────────────────▼────────────────────────────────┐
│  data/Itens.enc (Criptografado com Fernet)                  │
│                                                              │
│  {                                                           │
│    "4": {                                                    │
│      "espada_lendaria": {                                    │
│        "base_damage": 2500,                                  │
│        "base_defense": 0,                                    │
│        "scaling": { "str": 3.5, ... },                       │
│        "buffs": [...],                                       │
│        "flags": { "legendary": true, ... }                   │
│      }                                                       │
│    }                                                         │
│  }                                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                      AttributeS Resolved
                             │
┌────────────────────────────▼────────────────────────────────┐
│  INSERT INTO items (Com valores REAIS de Itens.enc)          │
│  - name: "Espada X"                                          │
│  - basedamage: 2500                                          │
│  - basedefense: 0                                            │
│  - tier/subtier: 1.0 até 8.4 (loop)                          │
└────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. **utils/item_integrity.py** 🔐
Gerencia criptografia e descriptografia do arquivo.

```python
from utils.item_integrity import item_integrity

# Criptografa JSON para Itens.enc
items_dict = {...}
item_integrity.encrypt_items(items_dict)

# Descriptografa (com fail-safe)
items = item_integrity.decrypt_items()  # None se falhar
```

**Fail-safe Automático**:
- Arquivo corrompido → retorna `None` (silencioso)
- Chave inválida → retorna `None` (silencioso)
- Arquivo inexistente → retorna `None` (silencioso)

### 2. **services/item_resolver.py** 🎯
Resolve atributos de itens durante execução.

```python
from services.item_resolver import item_resolver

# Resolve atributos de um item
attrs = item_resolver.resolve_item(slot_id=4, item_identifier="espada_lendaria")

if attrs:  # Só executa se encontrado
    damage = attrs["base_damage"]
    buffs = attrs.get("buffs", [])
```

### 3. **data/Itens.enc** 🗝️
Arquivo criptografado com configuração de itens.

**Estrutura JSON (antes de criptografar)**:
```json
{
  "slot_id": {
    "item_identifier": {
      "base_damage": int,
      "base_defense": int,
      "scaling": {
        "str": float,
        "dex": float,
        "int": float
      },
      "buffs": [
        {"type": "crit_chance", "value": 15}
      ],
      "flags": {
        "legendary": bool,
        "tradeable": bool,
        "quest_item": bool
      }
    }
  }
}
```

### 4. **Comando /genitem (Desacoplado)** ⚔️
Apenas autoriza criação, sem definir poder.

**Antes**:
```
/genitem nome:"Espada" base_damage:500 base_defense:0 ...
                       ↑ Admin define poder aqui (INSEGURO!)
```

**Agora**:
```
/genitem nome:"Espada" item_identifier:"espada_lendaria" slot_id:4 ...
                       ↑ Busca no arquivo criptografado
```

---

## Como Usar

### Setup Inicial

1. **Crear arquivo itens_config.json** em `data/`:
```json
{
  "4": {
    "minha_espada": {
      "base_damage": 1000,
      "base_defense": 0,
      "scaling": {"str": 2.0, "dex": 1.0, "int": 0},
      "buffs": [{"type": "lifesteal", "value": 10}],
      "flags": {"legendary": false, "tradeable": true, "quest_item": false}
    }
  }
}
```

2. **Criptografar** (gera `data/Itens.enc`):
```bash
python scripts/encrypt_items.py
```

3. **Bot já carrega automaticamente**:
- `main.py` chama `item_resolver.load()` no startup
- logs: `"✅ Itens carregados: 9 slots, 13 itens"`

### Criando Items

```bash
# Sintaxe: /genitem nome IDENTIFIER slot_id [tier_range] [coletavel]
/genitem nome:"Espada Lendária" item_identifier:"lamina_abissal" slot_id:4 start_tier:1 end_tier:8

# Bot busca "lamina_abissal" no slot 4 de Itens.enc
# Se encontrado: cria os items com atributos do arquivo
# Se NÃO encontrado: ❌ "Item 'lamina_abissal' não encontrado no slot 4"
```

### Atualizando Items

Editar `data/itens_config.json` e reexecutar:
```bash
python scripts/encrypt_items.py
```

O bot recarrega na próxima inicialização.

---

## Segurança

### ✅ O que é Protegido

- **base_damage/defense**: Nunca exposto no comando Discord
- **Buffs secretos**: Definidos no arquivo, usuário nunca vê
- **Flags**: `legendary`, `quest_item`, etc vêm do arquivo
- **Scaling**: Fórmulas de stat escalation protegidas

### ⚠️ O que Ainda é Visível

- **Nome do item**: Visto no comando (é intencional)
- **Slot ID**: Visto no comando (é necessário para validação)
- **Tier range**: Visto (quantas cópias criar)

### 🔐 Proteção da Chave

A chave de criptografia Fernet está em `utils/item_integrity.py`:
```python
ENCRYPTION_KEY = b'Zq4t7w!z%C*F-JaNdRgUkXp2s5v8y/B?E(H+MbQeThW'
```

**Em Produção (Railway)**:
1. Gerar chave nova: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"`
2. Adicionar em variável de ambiente Railway: `ITEMS_ENCRYPTION_KEY=...`
3. Sistema usa env var automaticamente

---

## Troubleshooting

### ❌ "Item 'X' não encontrado no slot Y"
- Verifique o identificador em `data/itens_config.json`
- Pode ser case-sensitive

### ❌ "Falha ao carregar arquivo de itens"
- `data/Itens.enc` corrompido ou não existe
- Reexecute `python scripts/encrypt_items.py`

### ❌ "Bot carregou mas /genitem não funciona"
- Sincronize comandos: `/` (slash) → espere ou restart bot
- Ou use `/reload` se implementado

---

## Exemplos Real

### Exemplo 1: Espada Simples
```json
{
  "4": {
    "espada_ferro": {
      "base_damage": 150,
      "base_defense": 0,
      "scaling": {
        "str": 1.5,
        "dex": 0.8,
        "int": 0
      },
      "buffs": [],
      "flags": {
        "legendary": false,
        "tradeable": true,
        "quest_item": false
      }
    }
  }
}
```

### Exemplo 2: Item Lendário com Buffs
```json
{
  "5": {
    "armadura_celestial": {
      "base_damage": 0,
      "base_defense": 1800,
      "scaling": {
        "str": 2.5,
        "dex": 1.0,
        "int": 1.5
      },
      "buffs": [
        {"type": "holy_resistance", "value": 50},
        {"type": "damage_reflection", "value": 20},
        {"type": "exp_boost", "value": 10}
      ],
      "flags": {
        "legendary": true,
        "tradeable": false,
        "quest_item": true
      }
    }
  }
}
```

---

## API Reference

### ItemIntegrityManager

```python
from utils.item_integrity import item_integrity

# Todos os métodos são fail-safe (retornam None em caso de erro)
item_integrity.decrypt_items() -> Dict or None
item_integrity.encrypt_items(dict) -> bool
item_integrity.get_item_config(slot_id, item_id) -> Dict or None
item_integrity.clear_cache()
```

### ItemResolverService

```python
from services.item_resolver import item_resolver

# Carregar na inicialização
item_resolver.load() -> bool

# Resolver um item
item_resolver.resolve_item(slot_id, item_identifier) -> Dict or None

# Listar items em um slot
item_resolver.list_item_identifiers(slot_id) -> list

# Validar existência
item_resolver.validate_item_exists(slot_id, item_identifier) -> bool
```

---

## Próximas Melhorias

- [ ] Dashboard web para editar Itens.enc
- [ ] Auditoria de criação de items (log com timestamp)
- [ ] Versioning de Itens.enc (backup)
- [ ] Sistema de "templates" para gerar múltiplos items
- [ ] Discord webhook para notificar quando arquivo é carregado

---

**Status**: ✅ Implementado e Testado  
**Última Atualização**: [DATA]  
**Autor**: Sistema de Desacoplamento Total v2.0
