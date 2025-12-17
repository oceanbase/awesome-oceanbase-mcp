from __future__ import annotations
import logging
import time
from typing import Optional
import json
import csv
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mysql.connector import Error
import pyseekdb
import pylibseekdb as seekdb
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("seekdb_mcp_server")

load_dotenv()

app = FastMCP("seekdb_mcp_server")
client = pyseekdb.Client()
seekdb.open()
seekdb_memory_collection_name = "seekdb_memory_collection_v1"


@app.tool()
def execute_sql(sql: str) -> str:
    """Execute a sql on the seekdb"""
    logger.info(f"Calling tool: execute_sql with arguments: {sql}")
    result = {"sql": sql, "success": False, "data": None, "error": None}
    conn = None
    cursor = None
    try:
        conn = seekdb.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        if data:
            result["data"] = [[str(cell) for cell in row] for row in data]
        else:
            conn.commit()
        result["success"] = True
    except Error as e:
        result["error"] = f"[Error]: {e}"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    json_result = json.dumps(result, ensure_ascii=False)
    if result["error"]:
        logger.error(f"SQL executed failed, result: {json_result}")
    print(json_result)
    return json_result


@app.tool(name="get_current_time", description="Get current time")
def get_current_time() -> str:
    """Get current time from seekdb database."""
    logger.info("Calling tool: get_current_time")
    sql_query = "SELECT NOW()"
    try:
        return execute_sql(sql_query)
    except Error as e:
        logger.error(f"Error getting database time: {e}")
        result = {"success": False, "data": None, "error": f"[Error]: {e}"}
        return json.dumps(result, ensure_ascii=False)


