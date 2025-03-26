-- Criação de índices para otimizar as consultas
CREATE INDEX IF NOT EXISTS idx_demonstracoes_registro_ans ON demonstracoes_contabeis(registro_ans);
CREATE INDEX IF NOT EXISTS idx_demonstracoes_data_base ON demonstracoes_contabeis(data_base);
CREATE INDEX IF NOT EXISTS idx_demonstracoes_cd_conta ON demonstracoes_contabeis(cd_conta_contabil);

-- Query 1: Top 10 operadoras com maiores despesas em "EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS 
-- DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR" no último trimestre
WITH UltimoTrimestre AS (
    SELECT MAX(data_base) as ultima_data
    FROM demonstracoes_contabeis
)
SELECT 
    o.razao_social,
    o.registro_ans,
    o.modalidade,
    ABS(d.saldo_final) as despesa_total
FROM 
    demonstracoes_contabeis d
    INNER JOIN operadoras_ativas o ON d.registro_ans = o.registro_ans
    CROSS JOIN UltimoTrimestre ut
WHERE 
    d.cd_conta_contabil = '411111' -- Código da conta de eventos/sinistros
    AND d.data_base = ut.ultima_data
ORDER BY 
    despesa_total DESC
LIMIT 10;

-- Query 2: Top 10 operadoras com maiores despesas na mesma categoria no último ano
WITH UltimoAno AS (
    SELECT EXTRACT(YEAR FROM MAX(data_base)) as ultimo_ano
    FROM demonstracoes_contabeis
)
SELECT 
    o.razao_social,
    o.registro_ans,
    o.modalidade,
    SUM(ABS(d.saldo_final)) as despesa_total_ano
FROM 
    demonstracoes_contabeis d
    INNER JOIN operadoras_ativas o ON d.registro_ans = o.registro_ans
    CROSS JOIN UltimoAno ua
WHERE 
    d.cd_conta_contabil = '411111' -- Código da conta de eventos/sinistros
    AND EXTRACT(YEAR FROM d.data_base) = ua.ultimo_ano
GROUP BY 
    o.razao_social,
    o.registro_ans,
    o.modalidade
ORDER BY 
    despesa_total_ano DESC
LIMIT 10;

-- Análises Adicionais

-- 1. Evolução trimestral das despesas por operadora
SELECT 
    o.razao_social,
    o.modalidade,
    d.data_base,
    ABS(d.saldo_final) as despesa_trimestre
FROM 
    demonstracoes_contabeis d
    INNER JOIN operadoras_ativas o ON d.registro_ans = o.registro_ans
WHERE 
    d.cd_conta_contabil = '411111'
    AND o.registro_ans IN (
        -- Seleciona as top 5 operadoras do último trimestre
        SELECT DISTINCT d2.registro_ans
        FROM demonstracoes_contabeis d2
        WHERE d2.cd_conta_contabil = '411111'
        ORDER BY ABS(d2.saldo_final) DESC
        LIMIT 5
    )
ORDER BY 
    o.razao_social,
    d.data_base;

-- 2. Comparativo de despesas por modalidade de operadora
SELECT 
    o.modalidade,
    COUNT(DISTINCT o.registro_ans) as num_operadoras,
    SUM(ABS(d.saldo_final)) as despesa_total,
    AVG(ABS(d.saldo_final)) as despesa_media
FROM 
    demonstracoes_contabeis d
    INNER JOIN operadoras_ativas o ON d.registro_ans = o.registro_ans
WHERE 
    d.cd_conta_contabil = '411111'
    AND EXTRACT(YEAR FROM d.data_base) = (
        SELECT EXTRACT(YEAR FROM MAX(data_base))
        FROM demonstracoes_contabeis
    )
GROUP BY 
    o.modalidade
ORDER BY 
    despesa_total DESC;

-- 3. Variação percentual das despesas entre trimestres
WITH DespesasTrimestrais AS (
    SELECT 
        d.registro_ans,
        d.data_base,
        ABS(d.saldo_final) as despesa,
        LAG(ABS(d.saldo_final)) OVER (
            PARTITION BY d.registro_ans 
            ORDER BY d.data_base
        ) as despesa_anterior
    FROM 
        demonstracoes_contabeis d
    WHERE 
        d.cd_conta_contabil = '411111'
)
SELECT 
    o.razao_social,
    dt.data_base,
    dt.despesa,
    dt.despesa_anterior,
    CASE 
        WHEN dt.despesa_anterior = 0 THEN NULL
        ELSE ((dt.despesa - dt.despesa_anterior) / dt.despesa_anterior * 100)
    END as variacao_percentual
FROM 
    DespesasTrimestrais dt
    INNER JOIN operadoras_ativas o ON dt.registro_ans = o.registro_ans
WHERE 
    dt.despesa_anterior IS NOT NULL
    AND o.registro_ans IN (
        -- Top 5 operadoras do último trimestre
        SELECT DISTINCT d2.registro_ans
        FROM demonstracoes_contabeis d2
        WHERE d2.cd_conta_contabil = '411111'
        ORDER BY ABS(d2.saldo_final) DESC
        LIMIT 5
    )
ORDER BY 
    o.razao_social,
    dt.data_base; 