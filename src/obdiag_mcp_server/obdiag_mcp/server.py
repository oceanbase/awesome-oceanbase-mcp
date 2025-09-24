#!/usr/bin/env python
# -*- coding: UTF-8 -*
# Copyright (c) 2022 OceanBase
# OceanBase Diagnostic Tool is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import shutil
from fastmcp import FastMCP
from pathlib import Path
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
mcp = FastMCP("OBDiag MCP Server")


# 确认obdiag是否安装,是否存在 obdiag 命令
def check_obdiag_installed():
    return shutil.which("obdiag") is not None


def check_config_exist():
    return Path(os.path.expanduser("~/.obdiag/config.yml")).exists()


def run_obdiag_command(command: str, silent=True) -> str:
    """
    运行 obdiag 命令并返回结果
    :param command: 完整的 obdiag 命令
    :param silent: 是否静默执行
    :return: 指令执行的输出结果
    """
    try:
        if silent:
            command += " --inner_config obdiag.logger.silent=True"
        else:
            pass
        # 使用 subprocess 执行命令
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
        )
        # 返回标准输出或错误输出
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"


@mcp.tool()
async def obdiag_check_run() -> str:
    """
    巡检集群，并返回巡检报告
    :return: 指令执行的输出结果
    """
    return run_obdiag_command("obdiag check run")


@mcp.tool()
async def obdiag_analyze_log() -> str:
    """
    分析集群日志，找出发生过的错误信息并返回
    :return: 指令执行的输出结果
    """
    return run_obdiag_command("obdiag analyze log")


@mcp.tool()
async def obdiag_display_list() -> str:
    """
    obdiag 集群信息查询功能功能，返回支持的指令列表
    :return: 支持的指令列表
    """

    return run_obdiag_command("obdiag display scene list")


@mcp.tool()
async def obdiag_display_run(scene: str, env_dict: dict = None) -> str:
    """
    obdiag 集群信息查询功能，执行获取的指令列表，需要功能来自obdiag_display_list的返回结果。只需要返回obdiag_display_list结果
    :param scene: 指令名，来自obdiag_display_list的返回结果，如 'obdiag display scene run --scene=observer.all_tenant',则赋值 scene=observer.all_tenant
    :param env_dict: 环境变量，来自obdiag_display_list的返回结果,只有在要求填入env的时候才需要赋值，如 'oobdiag display scene run --scene=observer.index --env database_name=test --env table_name=test',则赋值 env_dict={'database_name':'test','table_name':'test'}
    :return: 洞察结果
    """
    if env_dict is None:
        env_dict = {}
    cmd = "obdiag display scene run --scene={}".format(scene)
    if env_dict:
        for env in env_dict:
            env_name = env
            env_value = env_dict[env]
            cmd += " --env {}={}".format(env_name, env_value)
    return run_obdiag_command(cmd, silent=False)


@mcp.tool()
async def obdiag_gather_log(var: str) -> str:
    """
    obdiag 收集集群日志，根据需求添加参数或者默认不加任何参数收集日志
    :param var: 可以根据不同的需求使用不同的参数：
    1.按时间范围收集使用--from --to参数，例如obdiag gather log --from "2022-06-30 16:25:00" --to "2022-06-30 18:30:00"
    2.按时间时长收集使用--since参数，例如收集1小时内的日志：obdiag gather log --since 1h
    3.过滤关键字收集使用--grep参数，例如过滤TRACE_ID关键字：obdiag gather log --grep "TRACE_ID"，如果过滤多个关键字可以使用：obdiag gather log --from "2022-06-30 16:25:00" --to "2022-06-30 18:30:00" --grep "AAAAA" --grep "BBBBB"
    4.选择收集的OceanBase集群日志类型使用--scope参数，可配置的值为：observer、election、rootservice、all，默认值为all，例如obdiag gather log --scope=all
    5.选择存储结果的本地路径使用--store_dir参数，默认值为当前目录，例如obdiag gather log --store_dir=/home/obdiag/log
    6.远端节点在日志收集过程中产生的临时文件存储路径使用--temp_dir参数，默认值为/tmp，例如obdiag gather log --temp_dir=/home/obdiag/log
    :return: 指令执行的输出结果
    """
    cmd = "obdiag gather log {}".format(var)
    return run_obdiag_command(cmd, silent=True)


# 启动 MCP 服务
def main():
    if not check_obdiag_installed():
        print("obdiag is not installed, please install obdiag first")
        sys.exit(1)
    if not check_config_exist():
        print("obdiag config is not exist, please check ~/.obdiag/config.yml is exist")
        sys.exit(1)
    # 根据输入的参数，判别是使用stdio还是sse还是streamable-http,如果是sse还是streamable-http，则需要指定port
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        print("run mcp with stdio")
        mcp.run(transport="stdio")
    elif len(sys.argv) > 1 and sys.argv[1] == "sse":
        print("run mcp with sse")
        if len(sys.argv) > 2:
            mcp.run(transport="sse", host="0.0.0.0", port=int(sys.argv[2]), path="/mcp")
        else:
            mcp.run(transport="sse", host="0.0.0.0", port=8000, path="/mcp")
    else:
        print("run mcp with streamable-http")
        if len(sys.argv) > 2:
            mcp.run(
                transport="streamable-http",
                host="0.0.0.0",
                port=int(sys.argv[2]),
                path="/mcp",
            )
        else:
            mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")


if __name__ == "__main__":
    main()
