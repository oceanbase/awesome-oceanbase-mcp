"""OCP MCP Server implementation."""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel
from .ocp_tool import *


logger = logging.getLogger(__name__)

# Initialize FastMCP app
app = FastMCP("ocp_mcp_server")


class SetClusterParameterParam(BaseModel):
    """Cluster parameter update payload."""
    name: str
    value: str


class SetTenantParameterParam(BaseModel):
    """Tenant parameter update payload."""
    name: str
    value: str
    parameterType: str  # OB_SYSTEM_VARIABLE or OB_TENANT_PARAMETER


@app.tool()
def list_oceanbase_clusters(
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List OceanBase clusters
    
    This interface is used to query OceanBase cluster information managed by OCP.
    You can limit the query scope by cluster name keywords, cluster status, and other conditions.
    In primary-standby deployment mode, the returned results include both primary and standby clusters.
    """
    return get_clusters(page, size, sort, name, status)


@app.tool()
def get_oceanbase_cluster_zones(cluster_id: int) -> Dict[str, Any]:
    """
    Get OceanBase cluster Zone list
    
    This interface is used to query the Zone list of an OceanBase cluster.
    
    Args:
        cluster_id: The ID of the OceanBase cluster to query Zone list
    
    Returns:
        Dictionary containing Zone list and pagination information
    """
    return get_cluster_zones(cluster_id)


@app.tool()
def get_oceanbase_cluster_servers(
    cluster_id: int,
    region_name: Optional[str] = None,
    idc_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get OceanBase cluster OBServer list
    
    This interface is used to query all OBServer node information of the target OceanBase cluster.
    The caller must have at least read-only permissions on the target OceanBase cluster.
    
    Args:
        cluster_id: The ID of the target cluster
        region_name: Query OceanBase servers in the specified region (optional)
        idc_name: Query OceanBase servers in the specified IDC (optional)
    
    Returns:
        Dictionary containing server information list
    """
    return get_cluster_servers(cluster_id, region_name, idc_name)


@app.tool()
def get_oceanbase_zone_servers(
    cluster_id: int,
    zone_name: str,
) -> Dict[str, Any]:
    """
    Get Zone OBServer list
    
    This interface is used to query OBServer node information under the specified Zone 
    in the target OceanBase cluster.
    The caller must have at least read-only permissions on the target OceanBase cluster.
    
    Args:
        cluster_id: The ID of the target cluster
        zone_name: The name of the Zone
    
    Returns:
        Dictionary containing server information list
    """
    return get_zone_servers(cluster_id, zone_name)


@app.tool()
def get_oceanbase_cluster_stats(cluster_id: int) -> Dict[str, Any]:
    """
    Get OceanBase cluster resource statistics
    
    This interface is used to get resource statistics information of an OceanBase cluster.
    The caller must be authenticated through OCP application service.
    
    Args:
        cluster_id: The ID of the cluster
    
    Returns:
        Dictionary containing ClusterResourceStats information
    """
    return get_cluster_stats(cluster_id)


@app.tool()
def get_oceanbase_cluster_server_stats(cluster_id: int) -> Dict[str, Any]:
    """
    Get resource statistics for all OBServers in the cluster
    
    This interface is used to get resource statistics information for all OBServers in the cluster.
    The caller must be authenticated through OCP application service.
    
    Args:
        cluster_id: The ID of the cluster
    
    Returns:
        Dictionary containing ServerResourceStats list
    """
    return get_cluster_server_stats(cluster_id)


@app.tool()
def get_oceanbase_cluster_units(cluster_id: int) -> Dict[str, Any]:
    """
    Query OceanBase cluster Unit list
    
    This interface is used to query the Unit list of an OceanBase cluster.
    The caller must be authenticated through OCP application service.
    
    Args:
        cluster_id: The ID of the cluster
    
    Returns:
        Dictionary containing UnitInfo list
    """
    return get_cluster_units(cluster_id)


@app.tool()
def get_oceanbase_cluster_tenants(
    cluster_id: int,
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    mode: Optional[str] = None,
    locked: Optional[bool] = None,
    readonly: Optional[bool] = None,
    status: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Query cluster tenant list
    
    This interface is used to query the tenant list of a cluster.
    The caller must have read permissions on the specified cluster.
    
    Args:
        cluster_id: The ID of the cluster
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 2000
        sort: Sorting rule, e.g., "asc,name" (optional)
        name: Tenant name keyword, case-insensitive (optional)
        mode: Tenant mode: MYSQL or ORACLE (optional)
        locked: Whether locked (optional)
        readonly: Whether read-only (optional)
        status: Tenant status list (optional)
    
    Returns:
        Dictionary containing tenant information list and pagination information
    """
    return get_cluster_tenants(
        cluster_id, page, size, sort, name, mode, locked, readonly, status
    )


@app.tool()
def get_all_oceanbase_tenants(
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    mode: Optional[List[str]] = None,
    locked: Optional[bool] = None,
    readonly: Optional[bool] = None,
    status: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Query all tenant list
    
    This interface is used to query all tenant list.
    The caller must be authenticated through OCP application service.
    Only returns tenants under clusters that the caller has read permissions.
    
    Args:
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 2000
        sort: Sorting rule, e.g., "name,asc" (optional)
        name: Query tenants whose name contains the keyword, case-insensitive (optional)
        mode: Query tenants with specified modes: ORACLE or MYSQL (optional)
        locked: Query by locked status (optional)
        readonly: Query by read-only status (optional)
        status: Query tenants with specified status (optional)
    
    Returns:
        Dictionary containing tenant information list and pagination information
    """
    return get_all_tenants(page, size, sort, name, mode, locked, readonly, status)


@app.tool()
def get_oceanbase_tenant_detail(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Query tenant detail
    
    This interface is used to query details of a specified tenant.
    The caller must have read permissions on the specified cluster.
    
    Args:
        cluster_id: The ID of the cluster that the target tenant belongs to
        tenant_id: The ID of the target tenant
    
    Returns:
        Dictionary containing tenant detail information
    """
    return get_tenant_detail(cluster_id, tenant_id)


@app.tool()
def get_oceanbase_tenant_units(
    cluster_id: int,
    tenant_id: int,
    zone_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query tenant Unit list
    
    This interface is used to query the Unit list of a tenant.
    The caller must have read permissions on the specified cluster.
    
    Args:
        cluster_id: The ID of the cluster that the target tenant belongs to
        tenant_id: The ID of the target tenant
        zone_name: Zone name (optional)
    
    Returns:
        Dictionary containing Unit list and pagination information
    """
    return get_tenant_units(cluster_id, tenant_id, zone_name)


@app.tool()
def get_oceanbase_tenant_parameters(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get tenant parameters list
    
    This interface is used to get the parameter list of a tenant.
    The caller must be authenticated through OCP application service.
    
    Args:
        cluster_id: The ID of the OceanBase cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing TenantParameter list
    """
    return get_tenant_parameters(cluster_id, tenant_id)


@app.tool()
def get_oceanbase_cluster_parameters(cluster_id: int) -> Dict[str, Any]:
    """
    Get OceanBase cluster parameters list
    
    This interface is used to get the parameter list of the target OceanBase cluster.
    The caller must have at least read-only permissions on the target OceanBase cluster.
    
    Args:
        cluster_id: The ID of the target OceanBase cluster
    
    Returns:
        Dictionary containing cluster parameters list
    """
    return get_cluster_parameters(cluster_id)


@app.tool()
def set_oceanbase_cluster_parameters(
    cluster_id: int,
    parameters: List[SetClusterParameterParam],
) -> Dict[str, Any]:
    """
    Update OceanBase cluster parameters
    
    This interface is used to update parameters of the target OceanBase cluster.
    
    Args:
        cluster_id: The ID of the target cluster
        parameters: Parameter list containing parameter names and new values
    
    Returns:
        OCP API response data
    """
    payload = [param.model_dump() for param in parameters]
    return set_cluster_parameters(cluster_id, payload)


@app.tool()
def set_oceanbase_tenant_parameters(
    cluster_id: int,
    tenant_id: int,
    parameters: List[SetTenantParameterParam],
) -> Dict[str, Any]:
    """
    Update tenant parameters
    
    This interface is used to update parameters of a tenant.
    The caller must have update permissions on the target tenant.
    The caller must be authenticated through OCP application service.
    
    Args:
        cluster_id: The ID of the cluster that the target tenant belongs to
        tenant_id: The ID of the target tenant
        parameters: Parameter list containing parameter names, values, and parameter types
    
    Returns:
        OCP API response data
    """
    payload = [param.model_dump() for param in parameters]
    return set_tenant_parameters(cluster_id, tenant_id, payload)


@app.tool()
def list_obproxy_clusters(
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    """
    Query OBProxy cluster list
    
    This interface is used to query OBProxy cluster list information.
    The caller must be authenticated through OCP application service.
    
    Args:
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10
    
    Returns:
        Dictionary containing OBProxy cluster list and pagination information
    """
    return get_obproxy_clusters(page, size)


@app.tool()
def get_oceanbase_obproxy_cluster_detail(cluster_id: int) -> Dict[str, Any]:
    """
    Query OBProxy cluster detail
    
    This interface is used to query OBProxy cluster detail information.
    The caller must be authenticated through OCP application service.
    
    Args:
        cluster_id: The ID of the OBProxy cluster
    
    Returns:
        Dictionary containing OBProxy cluster detail information
    """
    return get_obproxy_cluster_detail(cluster_id)


@app.tool()
def get_oceanbase_obproxy_cluster_parameters(cluster_id: int) -> Dict[str, Any]:
    """
    Query OBProxy cluster parameters
    
    This interface is used to query OBProxy cluster parameter settings.
    The caller must be authenticated through OCP application service.
    
    Args:
        cluster_id: The ID of the OBProxy cluster
    
    Returns:
        Dictionary containing ObproxyClusterParameter array
    """
    return get_obproxy_cluster_parameters(cluster_id)


@app.tool()
def get_oceanbase_tenant_databases(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database list
    
    This interface is used to get the database list of a tenant.
    The caller must be authenticated through OCP application service.
    The caller must have read permissions on the specified tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database list
    """
    return get_tenant_databases(cluster_id, tenant_id)


@app.tool()
def get_oceanbase_tenant_users(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database user list
    
    This interface is used to get the database user list of a tenant.
    The caller must be authenticated through OCP application service.
    The caller must have read permissions on the specified tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database user list
    """
    return get_tenant_users(cluster_id, tenant_id)


@app.tool()
def get_oceanbase_tenant_user_detail(
    cluster_id: int,
    tenant_id: int,
    username: str,
    host_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get database user detail
    
    This interface is used to get the detail of a database user.
    The caller must be authenticated through OCP application service.
    The caller must have read permissions on the specified tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
        username: Username
        host_name: Host name (optional)
    
    Returns:
        Dictionary containing database user detail
    """
    return get_tenant_user_detail(cluster_id, tenant_id, username, host_name)


@app.tool()
def get_oceanbase_tenant_roles(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database role list
    
    This interface is used to get the database role list of a tenant.
    The caller must be authenticated through OCP application service.
    The caller must have read permissions on the specified tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database role list
    """
    return get_tenant_roles(cluster_id, tenant_id)


@app.tool()
def get_oceanbase_tenant_role_detail(
    cluster_id: int,
    tenant_id: int,
    role_name: str
) -> Dict[str, Any]:
    """
    Get database role detail
    
    This interface is used to get the detail of a database role.
    The caller must be authenticated through OCP application service.
    The caller must have read permissions on the specified tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
        role_name: Role name
    
    Returns:
        Dictionary containing database role detail
    """
    return get_tenant_role_detail(cluster_id, tenant_id, role_name)


@app.tool()
def get_oceanbase_tenant_objects(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database object list
    
    This interface is used to get the database object list of a tenant.
    The caller must be authenticated through OCP application service.
    The caller must have read permissions on the specified tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database object list
    """
    return get_tenant_objects(cluster_id, tenant_id)


@app.tool()
def get_oceanbase_metric_groups(
    type: str,
    scope: str,
    page: int = 1,
    size: int = 10,
    sort: Optional[str] = None,
    target: Optional[str] = None,
    target_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Query monitor metric description information
    
    This interface is used to query the description information of metrics currently provided by OCP application.
    Users can use these descriptions to further query corresponding monitoring data.
    The caller must be authenticated through OCP application service.
    
    Args:
        type: Metric type: TOP or NORMAL
        scope: Metric scope: CLUSTER, TENANT, HOST, or OBPROXY
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 2000
        sort: Sorting rule (optional)
        target: Metric metadata type: OBCLUSTER or OBPROXY (optional)
        target_id: Metric metadata ID (optional)
    
    Returns:
        Dictionary containing metric group list and pagination information
    """
    return get_metric_groups(type, scope, page, size, sort, target, target_id)

@app.tool()
def get_oceanbase_metric_data_with_label(
    start_time: str,
    end_time: str,
    metrics: List[str],
    group_by: List[str],
    interval: int,
    labels: List[str],
    min_step: Optional[int] = None,
    max_points: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Query monitor metric data with labels
    
    This interface is used to query monitoring data for specified metrics with grouping label values.
    Need to specify the time range, metric array, and aggregate data by specified labels.
    Query results contain multiple groups, each group contains time series data.
    The caller must be authenticated through OCP application service.
    
    Args:
        start_time: Start time of monitoring data (Datetime format, e.g., "2020-02-16T05:32:16+08:00")
        end_time: End time of monitoring data (Datetime format, e.g., "2020-02-16T07:32:16+08:00")
        metrics: Array of monitoring metrics
        group_by: Array of labels for aggregating monitoring data
        interval: Time granularity of monitoring data in seconds
        labels: Filter conditions for monitoring data
        min_step: Query sampling interval (optional)
        max_points: Maximum number of monitoring result points (optional)
    
    Returns:
        Dictionary containing monitoring sampling groups array
    """
    return get_metric_data_with_label(start_time, end_time, metrics, group_by, interval, labels, min_step, max_points)


@app.tool()
def get_oceanbase_alarms(
    page: int = 1,
    size: int = 10,
    app_type: Optional[str] = None,
    scope: Optional[str] = None,
    level: Optional[int] = None,
    status: Optional[str] = None,
    active_at_start: Optional[str] = None,
    active_at_end: Optional[str] = None,
    is_subscribed_by_me: Optional[bool] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query alarm event list
    
    This interface is used to query alarm event list.
    The caller must have read permissions for alarm functionality.
    
    Args:
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 200
        app_type: Application type (alarm source) (optional):
            - OceanBase
            - OCP
            - OMS
            - OBProxy
            - Log
            - Backup
        scope: Alarm scope (optional):
            - Cluster
            - Tenant
            - Host
            - Service
            - Arbitration
            - Backup
            - OceanBaseLog
            - OBProxyLog
            - *
            - HostLog
        level: Alarm level [1~5] (optional):
            - 1: Down
            - 2: Critical
            - 3: Alert
            - 4: Caution
            - 5: Info
        status: Alarm status (optional):
            - Active
            - Inactive
            - Silenced
            - Inhibited
        active_at_start: Alarm trigger start time (Datetime format, e.g., "2020-11-11T11:12:13.127+08:00") (optional)
        active_at_end: Alarm trigger end time (Datetime format, e.g., "2020-11-11T17:11:13.127+08:00") (optional)
        is_subscribed_by_me: Whether subscribed by me (optional)
        keyword: Keyword matching (optional)
    
    Returns:
        Dictionary containing alarm event list and pagination information
    """
    return get_alarms(
        page, size, app_type, scope, level, status,
        active_at_start, active_at_end, is_subscribed_by_me, keyword
    )


@app.tool()
def get_oceanbase_alarm_detail(alarm_id: int) -> Dict[str, Any]:
    """
    Query alarm event detail
    
    This interface is used to query detailed information of a specified alarm event.
    The caller must have read permissions for alarm functionality.
    
    Args:
        alarm_id: The ID of the alarm event
    
    Returns:
        Dictionary containing alarm event detail information
    """
    return get_alarm_detail(alarm_id)





@app.tool()
def get_oceanbase_inspection_tasks(
    inspectionObjectTypes: Optional[List[str]] = None,
    tags: Optional[List[int]] = None,
    taskStates: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query inspection task list
    
    This interface is used to query all inspection tasks.
    The caller must be authenticated through OCP application service.
    
    Args:
        inspectionObjectTypes: Inspection object types (optional):
            - OB_CLUSTER: Cluster
            - OB_TENANT: Tenant
            - HOST: Host
            - OB_PROXY: OBProxy
        tags: Inspection scenario tag IDs (optional):
            - 1: Basic inspection
            - 2: Performance inspection
            - 3: Deep inspection
            - 4: Installation inspection
        taskStates: Inspection task state (optional):
            - RUNNING: Running
            - FAILED: Failed
            - SUCCESSFUL: Successful
        name: Inspection object name (optional)
    
    Returns:
        Dictionary containing inspection task list and pagination information.
        Each inspection task includes:
        - id: Inspection report ID
        - tag: InspectionTag information
        - inspectionObject: InspectionObject information
        - startTime: Inspection start time
        - endTime: Inspection end time (not present when task is running)
        - taskId: Inspection task ID
        - itemTotalCount: Total number of inspection items
        - itemFinishedCount: Number of finished inspection items
        - highRiskCount: Number of high-risk inspection items
        - mediumRiskCount: Number of medium-risk inspection items
        - lowRiskCount: Number of low-risk inspection items
        - taskState: Inspection task state
    """
    from ocp_mcp.ocp_tool import get_inspection_tasks
    return get_inspection_tasks(inspectionObjectTypes, tags, taskStates, name)


@app.tool()
def get_oceanbase_inspection_overview(
    object_ids: Optional[List[int]] = None,
    inspection_object_type: Optional[List[str]] = None,
    schedule_states: Optional[List[str]] = None,
    name: Optional[str] = None,
    parent_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query inspection object list
    
    This interface can query inspection object list by category.
    The caller must be authenticated through OCP application service.
    
    Args:
        object_ids: Inspection object IDs in OCP (e.g., cluster ID, tenant ID).
                   Multiple IDs should be separated by commas (optional)
        inspection_object_type: Object types (optional):
            - OB_CLUSTER: Cluster
            - OB_TENANT: Tenant
            - HOST: Host
            - OB_PROXY: OBProxy
        schedule_states: Schedule states (optional):
            - ACTIVE: Enabled
            - INACTIVE: Disabled
            - EXPIRED: Expired
        name: Inspection object name (optional)
        parent_name: Parent object name of the inspection object (optional)
    
    Returns:
        Dictionary containing inspection object list and pagination information
    """
    return get_inspection_overview(object_ids, inspection_object_type, schedule_states, name, parent_name)


@app.tool()
def get_oceanbase_inspection_report(report_id: int) -> Dict[str, Any]:
    """
    Get inspection report detail
    
    This interface is used to get inspection report detail.
    The caller must be authenticated through OCP application service.
    
    Args:
        report_id: Inspection report ID (can be obtained from the query inspection tasks interface)
    
    Returns:
        Dictionary containing inspection report detail information
    """
    return get_inspection_report(report_id)


@app.tool()
def run_oceanbase_inspection(
    inspection_object_type: str,
    object_ids: List[int],
    tags: int,
) -> Dict[str, Any]:
    """
    Run inspection
    
    This interface is used to initiate inspection for specified objects with a specific scenario.
    The caller must be authenticated through OCP application service.
    
    Args:
        inspection_object_type: Inspection object type (required):
            - OB_CLUSTER: Cluster
            - OB_TENANT: Tenant
            - HOST: Host
            - OB_PROXY: OBProxy
        object_ids: Inspection object IDs in OCP (e.g., cluster ID, tenant ID).
                   Multiple IDs should be provided as a list (required)
        tags: Scenario tag ID (required):
            - 1: Basic inspection
            - 2: Performance inspection
            - 3: Deep inspection
            - 4: Installation inspection
    
    Returns:
        Dictionary containing async task information
    """
    return run_inspection(inspection_object_type, object_ids, tags)


@app.tool()
def get_oceanbase_inspection_item_last_result(
    item_id: int,
    tag_id: int,
    object_type: str,
    object_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Query the last inspection result of a specified inspection item
    
    This interface queries the last inspection result of a specified inspection item
    based on conditions such as inspection object type, inspection scenario, and inspection object ID (optional).
    The caller must be authenticated through OCP application service.
    
    Args:
        item_id: Inspection item ID (required)
        tag_id: Inspection scenario ID (required):
            - 1: Basic inspection
            - 2: Performance inspection
            - 3: Deep inspection
            - 4: Installation inspection
        object_type: Inspection object type (required):
            - OB_CLUSTER: Cluster
            - OB_TENANT: Tenant
            - HOST: Host
            - OB_PROXY: OBProxy
        object_id: Object ID (optional)
    
    Returns:
        Dictionary containing inspection result aggregation information
    """
    return get_inspection_item_last_result(item_id, tag_id, object_type, object_id)


@app.tool()
def get_oceanbase_inspection_report_info(
    tag_id: int,
    object_type: str,
    object_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get the last inspection result of a specific object
    
    This interface queries the last inspection result of objects that meet the conditions
    based on inspection object type, inspection scenario, and inspection object ID (optional).
    The caller must be authenticated through OCP application service.
    
    Args:
        tag_id: Inspection scenario ID (required):
            - 1: Basic inspection
            - 2: Performance inspection
            - 3: Deep inspection
            - 4: Installation inspection
        object_type: Inspection object type (required):
            - OB_CLUSTER: Cluster
            - OB_TENANT: Tenant
            - HOST: Host
            - OB_PROXY: OBProxy
        object_id: Object ID (optional)
    
    Returns:
        Dictionary containing inspection result aggregation information.
        The data includes:
        - contents: Array of InspectionReportAggrInfo
        
        InspectionReportAggrInfo includes:
        - reportId: Inspection report ID
        - objectId: Inspection object ID
        - objectName: Inspection object name
        - objectType: Inspection object type
        - tag: Inspection scenario information
        - startTime: Inspection start time
        - endTime: Inspection end time
        - resultList: Array of inspection item results
    """
    from ocp_mcp.ocp_tool import get_inspection_report_info
    return get_inspection_report_info(tag_id, object_type, object_id)


@app.tool()
def get_oceanbase_tenant_top_sql(
    cluster_id: int,
    tenant_id: int,
    start_time: str,
    end_time: str,
    server_id: Optional[int] = None,
    inner: Optional[bool] = None,
    sql_text: Optional[str] = None,
    search_attr: Optional[str] = None,
    search_op: Optional[str] = None,
    search_val: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query SQL performance statistics
    
    Query tenant SQL performance statistics within a specified time range.
    Performance data includes: cluster, tenant, server, database, user, SQL_ID,
    response time, CPU time, execution count, error count, etc.
    The caller must have read permissions for the specified tenant.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        start_time: Start time (Datetime format, e.g., "2020-02-16T05:32:16+08:00") (required)
        end_time: End time (Datetime format, e.g., "2020-02-16T07:32:16+08:00") (required)
        server_id: Query SQL executed on specified OceanBase server (optional)
        inner: Whether to include internal SQL (optional, default: false)
        sql_text: SQL text keyword (case-insensitive) (optional)
        search_attr: Advanced search metric name (optional)
        search_op: Advanced search operator: EQ, NE, GT, GE, LT, LE (optional)
        search_val: Advanced search value (optional)
    
    Returns:
        Dictionary containing SQL performance statistics list
    """
    from ocp_mcp.ocp_tool import get_tenant_top_sql
    return get_tenant_top_sql(
        cluster_id, tenant_id, start_time, end_time,
        server_id, inner, sql_text, search_attr, search_op, search_val
    )


@app.tool()
def get_oceanbase_sql_trends(
    cluster_id: int,
    tenant_id: int,
    sql_id: str,
    start_time: str,
    end_time: str,
    server_id: Optional[int] = None,
    db_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query SQL performance statistics trends
    
    Query the performance statistics trend of a specific SQL within a specified time range.
    Performance trend consists of multiple sampling points, each containing performance
    statistics at a specified timestamp.
    The caller must have read permissions for the specified tenant.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        sql_id: SQL ID (required)
        start_time: Start time (Datetime format, e.g., "2020-02-16T05:32:16+08:00") (required)
        end_time: End time (Datetime format, e.g., "2020-02-16T07:32:16+08:00") (required)
        server_id: Query SQL performance on specified OceanBase server (optional)
        db_name: Query SQL performance in specified database (optional)
    
    Returns:
        Dictionary containing SQL performance sampling data array
    """
    from ocp_mcp.ocp_tool import get_sql_trends
    return get_sql_trends(cluster_id, tenant_id, sql_id, start_time, end_time, server_id, db_name)


@app.tool()
def get_oceanbase_sql_text(
    cluster_id: int,
    tenant_id: int,
    sql_id: str,
    start_time: str,
    end_time: str,
) -> Dict[str, Any]:
    """
    Query SQL full text
    
    Query the full text of SQL with specified ID.
    The caller must have read permissions for the specified tenant.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        sql_id: SQL ID (required)
        start_time: Start time (Datetime format, e.g., "2020-02-16T05:32:16+08:00") (required)
        end_time: End time (Datetime format, e.g., "2020-02-16T07:32:16+08:00") (required)
    
    Returns:
        Dictionary containing SQL full text
    """
    from ocp_mcp.ocp_tool import get_sql_text
    return get_sql_text(cluster_id, tenant_id, sql_id, start_time, end_time)


@app.tool()
def get_oceanbase_tenant_slow_sql(
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
    """
    Query slow SQL list
    
    This interface is used to query slow SQL list.
    The caller must have read permissions for the specified tenant.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        start_time: Start time (UTC format: YYYY-MM-DDThh:mm:ssZ) (required)
        end_time: End time (UTC format: YYYY-MM-DDThh:mm:ssZ) (required)
        server_id: Query SQL performance on specified OceanBase server (optional)
        inner: Whether it's internal SQL (optional)
        sql_text: SQL text keyword (case-insensitive) (optional)
        filter_expression: Filter expression, all fields referenced by @ (optional)
        limit: Number of TOP results to return (optional)
        sql_text_length: Maximum length of returned SQL text (optional)
    
    Returns:
        Dictionary containing slow SQL list
    """
    from ocp_mcp.ocp_tool import get_tenant_slow_sql
    return get_tenant_slow_sql(
        cluster_id, tenant_id, start_time, end_time,
        server_id, inner, sql_text, filter_expression, limit, sql_text_length
    )


@app.tool()
def create_oceanbase_performance_report(
    cluster_id: int,
    start_snapshot_id: int,
    end_snapshot_id: int,
    name: str,
) -> Dict[str, Any]:
    """
    Generate performance report
    
    Generate cluster performance report.
    The caller must have read and write permissions for the specified cluster.
    
    Args:
        cluster_id: Target OceanBase cluster ID (required)
        start_snapshot_id: Start snapshot ID for the report (required)
        end_snapshot_id: End snapshot ID for the report (required)
        name: Report name (required)
    
    Returns:
        Dictionary containing report information including:
        - id: Report unique ID
        - clusterName: Cluster name
        - status: Report status (CREATING/SUCCESSFUL/FAILED)
        - taskInstanceId: Associated task instance ID
    """
    from ocp_mcp.ocp_tool import create_performance_report
    return create_performance_report(cluster_id, start_snapshot_id, end_snapshot_id, name)


@app.tool()
def get_oceanbase_performance_report(
    cluster_id: int,
    report_id: int,
) -> Dict[str, Any]:
    """
    Query performance report
    
    Query cluster performance report.
    The caller must have read and write permissions for the specified cluster.
    
    Note: This endpoint returns binary HTML content that can be saved as an HTML file.
    
    Args:
        cluster_id: Target OceanBase cluster ID (required)
        report_id: Performance report ID (required)
    
    Returns:
        Dictionary containing report data with HTML content
    """
    from ocp_mcp.ocp_tool import get_performance_report
    return get_performance_report(cluster_id, report_id)

