from typing import Annotated, Optional
from pydantic import Field, PositiveFloat

from workout_api.categorias.schemas import CategoriaIn
from workout_api.centro_treinamento.schemas import CentroTreinamentoAtleta
from workout_api.contrib.schemas import BaseSchema, OutMixin

class Atleta(BaseSchema):
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao', max_length=50)]
    cpf: Annotated[Optional[str], Field(description='CPF do atleta', example='12345678900', max_length=11)]
    idade: Annotated[int, Field(description='Idade do atleta', example=25)]
    peso: Annotated[PositiveFloat, Field(description='Peso do atleta', example=75.5)]
    altura: Annotated[PositiveFloat, Field(description='Altura do atleta', example=1.70)]
    sexo: Annotated[str, Field(description='Sexo do atleta', example='M', max_length=1)]
    categoria: Annotated[CategoriaIn, Field(description='Categoria do atleta')]
    centro_treinamento: Annotated[CentroTreinamentoAtleta, Field(description='Centro de treinamento do atleta')]

class AtletaIn(Atleta):
    pass

class AtletaOut(Atleta, OutMixin): 
    pass 

class AtletaOutGet(Atleta, OutMixin):
    cpf: Annotated[Optional[str], Field(description='CPF do atleta', example='12345678900', max_length=11, exclude=True)]
    idade: Annotated[Optional[int], Field(description='Idade do atleta', example=25, exclude=True)]
    peso: Annotated[Optional[PositiveFloat], Field(description='Peso do atleta', example=75.5, exclude=True)]
    altura: Annotated[Optional[PositiveFloat], Field(description='Altura do atleta', example=1.70, exclude=True)]
    sexo: Annotated[Optional[str], Field(description='Sexo do atleta', example='M', max_length=1, exclude=True)]
    
    class Config:
      json_schema_extra = {
        "example": {
            "id": "cca1ffc3-397b-467f-b923-6cde05d0993d",
            "created_at": "2024-06-25T12:11:16.660394",
            "nome": "Joao",
            "centro_treinamento": {
                "nome": "CT King"
            },
            "categoria": {
                "nome": "Scale"
            },    
        }
    }        
    

class AtletaUpdate(BaseSchema):
   nome: Annotated[Optional[str], Field(None, description='Nome do atleta', example='Joao', max_length=50)]
   idade: Annotated[Optional[int], Field(None, description='Idade do atleta', example=25)]