-- ============================================================================
-- ROLLBACK: Tier System → Depth System Migration
-- Versão: 1.0 | ESTE SCRIPT DESFAZ A MIGRAÇÃO
-- ============================================================================

-- PASSO 1: Remover colunas novas das tabelas
ALTER TABLE items DROP COLUMN IF EXISTS depth_new CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS quality_new CASCADE;
ALTER TABLE items DROP COLUMN IF EXISTS plus_level CASCADE;

ALTER TABLE equipment DROP COLUMN IF EXISTS depth_new CASCADE;
ALTER TABLE equipment DROP COLUMN IF EXISTS quality_new CASCADE;
ALTER TABLE equipment DROP COLUMN IF EXISTS plus_level CASCADE;

ALTER TABLE user_items DROP COLUMN IF EXISTS depth_new CASCADE;
ALTER TABLE user_items DROP COLUMN IF EXISTS quality_new CASCADE;
ALTER TABLE user_items DROP COLUMN IF EXISTS plus_level CASCADE;

-- PASSO 2: Remover função de conversão
DROP FUNCTION IF EXISTS tier_to_depth_converter(tier VARCHAR);

-- PASSO 3: Remover colunas de energia do sanctuary
ALTER TABLE sanctuary DROP COLUMN IF EXISTS energy;
ALTER TABLE sanctuary DROP COLUMN IF EXISTS max_energy;
ALTER TABLE sanctuary DROP COLUMN IF EXISTS last_energy_update;
ALTER TABLE sanctuary DROP COLUMN IF EXISTS energy_decay_rate;

-- PASSO 4: Renomear sanctuary de volta para hideout
ALTER TABLE sanctuary RENAME TO hideout;
ALTER TABLE sanctuary_members RENAME TO hideout_members;
ALTER TABLE sanctuary_upgrades RENAME TO hideout_upgrades;

-- PASSO 5: Remover índices criados
DROP INDEX IF EXISTS idx_items_depth_quality;
DROP INDEX IF EXISTS idx_equipment_depth_quality;
DROP INDEX IF EXISTS idx_sanctuary_energy;

COMMIT;
