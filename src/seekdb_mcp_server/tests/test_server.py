import csv
import json
import os
import tempfile

import pytest

from seekdb_mcp.server import (
    add_data_to_collection,
    ai_complete,
    ai_rerank,
    create_ai_model,
    create_ai_model_endpoint,
    create_collection,
    delete_collection,
    delete_documents,
    drop_ai_model,
    drop_ai_model_endpoint,
    execute_sql,
    export_csv_file_from_seekdb,
    get_ai_model_endpoints,
    get_current_time,
    get_registered_ai_models,
    hybrid_search,
    import_csv_file_to_seekdb,
    list_collections,
    query_collection,
    full_text_search,
    has_collection,
    seekdb_memory_insert,
    seekdb_memory_query,
    seekdb_memory_delete,
    seekdb_memory_update,
    update_collection,
    seekdb_memory_collection_name,
    client,
)


@pytest.fixture
def test_collection():
    """Fixture that creates a collection before test and deletes it after."""
    collection_name = "test_collection"
    create_collection(collection_name)
    yield collection_name
    delete_collection(collection_name)


@pytest.fixture
def test_ai_model():
    """Fixture that creates an AI embedding model before test and drops it after."""
    model_name = "seekdb_embed"
    model_type = "dense_embedding"
    provider_model_name = "BAAI/bge-m3"
    create_ai_model(
        model_name=model_name, model_type=model_type, provider_model_name=provider_model_name
    )
    yield model_name
    drop_ai_model(model_name)


@pytest.fixture
def test_ai_model_endpoint(test_ai_model):
    """Fixture that creates an AI model endpoint before test and drops it after.

    Depends on test_ai_model fixture to ensure the AI model exists first.
    """
    endpoint_name = "seekdb_embed_endpoint"
    url = "https://api.siliconflow.cn/v1/embeddings"
    access_key = os.getenv("siliconflow_access_key")
    provider = "siliconflow"
    create_ai_model_endpoint(
        endpoint_name=endpoint_name,
        ai_model_name=test_ai_model,
        url=url,
        access_key=access_key,
        provider=provider,
    )
    yield endpoint_name
    drop_ai_model_endpoint(endpoint_name)


@pytest.fixture
def test_memory():
    create_collection(seekdb_memory_collection_name)
    yield
    delete_collection(seekdb_memory_collection_name)


@pytest.fixture
def student_csv_file():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "student.csv")
        # Write CSV content
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "age"])
            writer.writerow(["张三", "20"])
            writer.writerow(["李四", "21"])
        yield file_path
        # Cleanup: drop the table if it exists
        table_name = "student"
        drop_sql = f"DROP TABLE IF EXISTS `{table_name}`"
        execute_sql(drop_sql)


@pytest.fixture
def documents_csv_file():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "documents.csv")
        # Write CSV content
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["document", "category"])
            writer.writerow(["Machine learning is a subset of artificial intelligence", "AI"])
            writer.writerow(["Vector databases enable semantic search", "Database"])
        yield file_path
        # Cleanup: delete the collection if it exists
        collection_name = "documents"
        delete_collection(collection_name)


def test_execute_sql():
    sql = "select 1"
    result = execute_sql(sql)
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    assert result_dict["data"] == [["1"]], f"Expected [['1']], got {result_dict['data']}"


def test_get_current_time():
    result = get_current_time()
    print(result)
    result_dict = json.loads(result)
    assert result_dict["success"] is True


def test_create_collection():
    collection_name = "test_collection"
    result = create_collection(collection_name)
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    delete_collection(collection_name)


def test_has_collection(test_collection):
    # Test that collection exists
    result = has_collection(test_collection)
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    assert result_dict["exists"] is True, (
        f"Expected 'exists' to be True, got {result_dict['exists']}"
    )


def test_list_collection(test_collection):
    result = list_collections()
    result_dict = json.loads(result)

    assert result_dict["success"] is True
    assert test_collection in result_dict["collections"], (
        f"Expected '{test_collection}' in collections, got {result_dict['collections']}"
    )


