"""
Modelo para entidade Foto
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FotoModel:
    """Modelo de dados para Foto da Vistoria"""
    
    # Campos obrigatórios
    vistoria_id: str
    categoria: str
    tipo: str  # 'obrigatoria', 'pneu', 'observacao', 'documento'
    
    # Campos opcionais
    id: Optional[str] = None
    arquivo_nome: Optional[str] = None
    arquivo_path: Optional[str] = None
    arquivo_url: Optional[str] = None
    arquivo_tamanho: Optional[int] = None
    arquivo_mime_type: Optional[str] = None
    arquivo_checksum: Optional[str] = None
    largura: Optional[int] = None
    altura: Optional[int] = None
    observacao_descricao: Optional[str] = None
    criado_em: Optional[datetime] = None
    
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
    def from_dict(cls, data: dict) -> 'FotoModel':
        """Criar instância a partir de dicionário"""
        # Filtrar apenas campos válidos
        valid_fields = {key for key in cls.__annotations__.keys()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # Converter string de data para datetime se necessário
        if 'criado_em' in filtered_data and isinstance(filtered_data['criado_em'], str):
            try:
                filtered_data['criado_em'] = datetime.fromisoformat(filtered_data['criado_em'])
            except (ValueError, TypeError):
                filtered_data['criado_em'] = None
        
        return cls(**filtered_data)
    
    def is_valid(self) -> tuple[bool, list[str]]:
        """Validar dados obrigatórios"""
        errors = []
        
        if not self.vistoria_id:
            errors.append("ID da vistoria é obrigatório")
        
        if not self.categoria or not self.categoria.strip():
            errors.append("Categoria da foto é obrigatória")
        
        if self.tipo not in ['obrigatoria', 'pneu', 'observacao', 'documento']:
            errors.append("Tipo da foto deve ser 'obrigatoria', 'pneu', 'observacao' ou 'documento'")
        
        return len(errors) == 0, errors
