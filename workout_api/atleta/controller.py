from datetime import datetime
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams, Page, paginate, Params
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import UUID4
from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaOutGet, AtletaUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select
from workout_api.configs.database import get_session

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
    )
async def post(
    db_session: DatabaseDependency,
    atleta_in: AtletaIn = Body(...)
    ):
    categoria_name = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome
    atleta_cpf = atleta_in.cpf

    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_name))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'A categoria {categoria_name} não foi encontrada.'
        )

    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O centro de trienamento {centro_treinamento_nome} não foi encontrado.'
        )

    try:
       atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
       atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

       atleta_model.categoria_id = categoria.pk_id
       atleta_model.centro_treinamento_id = centro_treinamento.pk_id

       db_session.add(atleta_model)
       await db_session.commit()

    except IntegrityError:
       db_session.rollback()
       raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Já existe um atleta cadastrado com o cpf: {atleta_cpf}'  
    )
    
    return atleta_out


@router.get(
    '/', 
    summary='Consultar todos os Atletas',
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[AtletaOutGet],
    )
async def query(nome: Optional[str] = None, cpf: Optional[str] = None, params: LimitOffsetParams = Depends(),
    db_session: AsyncSession = Depends(get_session)) -> LimitOffsetPage[AtletaOutGet]:
    query = (select(AtletaModel))

    if nome:
        query = query.filter(AtletaModel.nome == nome)
    if cpf:
        query = query.filter(AtletaModel.cpf == cpf)   

    result = await db_session.execute(query)
    atletas = result.scalars().all()
    
    if not atletas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atleta não encontrado")

    return paginate([AtletaOutGet.model_validate(atleta) for atleta in atletas], params)

@router.get(
    '/{id}', 
    summary='Consultar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
    )
async def query(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, 
           detail=f'Atleta não encontado no id: {id}'
           )
   
    return atleta

@router.patch(
    '/{id}', 
    summary='Editar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
    )
async def query(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, 
           detail=f'Atleta não encontado no id: {id}'
           )
    
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
       setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta

@router.delete(
    '/{id}', 
    summary='Deletar um Atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT,
    )
async def query(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, 
           detail=f'Atleta não encontado no id: {id}'
           )

    await db_session.delete(atleta)
    await db_session.commit()