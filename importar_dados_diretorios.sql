-- Script para importar dados dos diretórios específicos
-- Conecta ao banco de dados
\c rol_procedimentos;

-- Limpa dados existentes
TRUNCATE TABLE public.procedimentos;

-- Importa dados do diretório dados_operadoras_ativas
COPY public.procedimentos (
    codigo_procedimento,
    descricao,
    valor_ch,
    valor_faixa_1,
    valor_faixa_2,
    valor_faixa_3,
    valor_porte_anestesico,
    valor_porte_cirurgico,
    valor_sadt,
    valor_sh,
    valor_sp,
    data_vigencia
)
FROM 'dados_operadoras_ativas/procedimentos.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- Importa dados do diretório demo_contabeis_2023
COPY public.procedimentos (
    codigo_procedimento,
    descricao,
    valor_ch,
    valor_faixa_1,
    valor_faixa_2,
    valor_faixa_3,
    valor_porte_anestesico,
    valor_porte_cirurgico,
    valor_sadt,
    valor_sh,
    valor_sp,
    data_vigencia
)
FROM 'demo_contabeis_2023/procedimentos.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- Importa dados do diretório demo_contabeis_2024
COPY public.procedimentos (
    codigo_procedimento,
    descricao,
    valor_ch,
    valor_faixa_1,
    valor_faixa_2,
    valor_faixa_3,
    valor_porte_anestesico,
    valor_porte_cirurgico,
    valor_sadt,
    valor_sh,
    valor_sp,
    data_vigencia
)
FROM 'demo_contabeis_2024/procedimentos.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- Verifica quantidade de registros importados
SELECT COUNT(*) as total_registros FROM public.procedimentos;

-- Verifica registros por diretório de origem
SELECT 
    CASE 
        WHEN data_vigencia < '2023-01-01' THEN 'dados_operadoras_ativas'
        WHEN data_vigencia < '2024-01-01' THEN 'demo_contabeis_2023'
        ELSE 'demo_contabeis_2024'
    END as origem,
    COUNT(*) as quantidade
FROM public.procedimentos
GROUP BY 
    CASE 
        WHEN data_vigencia < '2023-01-01' THEN 'dados_operadoras_ativas'
        WHEN data_vigencia < '2024-01-01' THEN 'demo_contabeis_2023'
        ELSE 'demo_contabeis_2024'
    END
ORDER BY origem;

-- Verifica possíveis problemas de encoding
SELECT codigo_procedimento, descricao
FROM public.procedimentos
WHERE descricao ~ '[^\x00-\x7F]'
LIMIT 5; 