def test_add_data_to_collection(test_collection):
    ids = ["1", "2"]
    documents = ["I love apple", "I love pear"]
    metadatas = [{"category": "preference", "index": 0}, {"category": "preference", "index": 1}]
    result = add_data_to_collection(
        collection_name=test_collection, ids=ids, documents=documents, metadatas=metadatas
    )
    result_dict = json.loads(result)
    assert result_dict["success"] is True


def test_delete_documents(test_collection):
    test_add_data_to_collection(test_collection)
    where_document = {"$contains": "apple"}
    result = delete_documents(collection_name=test_collection, where_document=where_document)
    result_dict = json.loads(result)
    assert result_dict["success"] is True, (
        f"Expected delete_documents to succeed, got {result_dict}"
    )

    query_result = query_collection(
        collection_name=test_collection, query_texts=["apple"], n_results=10
    )
    query_result_dict = json.loads(query_result)
    # Verify "I love apple" is not in the returned documents
    returned_documents = query_result_dict["data"]["documents"]
    all_docs = [doc for docs in returned_documents for doc in docs]
    assert "I love apple" not in all_docs, (
        f"Expected 'I love apple' to be deleted, but found it in {all_docs}"
    )


def test_query_collection(test_collection):
    # Add data first
    test_add_data_to_collection(test_collection)
    query_texts = ["pear"]
    result = query_collection(collection_name=test_collection, query_texts=query_texts, n_results=1)
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    # Check if the returned documents contain "pear"
    documents = result_dict["data"]["documents"]
    assert any("pear" in doc for docs in documents for doc in docs), (
        f"Expected 'pear' in documents, got {documents}"
    )


def test_update_collection(test_collection):
    test_add_data_to_collection(test_collection)
    ids = ["1"]
    documents = ["I love banana"]
    result = update_collection(collection_name=test_collection, ids=ids, documents=documents)
    result_dict = json.loads(result)
    assert result_dict["success"] is True, (
        f"Expected update_collection to succeed, got {result_dict}"
    )

    # Query to verify document with id=1 has been updated to "I love banana"
    query_result = query_collection(
        collection_name=test_collection, query_texts=["banana"], n_results=1
    )
    query_result_dict = json.loads(query_result)
    returned_documents = query_result_dict["data"]["documents"]
    assert returned_documents[0][0] == "I love banana", (
        f"Expected 'I love banana', got {returned_documents[0][0]}"
    )


def test_delete_collection():
    collection_name = "test_collection"
    result = delete_collection(collection_name)
    result_dict = json.loads(result)
    assert result_dict["success"] is True


def test_full_text_search():
    drop_table = "drop table if exists sport_data_whole"
    execute_sql(drop_table)
    create_table = """
    CREATE TABLE if not exists sport_data_whole (
    event VARCHAR(64),
    date VARCHAR(20),
    news VARCHAR(65535),
    FULLTEXT INDEX ft_idx1_news(news)
        WITH PARSER ik PARSER_PROPERTIES = (ik_mode = "max_word")
)
    """
    execute_sql(create_table)
    insert_data = """insert into sport_data_whole values 
    ('世界杯','2025-12-11 16:00:00','格策 黄牌 冠军 乌龙球 博阿滕 比赛 观众 球员'),
    ('足球赛','2025-12-11 15:00:00','逆转 博阿滕 犯规 黄牌 进球 球员 精彩 精彩'),
    ('奥运会','2025-12-11 15:17:00','逆转 红牌 红牌 犯规 逆转 比赛 观众 观众')
    """
    execute_sql(insert_data)
    table_name = "sport_data_whole"
    column_name = "news"
    search_expr = "+黄牌 +进球"
    result = full_text_search(
        table_name=table_name, column_name=column_name, search_expr=search_expr
    )
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    assert result_dict["data"][0][2] == "逆转 博阿滕 犯规 黄牌 进球 球员 精彩 精彩", (
        f"Expected '逆转 博阿滕 犯规 黄牌 进球 球员 精彩 精彩', got {result_dict['data'][0][2]}"
    )
    drop_table = "drop table if exists sport_data_whole"
    execute_sql(drop_table)


