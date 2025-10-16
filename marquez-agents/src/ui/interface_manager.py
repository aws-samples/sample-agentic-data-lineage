"""
User Interface Manager Class - Responsible for handling user interaction and displaying information
"""

from typing import Any


class InterfaceManager:
    """User Interface Manager Class"""

    def show_welcome_message(self):
        """Show welcome message"""
        welcome_msg = """
欢迎使用 Agentic Lineage For Lakehouse！

这是一个智能数据血缘分析系统，采用多代理架构：

🎯 Orchestrator Agent - 协调器代理（默认）
📊 Metadata Agent - 元数据代理（带MCP工具）
📈 Lineage Agent - 血缘代理（带MCP工具）
🗂️ DataCatalog Agent - 数据目录代理（AWS Glue + Redshift）
🔍 Specialist Agent - 专家代理（带分析工具）

功能示例：
• 查询命名空间：marquez有多少命名空间？
• 查询字段血缘：请查询字段 user_id 的血缘来源
• 数据目录：AWS Glue有哪些数据库？
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

    def show_help(self):
        """Show help information"""
        help_msg = """
📚 Agentic Lineage For Lakehouse 帮助

这是一个智能数据血缘分析系统，采用多代理架构：

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

    def show_agents_status(self, agents: dict[str, Any]):
        """Show all agents status"""
        print("\n🤖 代理状态检查:")
        print("=" * 40)

        for agent_name, _agent in agents.items():
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

    def get_agent_display_name(self, agent_key: str) -> str:
        """Get agent display name"""
        return {
            "orchestrator": "协调器",
            "metadata": "元数据",
            "lineage": "血缘",
            "datacatalog": "数据目录",
            "specialist": "专家",
        }.get(agent_key, agent_key)

    def show_thinking(self, agent_name: str):
        """Show agent thinking status"""
        print(f"\n🤔 {agent_name}代理正在思考...")

    def show_response(self, agent_name: str, response: str):
        """Show agent response"""
        print(f"\n💡 {agent_name}代理回复：")
        print("-" * 50)
        print(response)
        print("-" * 50)

    def show_error(self, error_msg: str):
        """Show error message"""
        print(f"\n❌ 处理请求时出错: {error_msg}")
        print("请尝试重新表述您的问题或切换到其他代理。")

    def show_system_error(self, error_msg: str):
        """Show system error"""
        print(f"\n❌ 系统错误: {error_msg}")
        print("系统将继续运行，请重试。")

    def show_goodbye(self):
        """Show goodbye message"""
        print("\n\n👋 感谢使用 Agentic Lineage For Lakehouse！")

    def show_switch_success(self, agent_name: str):
        """Show switch success message"""
        print(f"✅ 已切换到 {agent_name} 代理")

    def show_switch_error(self, agent_name: str, available_agents: list):
        """Show switch error message"""
        print(f"❌ 未找到代理: {agent_name}")
        print(f"可用代理: {', '.join(available_agents)}")

    def get_user_input(self, agent_name: str) -> str:
        """Get user input"""
        return input(f"\n[{agent_name}代理] 请输入您的问题: ").strip()
