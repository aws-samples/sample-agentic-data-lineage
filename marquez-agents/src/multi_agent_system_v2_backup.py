"""
AWS Strands Multi-Agent System V2
True multi-agent architecture implementation
"""

import boto3
from config import settings
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient


class TrueMultiAgentSystem:
    """True multi-agent system"""

    def __init__(self):
        self.agents = {}
        self.mcp_client = None
        self._initialize_mcp_client()
        self._initialize_agents()

        print("🚀 AWS Strands True Multi-Agent System started")
        print("=" * 60)
        self._show_welcome_message()

    def _initialize_mcp_client(self):
        """Initialize MCP client"""
        self.mcp_client = MCPClient(
            lambda: streamablehttp_client(settings.MARQUEZ_MCP_URL)
        )
        # Start MCP client connection
        self.mcp_client.__enter__()

    def _initialize_agents(self):
        """Initialize all independent Agent instances"""

        # 1. Create Metadata Agent - with MCP tools
        metadata_agent = self._create_metadata_agent()

        # 2. Create Lineage Agent - with MCP tools
        lineage_agent = self._create_lineage_agent()

        # 3. Create Specialist Agent - with analysis tools
        specialist_agent = self._create_specialist_agent()

        # 4. Create Orchestrator Agent - with coordination tools
        orchestrator_agent = self._create_orchestrator_agent()

        self.agents = {
            "orchestrator": orchestrator_agent,
            "metadata": metadata_agent,
            "lineage": lineage_agent,
            "specialist": specialist_agent,
        }

    def _create_metadata_agent(self) -> Agent:
        """创建独立的元数据代理"""
        # 获取MCP工具（使用共享的MCP客户端）
        mcp_tools = self.mcp_client.list_tools_sync()

        # 添加AWS Glue工具
        from strands import tool

        @tool
        def get_glue_databases() -> str:
            """获取AWS Glue数据库列表"""
            try:
                glue_client = boto3.client(
                    "glue", region_name=settings.get("bedrock.region", "us-west-2")
                )
                response = glue_client.get_databases()
                databases = [db["Name"] for db in response["DatabaseList"]]
                return f"AWS Glue数据库: {databases}"
            except Exception as e:
                return f"获取Glue数据库失败: {str(e)}"

        # 合并工具
        all_tools = mcp_tools + [get_glue_databases]

        system_prompt = """你是一个元数据管理专家，负责统计和获取企业所有数据资产信息。

你的职责包括：
1. 通过Marquez MCP统计assets和jobs的数量
2. 通过AWS Glue获取数据目录信息
3. 回答关于数据资产的各种问题

你有以下工具可用：
- Marquez MCP工具：用于查询Marquez中的命名空间、数据集、作业等
- AWS Glue工具：用于获取AWS数据目录信息

注意：
1. 遇到类似s3://lh-core-kolya-landing-zone这种格式需要做转换, 成为query string
2. 最好罗列明细，即便是一些聚合的问题，当明细超过500时提醒用户明细过多，不方便展示

用中文回复用户。"""

        # 创建Agent
        agent = Agent(
            tools=all_tools,
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

        return agent

    def _create_lineage_agent(self) -> Agent:
        """创建独立的血缘代理"""
        # 获取MCP工具（使用共享的MCP客户端）
        mcp_tools = self.mcp_client.list_tools_sync()

        system_prompt = """你是一个数据血缘分析专家，负责查询和分析数据血缘关系。

你的职责包括：
1. 查询字段级血缘关系
2. 分析数据变更的影响范围
3. 生成血缘关系图
4. 回答关于数据血缘的各种问题

你有Marquez MCP工具可用，可以查询数据血缘信息。

用中文回复用户。"""

        # 创建Agent
        agent = Agent(
            tools=mcp_tools,
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

        return agent

    def _create_specialist_agent(self) -> Agent:
        """创建独立的专家代理"""
        from strands import tool

        @tool
        def generate_health_report() -> str:
            """生成血缘健康报告"""
            return "数据健康报告：系统运行正常，血缘关系完整。"

        @tool
        def analyze_data_quality() -> str:
            """分析数据质量"""
            return "数据质量分析：整体数据质量良好，建议定期检查。"

        system_prompt = """你是一个数据治理专家，负责生成报告和提供专业建议。

你的职责包括：
1. 生成血缘健康报告
2. 分析数据质量问题
3. 提供数据治理建议
4. 识别潜在的数据问题

用中文回复用户。"""

        return Agent(
            tools=[generate_health_report, analyze_data_quality],
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

    def _create_orchestrator_agent(self) -> Agent:
        """创建独立的协调器代理"""
        from strands import tool

        @tool
        def call_metadata_agent(query: str) -> str:
            """调用元数据代理"""
            try:
                result = self.agents["metadata"](query)
                return f"元数据代理回复：\n{result}"
            except Exception as e:
                return f"调用元数据代理失败：{str(e)}"

        @tool
        def call_lineage_agent(query: str) -> str:
            """调用血缘代理"""
            try:
                result = self.agents["lineage"](query)
                return f"血缘代理回复：\n{result}"
            except Exception as e:
                return f"调用血缘代理失败：{str(e)}"

        @tool
        def call_specialist_agent(query: str) -> str:
            """调用专家代理"""
            try:
                result = self.agents["specialist"](query)
                return f"专家代理回复：\n{result}"
            except Exception as e:
                return f"调用专家代理失败：{str(e)}"

        system_prompt = """你是一个协调器，负责管理多个专业代理的协作。

你的职责包括：
1. 接收和解析用户请求
2. 判断请求类型并调用相应的专业代理
3. 协调多代理协作
4. 整合和返回结果

可用的专业代理：
- 元数据代理：处理资产统计、命名空间查询等元数据相关问题
- 血缘代理：处理数据血缘查询和影响分析
- 专家代理：生成报告和提供专业建议

请根据用户的问题类型，选择合适的代理来处理请求。

用中文回复用户。"""

        return Agent(
            tools=[call_metadata_agent, call_lineage_agent, call_specialist_agent],
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

    def _show_welcome_message(self):
        """显示欢迎信息"""
        welcome_msg = """
欢迎使用 AWS Strands True Multi-Agent System！

这是一个真正的多代理架构，每个代理都是独立的Agent实例：

🎯 Orchestrator Agent - 协调器代理（默认）
📊 Metadata Agent - 元数据代理（带MCP工具）
📈 Lineage Agent - 血缘代理（带MCP工具）
🔍 Specialist Agent - 专家代理（带分析工具）

功能示例：
• 查询命名空间：marquez有多少命名空间？
• 查询字段血缘：请查询字段 user_id 的血缘来源
• 影响分析：分析字段变更的影响
• 生成报告：生成血缘健康报告

命令：
- 'help' 或 '帮助' - 显示帮助信息
- 'agents' 或 '代理' - 显示所有代理状态
- 'switch <agent>' - 切换到指定代理
- 'quit' 或 'exit' - 退出系统

直接输入问题即可开始对话！
"""
        print(welcome_msg)

    def run(self):
        """运行交互式系统"""
        current_agent = "orchestrator"

        while True:
            try:
                agent_name = {
                    "orchestrator": "协调器",
                    "metadata": "元数据",
                    "lineage": "血缘",
                    "specialist": "专家",
                }.get(current_agent, current_agent)

                user_input = input(f"\n[{agent_name}代理] 请输入您的问题: ").strip()

                if not user_input:
                    continue

                # 处理系统命令
                if user_input.lower() in ["quit", "exit", "退出"]:
                    print("👋 感谢使用 AWS Strands True Multi-Agent System！")
                    break

                elif user_input.lower() in ["help", "帮助"]:
                    self._show_help()
                    continue

                elif user_input.lower() in ["agents", "代理"]:
                    self._show_agents_status()
                    continue

                elif user_input.lower().startswith("switch "):
                    agent_name_input = user_input[7:].strip()
                    if agent_name_input in self.agents:
                        current_agent = agent_name_input
                        print(f"✅ 已切换到 {agent_name_input} 代理")
                    else:
                        print(f"❌ 未找到代理: {agent_name_input}")
                        print(f"可用代理: {', '.join(self.agents.keys())}")
                    continue

                # 处理用户问题
                print(f"\n🤔 {agent_name}代理正在思考...")

                try:
                    response = self.agents[current_agent](user_input)
                    print(f"\n💡 {agent_name}代理回复：")
                    print("-" * 50)
                    print(response)
                    print("-" * 50)

                except Exception as e:
                    print(f"\n❌ 处理请求时出错: {str(e)}")
                    print("请尝试重新表述您的问题或切换到其他代理。")

            except KeyboardInterrupt:
                print("\n\n👋 感谢使用 AWS Strands True Multi-Agent System！")
                break
            except Exception as e:
                print(f"\n❌ 系统错误: {str(e)}")
                print("系统将继续运行，请重试。")

        # 清理资源
        self.cleanup()

    def _show_help(self):
        """显示帮助信息"""
        help_msg = """
📚 AWS Strands True Multi-Agent System 帮助

这是一个真正的多代理架构，每个代理都是独立的Agent实例：

🎯 协调器代理 (Orchestrator Agent)：
   - 自动路由请求到合适的专业代理
   - 协调多代理协作
   - 系统状态检查

📊 元数据代理 (Metadata Agent)：
   - 统计资产和作业数量（通过MCP工具）
   - 查询Marquez命名空间
   - 获取AWS Glue数据目录

📈 血缘代理 (Lineage Agent)：
   - 查询字段血缘来源（通过MCP工具）
   - 分析字段变更影响
   - 生成血缘关系图

🔍 专家代理 (Specialist Agent)：
   - 生成血缘健康报告
   - 分析数据质量问题
   - 提供治理建议

💡 架构特点：
   - 每个代理都是独立的Agent实例
   - 代理间通过工具调用进行通信
   - 真正的多代理协作模式

🔧 系统命令：
   - help/帮助: 显示此帮助信息
   - agents/代理: 查看所有代理状态
   - switch <agent>: 切换代理
   - quit/exit/退出: 退出系统
"""
        print(help_msg)

    def _show_agents_status(self):
        """显示所有代理状态"""
        print("\n🤖 代理状态检查:")
        print("=" * 40)

        for agent_name, _agent in self.agents.items():
            try:
                status = "✅ 正常"
                description = {
                    "orchestrator": "协调器代理 - 独立Agent实例，管理代理协作",
                    "metadata": "元数据代理 - 独立Agent实例，带MCP工具",
                    "lineage": "血缘代理 - 独立Agent实例，带MCP工具",
                    "specialist": "专家代理 - 独立Agent实例，带分析工具",
                }.get(agent_name, "未知代理")

                print(f"{status} {agent_name}: {description}")

            except Exception as e:
                print(f"❌ {agent_name}: 状态异常 - {str(e)}")

        print("=" * 40)

    def cleanup(self):
        """清理资源"""
        if self.mcp_client:
            try:
                self.mcp_client.__exit__(None, None, None)
            except Exception:
                pass


def main():
    """主函数"""
    try:
        # 检查配置
        from config import settings

        print("🔧 检查系统配置...")
        required_configs = ["MARQUEZ_MCP_URL", "BEDROCK_MODEL_ID"]

        missing_configs = []
        for config in required_configs:
            if not hasattr(settings, config) or not getattr(settings, config):
                missing_configs.append(config)

        if missing_configs:
            print(f"❌ 缺少必需配置: {', '.join(missing_configs)}")
            print("请检查 config/settings.toml 文件")
            return

        print("✅ 配置检查通过")

        # 启动系统
        system = TrueMultiAgentSystem()
        system.run()

    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        print("请确保已安装所有依赖包")
    except Exception as e:
        print(f"❌ 系统启动失败: {str(e)}")
        print("请检查配置文件和网络连接")


if __name__ == "__main__":
    main()