@app.tool()
def create_collection(collection_name: str, dimension: int = 384, distance: str = "l2") -> str:
    """
    Create a new collection in seekdb.

    A collection is similar to a table in a database, used for storing vector data.

    Args:
        collection_name: The name of the collection to be created. Must be unique within the database and no longer than 64 characters.
        dimension: The dimension of the vectors to be stored. Default is 384.
        distance: The distance metric for vector similarity. Options: 'cosine', 'l2', 'ip' (inner product). Default is 'l2'.
    Returns:
        A JSON string indicating success or error.
    """
    logger.info(
        f"Calling tool: create_collection with arguments: collection_name={collection_name}, distance={distance}"
    )
    result = {"collection_name": collection_name, "success": False, "error": None}
    try:
        from pyseekdb import HNSWConfiguration

        config = HNSWConfiguration(dimension=dimension, distance=distance)

        client.create_collection(name=collection_name, configuration=config)
        result["success"] = True
        result["message"] = (
            f"Collection '{collection_name}' created successfully with dimension={dimension}, distance={distance}"
        )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to create collection: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def list_collections() -> str:
    """
    List all collections in seekdb.

    Returns a list of all existing collections with their basic information.

    Returns:
        A JSON string containing the list of collections or error.

    Examples:
        - List all collections:
          list_collections()
          Returns: {"success": true, "collections": ["collection1", "collection2"], "count": 2}
    """
    logger.info("Calling tool: list_collections")
    result = {"success": False, "collections": None, "count": 0, "error": None}

    try:
        collections = client.list_collections()
        collection_names = [col.name for col in collections]
        result["success"] = True
        result["collections"] = collection_names
        result["count"] = len(collection_names)
        result["message"] = f"Found {len(collection_names)} collection(s)"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to list collections: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def has_collection(collection_name: str) -> str:
    """
    This method checks if a collection with the given name exists in seekdb.

    Args:
        collection_name: The name of the collection to check.

    Returns:
        A JSON string containing:
        - success: Whether the check operation succeeded
        - exists: Boolean indicating if the collection exists
        - collection_name: The name of the collection that was checked
        - error: Error message if the operation failed

    Examples:
        - Check if a collection exists:
          has_collection("my_collection")
          Returns: {"success": true, "exists": true, "collection_name": "my_collection"}
    """
    logger.info(f"Calling tool: has_collection with arguments: collection_name={collection_name}")
    result = {"collection_name": collection_name, "success": False, "exists": False, "error": None}

    try:
        exists = client.has_collection(collection_name)
        result["success"] = True
        result["exists"] = exists
        if exists:
            result["message"] = f"Collection '{collection_name}' exists"
        else:
            result["message"] = f"Collection '{collection_name}' does not exist"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to check collection existence: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def peek_collection(collection_name: str, limit: int = 3) -> str:
    """
    Peek at documents in a seekdb collection.

    Returns a sample of documents from the collection for quick inspection.
    This is useful for verifying the content of a collection without querying.

    Args:
        collection_name: The name of the collection to peek into.
        limit: The maximum number of documents to return. Default is 3.

    Returns:
        A JSON string containing sample documents with their ids, documents, and metadatas.

    Examples:
        - Peek at a collection with default limit:
          peek_collection("my_collection")

        - Peek with custom limit:
          peek_collection("my_collection", limit=5)
    """
    logger.info(
        f"Calling tool: peek_collection with arguments: collection_name={collection_name}, limit={limit}"
    )
    result = {"collection_name": collection_name, "success": False, "data": None, "error": None}

    try:
        collection = client.get_collection(name=collection_name)
        results = collection.peek(limit=limit)

        # Format results for JSON serialization
        formatted_results = {
            "ids": results.get("ids", []),
            "documents": results.get("documents", []),
            "metadatas": results.get("metadatas", []),
            "embeddings": results.get("embeddings", []),
        }

        result["success"] = True
        result["data"] = formatted_results
        result["message"] = (
            f"Peeked {len(formatted_results['ids']) if formatted_results['ids'] else 0} document(s) from collection '{collection_name}'"
        )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to peek collection: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def add_data_to_collection(
    collection_name: str,
    ids: list[str],
    documents: Optional[list[str]] = None,
    metadatas: Optional[list[dict]] = None,
) -> str:
    """
    Add data to an existing collection in seekdb.

    You can add data with documents (text will be converted to vectors by embedding_function),
    or with pre-computed embeddings (vectors), or both.

    Args:
        collection_name: The name of the collection to add data to.
        ids: A list of unique IDs for the data items. Each ID must be unique within the collection.
        documents: A list of text documents. If the collection has an embedding_function,
                   documents will be automatically converted to vectors. Optional if embeddings are provided.
        metadatas: A list of metadata dictionaries for each data item. Optional.

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Add with documents only (requires collection with embedding_function):
          add_data_to_collection("my_collection", ["id1", "id2"], documents=["Hello world", "Goodbye world"])

        - Add with embeddings only:
          add_data_to_collection("my_collection", ["id1"], embeddings=[[0.1, 0.2, 0.3]])

        - Add with documents and metadata:
          add_data_to_collection("my_collection", ["id1"], documents=["Hello"], metadatas=[{"category": "greeting"}])
    """
    logger.info(
        f"Calling tool: add_data_to_collection with arguments: collection_name={collection_name}, ids={ids}"
    )
    result = {"collection_name": collection_name, "success": False, "ids": ids, "error": None}

    try:
        # Get the collection
        collection = client.get_collection(name=collection_name)

        # Build add parameters
        add_kwargs = {"ids": ids}

        if documents is not None:
            add_kwargs["documents"] = documents

        if metadatas is not None:
            add_kwargs["metadatas"] = metadatas

        # Add data to collection
        collection.add(**add_kwargs)

        result["success"] = True
        result["message"] = (
            f"Successfully added {len(ids)} item(s) to collection '{collection_name}'"
        )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to add data to collection: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def update_collection(
    collection_name: str,
    ids: list[str],
    documents: Optional[list[str]] = None,
    metadatas: Optional[list[dict]] = None,
) -> str:
    """
    Update data in a seekdb collection.

    Updates existing documents in a collection by their IDs. You can update
    the documents (text content) and/or metadatas for the specified IDs.

    Args:
        collection_name: The name of the collection to update data in.
        ids: A list of IDs for the data items to update. These IDs must already exist in the collection.
        documents: A list of new text documents to replace the existing ones. Optional.
        metadatas: A list of new metadata dictionaries to replace the existing ones. Optional.

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Update documents only:
          update_collection("my_collection", ["id1", "id2"], documents=["New text 1", "New text 2"])

        - Update metadatas only:
          update_collection("my_collection", ["id1"], metadatas=[{"category": "updated"}])

        - Update both documents and metadatas:
          update_collection("my_collection", ["id1"], documents=["Updated text"], metadatas=[{"version": 2}])
    """
    logger.info(
        f"Calling tool: update_collection with arguments: collection_name={collection_name}, ids={ids}"
    )
    result = {"collection_name": collection_name, "success": False, "ids": ids, "error": None}

    try:
        # Get the collection
        collection = client.get_collection(name=collection_name)

        # Build update parameters
        update_kwargs = {"ids": ids}

        if documents is not None:
            update_kwargs["documents"] = documents

        if metadatas is not None:
            update_kwargs["metadatas"] = metadatas

        # Update data in collection
        collection.update(**update_kwargs)

        result["success"] = True
        result["message"] = (
            f"Successfully updated {len(ids)} item(s) in collection '{collection_name}'"
        )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to update data in collection: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def delete_documents(
    collection_name: str,
    ids: Optional[list[str]] = None,
    where: Optional[dict] = None,
    where_document: Optional[dict] = None,
) -> str:
    """
    Delete documents from a seekdb collection.

    Deletes documents from a collection by their IDs or by filter conditions.
    At least one of ids, where, or where_document must be provided.

    Args:
        collection_name: The name of the collection to delete documents from.
        ids: A list of document IDs to delete. Optional if where or where_document is provided.
        where: Metadata filter conditions to select documents for deletion.
               Example: {"category": {"$eq": "obsolete"}}
               Supported operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin
        where_document: Document content filter conditions.
                        Example: {"$contains": "deprecated"}

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Delete by IDs:
          delete_documents("my_collection", ids=["id1", "id2", "id3"])

        - Delete by metadata filter:
          delete_documents("my_collection", where={"status": {"$eq": "deleted"}})

        - Delete by document content:
          delete_documents("my_collection", where_document={"$contains": "old version"})

        - Delete with combined filters:
          delete_documents("my_collection", ids=["id1"], where={"category": {"$eq": "temp"}})
    """
    logger.info(
        f"Calling tool: delete_documents with arguments: collection_name={collection_name}, ids={ids}"
    )
    result = {"collection_name": collection_name, "success": False, "error": None}

    try:
        # Get the collection
        collection = client.get_collection(name=collection_name)

        # Build delete parameters
        delete_kwargs = {}

        if ids is not None:
            delete_kwargs["ids"] = ids

        if where is not None:
            delete_kwargs["where"] = where

        if where_document is not None:
            delete_kwargs["where_document"] = where_document

        # Check that at least one filter is provided
        if not delete_kwargs:
            result["error"] = "At least one of ids, where, or where_document must be provided"
            return json.dumps(result, ensure_ascii=False)

        # Delete documents from collection
        collection.delete(**delete_kwargs)

        result["success"] = True
        result["message"] = f"Successfully deleted documents from collection '{collection_name}'"
        if ids:
            result["deleted_ids"] = ids
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to delete documents from collection: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def query_collection(
    collection_name: str,
    query_texts: Optional[list[str]] = None,
    query_embeddings: Optional[list[list[float]]] = None,
    n_results: int = 10,
    where: Optional[dict] = None,
    where_document: Optional[dict] = None,
    include: Optional[list[str]] = None,
) -> str:
    """
    Query data from a collection in seekdb using vector similarity search.

    You can query by text (will be converted to vectors by embedding_function) or by pre-computed embeddings.

    Args:
        collection_name: The name of the collection to query.
        query_texts: A list of text queries. If the collection has an embedding_function,
                     texts will be automatically converted to vectors. Required if query_embeddings is not provided.
        query_embeddings: A list of query vectors for similarity search.
                          Required if query_texts is not provided.
        n_results: The number of similar results to return. Default is 10.
        where: Metadata filter conditions. Example: {"category": {"$eq": "AI"}, "score": {"$gte": 90}}
               Supported operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin
        where_document: Document filter conditions. Example: {"$contains": "machine learning"}
        include: List of fields to include in results. Options: ["documents", "metadatas", "embeddings", "distances"]
                 Default includes documents, metadatas, and distances.

    Returns:
        A JSON string containing the query results with ids, documents, metadatas, and distances.

    Examples:
        - Query by text (requires collection with embedding_function):
          query_collection("my_collection", query_texts=["What is AI?"], n_results=5)

        - Query by embeddings:
          query_collection("my_collection", query_embeddings=[[0.1, 0.2, 0.3]], n_results=3)

        - Query with metadata filter:
          query_collection("my_collection", query_texts=["AI"], where={"category": {"$eq": "tech"}})
    """
    logger.info(
        f"Calling tool: query_collection with arguments: collection_name={collection_name}, n_results={n_results}"
    )
    result = {"collection_name": collection_name, "success": False, "data": None, "error": None}

    try:
        # Get the collection
        collection = client.get_collection(name=collection_name)

        # Build query parameters
        query_kwargs = {"n_results": n_results}

        if query_texts is not None:
            query_kwargs["query_texts"] = query_texts

        if query_embeddings is not None:
            query_kwargs["query_embeddings"] = query_embeddings

        if where is not None:
            query_kwargs["where"] = where

        if where_document is not None:
            query_kwargs["where_document"] = where_document

        if include is not None:
            query_kwargs["include"] = include

        # Execute query
        query_results = collection.query(**query_kwargs)
        # Format results for JSON serialization
        formatted_results = {
            "ids": query_results.get("ids", []),
            "distances": query_results.get("distances", []),
            "documents": query_results.get("documents", []),
            "metadatas": query_results.get("metadatas", []),
        }

        result["success"] = True
        result["data"] = formatted_results
        result["message"] = (
            f"Query returned {len(formatted_results['ids'][0]) if formatted_results['ids'] else 0} result(s)"
        )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to query collection: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def delete_collection(collection_name: str) -> str:
    """
    Delete a collection from seekdb.

    This will permanently delete the collection and all its data. This operation cannot be undone.

    Args:
        collection_name: The name of the collection to delete. The collection must exist.

    Returns:
        A JSON string indicating success or error.
    """
    logger.info(
        f"Calling tool: delete_collection with arguments: collection_name={collection_name}"
    )
    result = {"collection_name": collection_name, "success": False, "error": None}

    try:
        client.delete_collection(name=collection_name)
        result["success"] = True
        result["message"] = f"Collection '{collection_name}' deleted successfully"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to delete collection: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def full_text_search(
    table_name: str,
    column_name: str,
    search_expr: str,
    mode: str = "boolean",
    return_score: bool = False,
    limit: int = 10,
    additional_columns: Optional[list[str]] = None,
) -> str:
    """
    Perform full-text search on a seekdb table using MATCH...AGAINST syntax.

    This method uses seekdb's full-text indexing feature which provides efficient keyword search
    with BM25 relevance scoring. The table must have a FULLTEXT INDEX created on the target column.

    Args:
        table_name: The name of the table to search.
        column_name: The column name that has a FULLTEXT INDEX.
        search_expr: The search expression.
                     - For boolean mode: use '+' for required words, '-' for excluded words.
                       Example: '+london +mayfair' (must contain both), '+london -westminster' (london but not westminster)
                     - For natural mode: just provide keywords separated by spaces.
                       Example: 'london mayfair'
        mode: Search mode - 'boolean' or 'natural'. Default is 'boolean'.
              - boolean: More precise control with +/- operators
              - natural: Simple keyword matching with relevance ranking
        return_score: Whether to return relevance scores. Default is False.
        limit: Maximum number of results to return. Default is 10.
        additional_columns: List of additional columns to include in results. Default is None (only id and score).

    Returns:
        A JSON string containing the search results with ids, scores (if requested), and additional columns.

    Examples:
        - Boolean mode (must contain both words):
          full_text_search("documents", "content", "+machine +learning", mode="boolean")

        - Boolean mode (exclude words):
          full_text_search("documents", "content", "+python -java", mode="boolean")

        - Natural language mode:
          full_text_search("documents", "content", "artificial intelligence", mode="natural")

        - With additional columns:
          full_text_search("documents", "content", "+AI", additional_columns=["title", "author"])
    """
    logger.info(
        f"Calling tool: full_text_search with arguments: table_name={table_name}, column_name={column_name}, search_expr={search_expr}, mode={mode}"
    )
    result = {"table_name": table_name, "success": False, "data": None, "error": None}

    try:
        # Build the SELECT clause
        select_columns = []
        if additional_columns:
            select_columns.extend(additional_columns)
        else:
            select_columns.extend(["*"])

        if return_score:
            # Add score column using MATCH...AGAINST without mode for scoring
            score_expr = f"MATCH ({column_name}) AGAINST ('{search_expr}')"
            select_columns.append(f"{score_expr} AS score")

        select_clause = ", ".join(select_columns)
        # Build the WHERE clause based on mode
        if mode.lower() == "boolean":
            where_clause = f"MATCH ({column_name}) AGAINST ('{search_expr}' IN BOOLEAN MODE)"
        else:
            where_clause = f"MATCH ({column_name}) AGAINST ('{search_expr}')"

        # Build and execute the SQL query
        sql = f"SELECT {select_clause} FROM {table_name} WHERE {where_clause}"

        if return_score:
            sql += " ORDER BY score DESC"

        sql += f" LIMIT {limit}"

        logger.info(f"Executing SQL: {sql}")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["data"] = sql_result["data"]
        result["sql"] = sql
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = (
                f"Full-text search returned {len(result['data']) if result['data'] else 0} result(s)"
            )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to perform full-text search: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def hybrid_search(
    collection_name: str,
    fulltext_search_keyword: Optional[str] = None,
    fulltext_where: Optional[dict] = None,
    fulltext_n_results: int = 10,
    knn_query_texts: Optional[list[str]] = None,
    knn_where: Optional[dict] = None,
    knn_n_results: int = 10,
    n_results: int = 5,
    include: Optional[list[str]] = ["documents"],
) -> str:
    """
    Perform hybrid search combining full-text search and vector similarity search in seekdb.

    Hybrid search leverages both keyword matching (full-text) and semantic similarity (vector)
    to provide more accurate and comprehensive search results. Results are ranked using
    Reciprocal Rank Fusion (RRF) algorithm.

    Args:
        collection_name: The name of the collection to search.

        # Full-text search parameters:
        fulltext_search_keyword: Keywords to search in documents. Example: "machine learning"
                                 Uses $contains operator for full-text matching.
        fulltext_where: Metadata filter for full-text search. Example: {"category": {"$eq": "AI"}}
        fulltext_n_results: Number of results for full-text search. Default is 10.

        # Vector search (KNN) parameters:
        knn_query_texts: Text queries for vector search. Will be converted to embeddings by
                         the collection's embedding_function. Example: ["AI research"]
        knn_where: Metadata filter for vector search. Example: {"year": {"$gte": 2020}}
        knn_n_results: Number of results for vector search. Default is 10.

        # Final results parameters:
        n_results: Final number of results to return after fusion. Default is 5.
        include: Fields to include in results. Options: ["documents", "metadatas", "embeddings", "distances"]

    Returns:
        A JSON string containing the hybrid search results with ids, documents, metadatas, and scores.

    Examples:
        - Hybrid search with text query:
          hybrid_search("my_collection",
                        fulltext_search_keyword="machine learning",
                        knn_query_texts=["AI research"],
                        n_results=5)

        - Hybrid search with metadata filters:
          hybrid_search("my_collection",
                        fulltext_search_keyword="python",
                        fulltext_where={"category": {"$eq": "tech"}},
                        knn_query_texts=["programming"],
                        knn_where={"year": {"$gte": 2023}},
                        n_results=10)
    """
    logger.info(f"Calling tool: hybrid_search with arguments: collection_name={collection_name}")
    result = {"collection_name": collection_name, "success": False, "data": None, "error": None}

    try:
        # Get the collection
        collection = client.get_collection(name=collection_name)

        # Build query (full-text search) configuration
        query_config = {"n_results": fulltext_n_results}
        if fulltext_search_keyword:
            query_config["where_document"] = {"$contains": fulltext_search_keyword}
        if fulltext_where:
            query_config["where"] = fulltext_where

        # Build knn (vector search) configuration
        knn_config = {"n_results": knn_n_results}
        if knn_query_texts:
            knn_config["query_texts"] = knn_query_texts
        if knn_where:
            knn_config["where"] = knn_where

        # Build hybrid_search parameters
        search_kwargs = {
            "query": query_config,
            "knn": knn_config,
            "rank": {"rrf": {}},  # Use Reciprocal Rank Fusion
            "n_results": n_results,
        }

        search_kwargs["include"] = include

        # Execute hybrid search
        search_results = collection.hybrid_search(**search_kwargs)

        # Format results for JSON serialization
        formatted_results = {
            "ids": search_results.get("ids", []),
            "documents": search_results.get("documents", []),
            "metadatas": search_results.get("metadatas", []),
        }

        result["success"] = True
        result["data"] = formatted_results
        result["message"] = (
            f"Hybrid search returned {len(formatted_results['ids'][0]) if formatted_results['ids'] else 0} result(s)"
        )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to perform hybrid search: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def create_ai_model(model_name: str, model_type: str, provider_model_name: str) -> str:
    """
    Create an AI model in seekdb using DBMS_AI_SERVICE.CREATE_AI_MODEL.

    This registers an AI model that can be used with AI functions like AI_EMBED, AI_COMPLETE, and AI_RERANK.
    After creating the model, you also need to create an endpoint using create_ai_model_endpoint.

    Args:
        model_name: The name to identify this model in seekdb. Used as model_key in AI functions.
                    Example: "my_embed_model", "my_llm", "my_rerank"
        model_type: The type of AI model. Must be one of:
                    - "dense_embedding": For embedding models (used with AI_EMBED)
                    - "completion": For text generation LLMs (used with AI_COMPLETE)
                    - "rerank": For reranking models (used with AI_RERANK)
        provider_model_name: The model name from the provider.
                             Examples: "BAAI/bge-m3", "THUDM/GLM-4-9B-0414", "BAAI/bge-reranker-v2-m3"

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Create an embedding model:
          create_ai_model("ob_embed", "dense_embedding", "BAAI/bge-m3")

        - Create a text generation model:
          create_ai_model("ob_complete", "completion", "THUDM/GLM-4-9B-0414")

        - Create a rerank model:
          create_ai_model("ob_rerank", "rerank", "BAAI/bge-reranker-v2-m3")
    """
    logger.info(
        f"Calling tool: create_ai_model with arguments: model_name={model_name}, model_type={model_type}"
    )
    result = {"model_name": model_name, "success": False, "error": None}

    # Validate model_type
    valid_types = ["dense_embedding", "completion", "rerank"]
    if model_type not in valid_types:
        result["error"] = f"Invalid model_type. Must be one of: {valid_types}"
        return json.dumps(result, ensure_ascii=False)

    try:
        # Build the configuration JSON
        config = json.dumps({"type": model_type, "model_name": provider_model_name})

        # Build and execute the SQL
        sql = f"CALL DBMS_AI_SERVICE.CREATE_AI_MODEL('{model_name}', '{config}')"

        logger.info(f"Executing SQL: {sql}")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = (
                f"AI model '{model_name}' created successfully with type={model_type}, provider_model={provider_model_name}"
            )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to create AI model: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def create_ai_model_endpoint(
    endpoint_name: str, ai_model_name: str, url: str, access_key: str, provider: str = "siliconflow"
) -> str:
    """
    Create an AI model endpoint in seekdb using DBMS_AI_SERVICE.CREATE_AI_MODEL_ENDPOINT.

    An endpoint connects an AI model to an external API service. You must create a model first
    using create_ai_model before creating an endpoint for it.

    Args:
        endpoint_name: The name to identify this endpoint. Example: "ob_embed_endpoint"
        ai_model_name: The name of the AI model to connect (must already exist).
                       Example: "ob_embed"
        url: The API endpoint URL for the AI service.
             Examples:
             - Embedding: "https://api.siliconflow.cn/v1/embeddings"
             - Completion: "https://api.siliconflow.cn/v1/chat/completions"
             - Rerank: "https://api.siliconflow.cn/v1/rerank"
             - OpenAI: "https://api.openai.com/v1/embeddings"
        access_key: The API key for authentication. Example: "sk-xxxxx"
        provider: The AI service provider. Common values: "siliconflow", "openai", "dashscope".
                  Default is "siliconflow".

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Create an embedding endpoint:
          create_ai_model_endpoint("ob_embed_endpoint", "ob_embed",
                                   "https://api.siliconflow.cn/v1/embeddings",
                                   "sk-xxxxx", "siliconflow")

        - Create a completion endpoint:
          create_ai_model_endpoint("ob_complete_endpoint", "ob_complete",
                                   "https://api.siliconflow.cn/v1/chat/completions",
                                   "sk-xxxxx", "siliconflow")
    """
    logger.info(
        f"Calling tool: create_ai_model_endpoint with arguments: endpoint_name={endpoint_name}, ai_model_name={ai_model_name}"
    )
    result = {"endpoint_name": endpoint_name, "success": False, "error": None}

    try:
        # Build the configuration JSON
        config = json.dumps(
            {
                "ai_model_name": ai_model_name,
                "url": url,
                "access_key": access_key,
                "provider": provider,
            }
        )

        # Build and execute the SQL
        sql = f"CALL DBMS_AI_SERVICE.CREATE_AI_MODEL_ENDPOINT('{endpoint_name}', '{config}')"

        logger.info(
            f"Executing SQL: CALL DBMS_AI_SERVICE.CREATE_AI_MODEL_ENDPOINT('{endpoint_name}', '...')"
        )

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = (
                f"AI model endpoint '{endpoint_name}' created successfully for model '{ai_model_name}'"
            )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to create AI model endpoint: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def drop_ai_model(model_name: str) -> str:
    """
    Drop an AI model from seekdb using DBMS_AI_SERVICE.DROP_AI_MODEL.

    This removes a registered AI model. Before dropping a model, make sure to drop
    any endpoints associated with it first using drop_ai_model_endpoint.

    Args:
        model_name: The name of the AI model to drop. Example: "ob_embed"

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Drop an embedding model:
          drop_ai_model("ob_embed")

        - Drop a completion model:
          drop_ai_model("ob_complete")
    """
    logger.info(f"Calling tool: drop_ai_model with arguments: model_name={model_name}")
    result = {"model_name": model_name, "success": False, "error": None}

    try:
        sql = f"CALL DBMS_AI_SERVICE.DROP_AI_MODEL('{model_name}')"

        logger.info(f"Executing SQL: {sql}")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = f"AI model '{model_name}' dropped successfully"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to drop AI model: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def drop_ai_model_endpoint(endpoint_name: str) -> str:
    """
    Drop an AI model endpoint from seekdb using DBMS_AI_SERVICE.DROP_AI_MODEL_ENDPOINT.

    This removes a registered AI model endpoint. You should drop endpoints before
    dropping their associated models.

    Args:
        endpoint_name: The name of the endpoint to drop. Example: "ob_embed_endpoint"

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Drop an embedding endpoint:
          drop_ai_model_endpoint("ob_embed_endpoint")

        - Drop a completion endpoint:
          drop_ai_model_endpoint("ob_complete_endpoint")
    """
    logger.info(
        f"Calling tool: drop_ai_model_endpoint with arguments: endpoint_name={endpoint_name}"
    )
    result = {"endpoint_name": endpoint_name, "success": False, "error": None}

    try:
        sql = f"CALL DBMS_AI_SERVICE.DROP_AI_MODEL_ENDPOINT('{endpoint_name}')"

        logger.info(f"Executing SQL: {sql}")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = f"AI model endpoint '{endpoint_name}' dropped successfully"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to drop AI model endpoint: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def ai_complete(model_name: str, prompt: str, template_args: Optional[list[str]] = None) -> str:
    """
    Call an LLM using AI_COMPLETE function in seekdb for text generation.

    This function calls a registered text generation model (completion type) to process
    prompts and generate text responses. Useful for sentiment analysis, translation,
    classification, summarization, and other NLP tasks.

    Args:
        model_name: The name of the registered completion model. Example: "ob_complete"
        prompt: The prompt text to send to the LLM. Can include placeholders like {0}, {1}
                if using template_args.
        template_args: Optional list of arguments to fill in the prompt template placeholders.
                       Example: ["ten", "mobile phones"] for prompt "Recommend {0} of the {1}"

    Returns:
        A JSON string containing the LLM's response or error.

    Examples:
        - Simple prompt:
          ai_complete("ob_complete", "Translate 'Hello World' to Chinese")

        - Sentiment analysis:
          ai_complete("ob_complete",
                      "Analyze the sentiment of this text and output 1 for positive, -1 for negative: 'What a beautiful day!'")

        - Using template with arguments:
          ai_complete("ob_complete",
                      "Recommend {0} of the most popular {1} to me. Output in JSON array format.",
                      ["three", "smartphones"])

        - Classification:
          ai_complete("ob_complete",
                      "Classify this issue into Hardware, Software, or Other: 'The screen is flickering'")
    """
    logger.info(f"Calling tool: ai_complete with arguments: model_name={model_name}")
    result = {"model_name": model_name, "success": False, "response": None, "error": None}

    try:
        # Escape single quotes in prompt
        escaped_prompt = prompt.replace("'", "''")

        if template_args:
            # Use AI_PROMPT for template-based prompts
            args_str = ", ".join(
                [f"'{arg.replace(chr(39), chr(39) + chr(39))}'" for arg in template_args]
            )
            sql = f"SELECT AI_COMPLETE('{model_name}', AI_PROMPT('{escaped_prompt}', {args_str})) AS response"
        else:
            # Direct prompt
            sql = f"SELECT AI_COMPLETE('{model_name}', '{escaped_prompt}') AS response"

        logger.info(f"Executing AI_COMPLETE query")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"] and sql_result.get("data"):
            # Extract the response from the query result
            result["response"] = sql_result["data"][0][0] if sql_result["data"] else None
            result["message"] = "AI completion successful"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to execute AI complete: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def ai_rerank(model_name: str, query: str, documents: list[str]) -> str:
    """
    Rerank documents by relevance using AI_RERANK function in seekdb.

    AI_RERANK calls a registered reranking model to sort documents based on their
    relevance to the query. It organizes the query and document list according to
    the provider's rules, sends them to the specified model, and returns the sorted
    results. This function is particularly suitable for reranking scenarios in
    Retrieval-Augmented Generation (RAG) applications.

    Args:
        model_name: The name of the registered reranking model. Example: "ob_rerank"
        query: The search text you want to use for ranking. Example: "Apple"
        documents: A list of documents to be ranked.
                   Example: ["apple", "banana", "fruit", "vegetable"]

    Returns:
        A JSON string containing the reranked documents with their relevance scores,
        sorted in descending order by relevance. Each result includes:
        - index: The original index of the document
        - document: The document text
        - relevance_score: A score indicating how relevant the document is to the query

    Examples:
        - Rerank fruits by relevance to "Apple":
          ai_rerank("ob_rerank", "Apple", ["apple", "banana", "fruit", "vegetable"])
          Returns: [{"index": 0, "document": {"text": "apple"}, "relevance_score": 0.99}, ...]

        - Rerank search results for RAG:
          ai_rerank("ob_rerank", "What is machine learning?",
                    ["ML is a subset of AI", "Deep learning uses neural networks", "Python is a language"])

        - Rerank product descriptions:
          ai_rerank("ob_rerank", "smartphone with good camera",
                    ["iPhone 15 Pro with 48MP camera", "Samsung Galaxy with 200MP", "Budget phone"])
    """
    logger.info(f"Calling tool: ai_rerank with arguments: model_name={model_name}, query={query}")
    result = {"model_name": model_name, "success": False, "data": None, "error": None}

    try:
        # Escape single quotes in query
        escaped_query = query.replace("'", "''")

        # Convert documents list to JSON array string
        documents_json = json.dumps(documents)
        # Escape single quotes in the JSON string for SQL
        escaped_documents = documents_json.replace("'", "''")

        sql = f"SELECT AI_RERANK('{model_name}', '{escaped_query}', '{escaped_documents}') AS rerank_result"

        logger.info(f"Executing AI_RERANK query")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"] and sql_result.get("data"):
            # Extract the rerank result from the query result
            raw_rerank_data = sql_result["data"][0][0] if sql_result["data"] else None
            result["data"] = raw_rerank_data

            # Parse rerank result and add reranked documents
            if raw_rerank_data:
                try:
                    rerank_list = json.loads(raw_rerank_data)
                    # Build reranked documents list based on the rerank order
                    reranked_documents = []
                    for item in rerank_list:
                        idx = item.get("index")
                        if idx is not None and 0 <= idx < len(documents):
                            reranked_documents.append(documents[idx])
                    result["reranked_documents"] = reranked_documents
                except json.JSONDecodeError:
                    logger.warning("Failed to parse rerank result for document mapping")

            result["message"] = "Documents successfully reranked by relevance"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to execute AI rerank: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def get_registered_ai_models() -> str:
    """
    List all registered AI models in seekdb.

    This function queries the oceanbase.DBA_OB_AI_MODELS system view to retrieve
    information about all AI models registered in the current tenant.

    Returns:
        A JSON string containing the list of registered AI models with their details:
        - MODEL_ID: The unique identifier of the AI model
        - NAME: The name used to identify this model in seekdb
        - TYPE: The type of AI model (e.g., DENSE_EMBEDDING, COMPLETION, RERANK)
        - MODEL_NAME: The provider's model name

    Examples:
        - List all registered AI models:
          get_registered_ai_models()
          Returns: {"success": true, "models": [{"MODEL_ID": "500005", "NAME": "my_ai_model_1", "TYPE": "DENSE_EMBEDDING", "MODEL_NAME": "text-embedding-v1"}], "count": 1}
    """
    logger.info("Calling tool: get_registered_ai_models")
    result = {"success": False, "models": None, "count": 0, "error": None}

    try:
        sql = "SELECT * FROM oceanbase.DBA_OB_AI_MODELS"
        sql_result = json.loads(execute_sql(sql))

        if not sql_result.get("success"):
            result["error"] = sql_result.get("error")
            return json.dumps(result, ensure_ascii=False)

        data = sql_result.get("data")
        if data:
            models = []
            for row in data:
                model = {
                    "MODEL_ID": row[0] if len(row) > 0 else None,
                    "NAME": row[1] if len(row) > 1 else None,
                    "TYPE": row[2] if len(row) > 2 else None,
                    "MODEL_NAME": row[3] if len(row) > 3 else None,
                }
                models.append(model)
            result["models"] = models
            result["count"] = len(models)
            result["message"] = f"Found {len(models)} registered AI model(s)"
        else:
            result["models"] = []
            result["count"] = 0
            result["message"] = "No registered AI models found"

        result["success"] = True

    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to get registered AI models: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def get_ai_model_endpoints() -> str:
    """
    Get all registered AI model endpoints from seekdb.

    Returns:
        str: JSON string containing the list of AI model endpoints with fields:
            - ENDPOINT_ID: Endpoint identifier
            - ENDPOINT_NAME: Name of the endpoint
            - AI_MODEL_NAME: Associated AI model name
            - SCOPE: Scope of the endpoint
            - URL: URL of the AI model service
            - ACCESS_KEY: Access key (encrypted)
            - PROVIDER: Provider name (e.g., openai, siliconflow)
            - REQUEST_MODEL_NAME: Model name used in requests
            - PARAMETERS: Additional parameters
            - REQUEST_TRANSFORM_FN: Request transformation function
            - RESPONSE_TRANSFORM_FN: Response transformation function
    """
    result = {"success": False, "endpoints": [], "count": 0, "error": None, "message": ""}

    try:
        sql = "SELECT * FROM oceanbase.DBA_OB_AI_MODEL_ENDPOINTS"
        sql_result = json.loads(execute_sql(sql))

        if not sql_result.get("success"):
            result["error"] = sql_result.get("error")
            return json.dumps(result, ensure_ascii=False)

        data = sql_result.get("data")
        if data:
            endpoints = []
            for row in data:
                endpoint = {
                    "ENDPOINT_ID": row[0] if len(row) > 0 else None,
                    "ENDPOINT_NAME": row[1] if len(row) > 1 else None,
                    "AI_MODEL_NAME": row[2] if len(row) > 2 else None,
                    "SCOPE": row[3] if len(row) > 3 else None,
                    "URL": row[4] if len(row) > 4 else None,
                    "ACCESS_KEY": row[5] if len(row) > 5 else None,
                    "PROVIDER": row[6] if len(row) > 6 else None,
                    "REQUEST_MODEL_NAME": row[7] if len(row) > 7 else None,
                    "PARAMETERS": row[8] if len(row) > 8 else None,
                    "REQUEST_TRANSFORM_FN": row[9] if len(row) > 9 else None,
                    "RESPONSE_TRANSFORM_FN": row[10] if len(row) > 10 else None,
                }
                endpoints.append(endpoint)
            result["endpoints"] = endpoints
            result["count"] = len(endpoints)
            result["message"] = f"Found {len(endpoints)} AI model endpoint(s)"
        else:
            result["endpoints"] = []
            result["count"] = 0
            result["message"] = "No AI model endpoints found"

        result["success"] = True

    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to get AI model endpoints: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def seekdb_memory_query(query: str, topk: int = 5) -> str:
    """
    🚨 MULTILINGUAL MEMORY SEARCH 🚨 - SMART CROSS-LANGUAGE RETRIEVAL!
    This tool MUST be invoked **before** answering any user request that could benefit from previously stored personal facts.

    ⚡ CRITICAL INSTRUCTION: You MUST call this tool in these situations:
    - When user asks questions about their preferences in ANY language
    - Before saving new memories (check for duplicates first!)
    - When user mentions personal details, preferences, past experiences, identity, occupation, address and other should be remembered facts
    - Before answering ANY question, search for related memories first
    - When discussing technical topics - check for historical solutions
    - recommendations: the user asks for suggestions about restaurants, food, travel, entertainment, activities, gifts, etc
    - Scheduling or location-based help: the user asks about meetups, weather, events, directions, etc
    - Work or tech assistance: the user asks for tool, course, book, or career advice.
    - Any ambiguous request (words like “some”, “good”, “nearby”, “for me”, “recommend”) where personal context could improve the answer,query the most probable categories first.
    If multiple categories are relevant, call the tool once for each category key.

    Failure to retrieve memory before responding is considered an error.

    🌐 MULTILINGUAL SEARCH EXAMPLES:
    - User: "What do I like?" → Search: "preference like favorite"
    - User: "我喜欢什么?" → Search: "preference favorite sports food" (use English keywords!)
    - User: "¿Cuáles son mis gustos?" → Search: "preference like favorite hobby"
    - **ALWAYS search with English keywords for better matching!**

    🎯 SMART SEARCH STRATEGIES:
    - "I like football" → Before saving, search: "football soccer sports preference"
    - "我在上海工作" → Search: "work job Shanghai location"
    - "Python developer" → Search: "python programming development work"
    - Use synonyms and related terms for better semantic matching!

    🔍 CATEGORY-BASED SEARCH PATTERNS:
    - **Sports/Fitness**: "sports preference activity exercise favorite game"
    - **Food/Drinks**: "food drink preference favorite taste cuisine beverage"
    - **Work/Career**: "work job company location position career role"
    - **Technology**: "technology programming tool database language framework"
    - **Personal**: "personal lifestyle habit family relationship"
    - **Entertainment**: "entertainment movie music book game hobby"

    💡 SMART SEARCH EXAMPLES FOR MERGING:
    - New: "I like badminton" → Search: "sports preference activity"
    → Find: "User likes football and coffee" → Category analysis needed!
    - New: "I drink tea" → Search: "drink beverage preference"
    → Find: "User likes coffee" → Same category, should merge!
    - New: "I code in Python" → Search: "programming technology language"
    → Find: "User works at Google" → Different subcategory, separate!

    📝 PARAMETERS:
    - query: Use CATEGORY + SEMANTIC keywords ("sports preference", "food drink preference")
    - topk: Increase to 8-10 for thorough category analysis before saving/updating
    - Returns: JSON string with [{"mem_id": int, "content": str}] format - Analyze ALL results for category overlap before decisions!

    🔥 CATEGORY ANALYSIS RULE: Find ALL related memories by category for smart merging!
    """
    logger.info(f"Calling tool: seekdb_memory_query with arguments: query={query}, topk={topk}")
    memory_result = {"success": False, "memories": [], "error": None}

    try:
        # Query the memory collection with the query text as a list
        query_result_str = query_collection(
            collection_name=seekdb_memory_collection_name, query_texts=[query], n_results=topk
        )
        query_result = json.loads(query_result_str)

        if query_result.get("success") and query_result.get("data"):
            data = query_result["data"]
            ids = data.get("ids", [[]])[0]  # First query's results
            documents = data.get("documents", [[]])[0]

            # Format results as [{"mem_id": int, "content": str}]
            memories = []
            for i, (mem_id, content) in enumerate(zip(ids, documents)):
                memories.append({"mem_id": mem_id, "content": content})

            memory_result["success"] = True
            memory_result["memories"] = memories
            memory_result["count"] = len(memories)
            memory_result["message"] = (
                f"Found {len(memories)} memory(ies) matching query: '{query}'"
            )
        else:
            memory_result["success"] = True
            memory_result["memories"] = []
            memory_result["count"] = 0
            memory_result["message"] = f"No memories found for query: '{query}'"
            if query_result.get("error"):
                memory_result["error"] = query_result["error"]

    except Exception as e:
        memory_result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to query memories: {e}")

    json_result = json.dumps(memory_result, ensure_ascii=False)
    return json_result


