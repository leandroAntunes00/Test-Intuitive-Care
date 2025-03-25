-- Criar banco de dados específico
CREATE DATABASE rol_procedimentos;

-- Conectar ao banco de dados criado
\c rol_procedimentos

-- Criar schema para organizar as tabelas
CREATE SCHEMA IF NOT EXISTS public;

-- Criar tabela principal de procedimentos
CREATE TABLE public.procedimentos (
    id SERIAL PRIMARY KEY,
    procedimento VARCHAR(500) NOT NULL,
    rn_alteracao VARCHAR(50),
    vigencia VARCHAR(50),
    odontologia VARCHAR(50),
    atendimento_ambulatorial VARCHAR(50),
    hco VARCHAR(50),
    hso VARCHAR(50),
    ref VARCHAR(50),
    pac VARCHAR(50),
    dut VARCHAR(50),
    subgrupo VARCHAR(200),
    grupo VARCHAR(200),
    capitulo VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para melhorar a performance das consultas
CREATE INDEX idx_procedimento ON public.procedimentos(procedimento);
CREATE INDEX idx_capitulo ON public.procedimentos(capitulo);
CREATE INDEX idx_grupo ON public.procedimentos(grupo);
CREATE INDEX idx_subgrupo ON public.procedimentos(subgrupo);

-- Criar função para atualizar o timestamp de atualização
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar trigger para atualizar automaticamente o updated_at
CREATE TRIGGER update_procedimentos_updated_at
    BEFORE UPDATE ON public.procedimentos
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Comentários nas colunas
COMMENT ON TABLE public.procedimentos IS 'Tabela que armazena os procedimentos do Rol de Procedimentos e Eventos em Saúde';
COMMENT ON COLUMN public.procedimentos.id IS 'Identificador único do procedimento';
COMMENT ON COLUMN public.procedimentos.procedimento IS 'Nome do procedimento';
COMMENT ON COLUMN public.procedimentos.rn_alteracao IS 'RN de alteração do procedimento';
COMMENT ON COLUMN public.procedimentos.vigencia IS 'Vigência do procedimento';
COMMENT ON COLUMN public.procedimentos.odontologia IS 'Código de odontologia';
COMMENT ON COLUMN public.procedimentos.atendimento_ambulatorial IS 'Código de atendimento ambulatorial';
COMMENT ON COLUMN public.procedimentos.hco IS 'Código HCO';
COMMENT ON COLUMN public.procedimentos.hso IS 'Código HSO';
COMMENT ON COLUMN public.procedimentos.ref IS 'Código REF';
COMMENT ON COLUMN public.procedimentos.pac IS 'Código PAC';
COMMENT ON COLUMN public.procedimentos.dut IS 'Código DUT';
COMMENT ON COLUMN public.procedimentos.subgrupo IS 'Subgrupo do procedimento';
COMMENT ON COLUMN public.procedimentos.grupo IS 'Grupo do procedimento';
COMMENT ON COLUMN public.procedimentos.capitulo IS 'Capítulo do procedimento';
COMMENT ON COLUMN public.procedimentos.created_at IS 'Data e hora de criação do registro';
COMMENT ON COLUMN public.procedimentos.updated_at IS 'Data e hora da última atualização do registro';

-- Criar usuário específico para a aplicação (opcional)
CREATE USER rol_user WITH PASSWORD 'rol_password';

-- Conceder permissões
GRANT USAGE ON SCHEMA public TO rol_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO rol_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO rol_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO rol_user; 