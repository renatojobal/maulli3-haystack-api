from typing import Dict, Any

import logging
import time
import json

from pydantic import BaseConfig
from fastapi import FastAPI, APIRouter
import haystack
from haystack import Pipeline

from rest_api.utils import get_app, get_pipelines
from rest_api.config import LOG_LEVEL
from rest_api.schema import QueryRequest, QueryResponse


logging.getLogger("haystack").setLevel(LOG_LEVEL)
logger = logging.getLogger("haystack")


BaseConfig.arbitrary_types_allowed = True


router = APIRouter()
app: FastAPI = get_app()
query_pipeline: Pipeline = get_pipelines().get("query_pipeline", None)
concurrency_limiter = get_pipelines().get("concurrency_limiter", None)


@router.get("/initialized")
def check_status():
    """
    This endpoint can be used during startup to understand if the
    server is ready to take any requests, or is still loading.

    The recommended approach is to call this endpoint with a short timeout,
    like 500ms, and in case of no reply, consider the server busy.
    """
    return True


@router.get("/hs_version")
def haystack_version():
    """
    Get the running Haystack version.
    """
    return {"hs_version": haystack.__version__}


@router.post("/query", response_model=QueryResponse, response_model_exclude_none=True)
def query(request: QueryRequest):
    """
    This endpoint receives the question as a string and allows the requester to set
    additional parameters that will be passed on to the Haystack pipeline.
    """
    with concurrency_limiter.run():
        result = _process_request(query_pipeline, request)
        return result
    

@router.post("/advanced_query", response_model=QueryResponse, response_model_exclude_none=True)
def advanced_query():
    """
    This endpoint receive no queries, instead make a preloaded queries for each file.
    """
    listOfQueries = [
        QueryRequest(query="¿Cuál es el nombre de la compañia?", filters=None, top_k_reader=1, top_k_retriever=1),

        QueryRequest(query="¿Cúal es el capital intelectual?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son los activos intagibles?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son los activos valiosos?", filters=None, top_k_reader=1, top_k_retriever=1),

        QueryRequest(query="¿Cuál es el capital humano?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuál es el directorio de la compañia?", filters=None, top_k_reader=1, top_k_retriever=1),

        QueryRequest(query="¿Cual es la formación que tienen los empleados?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuál es la política de remuneraciones?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son los beneficios al personal?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuál es el reconocimiento a los empleados?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son los planes de carrera?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo es el clima laboral?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo e sla política de diversidad e inclusión?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuál es la política de salud y seguridad ocupacional?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo es la comunicación interna?", filters=None, top_k_reader=1, top_k_retriever=1),

        QueryRequest(query="¿Cómo es el capital estructural?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cúal es la filosofía interna?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo es la cultura organizacional?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo se lleva a cabo la transformación digital?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo es la seguridad de la información y privacidad de datos?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cúales son los canales de atención?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómoson los sitemas de gestión de calidad?", filters=None, top_k_reader=1, top_k_retriever=1),



        QueryRequest(query="¿Cómo es el capital relacional?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cúales son los socios estratégicos?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son los clientes?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son los proveedeores", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son los accionistas?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo es el cumplimineto de normas e impuestos?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuál es la política ambiental?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuáles son los programas de educación financiera?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo se fomenta el empleo?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cuales son las acciones por la comunidad?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Cómo es la reputación de la empresa?", filters=None, top_k_reader=1, top_k_retriever=1),
        QueryRequest(query="¿Qué premios o reconocimientos ha obtenido la empresa?", filters=None, top_k_reader=1, top_k_retriever=1),
    ]
    
    for request in listOfQueries:

        with concurrency_limiter.run():
            result = _process_request(query_pipeline, request)
            return result



def _process_request(pipeline, request) -> Dict[str, Any]:
    start_time = time.time()

    params = request.params or {}
    result = pipeline.run(query=request.query, params=params, debug=request.debug)

    # Ensure answers and documents exist, even if they're empty lists
    if not "documents" in result:
        result["documents"] = []
    if not "answers" in result:
        result["answers"] = []

    logger.info(
        json.dumps({"request": request, "response": result, "time": f"{(time.time() - start_time):.2f}"}, default=str)
    )
    return result
