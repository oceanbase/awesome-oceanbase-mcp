import os
import logging
from typing import Optional, Dict, Any
from mysql.connector import connect, Error
from okctl_mcp_server.utils.security import validate_identifier, safe_execute_command, SecurityError

# 导入mcp实例
from okctl_mcp_server import mcp

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("okctl_mcp_server")

# 全局配置
global_config = None

@mcp.tool()
def configure_cluster_connection(
    cluster_name: str,
    tenant_name: str = "sys",
    namespace: str = "default",
    user: str = "root",
    password: Optional[str] = None,
    port: int = 2881,
    zone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    配置集群查询相关的连接

    Args:
        cluster_name: 集群名称
        tenant_name: 租户名称，默认为sys
        namespace: 命名空间，默认为default
        user: 用户，默认为root
        password: 租户密码，如果未提供则从环境变量中获取集群密码
        port: 端口，默认为2881
        zone: 指定要连接的可用区，如果不指定则使用第一个可用的zone

    Returns:
        数据库连接配置信息
    """
    if not cluster_name:
        raise ValueError("必须指定集群名称")

    try:
        validate_identifier(cluster_name, "Cluster name")
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        # 首先确认集群存在
        success, result_stdout = safe_execute_command(["okctl", "cluster", "show", cluster_name, "-n", namespace])
        if not success:
            raise ValueError(f"集群 {cluster_name} 不存在")

        # 从集群信息中提取 zone 名称
        zones = []
        in_zone_section = False
        for line in result_stdout.split("\n"):
            line = line.strip()
            if not line:
                continue

            # 检测是否进入ZONE部分
            if line.startswith("ZONE"):
                in_zone_section = True
                continue
            # 检测是否离开ZONE部分（遇到下一个标题部分）
            elif line and line.startswith("KEY") and "ZONE" not in line:
                in_zone_section = False
                continue

            # 在ZONE部分中解析可用区信息
            if in_zone_section and "running" in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    zones.append(parts[0].strip())

        if not zones:
            raise ValueError(f"未找到集群 {cluster_name} 的可用区信息")

        # 如果指定了zone，验证其是否存在
        if zone and zone not in zones:
            raise ValueError(
                f"指定的可用区 {zone} 不存在于集群 {cluster_name} 中。可用的区域: {', '.join(zones)}"
            )

        # 使用 kubectl 命令获取所有 pod 信息
        success, kubectl_output = safe_execute_command(["kubectl", "get", "pods", "-o", "wide"])
        if not success:
            raise ValueError("未找到任何 POD 信息")

        # 解析 POD 信息，根据指定的zone筛选pod
        pod_info = kubectl_output.strip().split("\n")
        pod_data = []

        target_zone = zone if zone else zones[0]
        for line in pod_info[1:]:  # 跳过标题行
            parts = line.split()
            if len(parts) >= 6:  # 确保有足够的列
                pod_name = parts[0]
                # 检查 pod 名称是否与目标 zone 匹配
                if target_zone in pod_name:
                    pod_ip = parts[5]
                    pod_data.append({"pod_name": pod_name, "pod_ip": pod_ip})

        if not pod_data:
            raise ValueError(f"未找到与可用区 {target_zone} 相关的 POD 信息")

        # 获取第一个 pod 的 IP 地址
        ip_address = pod_data[0]["pod_ip"]
        logger.info(
            f"获取到集群IP地址: {ip_address}，来自POD: {pod_data[0]['pod_name']}，可用区: {target_zone}"
        )

        # 如果没有提供密码, 则从环境变量中获取集群密码
        if not password:
            password = os.getenv("OB_CLUSTER_PASSWORD")
            if not password:
                raise ValueError("未提供密码，且未设置环境变量 OB_CLUSTER_PASSWORD")
            else:
                logger.info("使用环境变量 OB_CLUSTER_PASSWORD 作为密码")

        # 配置数据库连接
        global global_config
        global_config = {
            "host": ip_address,
            "port": port,
            "user": f"{user}@{tenant_name}",
            "password": password,
        }

        logger.info(
            f"数据库连接配置成功: host={ip_address}, port={port}, user={user}, tenant_name={tenant_name}"
        )

        return global_config
    except SecurityError as e:
        logger.error(f"Security error: {str(e)}")
        raise ValueError(f"Security error: {str(e)}")
    except Exception as e:
        logger.error(f"配置数据库连接时发生错误: {str(e)}")
        raise ValueError(
            f"配置数据库连接时发生错误: {str(e)}, 目前连接配置为: {global_config}"
        )

@mcp.tool()
def execute_cluster_sql(
    query: str,
    cluster_name: str = None,
    tenant_name: str = None,
    database: str = "oceanbase",
    namespace: str = "default",
) -> str:
    """
    在集群指定租户下执行SQL查询，支持各种常见SQL查询语句，如SELECT、SHOW TABLES、SHOW COLUMNS等

    Args:
        query: SQL查询语句
        cluster_name: 集群名称，如果提供则会重新配置连接
        tenant_name: 租户名称，如果提供则会重新配置连接
        database: 数据库名称，默认为oceanbase，也可以为业务数据库
        namespace: 命名空间，默认为default

    Returns:
        查询结果
    """
    global global_config

    # 如果提供了集群名称和租户名称，则重新配置连接
    if cluster_name and tenant_name:
        try:
            configure_cluster_connection(cluster_name, tenant_name, namespace)
        except ValueError as e:
            return f"配置数据库连接失败: {str(e)}, 目前连接配置为: {global_config}"

    # 检查是否已配置连接
    if not global_config:
        return "未配置数据库连接，请先调用 configure_cluster_connection"

    logger.info(f"执行SQL查询: {query}")

    try:
        with connect(**global_config, database=database) as conn:
            with conn.cursor() as cursor:
                # 执行SQL查询
                cursor.execute(query)

                # 特殊处理SHOW TABLES
                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = [f"{global_config['tenant_name']}租户中的表: "]  # 标题
                    result.extend([table[0] for table in tables])
                    return "\n".join(result)

                elif query.strip().upper().startswith("SHOW COLUMNS"):
                    resp_header = "表的列信息: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                elif query.strip().upper().startswith("DESCRIBE"):
                    resp_header = "表的描述: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                # 常规SELECT查询
                elif query.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return "\n".join([",".join(columns)] + result)

                # 非SELECT查询
                else:
                    conn.commit()
                    return f"查询执行成功。影响的行数: {cursor.rowcount}"

    except Error as e:
        logger.error(f"执行SQL '{query}'时出错: {e}")
        return f"执行查询时出错: {str(e)}，SQL语句为: {query}"
    except Exception as e:
        logger.error(
            f"执行查询时发生未知错误: {str(e)}，目前连接配置为: {global_config}，SQL语句为: {query}"
        )
        return f"执行查询时发生未知错误: {str(e)}, 目前连接配置为: {global_config}，SQL语句为: {query}"