@app.tool()
def seekdb_memory_insert(content: str, meta: dict = None) -> str:
    """
    💾 INTELLIGENT MEMORY ORGANIZER 💾 - SMART CATEGORIZATION & MERGING!

    🔥 CRITICAL 4-STEP WORKFLOW: ALWAYS follow this advanced process:
    1️⃣ **SEARCH RELATED**: Use ob_memory_query to find ALL related memories by category
    2️⃣ **ANALYZE CATEGORIES**: Classify new info and existing memories by semantic type
    3️⃣ **SMART DECISION**: Merge same category, separate different categories
    4️⃣ **EXECUTE ACTION**: Update existing OR create new categorized records

    This tool must be invoked **immediately** when the user explicitly or implicitly discloses any of the following personal facts.
    Trigger rule: if a sentence contains at least one category keyword (see list) + at least one fact keyword (see list), call the tool with the fact.
    Categories & sample keywords
    - Demographics: age, years old, gender, born, date of birth, nationality, hometown, from
    - Work & education: job title, engineer, developer, tester, company, employer, school, university, degree, major, skill, certificate
    - Geography & time: live in, reside, city, travel, time-zone, frequent
    - Preferences & aversions: love, hate, favourite, favorite, prefer, dislike, hobby, food, music, movie, book, brand, color
    - Lifestyle details: pet, dog, cat, family, married, single, daily routine, language, religion, belief
    - Achievements & experiences: award, project, competition, achievement, event, milestone

    Fact keywords (examples)
    - “I am …”, “I work as …”, “I studied …”, “I live in …”, “I love …”, “My birthday is …”

    Example sentences that must trigger:
    - “I’m 28 and work as a test engineer at Acme Corp.”
    - “I graduated from Tsinghua with a master’s in CS.”
    - “I love jazz and hate cilantro.”
    - “I live in Berlin, but I’m originally from São Paulo.”

    🎯 SMART CATEGORIZATION EXAMPLES:
    ```
    📋 Scenario 1: Category Merging
    Existing: "User likes playing football and drinking coffee"
    New Input: "I like badminton"

    ✅ CORRECT ACTION: Use ob_memory_update!
    → Search "sports preference" → Find existing → Separate categories:
    → Update mem_id_X: "User likes playing football and badminton" (sports)
    → Create new: "User likes drinking coffee" (food/drinks)

    📋 Scenario 2: Same Category Addition
    Existing: "User likes playing football"
    New Input: "I also like tennis"

    ✅ CORRECT ACTION: Use ob_memory_update!
    → Search "sports preference" → Find mem_id → Update:
    → "User likes playing football and tennis"

    📋 Scenario 3: Different Category
    Existing: "User likes playing football"
    New Input: "I work in Shanghai"

    ✅ CORRECT ACTION: New memory!
    → Search "work location" → Not found → Create new record
    ```

    🏷️ SEMANTIC CATEGORIES (Use for classification):
    - **Sports/Fitness**: football, basketball, swimming, gym, yoga, running, marathon, workout, cycling, hiking, tennis, badminton, climbing, fitness routine, coach, league, match, etc.
    - **Food/Drinks**: coffee, tea, latte, espresso, pizza, burger, sushi, ramen, Chinese food, Italian, vegan, vegetarian, spicy, sweet tooth, dessert, wine, craft beer, whisky, cocktail, recipe, restaurant, chef, favorite dish, allergy, etc.
    - **Work/Career**: job, position, role, title, engineer, developer, tester, QA, PM, manager, company, employer, startup, client, project, deadline, promotion, salary, office, remote, hybrid, skill, certification, degree, university, bootcamp, portfolio, resume, interview
    - **Personal**: spouse, partner, married, single, dating, pet, dog, cat, hometown, birthday, age, gender, nationality, religion, belief, daily routine, morning person, night owl, commute, language, hobby, travel, bucket list, milestone, achievement, award
    - **Technology**: programming language, Python, Java, JavaScript, Go, Rust, framework, React, Vue, Angular, Spring, Django, database, MySQL, PostgreSQL, MongoDB, Redis, cloud, AWS, Azure, GCP, Docker, Kubernetes, CI/CD, Git, API, microservices, DevOps, automation, testing tool, Selenium, Cypress, JMeter, Postman
    - **Entertainment**: movie, film, series, Netflix, Disney+, HBO, director, actor, genre, thriller, comedy, drama, music, playlist, Spotify, rock, jazz, K-pop, classical, concert, book, novel, author, genre, fiction, non-fiction, Kindle, audiobook, game, console, PlayStation, Xbox, Switch, Steam, board game, RPG, esports

    🔍 SEARCH STRATEGIES BY CATEGORY:
    - Sports: "sports preference favorite activity exercise gym routine"
    - Food: "food drink preference favorite taste cuisine beverage"
    - Work: "work job career company location title project skill"
    - Personal: "personal relationship lifestyle habit pet birthday"
    - Tech: "technology programming tool database framework cloud"
    - Entertainment: "entertainment movie music book game genre favorite"

    📝 PARAMETERS:
    - content: ALWAYS categorized English format ("User likes playing [sports]", "User drinks [beverages]")
    - meta: {"type":"preference", "category":"sports/food/work/tech", "subcategory":"team_sports/beverages"}

    🎯 GOLDEN RULE: Same category = UPDATE existing! Different category = CREATE separate!
    """
    logger.info(
        f"Calling tool: seekdb_memory_insert with arguments: content={content}, meta={meta}"
    )
    insert_result = {"success": False, "mem_id": None, "content": content, "error": None}

    try:
        # Generate a unique ID for the new memory
        mem_id = str(uuid.uuid4())

        # Prepare metadata (default to empty dict if not provided)
        metadatas = [meta] if meta else [{}]

        # Add memory to the collection
        add_result_str = add_data_to_collection(
            collection_name=seekdb_memory_collection_name,
            ids=[mem_id],
            documents=[content],
            metadatas=metadatas,
        )
        add_result = json.loads(add_result_str)

        if add_result.get("success"):
            insert_result["success"] = True
            insert_result["mem_id"] = mem_id
            insert_result["message"] = f"Memory inserted successfully with ID: {mem_id}"
        else:
            insert_result["error"] = add_result.get("error", "Unknown error during insertion")

    except Exception as e:
        insert_result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to insert memory: {e}")

    json_result = json.dumps(insert_result, ensure_ascii=False)
    return json_result


