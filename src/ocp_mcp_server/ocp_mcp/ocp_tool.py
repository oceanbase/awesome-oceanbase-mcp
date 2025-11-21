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
    status: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Query OceanBase cluster list
    
    Args:
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 2000
        sort: Sorting rule for request data, e.g., "name,asc"
        name: Cluster name keyword, case-insensitive matching
        status: Cluster status list, optional values:
            - RUNNING: Running
            - CREATING: Creating
            - DELETING: Deleting
            - STARTING: Starting
            - RESTARTING: Restarting
            - STOPPING: Stopping
            - STOPPED: Stopped
            - TAKINGOVER: Taking over
            - MOVINGOUT: Moving out
            - SWITCHOVER: Primary-standby cluster switching
            - FAILOVER: Standby cluster failover
            - OPERATING: Operating
    
    Returns:
        Dictionary containing cluster list and pagination information
    """
    try:
        # Build query parameters
        params = {
            "page": str(page),
            "size": str(size)
        }
        
        if sort:
            params["sort"] = sort
        if name:
            params["name"] = name
        if status:
            params["status"] = ",".join(status)
        
        result = get_ocp_client().get("/api/v2/ob/clusters", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to list OceanBase clusters: {e}")
        raise


def get_cluster_zones(
    cluster_id: int
) -> Dict[str, Any]:
    """
    Query OceanBase cluster Zone list
    
    This interface is used to query the Zone list of an OceanBase cluster.
    
    Args:
        cluster_id: The ID of the OceanBase cluster to query Zone list
    
    Returns:
        Dictionary containing Zone list and pagination information. Zone data structure includes:
        - name: Zone name
        - idcName: IDC name
        - regionName: Region name
        - servers: Server list
        - clusterId: Cluster ID
        - obClusterId: OceanBase cluster ID
        - serverCount: Server count
        - hostCount: Host count
        
        Server data structure includes:
        - id: OBServer ID
        - ip: OBServer IP
        - port: Port
        - sqlPort: SQL port
        - version: Version
        - withRootserver: Whether with root service
        - status: Status
        - clusterId: Cluster ID
        - zoneName: Zone name
        - regionName: Region name
        - idcName: IDC name
        - hostId: Host ID
        - hostTypeName: Host type name
        - startTime: Start time
        - stopTime: Stop time
    """
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
    """
    Query OceanBase cluster OBServer list
    
    This interface is used to query all OBServer node information of the target OceanBase cluster.
    
    Args:
        cluster_id: The ID of the target cluster
        region_name: Query OceanBase servers in the specified region (optional)
        idc_name: Query OceanBase servers in the specified IDC (optional)
    
    Returns:
        Dictionary containing server information list. Server data structure includes:
        - id: Server ID
        - ip: Server IP address
        - port: Server RPC port
        - sqlPort: Server SQL port
        - version: Server OceanBase version
        - withRootServer: Whether with Root Service
        - status: Server status (CREATING, RUNNING, STOPPING, STOPPED, STARTING, 
                 RESTARTING, DELETING, UNAVAILABLE, OPERATING, DELETED)
        - updateTime: Server last update time
        - clusterId: Cluster ID that the server belongs to
        - zoneName: Zone name that the server belongs to
        - regionName: Region name that the server belongs to
        - idcName: IDC name that the server belongs to
        - hostId: Server host ID
        - hostTypeName: Server host type
        - startTime: Server start time
        - stopTime: Server stop time
        - availableOperations: Available operations list for the server
    """
    try:
        params = {}
        if region_name:
            params["regionName"] = region_name
        if idc_name:
            params["idcName"] = idc_name
        
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/servers",
            params=params if params else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get servers for cluster {cluster_id}: {e}")
        raise


def get_zone_servers(
    cluster_id: int,
    zone_name: str,
) -> Dict[str, Any]:
    """
    Query Zone OBServer list
    
    This interface is used to query OBServer node information under the specified Zone 
    in the target OceanBase cluster.
    
    Args:
        cluster_id: The ID of the target cluster
        zone_name: The name of the Zone
    
    Returns:
        Dictionary containing server information list. Server data structure includes:
        - id: Server ID
        - ip: Server IP address
        - port: Server RPC port
        - sqlPort: Server SQL port
        - version: Server OceanBase version
        - withRootServer: Whether with Root Service
        - status: Server status (CREATING, RUNNING, STOPPING, STOPPED, STARTING, 
                 RESTARTING, DELETING, UNAVAILABLE, OPERATING, DELETED)
        - updateTime: Server last update time
        - clusterId: Cluster ID that the server belongs to
        - zoneName: Zone name that the server belongs to
        - regionName: Region name that the server belongs to
        - idcName: IDC name that the server belongs to
        - hostId: Server host ID
        - hostTypeName: Server host type
        - startTime: Server start time
        - stopTime: Server stop time
        - availableOperations: Available operations list for the server
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/zones/{zone_name}/servers"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get servers for cluster {cluster_id} zone {zone_name}: {e}")
        raise


def get_cluster_stats(
    cluster_id: int
) -> Dict[str, Any]:
    """
    Get OceanBase cluster resource statistics
    
    This interface is used to get resource statistics information of an OceanBase cluster.
    
    Args:
        cluster_id: The ID of the cluster
    
    Returns:
        Dictionary containing ClusterResourceStats information, which includes:
        - clusterId: Cluster ID
        - clusterName: Cluster name
        - obClusterId: OceanBase cluster ID
        - cpuTotal: Total CPU
        - cpuAssigned: Assigned CPU
        - memoryTotalByte: Total memory in bytes
        - memoryAssignedByte: Assigned memory in bytes
        - logDiskTotalByte: Total log disk in bytes
        - logDiskAssignedByte: Assigned log disk in bytes
        - logDiskUsedByte: Used log disk in bytes
        - dataDiskTotalByte: Total data disk in bytes
        - dataDiskUsedByte: Used data disk in bytes
    """
    try:
        result = get_ocp_client().get(f"/api/v2/ob/clusters/{cluster_id}/stats")
        return result
    except Exception as e:
        logger.error(f"Failed to get stats for cluster {cluster_id}: {e}")
        raise


def get_cluster_server_stats(
    cluster_id: int
) -> Dict[str, Any]:
    """
    Get resource statistics for all OBServers in the cluster
    
    This interface is used to get resource statistics information for all OBServers in the cluster.
    
    Args:
        cluster_id: The ID of the cluster
    
    Returns:
        Dictionary containing ServerResourceStats list. Each ServerResourceStats includes:
        - ip: OBServer IP
        - port: OBServer port
        - zone: Zone name
        - cpuTotal: Total CPU
        - cpuAssigned: Assigned CPU
        - memoryTotalByte: Total memory in bytes
        - memoryAssignedByte: Assigned memory in bytes
        - logDiskTotalByte: Total log disk in bytes
        - logDiskAssignedByte: Assigned log disk in bytes
        - logDiskUsedByte: Used log disk in bytes
        - dataDiskTotalByte: Total data disk in bytes
        - dataDiskUsedByte: Used data disk in bytes
    """
    try:
        result = get_ocp_client().get(f"/api/v2/ob/clusters/{cluster_id}/serverStats")
        return result
    except Exception as e:
        logger.error(f"Failed to get server stats for cluster {cluster_id}: {e}")
        raise


