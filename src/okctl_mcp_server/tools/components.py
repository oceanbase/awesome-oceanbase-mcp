from typing import Optional
from okctl_mcp_server.utils.errors import format_error
from okctl_mcp_server.utils.security import (
    validate_identifier,
    safe_execute_command,
    SecurityError,
)

# 导入mcp实例
from okctl_mcp_server import mcp


# 组件安装和更新相关的工具
@mcp.tool()
def install_component(
    component_name: Optional[str] = None,
    version: Optional[str] = None,
):
    """安装OceanBase组件, 目前支持ob-operator，ob-dashboard, local-path-provisioner,cert-manager,不支持其他组件，
    如果未指定，默认将安装ob-operator和 ob-dashboard

    Args:
        component_name: 组件名称
        version: 组件版本
    """
    if component_name and component_name not in [
        "ob-operator",
        "ob-dashboard",
        "local-path-provisioner",
        "cert-manager",
    ]:
        return f"不支持安装{component_name}组件"
    try:
        cmd = ["okctl", "install"]
        if component_name:
            validate_identifier(component_name, "Component name")
            cmd.append(component_name)
        if version:
            cmd.extend(["--version", version])

        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)


@mcp.tool()
def update_component(
    component_name: Optional[str] = None,
):
    """更新OceanBase组件, 目前支持ob-operator，ob-dashboard, local-path-provisioner,cert-manager,不支持其他组件，
    如果未指定，默认将更新ob-operator和 ob-dashboard

    Args:
        component_name: 组件名称
    """
    if component_name and component_name not in [
        "ob-operator",
        "ob-dashboard",
        "local-path-provisioner",
        "cert-manager",
    ]:
        return f"不支持更新{component_name}组件"
    try:
        cmd = ["okctl", "update"]
        if component_name:
            validate_identifier(component_name, "Component name")
            cmd.append(component_name)

        success, output = safe_execute_command(cmd)
        return output
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return format_error(e)
