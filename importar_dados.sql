-- Conectar ao banco de dados
\c rol_procedimentos

-- Limpar dados existentes (opcional)
TRUNCATE TABLE public.procedimentos RESTART IDENTITY CASCADE;

-- Importar dados do CSV
COPY public.procedimentos (
    procedimento,
    rn_alteracao,
    vigencia,
    odontologia,
    atendimento_ambulatorial,
    hco,
    hso,
    ref,
    pac,
    dut,
    subgrupo,
    grupo,
    capitulo
)
FROM 'tabela_rol_procedimentos.csv'
WITH (
    FORMAT csv,
    DELIMITER ';',
    NULL '',
    ENCODING 'UTF8',
    HEADER true
);

-- Verificar quantidade de registros importados
SELECT COUNT(*) as total_registros FROM public.procedimentos;

-- Verificar amostra dos dados importados
SELECT * FROM public.procedimentos LIMIT 5;

-- Verificar se há registros com problemas de encoding
SELECT procedimento 
FROM public.procedimentos 
WHERE procedimento ~ '[^\x00-\x7F]' 
LIMIT 5; 