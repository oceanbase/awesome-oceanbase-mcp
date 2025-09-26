import subprocess


def format_error(e):
    """format errors"""
    if isinstance(e, subprocess.CalledProcessError):
        return f"执行命令失败:\n命令: {e.cmd}\n错误信息: {e.output}"
    return f"执行失败:\n错误类型: {type(e).__name__}\n错误信息: {str(e)}"