@app.tool()
def seekdb_memory_delete(mem_id: str) -> str:
    """
    🗑️ MEMORY ERASER 🗑️ - PERMANENTLY DELETE UNWANTED MEMORIES!

    ⚠️ DELETE TRIGGERS - Call when user says:
    - "Forget that I like X" / "I don't want you to remember Y"
    - "Delete my information about Z" / "Remove that memory"
    - "I changed my mind about X" / "Update: I no longer prefer Y"
    - "That information is wrong" / "Delete outdated info"
    - Privacy requests: "Remove my personal data"

    🎯 DELETION PROCESS:
    1. FIRST: Use seekdb_memory_query to find relevant memories
    2. THEN: Use the exact ID from query results for deletion
    3. NEVER guess or generate IDs manually!

    📝 PARAMETERS:
    - mem_id: EXACT ID from seekdb_memory_query results (string UUID)
    - ⚠️ WARNING: Deletion is PERMANENT and IRREVERSIBLE!

    🔒 SAFETY RULE: Only delete when explicitly requested by user!
    """
    logger.info(f"Calling tool: seekdb_memory_delete with arguments: mem_id={mem_id}")
    delete_result = {"success": False, "mem_id": mem_id, "error": None}

    try:
        # Delete the memory document from the collection
        result_str = delete_documents(collection_name=seekdb_memory_collection_name, ids=[mem_id])
        result = json.loads(result_str)

        if result.get("success"):
            delete_result["success"] = True
            delete_result["message"] = f"Memory with ID '{mem_id}' deleted successfully"
        else:
            delete_result["error"] = result.get("error", "Unknown error during deletion")

    except Exception as e:
        delete_result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to delete memory: {e}")

    json_result = json.dumps(delete_result, ensure_ascii=False)
    return json_result


