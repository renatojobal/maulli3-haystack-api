from typing import Dict, Any, List

import logging
import time
import json

from pydantic import BaseConfig
from fastapi import FastAPI, APIRouter
import haystack
from haystack import Pipeline

from main_rest_api.utils import get_app, get_pipelines
from main_rest_api.config import LOG_LEVEL
from main_rest_api.schema import QueryRequest, QueryResponse, AdvancedQueryRequest, AdvancedQueryResponse


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
    

@router.post("/advanced_query", response_model=List[QueryResponse], response_model_exclude_none=True)
def advanced_query(request: AdvancedQueryRequest):
    """
    This endpoint receive no queries, instead make a preloaded queries for each file.
    """
    listOfQueries = request.queries
    
    all_queries = []

    with concurrency_limiter.run():
        for request in listOfQueries:
            result = _process_request(query_pipeline, request)
            all_queries.append(result)

        return all_queries


def _process_request(pipeline, request: QueryRequest) -> Dict[str, Any]:
    start_time = time.time()

    # Prepare params for the pipeline. Merge with request.params if it exists.
    params = request.params or {}
    if request.pdf_name:
        # Assuming the Retriever node needs the PDF name to filter documents
        if 'Retriever' not in params:
            params['Retriever'] = {}
        # Here you might need to define how the PDF name should be used as a filter
        # For example, using 'pdf_name' as a key in the metadata
        params['Retriever']['filters'] = {'pdf_name': request.pdf_name}

    # Execute the query through the pipeline
    result = pipeline.run(query=request.query, params=params, debug=request.debug)

    # Remove empty answers, if any
    result["answers"] = [answer for answer in result.get("answers", []) if answer.answer.strip()]

    # Log the processing time
    logger.info(f"Processed query in {(time.time() - start_time):.2f} seconds")

    return result

