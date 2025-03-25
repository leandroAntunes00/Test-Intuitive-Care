-- Criar tabela de operadoras ativas
CREATE TABLE IF NOT EXISTS public.operadoras_ativas (
    id SERIAL PRIMARY KEY,
    registro_ans VARCHAR(20),
    cnpj VARCHAR(20),
    razao_social VARCHAR(200),
    nome_fantasia VARCHAR(200),
    modalidade VARCHAR(100),
    logradouro VARCHAR(200),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf VARCHAR(2),
    cep VARCHAR(10),
    ddd INTEGER,
    telefone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(100),
    representante VARCHAR(200),
    cargo_representante VARCHAR(100),
    data_registro_ans DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de demonstrações contábeis
CREATE TABLE IF NOT EXISTS public.demonstracoes_contabeis (
    id SERIAL PRIMARY KEY,
    data_base DATE,
    registro_ans VARCHAR(20),
    cd_conta_contabil VARCHAR(20),
    descricao VARCHAR(200),
    saldo_inicial DECIMAL(15,2),
    saldo_final DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar função para atualizar o timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar triggers para atualizar automaticamente o updated_at
CREATE TRIGGER update_operadoras_updated_at
    BEFORE UPDATE ON public.operadoras_ativas
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_demonstracoes_updated_at
    BEFORE UPDATE ON public.demonstracoes_contabeis
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Criar índices para melhorar a performance
CREATE INDEX IF NOT EXISTS idx_registro_ans_op ON public.operadoras_ativas(registro_ans);
CREATE INDEX IF NOT EXISTS idx_cnpj_op ON public.operadoras_ativas(cnpj);
CREATE INDEX IF NOT EXISTS idx_registro_ans_dem ON public.demonstracoes_contabeis(registro_ans);
CREATE INDEX IF NOT EXISTS idx_data_base_dem ON public.demonstracoes_contabeis(data_base); 