def test_hybrid_search(test_collection):
    documents = [
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language",
        "Vector databases enable semantic search",
        "Neural networks are inspired by the human brain",
        "Natural language processing helps computers understand text",
    ]
    ids = ["id1", "id2", "id3", "id4", "id5"]
    metadatas = [
        {"category": "AI", "index": 0, "year": 2021},
        {"category": "Programming", "index": 1, "year": 2018},
        {"category": "Database", "index": 2, "year": 2027},
        {"category": "AI", "index": 3, "year": 2019},
        {"category": "NLP", "index": 4, "year": 2016},
    ]
    add_data_to_collection(
        collection_name=test_collection, ids=ids, documents=documents, metadatas=metadatas
    )
    fulltext_search_keyword = "machine learning"
    fulltext_where = {"category": {"$eq": "AI"}}
    knn_query_texts = ["AI research"]
    knn_where = {"year": {"$gte": 2020}}
    result = hybrid_search(
        collection_name=test_collection,
        fulltext_search_keyword=fulltext_search_keyword,
        fulltext_where=fulltext_where,
        knn_query_texts=knn_query_texts,
        knn_where=knn_where,
    )
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    assert result_dict["data"]["ids"][0] == ["id1", "id3"], (
        f"Expected ['id1', 'id3'], got {result_dict['data']['ids'][0]}"
    )


def test_create_ai_model():
    model_name = "seekdb_embed"
    model_type = "dense_embedding"
    provider_model_name = "BAAI/bge-m3"
    result = create_ai_model(
        model_name=model_name, model_type=model_type, provider_model_name=provider_model_name
    )
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    drop_ai_model(model_name)


def test_drop_ai_model():
    model_name = "seekdb_embed"
    result = drop_ai_model(model_name)
    result_dict = json.loads(result)
    assert result_dict["success"] is True


def test_create_ai_model_endpoint(test_ai_model):
    endpoint_name = "seekdb_embed_endpoint"
    url = "https://api.siliconflow.cn/v1/embeddings"
    access_key = os.getenv("siliconflow_access_key")
    provider = "siliconflow"
    result = create_ai_model_endpoint(
        endpoint_name=endpoint_name,
        ai_model_name=test_ai_model,
        url=url,
        access_key=access_key,
        provider=provider,
    )
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    drop_ai_model_endpoint(endpoint_name)


def test_drop_ai_model_endpoint():
    endpoint_name = "seekdb_embed_endpoint"
    result = drop_ai_model_endpoint(endpoint_name)
    result_dict = json.loads(result)
    assert result_dict["success"] is True


def test_ai_complete():
    model_name = "seekdb_complete"
    model_type = "completion"
    provider_model_name = "THUDM/GLM-4-9B-0414"
    create_ai_model(
        model_name=model_name, model_type=model_type, provider_model_name=provider_model_name
    )
    endpoint_name = "seekdb_complete_endpoint"
    url = "https://api.siliconflow.cn/v1/chat/completions"
    access_key = os.getenv("siliconflow_access_key")
    provider = "siliconflow"
    create_ai_model_endpoint(
        endpoint_name=endpoint_name,
        ai_model_name=model_name,
        url=url,
        access_key=access_key,
        provider=provider,
    )
    prompt = "Translate 'Hello World' to Chinese"
    result = ai_complete(model_name, prompt)
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    response_text = result_dict["response"]
    assert "你好" in response_text and "世界" in response_text, (
        f"Expected '你好，世界' in response, got {response_text}"
    )


def test_ai_rerank():
    model_name = "seekdb_rerank"
    model_type = "rerank"
    provider_model_name = "BAAI/bge-reranker-v2-m3"
    create_ai_model(
        model_name=model_name, model_type=model_type, provider_model_name=provider_model_name
    )
    endpoint_name = "seekdb_rerank_endpoint"
    url = "https://api.siliconflow.cn/v1/rerank"
    access_key = os.getenv("siliconflow_access_key")
    provider = "siliconflow"
    create_ai_model_endpoint(
        endpoint_name=endpoint_name,
        ai_model_name=model_name,
        url=url,
        access_key=access_key,
        provider=provider,
    )
    query = "Apple"
    documents = ["vegetable", "fruit", "banana", "apple"]
    result = ai_rerank(model_name, query, documents)
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    assert result_dict["reranked_documents"] == ["apple", "banana", "fruit", "vegetable"], (
        f"Expected ['apple', 'banana', 'fruit', 'vegetable'], got {result_dict['reranked_documents']}"
    )


