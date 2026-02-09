-- ============================================================================
-- Migration: Tier System → Depth System
-- Versão: 1.0 | Data: 2026-02-08
-- STATUS: PLACEHOLDER - Colunas já criadas pela migration 000
-- ============================================================================

-- Esta migration é um placeholder.
-- As colunas depth_new e quality_new já foram criadas pela migration 000.
-- Nenhuma ação adicional necessária neste momento.

-- Indices são criados para performance
CREATE INDEX IF NOT EXISTS idx_items_depth_quality ON items(depth_new, quality_new);
CREATE INDEX IF NOT EXISTS idx_equipment_depth_quality ON equipment(depth_new, quality_new);