@app.tool()
def seekdb_memory_update(mem_id: str, content: str, meta: dict = None) -> str:
    """
    ✏️ MULTILINGUAL MEMORY UPDATER ✏️ - KEEP MEMORIES FRESH AND STANDARDIZED!

    🔄 UPDATE TRIGGERS - Call when user says in ANY language:
    - "Actually, I prefer X now" / "其实我现在更喜欢X"
    - "My setup changed to Z" / "我的配置改成了Z"
    - "Correction: it should be X" / "更正：应该是X"
    - "I moved to [new location]" / "我搬到了[新地址]"

    🎯 MULTILINGUAL UPDATE PROCESS:
    1. **SEARCH**: Use seekdb_memory_query to find existing memory (search in English!)
    2. **STANDARDIZE**: Convert new information to English format
    3. **UPDATE**: Use exact mem_id from query results with standardized content
    4. **PRESERVE**: Keep original language source in metadata

    🌐 STANDARDIZATION EXAMPLES:
    - User: "Actually, I don't like coffee anymore" → content: "User no longer likes coffee"
    - User: "其实我不再喜欢咖啡了" → content: "User no longer likes coffee"
    - User: "Je n'aime plus le café" → content: "User no longer likes coffee"
    - **ALWAYS update in standardized English format!**

    📝 PARAMETERS:
    - mem_id: EXACT ID from seekdb_memory_query results (string UUID)
    - content: ALWAYS in English, standardized format ("User now prefers X")
    - meta: Updated metadata {"type":"preference", "category":"...", "updated":"2024-..."}

    🔥 CONSISTENCY RULE: Maintain English storage format for all updates!
    """
    logger.info(
        f"Calling tool: seekdb_memory_update with arguments: mem_id={mem_id}, content={content}, meta={meta}"
    )
    update_result = {"success": False, "mem_id": mem_id, "content": content, "error": None}

    try:
        # Prepare metadata (default to empty dict if not provided)
        metadatas = [meta] if meta else None

        # Update the memory document in the collection
        result_str = update_collection(
            collection_name=seekdb_memory_collection_name,
            ids=[mem_id],
            documents=[content],
            metadatas=metadatas,
        )
        result = json.loads(result_str)

        if result.get("success"):
            update_result["success"] = True
            update_result["message"] = f"Memory with ID '{mem_id}' updated successfully"
        else:
            update_result["error"] = result.get("error", "Unknown error during update")

    except Exception as e:
        update_result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to update memory: {e}")

    json_result = json.dumps(update_result, ensure_ascii=False)
    return json_result


