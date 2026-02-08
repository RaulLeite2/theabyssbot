-- ============================================================================
-- Migration: Tier System → Depth System
-- Versão: 1.0 | Data: 2026-02-08
-- BACKUP REQUERIDO ANTES DE EXECUTAR!
-- ============================================================================

-- PASSO 1: Criar novas colunas em tabelas existentes (abordagem segura)
ALTER TABLE items ADD COLUMN IF NOT EXISTS depth_new INTEGER DEFAULT 1;
ALTER TABLE items ADD COLUMN IF NOT EXISTS quality_new VARCHAR(20) DEFAULT 'common';
ALTER TABLE items ADD COLUMN IF NOT EXISTS plus_level INTEGER DEFAULT 0;

ALTER TABLE equipment ADD COLUMN IF NOT EXISTS depth_new INTEGER DEFAULT 1;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS quality_new VARCHAR(20) DEFAULT 'common';
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS plus_level INTEGER DEFAULT 0;

ALTER TABLE user_items ADD COLUMN IF NOT EXISTS depth_new INTEGER DEFAULT 1;
ALTER TABLE user_items ADD COLUMN IF NOT EXISTS quality_new VARCHAR(20) DEFAULT 'common';  
ALTER TABLE user_items ADD COLUMN IF NOT EXISTS plus_level INTEGER DEFAULT 0;

-- PASSO 2: Função de conversão Tier → Depth (PL/pgSQL)
DROP FUNCTION IF EXISTS tier_to_depth_converter(tier VARCHAR);

CREATE FUNCTION tier_to_depth_converter(tier VARCHAR) 
RETURNS TABLE(depth INTEGER, quality VARCHAR) AS $$
DECLARE
BEGIN
  RETURN QUERY
  SELECT 
    (CASE tier
      WHEN 'T1.0' THEN 1 WHEN 'T1.1' THEN 1 WHEN 'T1.2' THEN 1 WHEN 'T1.3' THEN 1 WHEN 'T1.4' THEN 1
      WHEN 'T2.0' THEN 2 WHEN 'T2.1' THEN 2 WHEN 'T2.2' THEN 2 WHEN 'T2.3' THEN 2 WHEN 'T2.4' THEN 2
      WHEN 'T3.0' THEN 2 WHEN 'T3.1' THEN 3 WHEN 'T3.2' THEN 3 WHEN 'T3.3' THEN 3 WHEN 'T3.4' THEN 3
      WHEN 'T4.0' THEN 3 WHEN 'T4.1' THEN 4 WHEN 'T4.2' THEN 4 WHEN 'T4.3' THEN 4 WHEN 'T4.4' THEN 4
      WHEN 'T5.0' THEN 4 WHEN 'T5.1' THEN 5 WHEN 'T5.2' THEN 5 WHEN 'T5.3' THEN 5 WHEN 'T5.4' THEN 5
      WHEN 'T6.0' THEN 5 WHEN 'T6.1' THEN 6 WHEN 'T6.2' THEN 6 WHEN 'T6.3' THEN 6 WHEN 'T6.4' THEN 6
      WHEN 'T7.0' THEN 6 WHEN 'T7.1' THEN 7 WHEN 'T7.2' THEN 7 WHEN 'T7.3' THEN 7 WHEN 'T7.4' THEN 7
      WHEN 'T8.0' THEN 7 WHEN 'T8.1' THEN 8 WHEN 'T8.2' THEN 8 WHEN 'T8.3' THEN 8 WHEN 'T8.4' THEN 8
      ELSE 1
    END)::INTEGER AS depth_val,
    (CASE tier
      WHEN 'T1.0' THEN 'common' WHEN 'T1.1' THEN 'common' WHEN 'T1.2' THEN 'uncommon' WHEN 'T1.3' THEN 'uncommon' WHEN 'T1.4' THEN 'rare'
      WHEN 'T2.0' THEN 'common' WHEN 'T2.1' THEN 'common' WHEN 'T2.2' THEN 'uncommon' WHEN 'T2.3' THEN 'uncommon' WHEN 'T2.4' THEN 'rare'
      WHEN 'T3.0' THEN 'rare' WHEN 'T3.1' THEN 'rare' WHEN 'T3.2' THEN 'rare' WHEN 'T3.3' THEN 'epic' WHEN 'T3.4' THEN 'epic'
      WHEN 'T4.0' THEN 'epic' WHEN 'T4.1' THEN 'epic' WHEN 'T4.2' THEN 'epic' WHEN 'T4.3' THEN 'legendary' WHEN 'T4.4' THEN 'legendary'
      WHEN 'T5.0' THEN 'legendary' WHEN 'T5.1' THEN 'epic' WHEN 'T5.2' THEN 'epic' WHEN 'T5.3' THEN 'legendary' WHEN 'T5.4' THEN 'legendary'
      WHEN 'T6.0' THEN 'legendary' WHEN 'T6.1' THEN 'legendary' WHEN 'T6.2' THEN 'legendary' WHEN 'T6.3' THEN 'mythic' WHEN 'T6.4' THEN 'mythic'
      WHEN 'T7.0' THEN 'legendary' WHEN 'T7.1' THEN 'legendary' WHEN 'T7.2' THEN 'legendary' WHEN 'T7.3' THEN 'mythic' WHEN 'T7.4' THEN 'mythic'
      WHEN 'T8.0' THEN 'mythic' WHEN 'T8.1' THEN 'legendary' WHEN 'T8.2' THEN 'legendary' WHEN 'T8.3' THEN 'mythic' WHEN 'T8.4' THEN 'mythic'
      ELSE 'common'
    END) AS quality_val;
