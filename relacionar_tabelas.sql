-- Adicionar constraint de chave estrangeira
ALTER TABLE operadoras_ativas
ADD CONSTRAINT fk_operadora
FOREIGN KEY (registro_ans)
REFERENCES operadoras(registro_ans)
ON DELETE CASCADE
ON UPDATE CASCADE; 