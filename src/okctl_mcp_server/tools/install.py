import subprocess
import logging
from okctl_mcp_server.utils.errors import format_error
from okctl_mcp_server.utils.security import safe_execute_command

# 导入mcp实例
from okctl_mcp_server import mcp

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_command_exists(command: str) -> bool:
    """检查命令是否存在

    Args:
        command: 要检查的命令

    Returns:
        bool: 命令是否存在
    """
    try:
        result = subprocess.run(["which", command], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def check_kubernetes_available() -> bool:
    """检查Kubernetes是否可用

    Returns:
        bool: Kubernetes是否可用
    """
    try:
        success, _ = safe_execute_command(["kubectl", "version", "--client"])
        return success
    except Exception:
        return False


def check_component_installed(component_name: str) -> bool:
    """检查组件是否已安装，目前支持ob-operator和okctl，
    一般来说，当第一次使用okctl-mcp-server的相关工具时
    首先可以检查是否安装了ob-operator和okctl

    Args:
        component_name: 组件名称

    Returns:
        bool: 组件是否已安装
    """
    if component_name == "okctl":
        return check_command_exists("okctl")
    elif component_name == "ob-operator":
        try:
            success, _ = safe_execute_command(
                ["kubectl", "get", "deployment", "-n", "oceanbase", "ob-operator"]
            )
            return success
        except Exception:
            return False
    return False


@mcp.tool()
def install_okctl():
    """安装okctl"""
    try:
        if check_component_installed("okctl"):
            logger.info("okctl已经安装")
            return "okctl已经安装"

        logger.info("正在安装okctl...")
        
        # 安全地下载安装脚本
        success, download_output = safe_execute_command([
            "curl", "-sL", 
            "https://raw.githubusercontent.com/oceanbase/ob-operator/master/scripts/install-okctl.sh"
        ])
        if not success:
            return f"下载安装脚本失败: {download_output}"
        
        # 安全地执行安装脚本
        success, install_output = safe_execute_command([
            "bash", "-c", download_output
        ])
        if not success:
            return f"执行安装脚本失败: {install_output}"
        
        # 安全地设置权限和移动文件
        success, chmod_output = safe_execute_command([
            "chmod", "+x", "./okctl"
        ])
        if not success:
            return f"设置权限失败: {chmod_output}"
        
        success, move_output = safe_execute_command([
            "mv", "./okctl", "/usr/local/bin"
        ])
        if not success:
            return f"移动文件失败: {move_output}"
        
        logger.info("okctl安装完成")
        return "okctl安装完成"
    except subprocess.CalledProcessError as e:
        error_msg = format_error(e)
        logger.error("安装okctl失败: %s", error_msg)
        return f"安装okctl失败: {error_msg}"


@mcp.tool()
def install_ob_operator():
    """安装ob-operator"""
    try:
        if check_component_installed("ob-operator"):
            logger.info("ob-operator已经安装")
            return "ob-operator已经安装"

        logger.info("正在安装ob-operator...")
        success, output = safe_execute_command(
            [
                "kubectl",
                "apply",
                "-f",
                "https://raw.githubusercontent.com/oceanbase/ob-operator/stable/deploy/operator.yaml",
            ]
        )
        if success:
            logger.info("ob-operator安装完成")
            return "ob-operator安装完成"
        else:
            return f"安装ob-operator失败: {output}"
    except Exception as e:
        error_msg = format_error(e)
        logger.error("安装ob-operator失败: %s", error_msg)
        return f"安装ob-operator失败: {error_msg}"


# @mcp.tool()
# def setup_environment():
#     """设置环境，安装所有必要的组件"""
#     results = []

#     # 安装先决条件
#     prereq_result = install_prerequisites()
#     results.append(f"先决条件安装结果: {prereq_result}")

#     # 安装okctl
#     okctl_result = install_okctl()
#     results.append(f"okctl安装结果: {okctl_result}")

#     # 安装ob-operator
#     operator_result = install_ob_operator()
#     results.append(f"ob-operator安装结果: {operator_result}")

#     return "\n".join(results)