END;
$$ LANGUAGE plpgsql STABLE;

-- PASSO 3: Popular colunas novas (items)
UPDATE items i
SET depth_new = converted.depth, quality_new = converted.quality
FROM tier_to_depth_converter(i.tier) converted;

-- PASSO 4: Popular colunas novas (equipment)
UPDATE equipment e
SET depth_new = converted.depth, quality_new = converted.quality
FROM tier_to_depth_converter(e.tier) converted;

-- PASSO 5: Popular colunas novas (user_items)
UPDATE user_items ui
SET depth_new = converted.depth, quality_new = converted.quality
FROM items i, tier_to_depth_converter(i.tier) converted
WHERE ui.item_id = i.id;

-- PASSO 6: Renomear hideout para sanctuary (tabelas)
ALTER TABLE hideout RENAME TO sanctuary;
ALTER TABLE hideout_members RENAME TO sanctuary_members;
ALTER TABLE hideout_upgrades RENAME TO sanctuary_upgrades;

-- PASSO 7: Adicionar coluna de energia para sanctuary (autossustentável)
ALTER TABLE sanctuary ADD COLUMN IF NOT EXISTS energy INTEGER DEFAULT 100;
ALTER TABLE sanctuary ADD COLUMN IF NOT EXISTS max_energy INTEGER DEFAULT 100;
ALTER TABLE sanctuary ADD COLUMN IF NOT EXISTS last_energy_update TIMESTAMP DEFAULT NOW();
ALTER TABLE sanctuary ADD COLUMN IF NOT EXISTS energy_decay_rate FLOAT DEFAULT 0.5;

-- PASSO 8: Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_items_depth_quality ON items(depth_new, quality_new);
CREATE INDEX IF NOT EXISTS idx_equipment_depth_quality ON equipment(depth_new, quality_new);
CREATE INDEX IF NOT EXISTS idx_sanctuary_energy ON sanctuary(energy);

-- PASSO 9: Validar conversão
SELECT COUNT(*) as total_items, 
       COUNT(CASE WHEN depth_new IS NULL THEN 1 END) as nulls_depth,
       COUNT(CASE WHEN quality_new IS NULL THEN 1 END) as nulls_quality
FROM items;

COMMIT;
