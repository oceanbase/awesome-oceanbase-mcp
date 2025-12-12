from __future__ import annotations
import logging
import time
from typing import Optional
import json
import argparse
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mysql.connector import Error
import pyseekdb

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("seekdb_mcp_server")

load_dotenv()

app = FastMCP("seekdb_mcp_server")
client = pyseekdb.Client()
server = client._server


@app.tool()
def execute_sql(sql: str) -> str:
    """Execute a sql on the seekdb"""
    logger.info(f"Calling tool: execute_sql with arguments: {sql}")
    result = {"sql": sql, "success": False, "data": None, "error": None}
    try:
        data = server.execute(sql)
        if isinstance(data, list):
            result["data"] = [[str(cell) for cell in row] for row in data]
        result["success"] = True
    except Error as e:
        result["error"] = f"[Error]: {e}"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
    json_result = json.dumps(result, ensure_ascii=False)
    if result["error"]:
        logger.error(f"SQL executed failed, result: {json_result}")
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
        # Fallback to system time if database query fails
        local_time = time.localtime()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        logger.info(f"Fallback to system time: {formatted_time}")
        return formatted_time


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
def create_semantic_index(
    table_name: str,
    column_name: str,
    index_name: str,
    model_name: str,
    dimension: int = 1024,
    distance: str = "l2",
    sync_mode: str = "immediate",
) -> str:
    """
    Create a hybrid vector index (semantic index) on a VARCHAR column in seekdb.

    Hybrid vector indexes leverage seekdb's built-in embedding capabilities to greatly simplify
    the vector index usage process. They make the vector concept transparent to users: you can
    directly write raw text data, and seekdb will automatically convert it to vectors and build
    indexes internally. During retrieval, you only need to provide the original text.

    This function creates a semantic index on an existing table. The table must already exist
    and have a VARCHAR column to index.

    Args:
        table_name: The name of the existing table. Example: "items"
        column_name: The VARCHAR column to create the semantic index on. Example: "doc"
        index_name: The name for the vector index. Example: "vector_idx"
        model_name: The registered embedding model name. Example: "ob_embed"
                    The model must be registered using create_ai_model and create_ai_model_endpoint.
        dimension: The dimension of the embedding vectors. Default is 1024 (for BAAI/bge-m3).
                   Must match the embedding model's output dimension.
        distance: The distance metric. Options: "l2", "inner_product", "cosine". Default is "l2".
        sync_mode: The embedding mode. Options:
                   - "immediate": Synchronous mode, converts text to vectors immediately on insert.
                   - "async": Asynchronous mode, converts periodically or manually.
                   Default is "immediate".

    Returns:
        A JSON string indicating success or error.

    Examples:
        - Create a semantic index with default settings:
          create_semantic_index("items", "doc", "vector_idx", "ob_embed")

        - Create with custom dimension:
          create_semantic_index("items", "content", "content_idx", "ob_embed", dimension=512)

        - Create with inner product distance:
          create_semantic_index("documents", "text", "doc_idx", "ob_embed",
                               dimension=1024, distance="inner_product")

        - Create with async mode for better insert performance:
          create_semantic_index("articles", "body", "article_idx", "ob_embed", sync_mode="async")
    """
    logger.info(
        f"Calling tool: create_semantic_index with arguments: table_name={table_name}, column_name={column_name}"
    )
    result = {"table_name": table_name, "index_name": index_name, "success": False, "error": None}

    try:
        # Check if model exists
        check_model_sql = f"SELECT count(*) FROM oceanbase.DBA_OB_AI_MODEL_ENDPOINTS WHERE ai_model_name='{model_name}'"
        model_check_result = json.loads(execute_sql(check_model_sql))
        if not model_check_result["success"]:
            result["error"] = f"Failed to check model existence: {model_check_result.get('error')}"
            return json.dumps(result, ensure_ascii=False)
        model_count = int(model_check_result.get("data", [["0"]])[0][0])
        if model_count == 0:
            result["error"] = (
                f"Model '{model_name}' does not exist. Please create the model first using create_ai_model and create_ai_model_endpoint tools."
            )
            return json.dumps(result, ensure_ascii=False)

        # Validate distance parameter
        valid_distances = ["l2", "inner_product", "cosine"]
        if distance not in valid_distances:
            result["error"] = f"Invalid distance. Must be one of: {valid_distances}"
            return json.dumps(result, ensure_ascii=False)

        # Validate sync_mode parameter
        valid_sync_modes = ["immediate", "async"]
        if sync_mode not in valid_sync_modes:
            result["error"] = f"Invalid sync_mode. Must be one of: {valid_sync_modes}"
            return json.dumps(result, ensure_ascii=False)

        # Build the CREATE VECTOR INDEX SQL
        sql = f"""CREATE VECTOR INDEX {index_name} 
                ON {table_name} ({column_name}) 
                WITH (distance={distance}, lib=vsag, type=hnsw, model={model_name}, dim={dimension}, sync_mode={sync_mode})"""

        logger.info(f"Executing CREATE VECTOR INDEX: {sql}")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = (
                f"Semantic index '{index_name}' created successfully on {table_name}.{column_name}"
            )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to create semantic index: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def semantic_search(
    table_name: str,
    column_name: str,
    query_text: str,
    limit: int = 10,
    select_columns: Optional[list[str]] = None,
) -> str:
    """
    Perform semantic search on a table with a hybrid vector index in seekdb.

    This function uses the semantic_distance function to search for similar content
    based on text meaning, not exact keyword matching. The table must have a hybrid
    vector index (semantic index) created on the target column.

    The system automatically converts the query text to a vector and retrieves the
    most similar content from the vector index.

    Args:
        table_name: The name of the table to search. Example: "items"
        column_name: The column with the semantic index. Example: "doc"
        query_text: The text to search for similar content. Example: "flower"
                    The system will find content semantically similar to this text.
        limit: Maximum number of results to return. Default is 10.
        select_columns: List of columns to include in results. If None, includes all columns.
                        Example: ["id", "doc", "title"]

    Returns:
        A JSON string containing the search results ordered by semantic similarity.

    Examples:
        - Basic semantic search:
          semantic_search("items", "doc", "flower")
          Returns items semantically similar to "flower" (e.g., Rose, Sunflower, Lily)

        - Search with specific columns:
          semantic_search("articles", "content", "machine learning",
                         select_columns=["id", "title", "content"])

        - Search with custom limit:
          semantic_search("products", "description", "comfortable shoes", limit=5)

        - Search for similar documents:
          semantic_search("knowledge_base", "text", "How to configure database?", limit=3)
    """
    logger.info(
        f"Calling tool: semantic_search with arguments: table_name={table_name}, query_text={query_text}"
    )
    result = {"table_name": table_name, "success": False, "data": None, "error": None}

    try:
        # Escape single quotes in query_text
        # escaped_query = query_text.replace("'", "''")

        # Build SELECT clause
        if select_columns:
            select_clause = ", ".join(select_columns)
        else:
            select_clause = "*"

        # Build the semantic search SQL using semantic_distance function
        sql = f"""SELECT {select_clause} FROM {table_name}
            ORDER BY semantic_distance({column_name}, '{query_text}') 
            APPROXIMATE LIMIT {limit}"""

        logger.info(f"Executing semantic search query")

        # Reuse execute_sql method
        print(sql)
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["data"] = sql_result.get("data")
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = (
                f"Semantic search returned {len(result['data']) if result['data'] else 0} result(s)"
            )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to perform semantic search: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def semantic_vector_search(
    table_name: str,
    column_name: str,
    query_vector: list[float],
    limit: int = 10,
    select_columns: Optional[list[str]] = None,
) -> str:
    """
    Perform vector-based semantic search on a table with a hybrid vector index in seekdb.

    This function uses the semantic_vector_distance function to search using a pre-computed
    query vector instead of text. This is useful when you already have vector representations
    (e.g., pre-generated through AI_EMBED) and want to avoid repeated embedding operations.

    The table must have a hybrid vector index (semantic index) created on the target column.

    Args:
        table_name: The name of the table to search. Example: "items"
        column_name: The column with the semantic index. Example: "doc"
        query_vector: The pre-computed query vector for similarity search.
                      Example: [0.1, 0.2, 0.3, ...] (must match the index dimension)
        limit: Maximum number of results to return. Default is 10.
        select_columns: List of columns to include in results. If None, includes all columns.

    Returns:
        A JSON string containing the search results ordered by vector similarity.

    Examples:
        - Search with pre-computed vector:
          query_vec = ai_embed("ob_embed", "flower")  # Get vector first
          semantic_vector_search("items", "doc", query_vec, limit=3)

        - Search with specific columns:
          semantic_vector_search("articles", "content", embedding_vector,
                                select_columns=["id", "title"])
    """
    logger.info(f"Calling tool: semantic_vector_search with arguments: table_name={table_name}")
    result = {"table_name": table_name, "success": False, "data": None, "error": None}

    try:
        # Convert query_vector to string format
        vector_str = "[" + ",".join([str(v) for v in query_vector]) + "]"

        # Build SELECT clause
        if select_columns:
            select_clause = ", ".join(select_columns)
        else:
            select_clause = "*"

        # Build the semantic vector search SQL using semantic_vector_distance function
        sql = f"""SELECT {select_clause} FROM {table_name}
ORDER BY semantic_vector_distance({column_name}, '{vector_str}') 
APPROXIMATE LIMIT {limit}"""

        logger.info(f"Executing semantic vector search query")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["data"] = sql_result.get("data")
        result["error"] = sql_result.get("error")

        if result["success"]:
            result["message"] = (
                f"Semantic vector search returned {len(result['data']) if result['data'] else 0} result(s)"
            )
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to perform semantic vector search: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


