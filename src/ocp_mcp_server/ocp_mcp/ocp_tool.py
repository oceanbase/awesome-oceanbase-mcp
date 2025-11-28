"""OCP API tool wrapper module"""

import logging
from typing import Any, Dict, List, Optional

from .config import get_config
from .ocp_client import OCPClient

logger = logging.getLogger(__name__)

_ocp_client: Optional[OCPClient] = None


def get_ocp_client() -> OCPClient:
    """Lazily initialize and return the shared OCP client."""
    global _ocp_client
    if _ocp_client is None:
        config = get_config()
        _ocp_client = OCPClient(
            host=config.ocp_url,
            access_key_id=config.ocp_access_key_id,
            access_key_secret=config.ocp_access_key_secret,
        )
    return _ocp_client


def get_clusters(
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        # Build query parameters
        params = {"page": str(page), "size": str(size)}

        if sort:
            params["sort"] = sort
        if name:
            params["name"] = name
        if status and len(status) > 0:
            params["status"] = status

        logger.debug(f"Query parameters: {params}")
        result = get_ocp_client().get("/api/v2/ob/clusters", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to list OceanBase clusters: {e}")
        raise


def get_cluster_zones(cluster_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/ob/clusters/{cluster_id}/zones")
        return result
    except Exception as e:
        logger.error(f"Failed to get zones for cluster {cluster_id}: {e}")
        raise


def get_cluster_servers(
    cluster_id: int,
    region_name: Optional[str] = None,
    idc_name: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {}
        if region_name:
            params["regionName"] = region_name
        if idc_name:
            params["idcName"] = idc_name

        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/servers",
            params=params if params else None,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get servers for cluster {cluster_id}: {e}")
        raise


def get_zone_servers(
    cluster_id: int,
    zone_name: str,
) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/zones/{zone_name}/servers"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get servers for cluster {cluster_id} zone {zone_name}: {e}"
        )
        raise


def get_cluster_stats(cluster_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/ob/clusters/{cluster_id}/stats")
        return result
    except Exception as e:
        logger.error(f"Failed to get stats for cluster {cluster_id}: {e}")
        raise


def get_cluster_server_stats(cluster_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/ob/clusters/{cluster_id}/serverStats")
        return result
    except Exception as e:
        logger.error(f"Failed to get server stats for cluster {cluster_id}: {e}")
        raise


def get_cluster_units(cluster_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/ob/clusters/{cluster_id}/units")
        return result
    except Exception as e:
        logger.error(f"Failed to get units for cluster {cluster_id}: {e}")
        raise


def get_cluster_tenants(
    cluster_id: int,
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    mode: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {"page": str(page), "size": str(size)}

        if sort:
            params["sort"] = sort
        if name:
            params["name"] = name
        if mode:
            params["mode"] = mode
        if status:
            params["status"] = status

        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants", params=params
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get tenants for cluster {cluster_id}: {e}")
        raise


def get_all_tenants(
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    mode: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {"page": str(page), "size": str(size)}

        if sort:
            params["sort"] = sort
        if name:
            params["name"] = name
        if mode:
            params["mode"] = mode
        if status:
            params["status"] = status

        result = get_ocp_client().get("/api/v2/ob/tenants", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get all tenants: {e}")
        raise


def get_tenant_detail(cluster_id: int, tenant_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get tenant detail for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def get_tenant_units(
    cluster_id: int,
    tenant_id: int,
    zone_name: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {}
        if zone_name:
            params["zoneName"] = zone_name

        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/units",
            params=params if params else None,
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get units for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def get_tenant_parameters(cluster_id: int, tenant_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/parameters"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get parameters for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def get_cluster_parameters(cluster_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/ob/clusters/{cluster_id}/parameters")
        return result
    except Exception as e:
        logger.error(f"Failed to get parameters for cluster {cluster_id}: {e}")
        raise


def set_tenant_parameters(
    cluster_id: int,
    tenant_id: int,
    parameters: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not parameters:
        raise ValueError("parameters list cannot be empty")

    payload: List[Dict[str, Any]] = []
    for index, param in enumerate(parameters):
        if "name" not in param or not param["name"]:
            raise ValueError(f"parameters[{index}] is missing required field 'name'")
        if "value" not in param:
            raise ValueError(f"parameters[{index}] is missing required field 'value'")
        if "parameterType" not in param or not param["parameterType"]:
            raise ValueError(
                f"parameters[{index}] is missing required field 'parameterType'"
            )

        payload.append(
            {
                "name": str(param["name"]),
                "value": param["value"],
                "parameterType": str(param["parameterType"]),
            }
        )

    try:
        result = get_ocp_client().put(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/parameters",
            json=payload,
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to set parameters for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def set_cluster_parameters(
    cluster_id: int,
    parameters: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not parameters:
        raise ValueError("parameters list cannot be empty")

    payload: List[Dict[str, Any]] = []
    for index, param in enumerate(parameters):
        if "name" not in param or not param["name"]:
            raise ValueError(f"parameters[{index}] is missing required field 'name'")
        if "value" not in param:
            raise ValueError(f"parameters[{index}] is missing required field 'value'")

        payload.append(
            {
                "name": str(param["name"]),
                "value": param["value"],
            }
        )

    try:
        result = get_ocp_client().put(
            f"/api/v2/ob/clusters/{cluster_id}/parameters",
            json=payload,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to set parameters for cluster {cluster_id}: {e}")
        raise


def get_obproxy_clusters(
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    try:
        params = {"page": str(page), "size": str(size)}

        result = get_ocp_client().get("/api/v2/obproxy/clusters", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get OBProxy clusters: {e}")
        raise


def get_obproxy_cluster_detail(cluster_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/obproxy/clusters/{cluster_id}")
        return result
    except Exception as e:
        logger.error(
            f"Failed to get OBProxy cluster detail for cluster {cluster_id}: {e}"
        )
        raise


def get_obproxy_cluster_parameters(cluster_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/obproxy/clusters/{cluster_id}/parameters"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get parameters for OBProxy cluster {cluster_id}: {e}")
        raise


def get_tenant_databases(cluster_id: int, tenant_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/databases"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get databases for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def get_tenant_users(cluster_id: int, tenant_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/users"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get users for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def get_tenant_user_detail(
    cluster_id: int,
    tenant_id: int,
    username: str,
    host_name: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {}
        if host_name:
            params["hostName"] = host_name

        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/users/{username}",
            params=params if params else None,
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get user detail for cluster {cluster_id} tenant {tenant_id} user {username}: {e}"
        )
        raise


def get_tenant_roles(cluster_id: int, tenant_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/roles"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get roles for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def get_tenant_role_detail(
    cluster_id: int, tenant_id: int, role_name: str
) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/roles/{role_name}"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get role detail for cluster {cluster_id} tenant {tenant_id} role {role_name}: {e}"
        )
        raise


def get_tenant_objects(cluster_id: int, tenant_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/objects"
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get objects for cluster {cluster_id} tenant {tenant_id}: {e}"
        )
        raise


def get_metric_groups(
    type: str,
    scope: str,
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    target: Optional[str] = None,
    target_id: int = None,
) -> Dict[str, Any]:
    try:
        params = {"type": type, "scope": scope, "page": str(page), "size": str(size)}

        if sort:
            params["sort"] = sort
        if target:
            params["target"] = target
        if target_id is not None:
            params["targetId"] = target_id

        result = get_ocp_client().get("/api/v2/monitor/metricGroups", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get metric groups: {e}")
        raise


def get_metric_data_with_label(
    start_time: str,
    end_time: str,
    metrics: str,
    group_by: str,
    interval: int,
    labels: str,
    min_step: int = None,
    max_points: int = None,
) -> Dict[str, Any]:
    try:
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "metrics": metrics,
            "groupBy": group_by,
            "interval": str(interval),
            "labels": labels,
        }

        if min_step is not None:
            params["minStep"] = min_step
        if max_points is not None:
            params["maxPoints"] = max_points

        result = get_ocp_client().get("/api/v2/monitor/metricsWithLabel", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get metric data with label: {e}")
        raise


def get_alarms(
    page: int = 1,
    size: int = 10,
    app_type: Optional[str] = None,
    scope: Optional[str] = None,
    level: int = None,
    status: Optional[str] = None,
    active_at_start: str = None,
    active_at_end: str = None,
    is_subscribed_by_me: bool = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {"page": str(page), "size": str(size)}

        if app_type:
            params["appType"] = app_type
        if scope:
            params["scope"] = scope
        if level is not None:
            params["level"] = level
        if status:
            params["status"] = status
        if active_at_start:
            params["activeAtStart"] = active_at_start
        if active_at_end:
            params["activeAtEnd"] = active_at_end
        if is_subscribed_by_me is not None:
            params["isSubscribedByMe"] = str(is_subscribed_by_me).lower()
        if keyword:
            params["keyword"] = keyword

        result = get_ocp_client().get("/api/v2/alarm/alarms", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get alarms: {e}")
        raise


def get_alarm_detail(alarm_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/alarm/alarms/{alarm_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get alarm {alarm_id}: {e}")
        raise


def get_inspection_tasks(
    inspectionObjectTypes: Optional[str] = None,
    tags: Optional[str] = None,
    taskStates: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {}

        if inspectionObjectTypes:
            params["inspectionObjectTypes"] = inspectionObjectTypes
        if tags:
            params["tags"] = tags
        if taskStates:
            params["taskStates"] = taskStates
        if name:
            params["name"] = name

        result = get_ocp_client().get(
            "/api/v2/inspection/task", params=params if params else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection tasks: {e}")
        raise


def get_inspection_overview(
    object_ids: str = None,
    inspection_object_type: Optional[str] = None,
    schedule_states: Optional[str] = None,
    name: Optional[str] = None,
    parent_name: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {}

        if object_ids:
            params["objectIds"] = object_ids
        if inspection_object_type:
            params["inspectionObjectType"] = inspection_object_type
        if schedule_states:
            params["scheduleStates"] = schedule_states
        if name:
            params["name"] = name
        if parent_name:
            params["parentName"] = parent_name

        result = get_ocp_client().get(
            "/api/v2/inspection/overview", params=params if params else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection overview: {e}")
        raise


def get_inspection_report(report_id: int) -> Dict[str, Any]:
    try:
        result = get_ocp_client().get(f"/api/v2/inspection/report/{report_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection report {report_id}: {e}")
        raise


def run_inspection(
    inspection_object_type: str,
    object_ids: str,
    tag: int,
) -> Dict[str, Any]:
    if not inspection_object_type:
        raise ValueError("inspection_object_type is required")
    if not object_ids:
        raise ValueError("object_ids list cannot be empty")
    if not tag:
        raise ValueError("tags is required")

    # Validate inspection_object_type
    valid_types = ["OB_CLUSTER", "OB_TENANT", "HOST", "OB_PROXY"]
    if inspection_object_type not in valid_types:
        raise ValueError(f"inspection_object_type must be one of {valid_types}")

    # Validate tags
    valid_tags = [1, 2, 3, 4]
    if tag not in valid_tags:
        raise ValueError(f"tag must be one of {valid_tags}")

    try:
        params = {}

        if inspection_object_type is not None:
            params["inspectionObjectType"] = inspection_object_type
        if object_ids is not None:
            params["objectIds"] = object_ids
        if tag is not None:
            params["tag"] = tag
        result = get_ocp_client().post(
            "/api/v2/inspection/run", params=params if params else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to run inspection: {e}")
        raise


def get_inspection_item_last_result(
    item_id: int,
    tag_id: int,
    object_type: str,
    object_id: Optional[int] = None,
) -> Dict[str, Any]:
    if not item_id:
        raise ValueError("item_id is required")
    if not tag_id:
        raise ValueError("tag_id is required")
    if not object_type:
        raise ValueError("object_type is required")

    # Validate tag_id
    valid_tags = [1, 2, 3, 4]
    if tag_id not in valid_tags:
        raise ValueError(f"tag_id must be one of {valid_tags}")

    # Validate object_type
    valid_types = ["OB_CLUSTER", "OB_TENANT", "HOST", "OB_PROXY"]
    if object_type not in valid_types:
        raise ValueError(f"object_type must be one of {valid_types}")

    params = {
        "tagId": str(tag_id),
        "objectType": object_type,
    }

    if object_id is not None:
        params["objectId"] = str(object_id)

    try:
        result = get_ocp_client().get(
            f"/api/v2/inspection/report/info/item/{item_id}", params=params
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to get inspection item last result for item {item_id}: {e}"
        )
        raise


def get_inspection_report_info(
    tag_id: int,
    object_type: str,
    object_id: Optional[int] = None,
) -> Dict[str, Any]:
    if not tag_id:
        raise ValueError("tag_id is required")
    if not object_type:
        raise ValueError("object_type is required")

    # Validate tag_id
    valid_tags = [1, 2, 3, 4]
    if tag_id not in valid_tags:
        raise ValueError(f"tag_id must be one of {valid_tags}")

    # Validate object_type
    valid_types = ["OB_CLUSTER", "OB_TENANT", "HOST", "OB_PROXY"]
    if object_type not in valid_types:
        raise ValueError(f"object_type must be one of {valid_types}")

    params = {
        "tagId": str(tag_id),
        "objectType": object_type,
    }

    if object_id is not None:
        params["objectId"] = str(object_id)

    try:
        result = get_ocp_client().get("/api/v2/inspection/report/info", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection report info: {e}")
        raise


def get_tenant_top_sql(
    cluster_id: int,
    tenant_id: int,
    start_time: str,
    end_time: str,
    inner: bool = None,
    server_id: int = None,
    sql_text: Optional[str] = None,
    search_attr: Optional[str] = None,
    search_op: Optional[str] = None,
    search_val: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {
            "startTime": start_time,
            "endTime": end_time,
        }

        if server_id is not None:
            params["serverId"] = str(server_id)
        if inner is not None:
            params["inner"] = str(inner).lower()
        if sql_text:
            params["sqlText"] = sql_text
        if search_attr:
            params["searchAttr"] = search_attr
        if search_op:
            params["searchOp"] = search_op
        if search_val:
            params["searchVal"] = search_val

        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/topSql",
            params=params,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get tenant top SQL: {e}")
        raise


def get_sql_text(
    cluster_id: int,
    tenant_id: int,
    sql_id: str,
    start_time: str,
    end_time: str,
    db_name: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        params = {
            "startTime": start_time,
            "endTime": end_time,
        }

        if db_name is not None:
            params["dbName"] = db_name

        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/sqls/{sql_id}/text",
            params=params,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get SQL text: {e}")
        raise


def get_tenant_slow_sql(
    cluster_id: int,
    tenant_id: int,
    start_time: str,
    end_time: str,
    server_id: Optional[int] = None,
    inner: Optional[bool] = None,
    sql_text: Optional[str] = None,
    filter_expression: Optional[str] = None,
    limit: Optional[int] = None,
    sql_text_length: Optional[int] = None,
) -> Dict[str, Any]:
    try:
        params = {
            "startTime": start_time,
            "endTime": end_time,
        }

        if server_id is not None:
            params["serverId"] = str(server_id)
        if inner is not None:
            params["inner"] = str(inner).lower()
        if sql_text:
            params["sqlText"] = sql_text
        if filter_expression:
            params["filterExpression"] = filter_expression
        if limit is not None:
            params["limit"] = str(limit)
        if sql_text_length is not None:
            params["sqlTextLength"] = str(sql_text_length)

        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/slowSql",
            params=params,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get tenant slow SQL: {e}")
        raise


def create_performance_report(
    cluster_id: int,
    start_snapshot_id: int,
    end_snapshot_id: int,
    name: str,
) -> Dict[str, Any]:
    try:
        params = {}
        if name:
            params["name"] = name
        if start_snapshot_id is not None:
            params["startSnapshotId"] = str(start_snapshot_id)
        if end_snapshot_id is not None:
            params["endSnapshotId"] = str(end_snapshot_id)

        result = get_ocp_client().post(
            f"/api/v2/ob/clusters/{cluster_id}/performance/workload/reports",
            params=params if params else None,
        )

        return result
    except Exception as e:
        logger.error(f"Failed to create performance report: {e}")
        raise


def get_cluster_snapshots(cluster_id: int) -> Dict[str, Any]:
    """
    Query cluster snapshot information

    This interface is used to query snapshot information of a specified cluster.
    The caller must have read and write permissions for the specified cluster.

    Args:
        cluster_id: The ID of the target OceanBase cluster

    Returns:
        Dictionary containing snapshot list with snapshotId and snapshotTime
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/performance/workload/snapshots"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get snapshots for cluster {cluster_id}: {e}")
        raise


def get_performance_report(
    cluster_id: int,
    report_id: int,
    directory: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query performance report

    This interface is used to query cluster performance report.
    The caller must have read and write permissions for the specified cluster.

    Note: This endpoint returns binary HTML content that can be saved as an HTML file.

    Args:
        cluster_id: The ID of the target OceanBase cluster
        report_id: Performance report ID
        directory: The directory where the HTML report is saved (required), and the absolute path is not empty
    Returns:
        Binary HTML content
    """
    try:
        import base64

        # Add query parameters as required by the API (even though they're in the path)
        params = {
            "id": str(cluster_id),
            "reportId": str(report_id),
        }

        # Set Accept header to accept any content type (like browser does)
        headers = {
            "Accept": "*/*",
        }

        binary_content = get_ocp_client().get_binary(
            f"/api/v2/ob/clusters/{cluster_id}/performance/workload/reports/{report_id}",
            params=params,
            headers=headers,
        )

        # Encode binary content as base64 for JSON serialization
        content_base64 = base64.b64encode(binary_content).decode("utf-8")

        if content_base64:
            html_content = base64.b64decode(content_base64)
            output_file = (
                f"{directory}/performance_report_{cluster_id}_{report_id}.html"
            )
            with open(output_file, "wb") as f:
                f.write(html_content)
            print(f"✓ HTML report saved to: {output_file}")

        if output_file:
            return {
                "success": True,
                "cluster_id": cluster_id,
                "report_id": report_id,
                "output_file": output_file,
                "message": f"HTML report saved successfully to {output_file}",
            }
        else:
            return {
                "success": False,
                "cluster_id": cluster_id,
                "report_id": report_id,
                "message": f"Failed to get performance report {report_id} for cluster {cluster_id}",
            }

    except Exception as e:
        logger.error(
            f"Failed to get performance report {report_id} for cluster {cluster_id}: {e}"
        )
        raise