def test_get_registered_ai_model(test_ai_model):
    result = get_registered_ai_models()
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    # Check that seekdb_embed is in the returned models
    model_names = [model["NAME"] for model in result_dict["models"]]
    assert test_ai_model in model_names, (
        f"Expected 'seekdb_embed' in model names, got {model_names}"
    )


def test_get_ai_model_endpoints(test_ai_model_endpoint):
    result = get_ai_model_endpoints()
    result_dict = json.loads(result)
    assert result_dict["success"] is True
    # Check that the endpoint we created is in the returned list
    endpoint_names = [endpoint["ENDPOINT_NAME"] for endpoint in result_dict["endpoints"]]
    assert test_ai_model_endpoint in endpoint_names, (
        f"Expected '{test_ai_model_endpoint}' in endpoint names, got {endpoint_names}"
    )


def test_seekdb_memory_insert_and_query(test_memory):
    content = "I love apple"
    meta = {}

    # Insert the memory
    insert_result = seekdb_memory_insert(content=content, meta=meta)
    insert_result_dict = json.loads(insert_result)
    assert insert_result_dict["success"] is True, (
        f"Expected insert to succeed, got {insert_result_dict}"
    )

    # Query to verify insertion
    query_result = seekdb_memory_query(query="apple", topk=5)
    query_result_dict = json.loads(query_result)

    # Find the memory we just inserted
    memories = query_result_dict["memories"]
    matching_memories = [m for m in memories if m["content"] == content]
    assert len(matching_memories) > 0, f"Expected to find '{content}' in memories, got {memories}"


def test_seekdb_memory_update(test_memory):
    content = "I love apple"
    meta = {}

    # Insert the memory
    insert_result = seekdb_memory_insert(content=content, meta=meta)
    insert_result_dict = json.loads(insert_result)
    assert insert_result_dict["success"] is True, (
        f"Expected insert to succeed, got {insert_result_dict}"
    )

    # Query to verify insertion
    query_result = seekdb_memory_query(query="apple", topk=5)
    query_result_dict = json.loads(query_result)

    # Find the memory we just inserted
    memories = query_result_dict["memories"]
    matching_memories = [m for m in memories if m["content"] == content]
    assert len(matching_memories) > 0, f"Expected to find '{content}' in memories, got {memories}"

    # Get the mem_id of the memory we want to update
    mem_id = matching_memories[0]["mem_id"]

    # Update the memory content
    new_content = "I love pear"
    update_result = seekdb_memory_update(mem_id=mem_id, content=new_content, meta=meta)
    update_result_dict = json.loads(update_result)
    assert update_result_dict["success"] is True, (
        f"Expected update to succeed, got {update_result_dict}"
    )

    # Query to verify update
    query_result_after_update = seekdb_memory_query(query="pear", topk=5)
    query_result_after_update_dict = json.loads(query_result_after_update)

    # Verify the memory was updated - same mem_id should now have new content
    memories_after_update = query_result_after_update_dict["memories"]
    matching_updated_memories = [m for m in memories_after_update if m["content"] == new_content]
    # Verify it's the same memory record (same mem_id)
    assert matching_updated_memories[0]["mem_id"] == mem_id, (
        f"Expected mem_id to be '{mem_id}', got '{matching_updated_memories[0]['mem_id']}'"
    )


