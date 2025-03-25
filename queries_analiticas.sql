-- Query 1: Top 10 operadoras com maiores despesas no último trimestre
WITH ultimo_trimestre AS (
    SELECT 
        operadora,
        SUM(valor) as total_despesas,
        COUNT(*) as quantidade_eventos
    FROM public.despesas_operadoras
    WHERE categoria = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
    AND data_referencia >= CURRENT_DATE - INTERVAL '3 months'
    GROUP BY operadora
)
SELECT 
    operadora,
    ROUND(total_despesas::numeric, 2) as total_despesas,
    quantidade_eventos,
    ROUND((total_despesas / SUM(total_despesas) OVER()) * 100, 2) as percentual_total
FROM ultimo_trimestre
ORDER BY total_despesas DESC
LIMIT 10;

-- Query 2: Top 10 operadoras com maiores despesas no último ano
WITH ultimo_ano AS (
    SELECT 
        operadora,
        SUM(valor) as total_despesas,
        COUNT(*) as quantidade_eventos,
        ROUND(AVG(valor), 2) as media_por_evento
    FROM public.despesas_operadoras
    WHERE categoria = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
    AND data_referencia >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY operadora
)
SELECT 
    operadora,
    ROUND(total_despesas::numeric, 2) as total_despesas,
    quantidade_eventos,
    media_por_evento,
    ROUND((total_despesas / SUM(total_despesas) OVER()) * 100, 2) as percentual_total
FROM ultimo_ano
ORDER BY total_despesas DESC
LIMIT 10;

-- Query adicional: Análise de tendência mensal
SELECT 
    DATE_TRUNC('month', data_referencia) as mes,
    COUNT(*) as total_eventos,
    ROUND(SUM(valor)::numeric, 2) as total_despesas,
    ROUND(AVG(valor)::numeric, 2) as media_por_evento
FROM public.despesas_operadoras
WHERE categoria = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
AND data_referencia >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY DATE_TRUNC('month', data_referencia)
ORDER BY mes DESC; 