def get_cluster_units(
    cluster_id: int
) -> Dict[str, Any]:
    """
    Query OceanBase cluster Unit list
    
    This interface is used to query the Unit list of an OceanBase cluster.
    
    Args:
        cluster_id: The ID of the cluster
    
    Returns:
        Dictionary containing UnitInfo list. Each UnitInfo includes:
        - obUnitId: Unit ID
        - tenantId: Tenant ID
        - tenantName: Tenant name
        - obTenantId: OceanBase tenant ID
        - svrIp: OBServer IP
        - svrPort: OBServer port
        - zone: Zone name
        - unitConfig: UnitConfig specification (see below)
        - status: Unit status
        - migrateType: Unit migration type
        - migrateOppositeSvrIp: Migration opposite OBServer IP
        - migrateOppositeSvrPort: Migration opposite OBServer port
        - manualMigrate: Whether manual migration
        - logDiskUsedByte: Log disk usage in bytes (OceanBase 4.0+)
        - dataDiskUsedByte: Data disk usage in bytes (OceanBase 4.0+)
        
        UnitConfig data structure includes:
        - maxCpuCoreCount: Maximum CPU core count
        - minCpuCoreCount: Minimum CPU core count
        - maxMemoryByte: Maximum memory size in bytes
        - minMemoryByte: Minimum memory size in bytes
        - logDiskSizeByte: Log disk size in bytes
        - maxIops: Maximum IOPS
        - minIops: Minimum IOPS
        - iopsWeight: IOPS weight
        - logDiskSize: Log disk size in GB
        - minMemorySize: Minimum memory size in GB
        - maxMemorySize: Maximum memory size in GB
    """
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
    locked: Optional[bool] = None,
    readonly: Optional[bool] = None,
    status: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Query cluster tenant list
    
    This interface is used to query the tenant list of a cluster.
    
    Args:
        cluster_id: The ID of the cluster
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 2000
        sort: Sorting rule, e.g., "asc,name"
        name: Tenant name keyword, case-insensitive (optional)
        mode: Tenant mode: MYSQL or ORACLE (optional)
        locked: Whether locked (optional)
        readonly: Whether read-only (optional)
        status: Tenant status list (optional):
            - NORMAL: Running
            - CREATING: Creating
            - MODIFYING: Modifying
            - DELETING: Deleting
    
    Returns:
        Dictionary containing tenant information list and pagination information.
        Each tenant includes:
        - id: Tenant ID
        - name: Tenant name
        - clusterName: Cluster name that the tenant belongs to
        - clusterId: Cluster ID that the tenant belongs to
        - obClusterId: OceanBase cluster ID
        - clusterType: Cluster type (PRIMARY or STANDBY)
        - mode: Tenant mode (ORACLE or MYSQL)
        - createTime: Tenant creation time
        - primaryZone: Zone priority
        - zoneList: Zone list
        - locality: Replica distribution
        - status: Tenant status (NORMAL, CREATING, MODIFYING, DELETING)
        - locked: Whether locked
        - readonly: Whether read-only
        - obVersion: OceanBase version
        - description: Tenant description
        - loadType: Load type (EXPRESS_OLTP, COMPLEX_OLTP, HTAP, OLAP, KV)
    """
    try:
        params = {
            "page": str(page),
            "size": str(size)
        }
        
        if sort:
            params["sort"] = sort
        if name:
            params["name"] = name
        if mode:
            params["mode"] = mode
        if locked is not None:
            params["locked"] = str(locked).lower()
        if readonly is not None:
            params["readonly"] = str(readonly).lower()
        if status:
            params["status"] = ",".join(status)
        
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants",
            params=params
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
    mode: Optional[List[str]] = None,
    locked: Optional[bool] = None,
    readonly: Optional[bool] = None,
    status: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Query all tenant list
    
    This interface is used to query all tenant list.
    Only returns tenants under clusters that the caller has read permissions.
    
    Args:
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 2000
        sort: Sorting rule, e.g., "name,asc"
        name: Query tenants whose name contains the keyword, case-insensitive (optional)
        mode: Query tenants with specified modes (optional):
            - ORACLE: Oracle mode
            - MYSQL: MySQL mode
        locked: Query by locked status (optional):
            - True: Only query locked tenants
            - False: Only query unlocked tenants
            - None: Query all tenants
        readonly: Query by read-only status (optional):
            - True: Only query read-only tenants
            - False: Only query non-read-only tenants
            - None: Query all tenants
        status: Query tenants with specified status (optional):
            - NORMAL: Running
            - CREATING: Creating
            - MODIFYING: Modifying
            - DELETING: Deleting
    
    Returns:
        Dictionary containing tenant information list and pagination information.
        Each tenant includes:
        - id: Tenant ID
        - name: Tenant name
        - clusterName: Cluster name that the tenant belongs to
        - clusterId: Cluster ID that the tenant belongs to
        - obClusterId: OceanBase cluster ID
        - clusterType: Cluster type (PRIMARY or STANDBY)
        - mode: Tenant mode (ORACLE or MYSQL)
        - createTime: Tenant creation time
        - primaryZone: Zone priority
        - zoneList: Zone list
        - locality: Replica distribution
        - status: Tenant status (NORMAL, CREATING, MODIFYING, DELETING)
        - locked: Whether locked
        - readonly: Whether read-only
        - obVersion: OceanBase version
        - description: Tenant description
        - loadType: Load type (EXPRESS_OLTP, COMPLEX_OLTP, HTAP, OLAP, KV)
    """
    try:
        params = {
            "page": str(page),
            "size": str(size)
        }
        
        if sort:
            params["sort"] = sort
        if name:
            params["name"] = name
        if mode:
            params["mode"] = ",".join(mode)
        if locked is not None:
            params["locked"] = str(locked).lower()
        if readonly is not None:
            params["readonly"] = str(readonly).lower()
        if status:
            params["status"] = ",".join(status)
        
        result = get_ocp_client().get("/api/v2/ob/tenants", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get all tenants: {e}")
        raise


def get_tenant_detail(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Query tenant detail
    
    This interface is used to query details of a specified tenant.
    
    Args:
        cluster_id: The ID of the cluster that the target tenant belongs to
        tenant_id: The ID of the target tenant
    
    Returns:
        Dictionary containing tenant detail information, which includes:
        - id: Tenant ID
        - name: Tenant name
        - clusterName: Cluster name that the tenant belongs to
        - clusterId: Cluster ID that the tenant belongs to
        - obClusterId: OceanBase cluster ID
        - clusterType: Cluster type (PRIMARY or STANDBY)
        - mode: Tenant mode (ORACLE or MYSQL)
        - createTime: Tenant creation time
        - primaryZone: Zone priority
        - zoneList: Zone list
        - locality: Replica distribution
        - status: Tenant status (NORMAL, CREATING, MODIFYING, DELETING)
        - locked: Whether locked
        - readonly: Whether read-only
        - obVersion: OceanBase version
        - description: Tenant description
        - charset: Character set
        - collation: Collation
        - zones: TenantZone list (see below)
        - whitelist: Whitelist
        - loadType: Load type (EXPRESS_OLTP, COMPLEX_OLTP, HTAP, OLAP, KV)
        
        TenantZone data structure includes:
        - name: Zone name
        - replicaType: Replica type
        - resourcePool: ResourcePool data structure (see below)
        - units: Unit list (see below)
        
        ResourcePool data structure includes:
        - id: Resource pool ID
        - name: Resource pool name
        - unitCount: Unit count
        - unitConfig: UnitConfig data structure (see below)
        
        UnitConfig data structure includes:
        - maxCpuCoreCount: Maximum CPU core count
        - minCpuCoreCount: Minimum CPU core count
        - maxMemorySize: Maximum memory in GB
        - minMemorySize: Minimum memory in GB
        
        Unit data structure includes:
        - id: Unit ID
        - resourcePoolId: Resource pool ID
        - serverId: OBServer node ID
        - serverIp: OBServer node IP
        - serverPort: OBServer node port
        - zoneName: Zone name
        - status: Unit status
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get tenant detail for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def get_tenant_units(
    cluster_id: int,
    tenant_id: int,
    zone_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query tenant Unit list
    
    This interface is used to query the Unit list of a tenant.
    
    Args:
        cluster_id: The ID of the cluster that the target tenant belongs to
        tenant_id: The ID of the target tenant
        zone_name: Zone name (optional)
    
    Returns:
        Dictionary containing Unit list and pagination information. Each Unit includes:
        - id: Unit ID
        - resourcePoolId: Resource pool ID
        - serverId: OBServer node ID
        - serverIp: OBServer node IP
        - serverPort: OBServer node port
        - zoneName: Zone name
        - status: Unit status
    """
    try:
        params = {}
        if zone_name:
            params["zoneName"] = zone_name
        
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/units",
            params=params if params else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get units for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def get_tenant_parameters(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get tenant parameters list
    
    This interface is used to get the parameter list of a tenant.
    
    Args:
        cluster_id: The ID of the OceanBase cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing TenantParameter list. Each TenantParameter includes:
        - name: Parameter name
        - compatibleType: Compatible type (ORACLE or MYSQL)
        - readonly: Whether read-only
        - defaultValue: Default value
        - currentValue: Current value
        - description: Parameter description
        - valueRange: ValueRange data structure (see below)
        
        ValueRange data structure includes:
        - type: Parameter type
        - allowedValues: Allowed values list
        - maxValue: Parameter maximum value
        - minValue: Parameter minimum value
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/parameters"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get parameters for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def get_cluster_parameters(
    cluster_id: int
) -> Dict[str, Any]:
    """
    Get OceanBase cluster parameters list
    
    This interface is used to get the parameter list of the target OceanBase cluster.
    
    Args:
        cluster_id: The ID of the target OceanBase cluster
    
    Returns:
        Dictionary containing cluster parameters list. ClusterParameter data structure includes:
        - name: Parameter name
        - section: Parameter category
        - defaultValue: Default value
        - valueRange: ValueRange data structure
        - currentValue: ClusterParameterValue data structure
        - needRestart: Whether restart is required
        - readonly: Whether read-only
        - description: Parameter description
        
        ValueRange data structure includes:
        - type: Parameter type
        - allowedValues: Allowed values list
        - maxValue: Parameter maximum value
        - minValue: Parameter minimum value
        
        ClusterParameterValue data structure includes:
        - values: Values list
        - valueToServersMap: OBServer values list
        - obParameters: ObParameter data structure list
        
        ObParameter data structure includes:
        - zone: Zone name
        - svrIp: OBServer node IP
        - svrPort: OBServer node port
        - name: Parameter name
        - value: Parameter value
    """
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
    """
    Update tenant parameters
    
    This interface is used to update parameters of a tenant.
    
    Args:
        cluster_id: The ID of the cluster that the target tenant belongs to
        tenant_id: The ID of the target tenant
        parameters: Parameter list to update
            - name: Parameter name (required)
            - value: Parameter value (required)
            - parameterType: Parameter type (required): OB_SYSTEM_VARIABLE or OB_TENANT_PARAMETER
    
    Returns:
        OCP API response data
    """
    if not parameters:
        raise ValueError("parameters list cannot be empty")
    
    payload: List[Dict[str, Any]] = []
    for index, param in enumerate(parameters):
        if "name" not in param or not param["name"]:
            raise ValueError(f"parameters[{index}] is missing required field 'name'")
        if "value" not in param:
            raise ValueError(f"parameters[{index}] is missing required field 'value'")
        if "parameterType" not in param or not param["parameterType"]:
            raise ValueError(f"parameters[{index}] is missing required field 'parameterType'")
        
        payload.append({
            "name": str(param["name"]),
            "value": param["value"],
            "parameterType": str(param["parameterType"]),
        })
    
    try:
        result = get_ocp_client().put(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/parameters",
            json=payload,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to set parameters for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def set_cluster_parameters(
    cluster_id: int,
    parameters: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Update OceanBase cluster parameters
    
    Args:
        cluster_id: The ID of the target OceanBase cluster
        parameters: Parameter list to update
            - name: Parameter name
            - value: Parameter value
    
    Returns:
        OCP API response data
    """
    if not parameters:
        raise ValueError("parameters list cannot be empty")
    
    payload: List[Dict[str, Any]] = []
    for index, param in enumerate(parameters):
        if "name" not in param or not param["name"]:
            raise ValueError(f"parameters[{index}] is missing required field 'name'")
        if "value" not in param:
            raise ValueError(f"parameters[{index}] is missing required field 'value'")
        
        payload.append({
            "name": str(param["name"]),
            "value": param["value"],
        })
    
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
    """
    Query OBProxy cluster list
    
    This interface is used to query OBProxy cluster list information.
    
    Args:
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10
    
    Returns:
        Dictionary containing OBProxy cluster list and pagination information.
        Each obproxyCluster includes:
        - id: OBProxy cluster ID
        - name: OBProxy cluster name
        - parameterVersion: OBProxy cluster parameter version
        - creatorId: Creator ID
        - creatorName: Creator name
        - createTime: Creation time
        - updateTime: Update time
        - configUrl: Config URL address
        - address: OBProxy cluster access address
        - port: OBProxy cluster access port
        - obLinks: Array of connectable OceanBase cluster information (ObLink)
        - versions: Array of OBProxy deployment version information (VersionStatInfo)
        - topo: Array of OBProxy deployment topo information (IdcStatInfo)
        - obproxies: Array of all OBProxy servers in the cluster (ObproxyServer)
        
        ObLink data structure includes:
        - clusterId: Cluster ID
        - clusterName: Cluster name
        - username: Connection user
        - status: Cluster status (RUNNING, UNAVAILABLE, STOPPED, etc.)
        - connections: OceanBase cluster connection count
        - obClusterId: OceanBase cluster ID
        - clusterType: Cluster type (PRIMARY or STANDBY)
        
        VersionStatInfo data structure includes:
        - version: Version information
        - count: OBProxy count
        
        IdcStatInfo data structure includes:
        - idcName: IDC name
        - count: OBProxy count
        
        ObproxyServer data structure includes:
        - id: OBProxy server ID
        - clusterId: OBProxy cluster ID
        - hostId: Host ID
        - idcName: IDC name
        - lastActiveTime: Last active time
        - parameterVersion: Parameter version
        - ip: IP address
        - sqlPort: SQL port
        - exporterPort: Exporter port
        - version: OBProxy version information
        - status: OBProxy status (CREATING, RUNNING, RESTARTING, etc.)
        - operateStatus: OBProxy operation status (NORMAL, OPERATING)
        - architecture: Host hardware architecture information
    """
    try:
        params = {
            "page": str(page),
            "size": str(size)
        }
        
        result = get_ocp_client().get("/api/v2/obproxy/clusters", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get OBProxy clusters: {e}")
        raise


def get_obproxy_cluster_detail(
    cluster_id: int
) -> Dict[str, Any]:
    """
    Query OBProxy cluster detail
    
    This interface is used to query OBProxy cluster detail information.
    
    Args:
        cluster_id: The ID of the OBProxy cluster
    
    Returns:
        Dictionary containing OBProxy cluster detail information. The obproxyCluster includes:
        - id: OBProxy cluster ID
        - name: OBProxy cluster name
        - parameterVersion: OBProxy cluster parameter version
        - creatorId: Creator ID
        - creatorName: Creator name
        - createTime: Creation time
        - updateTime: Update time
        - configUrl: Config URL address
        - address: OBProxy cluster access address
        - port: OBProxy cluster access port
        - obLinks: Array of connectable OceanBase cluster information (ObLink)
        - versions: Array of OBProxy deployment version information (VersionStatInfo)
        - topo: Array of OBProxy deployment topo information (IdcStatInfo)
        - obproxies: Array of all OBProxy servers in the cluster (ObproxyServer)
        
        ObLink data structure includes:
        - clusterId: Cluster ID
        - clusterName: Cluster name
        - username: Connection user
        - status: Cluster status (RUNNING, UNAVAILABLE, STOPPED, CREATING, TAKINGOVER, 
                 DELETING, MOVINGOUT, RESTARTING, STARTING, STOPPING, SWITCHOVER, 
                 FAILOVER, UPGRADING, OPERATING, ABANDONED)
        - obClusterId: OceanBase cluster ID
        - clusterType: Cluster type (PRIMARY or STANDBY)
        
        VersionStatInfo data structure includes:
        - version: Version information
        - count: OBProxy count
        
        IdcStatInfo data structure includes:
        - idcName: IDC name
        - count: OBProxy count
        
        ObproxyServer data structure includes:
        - id: OBProxy server ID
        - clusterId: OBProxy cluster ID
        - hostId: Host ID
        - idcName: IDC name
        - lastActiveTime: Last active time
        - parameterVersion: Parameter version
        - ip: IP address
        - sqlPort: SQL port
        - exporterPort: Exporter port
        - version: OBProxy version information
        - status: OBProxy status (CREATING, RUNNING, RESTARTING, UPGRADING, REFRESHING, 
                 DELETING, UNAVAILABLE, TAKINGOVER)
        - operateStatus: OBProxy operation status (NORMAL, OPERATING)
        - architecture: Host hardware architecture information
    """
    try:
        result = get_ocp_client().get(f"/api/v2/obproxy/clusters/{cluster_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get OBProxy cluster detail for cluster {cluster_id}: {e}")
        raise


def get_obproxy_cluster_parameters(
    cluster_id: int
) -> Dict[str, Any]:
    """
    Query OBProxy cluster parameters
    
    This interface is used to query OBProxy cluster parameter settings.
    
    Args:
        cluster_id: The ID of the OBProxy cluster
    
    Returns:
        Dictionary containing ObproxyClusterParameter array. Each ObproxyClusterParameter includes:
        - name: Parameter name
        - description: Parameter description
        - needReboot: Whether reboot is required
        - valueString: Parameter value string
        - values: Array of ObproxyParameterValue (see below)
        
        ObproxyParameterValue data structure includes:
        - value: Parameter value
        - obproxies: Array of OBProxy list
    """
    try:
        result = get_ocp_client().get(f"/api/v2/obproxy/clusters/{cluster_id}/parameters")
        return result
    except Exception as e:
        logger.error(f"Failed to get parameters for OBProxy cluster {cluster_id}: {e}")
        raise


def get_tenant_databases(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database list
    
    This interface is used to get the database list of a tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database list. Each database includes:
        - dbName: Database name
        - charset: Character set
        - collation: Collation
        - primaryZone: Zone priority
        - readonly: Whether read-only
        - createTime: Creation time
        - connectionUrls: Array of OBProxy and connection string list (see below)
        - requiredSize: Database required size
        - id: Database ID
        
        ConnectionUrl data structure includes:
        - connectionStringType: Connection string type (OBPROXY or DIRECT)
        - obProxyAddress: OBProxy address (only valid when type is OBPROXY)
        - obProxyPort: OBProxy port (only valid when type is OBPROXY)
        - connectionString: Connection string
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/databases"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get databases for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def get_tenant_users(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database user list
    
    This interface is used to get the database user list of a tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database user list. Each user includes:
        - username: Username
        - globalPrivileges: Global privileges list
            - For MySQL tenant: global privileges list
            - For Oracle tenant: system privileges list
        - dbPrivileges: Database privileges list (only for MySQL tenant)
            - dbName: Database name
            - privileges: Database privileges list
        - objectPrivileges: Object privileges list (only for Oracle tenant)
            - dbObject: Database object (see below)
            - privileges: Object privileges list
        - grantedRoles: Roles granted to the user (only for Oracle tenant)
        - isLocked: Whether the user is locked
        - createTime: User creation time
        - connectionStrings: Array of OBProxy and connection string list (see below)
        - accessibleDatabases: Accessible databases (only for MySQL tenant)
        
        dbObject data structure includes:
        - objectType: Database object type (TABLE, VIEW, STORED_PROCEDURE)
        - objectName: Database object name
        - schemaName: Schema name
        
        ConnectionString data structure includes:
        - connectionStringType: Connection string type (OBPROXY or DIRECT)
        - obProxyAddress: OBProxy address (only valid when type is OBPROXY)
        - obProxyPort: OBProxy port (only valid when type is OBPROXY)
        - connectionString: Connection string
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/users"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get users for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def get_tenant_user_detail(
    cluster_id: int,
    tenant_id: int,
    username: str,
    host_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get database user detail
    
    This interface is used to get the detail of a database user.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
        username: Username
        host_name: Host name (optional)
    
    Returns:
        Dictionary containing database user detail. The user includes:
        - username: Username
        - globalPrivileges: Global privileges list
            - For MySQL tenant: global privileges list
            - For Oracle tenant: system privileges list
        - dbPrivileges: Database privileges list (only for MySQL tenant)
            - dbName: Database name
            - privileges: Database privileges list
        - objectPrivileges: Object privileges list (only for Oracle tenant)
            - dbObject: Database object (see below)
            - privileges: Object privileges list
        - grantedRoles: Roles granted to the user (only for Oracle tenant)
        - isLocked: Whether the user is locked
        - createTime: User creation time
        - connectionStrings: Array of OBProxy and connection string list (see below)
        - accessibleDatabases: Accessible databases (only for MySQL tenant)
        
        dbObject data structure includes:
        - objectType: Database object type (TABLE, VIEW, STORED_PROCEDURE)
        - objectName: Database object name
        - schemaName: Schema name
        
        ConnectionString data structure includes:
        - connectionStringType: Connection string type (OBPROXY or DIRECT)
        - obProxyAddress: OBProxy address (only valid when type is OBPROXY)
        - obProxyPort: OBProxy port (only valid when type is OBPROXY)
        - connectionString: Connection string
    """
    try:
        params = {}
        if host_name:
            params["hostName"] = host_name
        
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/users/{username}",
            params=params if params else None
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get user detail for cluster {cluster_id} tenant {tenant_id} user {username}: {e}")
        raise


def get_tenant_roles(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database role list
    
    This interface is used to get the database role list of a tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database role list. Each role includes:
        - name: Role name
        - createTime: Role creation time
        - updateTime: Role update time
        - globalPrivileges: System privileges list
        - objectPrivileges: Object privileges list (see below)
        - grantedRoles: Roles granted to this role
        - userGrantees: Users that this role is granted to
        - roleGrantees: Roles that this role is granted to
        
        objectPrivileges data structure includes:
        - dbObject: Database object (see below)
        - privileges: Object privileges list
        
        dbObject data structure includes:
        - objectType: Database object type (TABLE, VIEW, STORED_PROCEDURE)
        - objectName: Database object name
        - schemaName: Schema name
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/roles"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get roles for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def get_tenant_role_detail(
    cluster_id: int,
    tenant_id: int,
    role_name: str
) -> Dict[str, Any]:
    """
    Get database role detail
    
    This interface is used to get the detail of a database role.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
        role_name: Role name
    
    Returns:
        Dictionary containing database role detail. The role includes:
        - name: Role name
        - createTime: Role creation time
        - updateTime: Role update time
        - globalPrivileges: System privileges list
        - objectPrivileges: Object privileges list (see below)
        - grantedRoles: Roles granted to this role
        - userGrantees: Users that this role is granted to
        - roleGrantees: Roles that this role is granted to
        
        objectPrivileges data structure includes:
        - dbObject: Database object (see below)
        - privileges: Object privileges list
        
        dbObject data structure includes:
        - objectType: Database object type (TABLE, VIEW, STORED_PROCEDURE)
        - objectName: Database object name
        - schemaName: Schema name
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/roles/{role_name}"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get role detail for cluster {cluster_id} tenant {tenant_id} role {role_name}: {e}")
        raise


def get_tenant_objects(
    cluster_id: int,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get database object list
    
    This interface is used to get the database object list of a tenant.
    
    Args:
        cluster_id: The ID of the cluster
        tenant_id: The ID of the tenant
    
    Returns:
        Dictionary containing database object list. Each object includes:
        - objectType: Database object type (TABLE, VIEW, STORED_PROCEDURE)
        - objectName: Database object name (table name, view name, or stored procedure name)
        - schemaName: Schema name (usually the same as username)
        - fullName: Full name of the object (e.g., "U1.T1")
    """
    try:
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/objects"
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get objects for cluster {cluster_id} tenant {tenant_id}: {e}")
        raise


def get_metric_groups(
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
    
    Args:
        type: Metric type (required):
            - TOP: Query Top type metric metadata
            - NORMAL: Query normal metric metadata
        scope: Metric scope (required):
            - CLUSTER: Cluster metrics
            - TENANT: Tenant metrics
            - HOST: Host metrics
            - OBPROXY: OBProxy metrics
        page: Pagination page number, starting from 1, default: 1
        size: Pagination size, default: 10, maximum: 2000
        sort: Sorting rule, default sorted by id ascending (optional)
        target: Metric metadata type (optional):
            - OBCLUSTER: OceanBase cluster
            - OBPROXY: OBProxy cluster
        target_id: Metric metadata ID (optional):
            - When target is OBCLUSTER: OceanBase cluster ID
            - When target is OBPROXY: OBProxy cluster ID
    
    Returns:
        Dictionary containing metric group list and pagination information. Each metric group includes:
        - id: Metric group ID
        - key: Metric group code name
        - name: Metric group name (supports internationalization)
        - description: Metric group description (supports internationalization)
        - scope: Metric scope (CLUSTER, TENANT, HOST, OBPROXY)
        - type: Metric type (TOP, NORMAL)
        - metricGroups: Array of metric subgroups (see below)
        
        Metric subgroup data structure includes:
        - id: Metric subgroup ID
        - key: Metric subgroup code name
        - name: Metric subgroup name (supports internationalization)
        - description: Metric subgroup description (supports internationalization)
        - metrics: Array of metric metadata (see below)
        - withLabel: Whether it's a labeled monitoring data group
        
        Metric metadata data structure includes:
        - id: Metric ID
        - key: Metric code name
        - name: Metric name (supports internationalization)
        - description: Metric description (supports internationalization)
        - unit: Metric unit
        - displayByDefault: Whether to display by default
    """
    try:
        params = {
            "type": type,
            "scope": scope,
            "page": str(page),
            "size": str(size)
        }
        
        if sort:
            params["sort"] = sort
        if target:
            params["target"] = target
        if target_id is not None:
            params["targetId"] = str(target_id)
        
        result = get_ocp_client().get("/api/v2/monitor/metricGroups", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get metric groups: {e}")
        raise

def get_metric_data_with_label(
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
    
    Args:
        start_time: Start time of monitoring data (Datetime format, e.g., "2020-02-16T05:32:16+08:00")
        end_time: End time of monitoring data (Datetime format, e.g., "2020-02-16T07:32:16+08:00")
        metrics: Array of monitoring metrics (required)
        group_by: Array of labels for aggregating monitoring data (required):
            - app: Source of monitoring data collection (host, ob, or obproxy)
            - ob_cluster_name: OceanBase cluster name
            - ob_cluster_id: OceanBase cluster ID
        interval: Time granularity of monitoring data in seconds (required)
        labels: Filter conditions for monitoring data (required, e.g., ["app:ob", "ob_cluster_name=foo"])
        min_step: Query sampling interval, minimum monitoring result sampling time interval, default: 0 (optional)
        max_points: Maximum number of monitoring result points, default: 1440 (optional)
    
    Returns:
        Dictionary containing monitoring sampling groups array. Each group includes:
        - label values: Values for corresponding labels (e.g., app, ob_cluster_name, ob_cluster_id)
        - data: Array of monitoring sampling (see below)
        
        Each monitoring sampling includes:
        - timestamp: Sampling time point (seconds since 1970-01-01 00:00:00)
        - metric_name: Sampling value for corresponding metric (Float)
    """
    try:
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "metrics": ",".join(metrics),
            "groupBy": ",".join(group_by),
            "interval": str(interval),
            "labels": ",".join(labels)
        }
        
        if min_step is not None:
            params["minStep"] = str(min_step)
        if max_points is not None:
            params["maxPoints"] = str(max_points)
        
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
        Dictionary containing alarm event list and pagination information.
        Each alarm event includes:
        - id: Alarm event ID
        - appType: Application type (OceanBase, OCP, OMS, OBProxy, Log)
        - alarmType: Alarm type
        - scope: Alarm scope (Cluster, Tenant, Host, Service, Arbitration, Backup, OceanBaseLog, OBProxyLog, *, HostLog)
        - level: Alarm level [1~5] (Down, Critical, Alert, Caution, Info)
        - status: Alarm status (Active, Inactive, Silenced, Inhibited)
        - target: Alarm event target object, generated based on alarm rule target template
        - summary: Alarm event summary, generated based on alarm rule summary template
        - description: Alarm event details, generated based on alarm rule description template
        - activeAt: Alarm event generation time
        - resolvedAt: Alarm event resolution time
        - updatedAt: Alarm event update time
        - labels: Alarm event labels and values
    """
    try:
        params = {
            "page": str(page),
            "size": str(size)
        }
        
        if app_type:
            params["appType"] = app_type
        if scope:
            params["scope"] = scope
        if level is not None:
            params["level"] = str(level)
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
    """
    Query alarm event detail
    
    This interface is used to query detailed information of a specified alarm event.
    The caller must have read permissions for alarm functionality.
    
    Args:
        alarm_id: The ID of the alarm event
    
    Returns:
        Dictionary containing alarm event detail information. The alarm event includes:
        - id: Alarm event ID
        - appType: Application type (OceanBase, OCP, OMS, OBProxy, Log)
        - alarmType: Alarm type
        - scope: Alarm scope (Cluster, Tenant, Host, Service, Arbitration, Backup, OceanBaseLog, OBProxyLog, HostLog)
        - level: Alarm level [1~5] (Down, Critical, Alert, Caution, Info)
        - status: Alarm status (Active, Inactive, Silenced, Inhibited)
        - target: Alarm event target object, generated based on alarm rule target template
        - summary: Alarm event summary, generated based on alarm rule summary template
        - description: Alarm event details, generated based on alarm rule description template
        - activeAt: Alarm event generation time
        - resolvedAt: Alarm event resolution time
        - updatedAt: Alarm event update time
        - labels: Alarm event labels and values
        - alarmTarget: Alarm target information
        - obCluster: OceanBase cluster information
        - targetLabels: Target labels
    """
    try:
        result = get_ocp_client().get(f"/api/v2/alarm/alarms/{alarm_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get alarm {alarm_id}: {e}")
        raise




def get_inspection_tasks(
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
        - tag: InspectionTag information (see below)
        - inspectionObject: InspectionObject information (see below)
        - startTime: Inspection start time
        - endTime: Inspection end time (not present when task is running)
        - taskId: Inspection task ID
        - itemTotalCount: Total number of inspection items
        - itemFinishedCount: Number of finished inspection items
        - highRiskCount: Number of high-risk inspection items
        - mediumRiskCount: Number of medium-risk inspection items
        - lowRiskCount: Number of low-risk inspection items
        - taskState: Inspection task state
        
        InspectionTag data structure includes:
        - id: Inspection scenario tag ID
        - name: Tag name
        - description: Tag description
        - configType: Configuration type
        
        InspectionObject data structure includes:
        - objectId: Inspection object ID
        - inspectionObjectType: Inspection object type
        - name: Inspection object name
        - info: Additional object information (optional)
    """
    try:
        params = {}
        
        if inspectionObjectTypes:
            params["inspectionObjectTypes"] = ",".join(inspectionObjectTypes)
        if tags:
            params["tags"] = ",".join(str(tag) for tag in tags)
        if taskStates:
            params["taskStates"] = taskStates
        if name:
            params["name"] = name
        
        result = get_ocp_client().get("/api/v2/inspection/task", params=params if params else None)
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection tasks: {e}")
        raise


def get_inspection_overview(
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
        Dictionary containing inspection object list and pagination information.
        Each inspection object includes:
        - inspectionObject: InspectionObject information (see below)
        - scheduleState: Inspection schedule state
        - deadline: Inspection schedule deadline (empty means no deadline)
        
        InspectionObject data structure includes:
        - objectId: Inspection object ID
        - inspectionObjectType: Inspection object type (OB_CLUSTER, OB_TENANT, HOST, OB_PROXY)
        - name: Inspection object name
        - info: Additional object information (optional)
    """
    try:
        params = {}
        
        if object_ids:
            params["objectIds"] = ",".join(str(obj_id) for obj_id in object_ids)
        if inspection_object_type:
            params["inspectionObjectType"] = ",".join(inspection_object_type)
        if schedule_states:
            params["scheduleStates"] = ",".join(schedule_states)
        if name:
            params["name"] = name
        if parent_name:
            params["parentName"] = parent_name
        
        result = get_ocp_client().get("/api/v2/inspection/overview", params=params if params else None)
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection overview: {e}")
        raise


def get_inspection_report(report_id: int) -> Dict[str, Any]:
    """
    Get inspection report detail
    
    This interface is used to get inspection report detail.
    The caller must be authenticated through OCP application service.
    
    Args:
        report_id: Inspection report ID (can be obtained from the query inspection tasks interface)
    
    Returns:
        Dictionary containing inspection report detail information. The report includes:
        - id: Inspection report ID
        - tag: InspectionTag information (see below)
        - inspectionObject: InspectionObject information (see below)
        - startTime: Inspection start time
        - endTime: Inspection end time (not present when task is running)
        - taskId: Inspection task ID
        - itemTotalCount: Total number of inspection items
        - itemFinishedCount: Number of finished inspection items
        - highRiskCount: Number of high-risk inspection items
        - mediumRiskCount: Number of medium-risk inspection items
        - lowRiskCount: Number of low-risk inspection items
        - taskState: Inspection task state
        - inspectionItems: Array of all inspection items information in the report
        - reportItems: Array of all inspection item entries
        
        InspectionTag data structure includes:
        - id: Inspection scenario tag ID
        - name: Tag name
        - description: Tag description
        - configType: Configuration type
        
        InspectionObject data structure includes:
        - objectId: Inspection object ID
        - inspectionObjectType: Inspection object type
        - name: Inspection object name
        - info: Additional object information (optional)
        
        InspectionItem data structure includes:
        - id: Inspection item ID
        - identifier: Inspection item identifier
        - name: Inspection item name
        - description: Inspection item description
        - targetType: Target type
        - state: Inspection item state
        - configType: Configuration type
        - minVersion: Minimum version
        - maxVersion: Maximum version
        - scriptId: Script ID
        - unit: Unit
        - tags: Array of inspection tags
        - rules: Array of validation rules
        
        ReportItem data structure includes:
        - itemId: Inspection item ID
        - key: Item key (optional)
        - target: Target object
        - rawValue: Raw value
        - value: Formatted value
        - level: Risk level (HIGH, MEDIUM, LOW) - not present when there is no risk
    """
    try:
        result = get_ocp_client().get(f"/api/v2/inspection/report/{report_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection report {report_id}: {e}")
        raise


def run_inspection(
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
        Dictionary containing async task information. The task includes:
        - contents: Array of task information (see below)
        
        Task information includes:
        - id: Task ID
        - name: Task name
        - type: Task type
        - status: Task status (RUNNING, etc.)
        - operation: Task operation
        - creator: Task creator
        - executor: Task executor
        - startTime: Task start time
        - prohibitRollback: Whether rollback is prohibited
        - taskDefinitionId: Task definition ID
        - subtasks: Array of subtask information
    """
    if not inspection_object_type:
        raise ValueError("inspection_object_type is required")
    if not object_ids:
        raise ValueError("object_ids list cannot be empty")
    if not tags:
        raise ValueError("tags is required")
    
    # Validate inspection_object_type
    valid_types = ["OB_CLUSTER", "OB_TENANT", "HOST", "OB_PROXY"]
    if inspection_object_type not in valid_types:
        raise ValueError(f"inspection_object_type must be one of {valid_types}")
    
    # Validate tags
    valid_tags = [1, 2, 3, 4]
    if tags not in valid_tags:
        raise ValueError(f"tags must be one of {valid_tags}")
    
    payload = {
        "inspectionObjectType": inspection_object_type,
        "objectIds": object_ids,
        "tags": tags,
    }
    
    try:
        result = get_ocp_client().post("/api/v2/inspection/run", json=payload)
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
        Dictionary containing inspection result aggregation information.
        The data includes:
        - contents: Array of InspectionReportAggrInfo (see below)
        
        InspectionReportAggrInfo data structure includes:
        - reportId: Inspection report ID
        - objectId: Inspection object ID
        - objectName: Inspection object name
        - objectType: Inspection object type
        - tag: Inspection scenario information (see below)
        - startTime: Inspection start time
        - endTime: Inspection end time
        - itemResults: Array of inspection item results (see below)
        
        Inspection scenario (tag) data structure includes:
        - id: Inspection scenario ID
        - name: Inspection scenario name
        - description: Inspection scenario description
        - configType: Inspection scenario configuration type
        
        Inspection item result (itemResults) data structure includes:
        - itemId: Inspection item ID
        - name: Inspection item name
        - description: Inspection item description
        - reportItems: Array of inspection item result details (see below)
        - rules: Array of inspection item rules (see below)
        
        Report item (reportItems) data structure includes:
        - itemId: Inspection item ID
        - key: Inspection item key
        - value: Inspection value
        - rawValue: Inspection item raw value
        - target: Inspection item target
        - level: Risk level (HIGH, MEDIUM, LOW)
        
        Rule data structure includes:
        - level: Risk level
        - validator: Risk validation expression
    """
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
        result = get_ocp_client().get(f"/api/v2/inspection/report/info/item/{item_id}", params=params)
        return result
    except Exception as e:
        logger.error(f"Failed to get inspection item last result for item {item_id}: {e}")
        raise


def get_inspection_report_info(
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
        - contents: Array of InspectionReportAggrInfo (see below)
        
        InspectionReportAggrInfo data structure includes:
        - reportId: Inspection report ID
        - objectId: Inspection object ID
        - objectName: Inspection object name
        - objectType: Inspection object type
        - tag: Inspection scenario information (see below)
        - startTime: Inspection start time
        - endTime: Inspection end time
        - resultList: Array of inspection item results (see below)
        
        Inspection scenario (tag) data structure includes:
        - id: Inspection scenario ID
        - name: Inspection scenario name
        - description: Inspection scenario description
        - configType: Inspection scenario configuration type
        
        Inspection item result (resultList) data structure includes:
        - itemId: Inspection item ID
        - name: Inspection item name
        - description: Inspection item description
        - reportItems: Array of inspection item result details (see below)
        - rules: Array of inspection item rules (see below)
        
        Report item (reportItems) data structure includes:
        - itemId: Inspection item ID
        - key: Inspection item key
        - value: Inspection value
        - rawValue: Inspection item raw value
        - target: Inspection item target
        - level: Risk level (HIGH, MEDIUM, LOW)
        
        Rule data structure includes:
        - level: Risk level
        - validator: Risk validation expression
    """
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
    Can query specific SQL performance metrics through conditions such as
    whether it's internal SQL, SQL text keywords, and advanced search.
    
    Note: This interface query is time-consuming. If the response time is long,
    please appropriately reduce the query frequency, query time range, or
    number of concurrent requests.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        start_time: Start time (Datetime format, e.g., "2020-02-16T05:32:16+08:00") (required)
        end_time: End time (Datetime format, e.g., "2020-02-16T07:32:16+08:00") (required)
        server_id: Query SQL executed on specified OceanBase server (optional)
        inner: Whether to include internal SQL (optional, default: false)
        sql_text: SQL text keyword (case-insensitive) (optional)
        search_attr: Advanced search metric name (optional, requires searchOp and searchVal)
        search_op: Advanced search operator (optional):
            - EQ: Equal
            - NE: Not equal
            - GT: Greater than
            - GE: Greater than or equal
            - LT: Less than
            - LE: Less than or equal
        search_val: Advanced search value (optional, requires searchAttr and searchOp)
    
    Returns:
        Dictionary containing SQL performance statistics list.
        Each SQL performance data includes:
        - sqlId: SQL ID
        - server: OceanBase server address
        - dbName: Database where SQL was executed
        - userName: User who executed SQL
        - sqlType: SQL type (SELECT, INSERT, UPDATE, DELETE, REPLACE, EXPLAIN, UNKNOWN)
        - sqlTextShort: First 100 characters of SQL text
        - inner: Whether it's internal SQL
        - waitEvent: Most time-consuming internal event
        - executions: Total execution count
        - execPs: Average executions per second
        - avgAffectedRows: Average affected rows
        - avgReturnRows: Average returned rows
        - avgPartitionCount: Average partition count accessed
        - failCount: Total error count
        - failPercentage: Error percentage [0, 1]
        - avgElapsedTime: Average response time (ms)
        - maxElapsedTime: Maximum response time (ms)
        - avgCpuTime: Average CPU time (ms)
        - maxCpuTime: Maximum CPU time (ms)
        - And many more performance metrics...
    """
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
            params=params
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get tenant top SQL: {e}")
        raise


def get_sql_trends(
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
    statistics at a specified timestamp. This interface can be used to observe SQL
    performance changes over time.
    
    Note: When specifying a large time range, the number of sampling points returned
    will approach 120 points.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        sql_id: SQL ID (required)
        start_time: Start time (Datetime format, e.g., "2020-02-16T05:32:16+08:00") (required)
        end_time: End time (Datetime format, e.g., "2020-02-16T07:32:16+08:00") (required)
        server_id: Query SQL performance on specified OceanBase server (optional)
        db_name: Query SQL performance in specified database (optional)
    
    Returns:
        Dictionary containing SQL performance sampling data array.
        Each sampling point includes:
        - timestamp: Sampling timestamp
        - executions: Total execution count
        - execPs: Average executions per second
        - avgAffectedRows: Average affected rows
        - avgReturnRows: Average returned rows
        - avgPartitionCount: Average partition count accessed
        - failCount: Total error count
        - failPercentage: Error percentage [0, 1]
        - avgElapsedTime: Average response time (ms)
        - maxElapsedTime: Maximum response time (ms)
        - avgCpuTime: Average CPU time (ms)
        - maxCpuTime: Maximum CPU time (ms)
        - And many more performance metrics...
    """
    try:
        params = {
            "startTime": start_time,
            "endTime": end_time,
        }
        
        if server_id is not None:
            params["serverId"] = str(server_id)
        if db_name:
            params["dbName"] = db_name
        
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/sqls/{sql_id}/trends",
            params=params
        )
        return result
    except Exception as e:
        logger.error(f"Failed to get SQL trends: {e}")
        raise


def get_sql_text(
    cluster_id: int,
    tenant_id: int,
    sql_id: str,
    start_time: str,
    end_time: str,
) -> Dict[str, Any]:
    """
    Query SQL full text
    
    Query the full text of SQL with specified ID.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        sql_id: SQL ID (required)
        start_time: Start time (Datetime format, e.g., "2020-02-16T05:32:16+08:00") (required)
        end_time: End time (Datetime format, e.g., "2020-02-16T07:32:16+08:00") (required)
    
    Returns:
        Dictionary containing SQL full text:
        - fulltext: SQL full text
    """
    try:
        params = {
            "startTime": start_time,
            "endTime": end_time,
        }
        
        result = get_ocp_client().get(
            f"/api/v2/ob/clusters/{cluster_id}/tenants/{tenant_id}/sqls/{sql_id}/text",
            params=params
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
    """
    Query slow SQL list
    
    This interface is used to query slow SQL list.
    The caller must have read permissions for the specified tenant.
    
    Args:
        cluster_id: Cluster ID (required)
        tenant_id: Tenant ID (required)
        start_time: Start time (UTC format: YYYY-MM-DDThh:mm:ssZ, e.g., "2023-04-12T04:38:38Z") (required)
        end_time: End time (UTC format: YYYY-MM-DDThh:mm:ssZ, e.g., "2023-04-12T05:38:38Z") (required)
        server_id: Query SQL performance on specified OceanBase server (optional)
        inner: Whether it's internal SQL (optional)
        sql_text: SQL text keyword (case-insensitive) (optional)
        filter_expression: Filter expression, all fields referenced by @ (optional)
        limit: Number of TOP results to return (optional)
        sql_text_length: Maximum length of returned SQL text (optional)
    
    Returns:
        Dictionary containing slow SQL list.
        Each SlowSQL includes:
        - sqlId: SQL ID
        - server: Server address
        - serverIp: OBServer node IP
        - dbName: Database name
        - userName: User name
        - sqlTextShort: SQL text (first 100 characters)
        - sqlType: SQL type
        - executions: Total execution count
        - execPs: Average executions per second
        - avgElapsedTime: Average response time (ms)
        - maxElapsedTime: Maximum response time (ms)
        - avgCpuTime: Average CPU time (ms)
        - maxCpuTime: Maximum CPU time (ms)
        - failCount: Error count
        - failPercentage: Error percentage
        - And many more performance metrics...
    """
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
            params=params
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
        Dictionary containing report information:
        - id: Report unique ID
        - clusterName: Cluster name
        - obClusterId: OceanBase cluster ID
        - clusterId: OCP cluster ID
        - name: Report name
        - beginReportTime: Report start time
        - endReportTime: Report end time
        - generateTime: Report generation time
        - status: Report status (CREATING/SUCCESSFUL/FAILED)
        - taskInstanceId: Associated task instance ID
        - scope: Report scope (CLUSTER/TENANT, currently only CLUSTER is supported)
        - creator: Operator
    """
    try:
        payload = {
            "startSnapshotId": start_snapshot_id,
            "endSnapshotId": end_snapshot_id,
            "name": name,
        }
        
        result = get_ocp_client().post(
            f"/api/v2/ob/clusters/{cluster_id}/performance/workload/reports",
            json=payload
        )
        return result
    except Exception as e:
        logger.error(f"Failed to create performance report: {e}")
        raise


def get_performance_report(
    cluster_id: int,
    report_id: int,
) -> Dict[str, Any]:
    """
    Query performance report
    
    Query cluster performance report.
    The caller must have read and write permissions for the specified cluster.
    
    Note: This endpoint returns binary HTML content. The response will contain
    the HTML content as a string or bytes that can be saved as an HTML file.
    
    Args:
        cluster_id: Target OceanBase cluster ID (required)
        report_id: Performance report ID (required)
    
    Returns:
        Dictionary containing report data. The actual structure depends on
        how OCP returns the binary content (may be base64 encoded or as text).
    """
    try:
        # This endpoint returns binary HTML, we'll let the client handle it
        # and return whatever format OCP provides
        client = get_ocp_client()
        path = f"/api/v2/ob/clusters/{cluster_id}/performance/workload/reports/{report_id}"
        
        # Make request directly to get binary content
        from datetime import datetime, timezone
        
        # Generate signature manually for binary request
        rfc_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers = {
            "x-ocp-origin": "mcp-server",
            "Date": rfc_date,
        }
        
        signature = client._get_signature(
            method="GET",
            path=path,
            headers=headers,
            params=None,
            body=None,
            rfc_date=rfc_date,
        )
        
        headers["Authorization"] = f"OCP-ACCESS-KEY-HMACSHA1 {client.access_key_id}:{signature}"
        
        url = f"{client.base_url}{path}"
        response = client.client.get(url, headers=headers)
        response.raise_for_status()
        
        # Return as dict with content
        return {
            "content": response.content,
            "content_type": response.headers.get("Content-Type", "text/html"),
            "status_code": response.status_code,
        }
    except Exception as e:
        logger.error(f"Failed to get performance report: {e}")
        raise