def test_seekdb_memory_delete(test_memory):
    content = "I love apple"
    meta = {}

    # Insert the memory
    insert_result = seekdb_memory_insert(content=content, meta=meta)
    insert_result_dict = json.loads(insert_result)
    assert insert_result_dict["success"] is True, (
        f"Expected insert to succeed, got {insert_result_dict}"
    )

    # Query to verify insertion
    query_result = seekdb_memory_query(query="apple", topk=5)
    query_result_dict = json.loads(query_result)

    # Find the memory we just inserted
    memories = query_result_dict["memories"]
    matching_memories = [m for m in memories if m["content"] == content]
    assert len(matching_memories) > 0, f"Expected to find '{content}' in memories, got {memories}"

    # Get the mem_id of the memory we want to delete
    mem_id = matching_memories[0]["mem_id"]

    # Delete the memory
    delete_result = seekdb_memory_delete(mem_id=mem_id)
    delete_result_dict = json.loads(delete_result)
    assert delete_result_dict["success"] is True, (
        f"Expected delete to succeed, got {delete_result_dict}"
    )

    # Query to verify deletion
    query_result_after_delete = seekdb_memory_query(query="apple", topk=5)
    query_result_after_delete_dict = json.loads(query_result_after_delete)

    # Verify the memory was deleted - same mem_id should no longer exist
    memories_after_delete = query_result_after_delete_dict["memories"]
    matching_deleted_memories = [m for m in memories_after_delete if m["mem_id"] == mem_id]
    assert len(matching_deleted_memories) == 0, (
        f"Expected mem_id '{mem_id}' to be deleted, but still found it in memories: {memories_after_delete}"
    )


def test_import_csv_file_to_seekdb_without_vector(student_csv_file):
    file_path = student_csv_file
    table_name = os.path.splitext(os.path.basename(file_path))[0]

    # Import CSV file to seekdb (without vector)
    result = import_csv_file_to_seekdb(file_path)
    result_dict = json.loads(result)
    assert result_dict["success"] is True, f"Expected import to succeed, got {result_dict}"

    # Verify table exists by querying it
    check_table_sql = f"SELECT 1 FROM `{table_name}` LIMIT 1"
    check_result = execute_sql(check_table_sql)
    check_result_dict = json.loads(check_result)
    assert check_result_dict["success"] is True, (
        f"Expected table '{table_name}' to exist, but query failed: {check_result_dict}"
    )

    # Query all data from the table
    query_sql = f"SELECT name, age FROM `{table_name}` ORDER BY age"
    query_result = execute_sql(query_sql)
    query_result_dict = json.loads(query_result)
    assert query_result_dict["success"] is True, (
        f"Expected query to succeed, got {query_result_dict}"
    )

    # Verify the data
    data = query_result_dict["data"]
    assert len(data) == 2, f"Expected 2 rows, got {len(data)}"

    # Check first row: 张三, 20
    assert data[0][0] == "张三", f"Expected first row name to be '张三', got '{data[0][0]}'"
    assert data[0][1] == "20", f"Expected first row age to be '20', got '{data[0][1]}'"

    # Check second row: 李四, 21
    assert data[1][0] == "李四", f"Expected second row name to be '李四', got '{data[1][0]}'"
    assert data[1][1] == "21", f"Expected second row age to be '21', got '{data[1][1]}'"


def test_import_csv_file_to_seekdb_with_vector(documents_csv_file):
    file_path = documents_csv_file
    collection_name = os.path.splitext(os.path.basename(file_path))[0]

    # Import CSV file to seekdb (with vector)
    result = import_csv_file_to_seekdb(file_path, 1)
    result_dict = json.loads(result)
    assert result_dict["success"] is True, f"Expected import to succeed, got {result_dict}"

    # Verify the 'documents' collection exists
    has_result = has_collection(collection_name)
    has_result_dict = json.loads(has_result)
    assert has_result_dict["success"] is True
    assert has_result_dict["exists"] is True, (
        f"Expected collection '{collection_name}' to exist, got {has_result_dict}"
    )

    # Query the collection and verify the content matches documents.csv
    # CSV content:
    # document,category
    # Machine learning is a subset of artificial intelligence,AI
    # Vector databases enable semantic search,Database

    # Query for "Machine learning"
    query_result1 = query_collection(
        collection_name=collection_name, query_texts=["Machine learning"], n_results=2
    )
    query_result1_dict = json.loads(query_result1)
    assert query_result1_dict["success"] is True, (
        f"Expected query to succeed, got {query_result1_dict}"
    )

    # Verify the documents contain expected content
    documents = query_result1_dict["data"]["documents"]
    all_docs = [doc for docs in documents for doc in docs]
    assert any("Machine learning is a subset of artificial intelligence" in doc for doc in all_docs), (
        f"Expected 'Machine learning is a subset of artificial intelligence' in documents, got {all_docs}"
    )
    assert any("Vector databases enable semantic search" in doc for doc in all_docs), (
        f"Expected 'Vector databases enable semantic search' in documents, got {all_docs}"
    )

    # Verify metadatas contain the category information
    metadatas = query_result1_dict["data"]["metadatas"]
    all_metadatas = [m for metas in metadatas for m in metas]
    categories = [m.get("category") for m in all_metadatas if m.get("category")]
    assert "AI" in categories, f"Expected 'AI' in categories, got {categories}"
    assert "Database" in categories, f"Expected 'Database' in categories, got {categories}"