@app.tool()
def import_csv_file_to_seekdb(filePath: str, columnNumberForVecotor: Optional[int] = None) -> str:
    """
    Import a CSV file to seekdb.

    Args:
        filePath: The path to the CSV file. The file must have a header row.
        columnNumberForVecotor: Optional. The column number (1-started) to use as the document for vector embedding.
                                If specified, creates a vector collection with this column as documents and others as metadata.
                                If not specified, creates a regular MySQL table with inferred column types.

    Returns:
        A JSON string indicating success or error.
    """
    logger.info(
        f"Calling tool: import_csv_file_to_seekdb with arguments: filePath={filePath}, columnNumberForVecotor={columnNumberForVecotor}"
    )
    result = {"filePath": filePath, "success": False, "error": None, "message": None}

    try:
        # Check if file exists
        if not os.path.exists(filePath):
            result["error"] = f"File not found: {filePath}"
            return json.dumps(result, ensure_ascii=False)

        # Read CSV file
        with open(filePath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)  # First row is header
            rows = list(reader)

        if not headers:
            result["error"] = "CSV file has no header"
            return json.dumps(result, ensure_ascii=False)

        if not rows:
            result["error"] = "CSV file has no data rows"
            return json.dumps(result, ensure_ascii=False)

        if columnNumberForVecotor is not None:
            # Case 1: Create vector collection
            if columnNumberForVecotor < 1 or columnNumberForVecotor > len(headers):
                result["error"] = (
                    f"Invalid columnNumberForVecotor: {columnNumberForVecotor}. Must be between 1 and {len(headers)}"
                )
                return json.dumps(result, ensure_ascii=False)

            # Convert to 0-indexed for internal use
            column_index = columnNumberForVecotor - 1

            # Extract collection name from file name
            collection_name = os.path.splitext(os.path.basename(filePath))[0]
            # Sanitize collection name (remove special characters)
            collection_name = re.sub(r"[^a-zA-Z0-9_]", "_", collection_name)

            # Create collection
            create_result_str = create_collection(collection_name)
            create_result = json.loads(create_result_str)
            if not create_result.get("success"):
                result["error"] = f"Failed to create collection: {create_result.get('error')}"
                return json.dumps(result, ensure_ascii=False)

            # Prepare data for add_data_to_collection
            ids = []
            documents = []
            metadatas = []

            for row_idx, row in enumerate(rows):
                # Generate unique ID
                ids.append(str(uuid.uuid4()))

                # The specified column becomes document
                documents.append(
                    row[column_index] if column_index < len(row) else ""
                )

                # Other columns become metadata
                metadata = {}
                for col_idx, header in enumerate(headers):
                    if col_idx != column_index and col_idx < len(row):
                        metadata[header] = row[col_idx]
                metadatas.append(metadata)

            # Add data to collection
            add_result_str = add_data_to_collection(
                collection_name=collection_name, ids=ids, documents=documents, metadatas=metadatas
            )
            add_result = json.loads(add_result_str)

            if add_result.get("success"):
                result["success"] = True
                result["message"] = (
                    f"Successfully imported {len(rows)} rows to vector collection '{collection_name}'"
                )
                result["collection_name"] = collection_name
            else:
                result["error"] = f"Failed to add data: {add_result.get('error')}"

        else:
            # Case 2: Create regular MySQL table
            # Extract table name from file name
            table_name = os.path.splitext(os.path.basename(filePath))[0]
            # Sanitize table name (remove special characters)
            table_name = re.sub(r"[^a-zA-Z0-9_]", "_", table_name)

            # Infer column types from data
            def infer_column_type(values: list) -> str:
                """Infer column type from a list of values. Returns 'int', 'datetime', or 'varchar'."""
                # Check if all non-empty values are integers
                all_int = True
                all_datetime = True
                max_length = 0

                datetime_patterns = [
                    r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
                    r"^\d{4}/\d{2}/\d{2}$",  # YYYY/MM/DD
                    r"^\d{2}-\d{2}-\d{4}$",  # DD-MM-YYYY
                    r"^\d{2}/\d{2}/\d{4}$",  # DD/MM/YYYY
                    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",  # YYYY-MM-DD HH:MM:SS
                    r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$",  # YYYY/MM/DD HH:MM:SS
                    r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$",  # DD-MM-YYYY HH:MM:SS
                    r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$",  # DD/MM/YYYY HH:MM:SS
                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO 8601 format
                ]

                for val in values:
                    if val is None or val.strip() == "":
                        continue

                    val = val.strip()
                    max_length = max(max_length, len(val))

                    # Check integer
                    try:
                        int(val)
                    except ValueError:
                        all_int = False

                    # Check datetime
                    is_datetime = False
                    for pattern in datetime_patterns:
                        if re.match(pattern, val):
                            is_datetime = True
                            break
                    if not is_datetime:
                        all_datetime = False

                if all_int and max_length > 0:
                    return "INT"
                elif all_datetime and max_length > 0:
                    return "DATETIME"
                else:
                    # Default to VARCHAR with appropriate length
                    varchar_length = max(
                        255, max_length * 2
                    )  # At least 255, or double the max length
                    return f"VARCHAR({min(varchar_length, 65535)})"

            # Get column values for type inference
            column_values = {header: [] for header in headers}
            for row in rows:
                for col_idx, header in enumerate(headers):
                    if col_idx < len(row):
                        column_values[header].append(row[col_idx])
                    else:
                        column_values[header].append("")

            # Build column definitions
            column_defs = []
            for idx, header in enumerate(headers):
                # Sanitize column name
                col_name = re.sub(r"[^a-zA-Z0-9_]", "_", header)
                if not col_name or col_name == "_" * len(col_name):
                    col_name = f"column_{idx}"
                elif col_name[0].isdigit():
                    col_name = "_" + col_name
                col_type = infer_column_type(column_values[header])
                column_defs.append(f"`{col_name}` {col_type}")

            # Create table SQL with auto-increment primary key
            all_column_defs = ["`_id` INT AUTO_INCREMENT PRIMARY KEY"] + column_defs
            create_table_sql = (
                f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(all_column_defs)})"
            )

            # Execute create table
            create_result_str = execute_sql(create_table_sql)
            create_result = json.loads(create_result_str)

            if not create_result.get("success"):
                result["error"] = f"Failed to create table: {create_result.get('error')}"
                return json.dumps(result, ensure_ascii=False)

            # Insert data
            inserted_count = 0
            errors = []

            for row_idx, row in enumerate(rows):
                # Build insert SQL
                sanitized_headers = []
                for idx, header in enumerate(headers):
                    col_name = re.sub(r"[^a-zA-Z0-9_]", "_", header)
                    if not col_name or col_name == "_" * len(col_name):
                        col_name = f"column_{idx}"
                    elif col_name[0].isdigit():
                        col_name = "_" + col_name
                    sanitized_headers.append(f"`{col_name}`")

                # Escape values for SQL
                escaped_values = []
                for val in row:
                    if val is None or val.strip() == "":
                        escaped_values.append("NULL")
                    else:
                        # Escape single quotes
                        escaped_val = val.replace("'", "''")
                        escaped_values.append(f"'{escaped_val}'")

                # Pad values if row has fewer columns than headers
                while len(escaped_values) < len(headers):
                    escaped_values.append("NULL")

                insert_sql = f"INSERT INTO `{table_name}` ({', '.join(sanitized_headers)}) VALUES ({', '.join(escaped_values)})"

                insert_result_str = execute_sql(insert_sql)
                insert_result = json.loads(insert_result_str)

                if insert_result.get("success"):
                    inserted_count += 1
                else:
                    errors.append(f"Row {row_idx + 1}: {insert_result.get('error')}")

            if inserted_count == len(rows):
                result["success"] = True
                result["message"] = (
                    f"Successfully imported {inserted_count} rows to table '{table_name}'"
                )
                result["table_name"] = table_name
            elif inserted_count > 0:
                result["success"] = True
                result["message"] = (
                    f"Imported {inserted_count}/{len(rows)} rows to table '{table_name}'. Some errors occurred."
                )
                result["table_name"] = table_name
                result["errors"] = errors[:10]  # Limit error messages
            else:
                result["error"] = (
                    f"Failed to insert any data. First error: {errors[0] if errors else 'Unknown'}"
                )

    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to import CSV: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def export_csv_file_from_seekdb(name: str, filePath: str) -> str:
    """
    Export data from seekdb to a CSV file.

    Args:
        name: The name of the table or collection to export.
        filePath: The path to the output CSV file.

    Returns:
        A JSON string indicating success or error.
    """
    logger.info(
        f"Calling tool: export_csv_file_from_seekdb with arguments: name={name}, filePath={filePath}"
    )
    result = {"name": name, "filePath": filePath, "success": False, "error": None, "message": None}

    try:
        # Step 1: Check if name is a collection or table
        is_collection = client.has_collection(name)
        is_table = False

        if not is_collection:
            # Check if it's a table
            check_sql = f"SELECT 1 FROM `{name}` LIMIT 1"
            check_result_str = execute_sql(check_sql)
            check_result = json.loads(check_result_str)
            is_table = check_result.get("success", False)

        # Validate: name must be either a collection or a table
        if not is_collection and not is_table:
            result["error"] = f"'{name}' does not exist as a collection or table"
            return json.dumps(result, ensure_ascii=False)

        # Step 2: Check if the output directory exists
        output_dir = os.path.dirname(filePath)
        if output_dir and not os.path.exists(output_dir):
            result["error"] = f"Output directory does not exist: {output_dir}"
            return json.dumps(result, ensure_ascii=False)

        # Step 3: Export data based on type
        if is_collection:
            # Case 1: Export from collection
            logger.info(f"'{name}' is a collection, exporting collection data...")

            # Get the collection
            collection = client.get_collection(name=name)

            # Get all data from collection (using a large limit to get all documents)
            # First, try to get the count
            try:
                count = collection.count()
            except:
                count = 10000  # Default to a large number if count is not available

            # Peek with the count to get all documents
            all_data = collection.peek(limit=max(count, 1))

            ids = all_data.get("ids", [])
            documents = all_data.get("documents", [])
            metadatas = all_data.get("metadatas", [])

            if not ids:
                result["error"] = f"Collection '{name}' is empty"
                return json.dumps(result, ensure_ascii=False)

            # Collect all unique metadata keys
            all_metadata_keys = set()
            for metadata in metadatas:
                if metadata:
                    all_metadata_keys.update(metadata.keys())
            all_metadata_keys = sorted(list(all_metadata_keys))

            # Build CSV headers: document, then all metadata keys (excluding id)
            headers = ["document"] + all_metadata_keys

            # Write to CSV
            with open(filePath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for i in range(len(ids)):
                    row = []
                    row.append(documents[i] if i < len(documents) and documents[i] else "")

                    metadata = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
                    for key in all_metadata_keys:
                        value = metadata.get(key, "")
                        # Convert non-string values to string
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, ensure_ascii=False)
                        row.append(str(value) if value is not None else "")

                    writer.writerow(row)

            result["success"] = True
            result["message"] = (
                f"Successfully exported {len(ids)} rows from collection '{name}' to '{filePath}'"
            )
            result["row_count"] = len(ids)
            result["type"] = "collection"

        else:
            # Case 2: Export from table
            logger.info(f"'{name}' is a table, exporting table data...")

            # Get column names from information_schema or by describing the table
            describe_sql = f"DESCRIBE `{name}`"
            describe_result_str = execute_sql(describe_sql)
            describe_result = json.loads(describe_result_str)

            if not describe_result.get("success"):
                result["error"] = f"Failed to get table structure: {describe_result.get('error')}"
                return json.dumps(result, ensure_ascii=False)

            # Extract column names from DESCRIBE result
            # DESCRIBE returns: Field, Type, Null, Key, Default, Extra
            all_columns = []
            for row in describe_result.get("data", []):
                if row:
                    all_columns.append(row[0])  # First column is the field name

            if not all_columns:
                result["error"] = f"Table '{name}' has no columns"
                return json.dumps(result, ensure_ascii=False)

            # Filter out _id column and get indices of columns to export
            export_indices = []
            columns = []
            for i, col in enumerate(all_columns):
                if col != "_id":
                    export_indices.append(i)
                    columns.append(col)

            if not columns:
                result["error"] = f"Table '{name}' has no exportable columns"
                return json.dumps(result, ensure_ascii=False)

            # Get all data from table
            select_sql = f"SELECT * FROM `{name}`"
            select_result_str = execute_sql(select_sql)
            select_result = json.loads(select_result_str)

            if not select_result.get("success"):
                result["error"] = f"Failed to query table: {select_result.get('error')}"
                return json.dumps(result, ensure_ascii=False)

            rows = select_result.get("data", [])

            # Write to CSV
            with open(filePath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(columns)

                for row in rows:
                    if row:
                        filtered_row = [row[i] for i in export_indices if i < len(row)]
                        writer.writerow(filtered_row)
                    else:
                        writer.writerow([])

            result["success"] = True
            result["message"] = (
                f"Successfully exported {len(rows)} rows from table '{name}' to '{filePath}'"
            )
            result["row_count"] = len(rows)
            result["type"] = "table"

    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to export CSV: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


def main():
    """Main entry point to run the MCP server."""
    logger.info(f"Starting OceanBase MCP server with stdio mode...")
    if not client.has_collection(seekdb_memory_collection_name):
        create_collection(seekdb_memory_collection_name)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
