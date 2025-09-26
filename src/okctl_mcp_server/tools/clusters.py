import asyncio
import re
from typing import Optional
from okctl_mcp_server.utils.errors import format_error
from okctl_mcp_server.utils.security import validate_identifier, safe_execute_command, SecurityError

# 导入mcp实例
from okctl_mcp_server import mcp

# 集群相关的工具

@mcp.tool()
def list_all_clusters():
    """列出所有的OceanBase集群"""
    try:
        success, output = safe_execute_command(["okctl", "cluster", "list"])
        if success:
            if not output.strip():
                return "没有找到集群"
            return output
        else:
            return output
    except Exception as e:
        return format_error(e)

@mcp.tool()
def show_cluster(cluster_name: str, namespace: str = "default"):
    """显示指定OceanBase集群的概览
    IMPORTANT:
        当集群状态不是"Running"时，直接停止回答返回信息
    Args:
        cluster_name: 要显示的集群名称
        namespace: 集群所在的命名空间（默认为"default"）
    Important:
        1. 不要在短时间内重复调用该命令
    """
    if not cluster_name:
        return "必须指定集群名称"
    try:
        validate_identifier(cluster_name, "Cluster name")
        validate_identifier(namespace, "Namespace")
        
        success, output = safe_execute_command(["okctl", "cluster", "show", cluster_name, "-n", namespace])
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def scale_cluster(cluster_name: str, zones: str, namespace: str = "default"):
    """扩缩OceanBase集群，支持添加/调整/删除可用区

    Args:
        cluster_name: 要扩缩的集群名称
        zones: 集群的可用区，例如 'z1=1'，设置副本数为0以删除可用区,每次只能修改一个可用区
        namespace: 集群所在的命名空间（默认为"default"）
    Important:
        1. 该操作可能需要几分钟时间
    """
    if not cluster_name or not zones:
        return "必须指定集群名称和可用区"
    try:
        validate_identifier(cluster_name, "Cluster name")
        validate_identifier(namespace, "Namespace")
        # Basic validation for zones format
        if not re.match(r'^[a-zA-Z0-9_=-]+$', zones):
            return "Error: Invalid zones format"
        
        success, output = safe_execute_command(["okctl", "cluster", "scale", cluster_name, "-n", namespace, f"--zones={zones}"])
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def update_cluster(
    cluster_name: str,
    namespace: str = "default",
    cpu: Optional[str] = None,
    memory: Optional[str] = None,
    data_storage_class: Optional[str] = None,
    data_storage_size: Optional[str] = None,
    log_storage_class: Optional[str] = None,
    log_storage_size: Optional[str] = None,
    redo_log_storage_class: Optional[str] = None,
    redo_log_storage_size: Optional[str] = None,
):
    """更新OceanBase集群，支持CPU/内存/存储的调整

    Args:
        cluster_name: 要更新的集群名称
        namespace: 集群所在的命名空间（默认为"default"）
        cpu: 观察者的CPU（默认为2）
        memory: 观察者的内存（默认为10）
        data_storage_class: 数据存储的存储类
        data_storage_size: 数据存储的大小（默认为50）
        log_storage_class: 日志存储的存储类
        log_storage_size: 日志存储的大小（默认为20）
        redo_log_storage_class: 重做日志存储的存储类
        redo_log_storage_size: 重做日志存储的大小（默认为50）
    Important:
        1. 该操作可能需要几分钟时间
    """
    if not cluster_name:
        return "必须指定集群名称"
    try:
        validate_identifier(cluster_name, "Cluster name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "cluster", "update", cluster_name, "-n", namespace]

        # 添加可选参数
        if cpu:
            cmd.extend(["--cpu", cpu])
        if memory:
            cmd.extend(["--memory", memory])
        if data_storage_class:
            cmd.extend(["--data-storage-class", data_storage_class])
        if data_storage_size:
            cmd.extend(["--data-storage-size", data_storage_size])
        if log_storage_class:
            cmd.extend(["--log-storage-class", log_storage_class])
        if log_storage_size:
            cmd.extend(["--log-storage-size", log_storage_size])
        if redo_log_storage_class:
            cmd.extend(["--redo-log-storage-class", redo_log_storage_class])
        if redo_log_storage_size:
            cmd.extend(["--redo-log-storage-size", redo_log_storage_size])

        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def upgrade_cluster(cluster_name: str, image: str, namespace: str = "default"):
    """升级OceanBase集群，请指定新的镜像

    Args:
        cluster_name: 要升级的集群名称
        image: 观察者的镜像
        namespace: 集群所在的命名空间（默认为"default"）
    Important:
        1. 该操作可能需要几分钟时间
    """
    if not cluster_name or not image:
        return "必须指定集群名称和镜像"
    try:
        validate_identifier(cluster_name, "Cluster name")
        validate_identifier(namespace, "Namespace")
        
        success, output = safe_execute_command(["okctl", "cluster", "upgrade", cluster_name, "-n", namespace, "--image", image])
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def delete_cluster(cluster_name: str, namespace: str = "default"):
    """删除指定命名空间中的OceanBase集群

    Args:
        cluster_name: 要删除的集群名称
        namespace: 要从中删除集群的命名空间
    """
    if not cluster_name:
        return "必须指定集群名称"
    try:
        validate_identifier(cluster_name, "Cluster name")
        validate_identifier(namespace, "Namespace")
        
        success, output = safe_execute_command(["okctl", "cluster", "delete", cluster_name, "-n", namespace])
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
async def create_cluster(
    cluster_name: str,
    namespace: str = "default",
    backup_storage_address: Optional[str] = None,
    backup_storage_path: Optional[str] = None,
    cpu: Optional[str] = None,
    data_storage_class: Optional[str] = None,
    data_storage_size: Optional[str] = None,
    id: Optional[str] = None,
    image: Optional[str] = None,
    log_storage_class: Optional[str] = None,
    log_storage_size: Optional[str] = None,
    memory: Optional[str] = None,
    mode: Optional[str] = None,
    parameters: Optional[str] = None,
    redo_log_storage_class: Optional[str] = None,
    redo_log_storage_size: Optional[str] = None,
    root_password: Optional[str] = None,
    zones: Optional[str] = None,
):
    """在指定命名空间中创建新的OceanBase集群

    Args:
        cluster_name: 要创建的集群名称
        namespace: 要在其中创建集群的命名空间（默认为"default"）
        backup_storage_address: 备份存储的存储类
        backup_storage_path: 备份存储的大小
        cpu: 观察者的CPU（默认为2）
        data_storage_class: 数据存储的存储类（默认为"local-path"）
        data_storage_size: 数据存储的大小（默认为50）
        id: 集群的ID
        image: 观察者的镜像（默认为"quay.io/oceanbase/oceanbase-cloud-native:4.3.3.1-101000012024102216"）
        log_storage_class: 日志存储的存储类（默认为"local-path"）
        log_storage_size: 日志存储的大小（默认为20）
        memory: 观察者的内存（默认为10）
        mode: 集群的模式（默认为"service"）
        parameters: OBCluster中的其他参数设置，例如__min_full_resource_pool_memory
        redo_log_storage_class: 重做日志存储的存储类（默认为"local-path"）
        redo_log_storage_size: 重做日志存储的大小（默认为50）
        root_password: 集群的root密码
        zones: 集群的可用区，例如'--zones=<zone>=<replica>'（默认为[z1=1]）
    Important:
        1. 该操作可能需要几分钟时间
    """
    if not cluster_name:
        return "必须指定集群名称"
    try:
        validate_identifier(cluster_name, "Cluster name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "cluster", "create", cluster_name, "-n", namespace]

        # 添加可选参数
        if backup_storage_address:
            cmd.extend(["--backup-storage-address", backup_storage_address])
        if backup_storage_path:
            cmd.extend(["--backup-storage-path", backup_storage_path])
        if cpu:
            cmd.extend(["--cpu", cpu])
        if data_storage_class:
            cmd.extend(["--data-storage-class", data_storage_class])
        if data_storage_size:
            cmd.extend(["--data-storage-size", data_storage_size])
        if id:
            cmd.extend(["--id", id])
        if image:
            cmd.extend(["--image", image])
        if log_storage_class:
            cmd.extend(["--log-storage-class", log_storage_class])
        if log_storage_size:
            cmd.extend(["--log-storage-size", log_storage_size])
        if memory:
            cmd.extend(["--memory", memory])
        if mode:
            cmd.extend(["--mode", mode])
        if parameters:
            cmd.extend(["--parameters", parameters])
        if redo_log_storage_class:
            cmd.extend(["--redo-log-storage-class", redo_log_storage_class])
        if redo_log_storage_size:
            cmd.extend(["--redo-log-storage-size", redo_log_storage_size])
        if root_password:
            cmd.extend(["--root-password", root_password])
        if zones:
            cmd.extend(["--zones", zones])

        # 执行创建集群命令
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout_bytes, stderr_bytes = await process.communicate()

        stdout = stdout_bytes.decode("utf-8") if stdout_bytes else ""
        stderr = stderr_bytes.decode("utf-8") if stderr_bytes else ""

        if process.returncode != 0:
            return format_error(f"命令执行失败: {stderr}")

        # 创建命令执行成功后，异步检测集群是否真正创建完成
        result = stdout

        # 异步等待集群就绪
        max_retries = 30  # 最大重试次数
        retry_interval = 10  # 重试间隔（秒）

        for i in range(max_retries):
            # 使用 okctl cluster list 检查集群状态
            check_process = await asyncio.create_subprocess_exec(
                "okctl", "cluster", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            check_stdout_bytes, _ = await check_process.communicate()
            check_stdout = (
                check_stdout_bytes.decode("utf-8") if check_stdout_bytes else ""
            )

            if cluster_name in check_stdout and "running" in check_stdout.lower():
                result += f"\n集群 {cluster_name} 已成功创建并准备就绪！"
                return result
            if i < max_retries - 1:
                await asyncio.sleep(retry_interval)
        # 如果达到最大重试次数仍未就绪
        result += f"\n警告：集群 {cluster_name} 已创建，但在规定时间内未检测到running状态。请手动检查集群状态。"
        return result
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)
