"""
Modelo para entidade Vistoria
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class VistoriaModel:
    """Modelo de dados para Vistoria"""
    
    # Campos obrigatórios
    placa: str
    modelo: str
    cor: str
    ano: str
    nome_conferente: str
    nome_cliente: str
    
    # Campos opcionais
    id: Optional[str] = None
    token: Optional[str] = None
    data_vistoria: Optional[datetime] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    status: str = 'pendente'
    
    # Assinatura
    cliente_nome: Optional[str] = None
    assinatura_path: Optional[str] = None
    assinatura_checksum: Optional[str] = None
    assinado_em: Optional[datetime] = None
    token_expira_em: Optional[datetime] = None
    
    # Questionário - Itens do veículo
    ar_condicionado: str = 'nao'
    antenas: str = 'nao'
    tapetes: str = 'nao'
    tapete_porta_malas: str = 'nao'
    bateria: str = 'nao'
    retrovisor_direito: str = 'nao'
    retrovisor_esquerdo: str = 'nao'
    extintor: str = 'nao'
    roda_comum: str = 'nao'
    roda_especial: str = 'nao'
    chave_principal: str = 'nao'
    chave_reserva: str = 'nao'
    manual: str = 'nao'
    documento: str = 'nao'
    nota_fiscal: str = 'nao'
    limpador_dianteiro: str = 'nao'
    limpador_traseiro: str = 'nao'
    triangulo: str = 'nao'
    macaco: str = 'nao'
    chave_roda: str = 'nao'
    pneu_step: str = 'nao'
    
    # Marcas dos pneus
    marca_pneu_dianteiro_esquerdo: Optional[str] = None
    marca_pneu_dianteiro_direito: Optional[str] = None
    marca_pneu_traseiro_esquerdo: Optional[str] = None
    marca_pneu_traseiro_direito: Optional[str] = None
    
    # Observações
    desc_obs_1: Optional[str] = None
    desc_obs_2: Optional[str] = None
    desc_obs_3: Optional[str] = None
    desc_obs_4: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converter para dicionário"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat() if value else None
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VistoriaModel':
        """Criar instância a partir de dicionário"""
        # Filtrar apenas campos válidos
        valid_fields = {key for key in cls.__annotations__.keys()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # Converter strings de data para datetime se necessário
        datetime_fields = ['data_vistoria', 'criado_em', 'atualizado_em', 'assinado_em', 'token_expira_em']
        for field in datetime_fields:
            if field in filtered_data and isinstance(filtered_data[field], str):
                try:
                    filtered_data[field] = datetime.fromisoformat(filtered_data[field])
                except (ValueError, TypeError):
                    filtered_data[field] = None
        
        return cls(**filtered_data)
    
    def is_valid(self) -> tuple[bool, List[str]]:
        """Validar dados obrigatórios"""
        errors = []
        
        if not self.placa or not self.placa.strip():
            errors.append("Placa é obrigatória")
        
        if not self.modelo or not self.modelo.strip():
            errors.append("Modelo é obrigatório")
        
        if not self.cor or not self.cor.strip():
            errors.append("Cor é obrigatória")
        
        if not self.ano or not self.ano.strip():
            errors.append("Ano é obrigatório")
        
        if not self.nome_conferente or not self.nome_conferente.strip():
            errors.append("Nome do conferente é obrigatório")
        
        if not self.nome_cliente or not self.nome_cliente.strip():
            errors.append("Nome do cliente é obrigatório")
        
        return len(errors) == 0, errors
