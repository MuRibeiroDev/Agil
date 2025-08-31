-- Script para adicionar novas colunas na tabela vistorias
-- Execute este script no seu banco PostgreSQL

-- Adicionar coluna KM rodado
ALTER TABLE vistorias 
ADD COLUMN IF NOT EXISTS km_rodado VARCHAR(50);

-- Adicionar coluna para documento/nota fiscal
ALTER TABLE vistorias 
ADD COLUMN IF NOT EXISTS documento_nota_fiscal TEXT;

-- Comentários das colunas
COMMENT ON COLUMN vistorias.km_rodado IS 'Quilometragem atual do veículo';
COMMENT ON COLUMN vistorias.documento_nota_fiscal IS 'Caminho do arquivo de documento ou nota fiscal';

-- Verificar se as colunas foram criadas
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'vistorias' 
AND column_name IN ('km_rodado', 'documento_nota_fiscal')
ORDER BY column_name;
