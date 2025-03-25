from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class OperadoraBase(BaseModel):
    """Modelo base para operadoras"""
    registro_ans: str = Field(..., description="Registro da operadora na ANS")
    cnpj: Optional[str] = Field(None, description="CNPJ da operadora")
    razao_social: Optional[str] = Field(None, description="Razão social da operadora")
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia da operadora")
    modalidade: Optional[str] = Field(None, description="Modalidade da operadora")

class OperadoraAtiva(OperadoraBase):
    """Modelo para operadoras ativas com informações adicionais"""
    ddd: Optional[int] = Field(None, description="DDD do telefone principal")
    telefone: Optional[str] = Field(None, description="Telefone principal")
    email: Optional[str] = Field(None, description="E-mail de contato")
    representante: Optional[str] = Field(None, description="Nome do representante")
    data_registro_ans: Optional[date] = Field(None, description="Data de registro na ANS")

class ResultadoBusca(BaseModel):
    """Modelo para resultados de busca de operadoras"""
    operadora: str = Field(..., description="Nome da operadora")
    total_eventos: int = Field(..., description="Total de eventos registrados")
    total_despesas: float = Field(..., description="Valor total das despesas")
    relevancia: float = Field(..., description="Pontuação de relevância da busca")
    percentual_total: float = Field(..., description="Percentual em relação ao total geral")

class DespesaTrimestre(BaseModel):
    """Modelo para despesas trimestrais"""
    operadora: str = Field(..., description="Nome da operadora")
    total_despesas: float = Field(..., description="Valor total das despesas no trimestre")
    quantidade_eventos: int = Field(..., description="Quantidade de eventos no trimestre")
    percentual_total: float = Field(..., description="Percentual em relação ao total do trimestre")

class DespesaAno(BaseModel):
    """Modelo para despesas anuais"""
    operadora: str = Field(..., description="Nome da operadora")
    total_despesas: float = Field(..., description="Valor total das despesas no ano")
    quantidade_eventos: int = Field(..., description="Quantidade de eventos no ano")
    media_por_evento: float = Field(..., description="Valor médio por evento")
    percentual_total: float = Field(..., description="Percentual em relação ao total do ano")

class TendenciaMensal(BaseModel):
    """Modelo para tendência mensal de despesas"""
    mes: date = Field(..., description="Mês de referência")
    total_eventos: int = Field(..., description="Total de eventos no mês")
    total_despesas: float = Field(..., description="Valor total das despesas no mês")
    media_por_evento: float = Field(..., description="Valor médio por evento no mês") 