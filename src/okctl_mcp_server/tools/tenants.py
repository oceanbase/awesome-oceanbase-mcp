import asyncio
from typing import Optional
from okctl_mcp_server.utils.errors import format_error
from okctl_mcp_server.utils.security import validate_identifier, safe_execute_command, SecurityError

# 导入mcp实例
from okctl_mcp_server import mcp

# 租户相关的工具

@mcp.tool()
def list_tenants(namespace: str = "default"):
    """列举租户

    Args:
        namespace: 命名空间（默认为"default"）
    """
    try:
        validate_identifier(namespace, "Namespace")
        success, output = safe_execute_command(["okctl", "tenant", "list", "-p", namespace])
        if success:
            if not output.strip():
                return "没有找到租户"
            return output
        else:
            return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
async def create_tenant(
    tenant_name: str,
    cluster: str,
    namespace: str = "default",
    archive_source: Optional[str] = None,
    bak_data_source: Optional[str] = None,
    bak_encryption_password: Optional[str] = None,
    charset: Optional[str] = None,
    connect_white_list: Optional[str] = None,
    cpu_count: Optional[str] = None,
    from_tenant: Optional[str] = None,
    iops_weight: Optional[int] = None,
    log_disk_size: Optional[str] = None,
    max_iops: Optional[int] = None,
    memory_size: Optional[str] = None,
    min_iops: Optional[int] = None,
    oss_access_id: Optional[str] = None,
    oss_access_key: Optional[str] = None,
    restore: bool = False,
    priority: Optional[str] = None,
    restore_type: Optional[str] = None,
    root_password: Optional[str] = None,
    tenant_name_override: Optional[str] = None,
    unit_number: Optional[int] = None,
    unlimited: Optional[bool] = None,
    until_timestamp: Optional[str] = None,
):
    """创建租户

    Args:
        tenant_name: 租户名称
        cluster: 租户所在集群名称（必需）
        namespace: 命名空间（默认为"default"）
        archive_source: 归档来源
        bak_data_source: 备份数据来源
        bak_encryption_password: 备份加密密码
        charset: 租户使用的字符集（默认为"utf8mb4"）
        connect_white_list: 租户使用的连接白名单（默认为"%"）
        cpu_count: 单位的CPU数量（默认为"1"）
        from_tenant: 创建租户时使用的源租户或归档租户
        iops_weight: 单位的IOPS权重（默认为1）
        log_disk_size: 单位的日志磁盘大小（默认为"4Gi"）
        max_iops: 单位的最大IOPS（默认为1024）
        memory_size: 单位的内存大小（默认为"2Gi"）
        min_iops: 单位的最小IOPS（默认为1024）
        oss_access_id: 归档的OSS访问ID
        oss_access_key: 归档的OSS访问密钥
        priority: 租户的可用区优先级，格式为'Zone=Priority'，可使用逗号分隔多个优先级（必需）
        restore: 是否从备份恢复，默认为False
        restore_type: 恢复类型，支持OSS或NFS（默认为"OSS"）
        root_password: 租户的root密码，如果不指定，则会自动生成
        tenant_name_override: 租户名称覆盖，如果不指定，则使用k8s的名称
        unit_number: 租户的单位数量（默认为1）
        unlimited: 是否不限制时间，默认为True
        until_timestamp: 租户的截止时间
    Important:
        1. 该操作可能需要几分钟时间
    """
    if not cluster:
        return "必须指定集群名称"
    if not tenant_name:
        return "必须指定租户名称"
    if not priority:
        return "必须指定租户的可用区优先级，例如'--priority zone1=1,zone2=2'"
    if from_tenant and not root_password:
        return "创建备用租户时，必须指定主租户的root密码"
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(cluster, "Cluster name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "create", tenant_name, f"--cluster={cluster}", "-n", namespace, "--priority", priority]

        # 添加可选参数
        if archive_source:
            cmd.extend(["--archive-source", archive_source])
        if bak_data_source:
            cmd.extend(["--bak-data-source", bak_data_source])
        if bak_encryption_password:
            cmd.extend(["--bak-encryption-password", bak_encryption_password])
        if charset:
            cmd.extend(["--charset", charset])
        if connect_white_list:
            cmd.extend(["--connect-white-list", connect_white_list])
        if cpu_count:
            cmd.extend(["--cpu-count", cpu_count])
        if from_tenant:
            cmd.extend(["--from", from_tenant])
        if iops_weight is not None:
            cmd.extend(["--iops-weight", str(iops_weight)])
        if log_disk_size:
            cmd.extend(["--log-disk-size", log_disk_size])
        if max_iops is not None:
            cmd.extend(["--max-iops", str(max_iops)])
        if memory_size:
            cmd.extend(["--memory-size", memory_size])
        if min_iops is not None:
            cmd.extend(["--min-iops", str(min_iops)])
        if oss_access_id:
            cmd.extend(["--oss-access-id", oss_access_id])
        if oss_access_key:
            cmd.extend(["--oss-access-key", oss_access_key])
        if restore:
            cmd.append("-r")
        if restore_type:
            cmd.extend(["--restore-type", restore_type])
        if root_password:
            cmd.extend(["--root-password", root_password])
        if tenant_name_override:
            cmd.extend(["--tenant-name", tenant_name_override])
        if unit_number is not None:
            cmd.extend(["--unit-number", str(unit_number)])
        if unlimited is not None:
            cmd.extend(["--unlimited", str(unlimited).lower()])
        if until_timestamp:
            cmd.extend(["--until-timestamp", until_timestamp])

        # 执行创建租户命令
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout_bytes, stderr_bytes = await process.communicate()

        stdout = stdout_bytes.decode("utf-8") if stdout_bytes else ""
        stderr = stderr_bytes.decode("utf-8") if stderr_bytes else ""

        if process.returncode != 0:
            return format_error(f"命令执行失败: {stderr}")

        # 创建命令执行成功后，异步检测租户是否真正创建完成
        result = stdout

        # 异步等待租户就绪
        max_retries = 30  # 最大重试次数
        retry_interval = 10  # 重试间隔（秒）

        for i in range(max_retries):
            # 使用 okctl tenant list 检查租户状态
            check_process = await asyncio.create_subprocess_exec(
                "okctl", "tenant", "list", "-p", namespace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            check_stdout_bytes, check_stderr_bytes = await check_process.communicate()
            check_stdout = (
                check_stdout_bytes.decode("utf-8") if check_stdout_bytes else ""
            )

            # 检查租户是否处于running状态
            if tenant_name in check_stdout and "running" in check_stdout.lower():
                result += f"\n租户 {tenant_name} 已成功创建并准备就绪！"
                return result
            # 如果还没准备好，等待一段时间后重试
            if i < max_retries - 1:
                await asyncio.sleep(retry_interval)
        # 如果达到最大重试次数仍未就绪
        result += f"\n警告：租户 {tenant_name} 已创建，但在规定时间内未检测到running状态。请手动检查租户状态。"
        return result
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def delete_tenant(tenant_name: str, namespace: str = "default"):
    """删除指定租户

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
    """
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        success, output = safe_execute_command(["okctl", "tenant", "delete", tenant_name, "-n", namespace])
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def activate_tenant(
    standby_tenant_name: str, namespace: str = "default", force: bool = False
):
    """激活备用租户

    Args:
        standby_tenant_name: 备用租户名称
        namespace: 命名空间（默认为"default"）
        force: 是否强制激活
    """
    try:
        validate_identifier(standby_tenant_name, "Standby tenant name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "activate", standby_tenant_name, "-n", namespace]
        if force:
            cmd.append("-f")
        
        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def change_tenant_password(
    tenant_name: str, password: str, namespace: str = "default", force: bool = False
):
    """修改租户密码

    Args:
        tenant_name: 租户名称
        password: 租户的新密码（必需）
        namespace: 命名空间（默认为"default"）
        force: 是否强制执行操作
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "changepwd", tenant_name, f"--password={password}", "-n", namespace]
        if force:
            cmd.append("-f")
        
        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def replay_tenant_log(
    tenant_name: str,
    namespace: str = "default",
    force: bool = False,
    unlimited: bool = True,
    until_timestamp: Optional[str] = None,
):
    """回放租户日志

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        force: 是否强制执行操作
        unlimited: 是否不限制时间（默认为True）
        until_timestamp: 租户恢复的时间戳，例如: 2024-02-23 17:47:00
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "replaylog", tenant_name, "-n", namespace]

        # 添加可选参数
        if force:
            cmd.append("-f")
        if unlimited is not None:
            cmd.extend(["--unlimited", str(unlimited).lower()])
        if until_timestamp:
            cmd.extend(["--until-timestamp", until_timestamp])

        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def scale_tenant(
    tenant_name: str,
    namespace: str = "default",
    cpu_count: Optional[str] = None,
    force: bool = False,
    iops_weight: Optional[int] = None,
    log_disk_size: Optional[str] = None,
    max_iops: Optional[int] = None,
    memory_size: Optional[str] = None,
    min_iops: Optional[int] = None,
    unit_number: Optional[int] = None,
):
    """扩缩租户资源,一次只能执行一种类型的扩展操作
    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        cpu_count: 单位的CPU数量（默认为"1"）
        force: 是否强制执行操作
        iops_weight: 单位的IOPS权重（默认为1）
        log_disk_size: 单位的日志磁盘大小（默认为"4Gi"）
        max_iops: 单位的最大IOPS（默认为1024）
        memory_size: 单位的内存大小（默认为"2Gi"）
        min_iops: 单位的最小IOPS（默认为1024）
        unit_number: 租户的单位数量（默认为1）
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "scale", tenant_name, "-n", namespace]

        # 添加可选参数
        if cpu_count:
            cmd.extend(["--cpu-count", cpu_count])
        if force:
            cmd.append("-f")
        if iops_weight is not None:
            cmd.extend(["--iops-weight", str(iops_weight)])
        if log_disk_size:
            cmd.extend(["--log-disk-size", log_disk_size])
        if max_iops is not None:
            cmd.extend(["--max-iops", str(max_iops)])
        if memory_size:
            cmd.extend(["--memory-size", memory_size])
        if min_iops is not None:
            cmd.extend(["--min-iops", str(min_iops)])
        if unit_number is not None:
            cmd.extend(["--unit-number", str(unit_number)])

        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def show_tenant(tenant_name: str, namespace: str = "default"):
    """显示租户信息

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
    Important:
        1. 注意不要在短时间内重复调用该命令
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        success, output = safe_execute_command(["okctl", "tenant", "show", tenant_name, "-n", namespace])
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def switchover_tenant(
    primary_tenant_name: str,
    standby_tenant_name: str,
    namespace: str = "default",
    force: bool = False,
):
    """切换主备租户

    Args:
        primary_tenant_name: 主租户名称
        standby_tenant_name: 备租户名称
        namespace: 命名空间（默认为"default"）
        force: 是否强制执行操作
    """
    if not primary_tenant_name or not standby_tenant_name:
        return "必须指定主租户和备租户名称"
    try:
        validate_identifier(primary_tenant_name, "Primary tenant name")
        validate_identifier(standby_tenant_name, "Standby tenant name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "switchover", primary_tenant_name, standby_tenant_name, "-n", namespace]
        if force:
            cmd.append("-f")
        
        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def update_tenant(
    tenant_name: str,
    namespace: str = "default",
    connect_white_list: Optional[str] = None,
    force: bool = False,
    priority: Optional[str] = None,
):
    """更新租户信息

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        connect_white_list: 租户的连接白名单
        force: 是否强制执行操作
        priority: 租户的可用区优先级，格式为'Zone=Priority'，可使用逗号分隔多个优先级
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "update", tenant_name, "-n", namespace]

        # 添加可选参数
        if connect_white_list:
            cmd.extend(["--connect-white-list", connect_white_list])
        if force:
            cmd.append("-f")
        if priority:
            cmd.extend(["--priority", priority])

        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)

@mcp.tool()
def upgrade_tenant(tenant_name: str, namespace: str = "default", force: bool = False):
    """升级租户

    Args:
        tenant_name: 租户名称
        namespace: 命名空间（默认为"default"）
        force: 是否强制升级
    """
    if not tenant_name:
        return "必须指定租户名称"
    try:
        validate_identifier(tenant_name, "Tenant name")
        validate_identifier(namespace, "Namespace")
        
        cmd = ["okctl", "tenant", "upgrade", tenant_name, "-n", namespace]
        if force:
            cmd.append("-f")
        
        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)
