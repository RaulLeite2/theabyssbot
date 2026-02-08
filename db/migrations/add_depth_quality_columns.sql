-- Migration: Adiciona colunas depth_new e quality_new à tabela items
-- Data: 2026-02-08
-- Descrição: Adiciona suporte ao novo sistema de Depth (1-8) e Quality (COMMON-MYTHIC)

-- Passo 1: Adicionar colunas se não existirem
DO $$
BEGIN
    -- Adiciona depth_new (1-8, equivalente aos ranks F até SS)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='items' AND column_name='depth_new'
    ) THEN
        ALTER TABLE items ADD COLUMN depth_new INTEGER;
        RAISE NOTICE 'Coluna depth_new adicionada';
    ELSE
        RAISE NOTICE 'Coluna depth_new já existe';
    END IF;

    -- Adiciona quality_new (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='items' AND column_name='quality_new'
    ) THEN
        ALTER TABLE items ADD COLUMN quality_new VARCHAR(20);
        RAISE NOTICE 'Coluna quality_new adicionada';
    ELSE
        RAISE NOTICE 'Coluna quality_new já existe';
    END IF;
END $$;

-- Passo 2: Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_items_depth_new ON items(depth_new);
CREATE INDEX IF NOT EXISTS idx_items_quality_new ON items(quality_new);
CREATE INDEX IF NOT EXISTS idx_items_depth_quality ON items(depth_new, quality_new);

-- Passo 3: Migrar dados antigos (tier → depth_new) se depth_new estiver NULL
-- Mapping: tier 1-8 → depth 1-8
UPDATE items 
SET depth_new = LEAST(tier, 8)
WHERE depth_new IS NULL AND tier IS NOT NULL;

-- Passo 4: Definir quality_new baseado em subtier antigo se quality_new estiver NULL
-- Mapping aproximado de subtier:
-- subtier 1-2 → COMMON
-- subtier 3-4 → UNCOMMON  
-- subtier 5-6 → RARE
-- subtier 7-8 → EPIC
-- subtier 9 → LEGENDARY
-- subtier 10 → MYTHIC
UPDATE items
SET quality_new = CASE
    WHEN subtier <= 2 THEN 'COMMON'
    WHEN subtier <= 4 THEN 'UNCOMMON'
    WHEN subtier <= 6 THEN 'RARE'
    WHEN subtier <= 8 THEN 'EPIC'
    WHEN subtier = 9 THEN 'LEGENDARY'
    WHEN subtier >= 10 THEN 'MYTHIC'
    ELSE 'COMMON'
END
WHERE quality_new IS NULL AND subtier IS NOT NULL;

-- Passo 5: Para itens sem tier/subtier, definir valores padrão
UPDATE items
SET depth_new = 1
WHERE depth_new IS NULL;

UPDATE items
SET quality_new = 'COMMON'
WHERE quality_new IS NULL;

-- Passo 6: Verificação final
DO $$
DECLARE
    total_items INTEGER;
    items_with_depth INTEGER;
    items_with_quality INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_items FROM items;
    SELECT COUNT(*) INTO items_with_depth FROM items WHERE depth_new IS NOT NULL;
    SELECT COUNT(*) INTO items_with_quality FROM items WHERE quality_new IS NOT NULL;
    
    RAISE NOTICE 'Migration concluída!';
    RAISE NOTICE 'Total de itens: %', total_items;
    RAISE NOTICE 'Itens com depth_new: %', items_with_depth;
    RAISE NOTICE 'Itens com quality_new: %', items_with_quality;
    
    IF items_with_depth = total_items AND items_with_quality = total_items THEN
        RAISE NOTICE '✅ Todos os itens foram migrados com sucesso!';
    ELSE
        RAISE WARNING '⚠️ Alguns itens podem não ter sido migrados corretamente';
    END IF;
END $$;