def test_export_csv_file_from_seekdb_with_table(student_csv_file):
    file_path_input = student_csv_file
    table_name = os.path.splitext(os.path.basename(file_path_input))[0]

    # Create output file in the same temp directory
    output_dir = os.path.dirname(file_path_input)
    file_path_output = os.path.join(output_dir, "student-output.csv")

    # Import CSV file to seekdb
    import_result = import_csv_file_to_seekdb(file_path_input)
    import_result_dict = json.loads(import_result)
    assert import_result_dict["success"] is True, f"Expected import to succeed, got {import_result_dict}"

    # Export data from seekdb to CSV file
    export_result = export_csv_file_from_seekdb(table_name, file_path_output)
    export_result_dict = json.loads(export_result)
    assert export_result_dict["success"] is True, f"Expected export to succeed, got {export_result_dict}"

    # Read input CSV file
    with open(file_path_input, 'r', encoding='utf-8') as f:
        input_reader = csv.reader(f)
        input_rows = list(input_reader)

    # Read output CSV file
    with open(file_path_output, 'r', encoding='utf-8') as f:
        output_reader = csv.reader(f)
        output_rows = list(output_reader)

    # Verify headers are the same
    assert input_rows[0] == output_rows[0], (
        f"Expected headers to match. Input: {input_rows[0]}, Output: {output_rows[0]}"
    )

    # Verify row count is the same (excluding header)
    assert len(input_rows) == len(output_rows), (
        f"Expected same number of rows. Input: {len(input_rows)}, Output: {len(output_rows)}"
    )

    # Verify data rows match (compare as sets to handle potential order differences)
    input_data = set(tuple(row) for row in input_rows[1:])
    output_data = set(tuple(row) for row in output_rows[1:])
    assert input_data == output_data, (
        f"Expected data to match. Input: {input_data}, Output: {output_data}"
    )


def test_export_csv_file_from_seekdb_with_collection(documents_csv_file):
    file_path_input = documents_csv_file
    collection_name = os.path.splitext(os.path.basename(file_path_input))[0]

    # Create output file in the same temp directory
    output_dir = os.path.dirname(file_path_input)
    file_path_output = os.path.join(output_dir, "documents-output.csv")

    # Import CSV file to seekdb as collection (with vector)
    import_result = import_csv_file_to_seekdb(file_path_input, 1)
    import_result_dict = json.loads(import_result)
    assert import_result_dict["success"] is True, f"Expected import to succeed, got {import_result_dict}"

    # Export data from seekdb collection to CSV file
    export_result = export_csv_file_from_seekdb(collection_name, file_path_output)
    export_result_dict = json.loads(export_result)
    assert export_result_dict["success"] is True, f"Expected export to succeed, got {export_result_dict}"

    # Read input CSV file
    with open(file_path_input, 'r', encoding='utf-8') as f:
        input_reader = csv.reader(f)
        input_rows = list(input_reader)

    # Read output CSV file
    with open(file_path_output, 'r', encoding='utf-8') as f:
        output_reader = csv.reader(f)
        output_rows = list(output_reader)

    # Verify headers are the same
    assert input_rows[0] == output_rows[0], (
        f"Expected headers to match. Input: {input_rows[0]}, Output: {output_rows[0]}"
    )

    # Verify row count is the same (excluding header)
    assert len(input_rows) == len(output_rows), (
        f"Expected same number of rows. Input: {len(input_rows)}, Output: {len(output_rows)}"
    )

    # Verify data rows match (compare as sets to handle potential order differences)
    input_data = set(tuple(row) for row in input_rows[1:])
    output_data = set(tuple(row) for row in output_rows[1:])
    assert input_data == output_data, (
        f"Expected data to match. Input: {input_data}, Output: {output_data}"
    )