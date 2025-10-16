#!/usr/bin/env python3
"""
System Diagnosis Script
"""
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def diagnose_system():
    """Diagnose system status"""
    print("🔍 System diagnosis started...")
    print("=" * 50)

    # 1. Test configuration
    try:
        from utils.config_validator import ConfigValidator

        is_valid, missing = ConfigValidator.validate_config()
        if is_valid:
            print("✅ Configuration validation passed")
        else:
            print(f"❌ Configuration validation failed: {', '.join(missing)}")
            return False
    except Exception as e:
        print(f"❌ Configuration validation exception: {str(e)}")
        return False

    # 2. Test MCP connection
    try:
        from config import settings
        from mcp.client.streamable_http import streamablehttp_client
        from strands.tools.mcp.mcp_client import MCPClient

        mcp_client = MCPClient(lambda: streamablehttp_client(settings.MARQUEZ_MCP_URL))
        with mcp_client:
            tools = mcp_client.list_tools_sync()
            print(f"✅ MCP连接成功，获取到 {len(tools)} 个工具")
    except Exception as e:
        print(f"❌ MCP连接失败: {str(e)}")
        return False

    # 3. 测试Agent创建
    try:
        from agents.agent_factory import AgentFactory

        mcp_client = MCPClient(lambda: streamablehttp_client(settings.MARQUEZ_MCP_URL))
        mcp_client.__enter__()

        factory = AgentFactory(mcp_client)

        # 测试元数据代理
        metadata_agent = factory.create_metadata_agent()
        print("✅ 元数据代理创建成功")

        # 测试简单查询
        metadata_agent("测试查询")
        print("✅ 元数据代理响应正常")

        mcp_client.__exit__(None, None, None)

    except Exception as e:
        print(f"❌ Agent创建失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    # 4. 测试完整系统
    try:
        from core.multi_agent_system import TrueMultiAgentSystem

        system = TrueMultiAgentSystem(use_cli_interface=False)
        print("✅ 多代理系统创建成功")

        # 测试协调器
        orchestrator = system.agents["orchestrator"]
        orchestrator("系统状态如何？")
        print("✅ 协调器响应正常")

        system.cleanup()

    except Exception as e:
        print(f"❌ 多代理系统失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    print("=" * 50)
    print("🎉 系统诊断完成，所有组件正常！")
    return True


if __name__ == "__main__":
    success = diagnose_system()
    if not success:
        print("\n💥 系统存在问题，需要修复")
        sys.exit(1)
    else:
        print("\n✅ 系统运行正常，可以启动应用")