@app.tool()
def ai_prompt(template: str, args: list[str]) -> str:
    """
    Construct and format prompts using AI_PROMPT function in seekdb.

    AI_PROMPT is used to construct and format prompts, supporting dynamic data insertion.
    It organizes the template string and dynamic data into JSON format, which can be used
    directly in the AI_COMPLETE function to replace the prompt parameter.

    The template can contain placeholders like {0}, {1}, etc., which correspond by index
    to the data in the args array and will be automatically replaced when used with AI_COMPLETE.

    Args:
        template: The prompt template with placeholders. Use {0}, {1}, etc. for dynamic data.
                  Example: "Recommend {0} of the most popular {1} to me."
        args: A list of arguments to fill in the template placeholders.
              Example: ["ten", "mobile phones"]

    Returns:
        A JSON string containing the formatted prompt result in the format:
        {
            "template": "...",
            "args": ["...", "..."]
        }

    Examples:
        - Simple template with arguments:
          ai_prompt("Recommend {0} of the most popular {1} to me.", ["ten", "mobile phones"])
          Returns: {"template": "Recommend {0} of the most popular {1} to me.", "args": ["ten", "mobile phones"]}

        - Sentiment analysis template:
          ai_prompt("Analyze the sentiment of this text: {0}. Output 1 for positive, -1 for negative.",
                    ["What a beautiful day!"])

        - Translation template:
          ai_prompt("Translate the following {0} text to {1}: {2}",
                    ["English", "Chinese", "Hello world"])

        - Classification template:
          ai_prompt("Classify this issue into {0}: {1}",
                    ["Hardware, Software, or Other", "The screen is flickering"])
    """
    logger.info(f"Calling tool: ai_prompt with template and {len(args)} arguments")
    result = {"success": False, "data": None, "error": None}

    try:
        # Escape single quotes in template
        escaped_template = template.replace("'", "''")

        # Build the args string for SQL
        if args:
            escaped_args = [arg.replace("'", "''") for arg in args]
            args_str = ", ".join([f"'{arg}'" for arg in escaped_args])
            sql = f"SELECT AI_PROMPT('{escaped_template}', {args_str}) AS prompt_result"
        else:
            # If no args, just use the template
            sql = f"SELECT AI_PROMPT('{escaped_template}') AS prompt_result"

        logger.info(f"Executing AI_PROMPT query")

        # Reuse execute_sql method
        sql_result = json.loads(execute_sql(sql))

        result["success"] = sql_result["success"]
        result["error"] = sql_result.get("error")

        if result["success"] and sql_result.get("data"):
            # Extract the prompt result from the query result
            result["data"] = sql_result["data"][0][0] if sql_result["data"] else None
            result["message"] = "AI prompt constructed successfully"
    except Exception as e:
        result["error"] = f"[Exception]: {e}"
        logger.error(f"Failed to execute AI prompt: {e}")

    json_result = json.dumps(result, ensure_ascii=False)
    return json_result


def main():
    """Main entry point to run the MCP server."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        help="Specify the MCP server transport type as stdio or sse or streamable-http.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    args = parser.parse_args()
    transport = args.transport
    logger.info(f"Starting OceanBase MCP server with {transport} mode...")
    if transport in {"sse", "streamable-http"}:
        app.settings.host = args.host
        app.settings.port = args.port
    app.run(transport=transport)


if __name__ == "__main__":
    main()
