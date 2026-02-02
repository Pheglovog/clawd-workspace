"""
Agent Executor - LangChain 智能执行器
创建多个子 Agent，根据任务类型智能选择执行
"""

from langchain.llms import OpenAI
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.output_parsers import OutputFixingParser, StrOutputParser
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from ..utils.config import get_api_key, get_llm_model
from ..utils.prompts import create_planning_prompt, create_checklist_prompt, create_budget_prompt
from ..tools import weather, currency, maps


class AgentInput(BaseModel):
    """Agent 输入模型"""
    destination: str = Field(description="目的地")
    days: int = Field(description="旅行天数")
    budget: int = Field(description="预算（人民币）")
    preference: str = Field(default="3", description="偏好：1.历史古迹 2.自然景观 3.购物")


class PlannerOutput(BaseModel):
    """行程规划输出"""
    daily_itinerary: List[Dict[str, Any]] = Field(description="每日行程")
    important_tips: List[str] = Field(description="重要提示")
    budget_breakdown: Dict[str, int] = Field(description="预算分析")


class ChecklistOutput(BaseModel):
    """打包清单输出"""
    categories: Dict[str, List[str]] = Field(description="分类清单")
    important_items: List[str] = Field(description="重要物品")
    total_items: int = Field(description="物品总数")


class BudgetOutput(BaseModel):
    """预算计算输出"""
    daily_costs: Dict[str, int] = Field(description="每日费用")
    total_cost: int = Field(description="总费用")
    exchange_rate: float = Field(description="汇率")
    suggestions: List[str] = Field(description="节约建议")


class WeatherOutput(BaseModel):
    """天气查询输出"""
    destination: str = Field(description="目的地")
    condition: str = Field(description="天气状况")
    temperature: str = Field(description="温度")
    tips: List[str] = Field(description="旅行建议")


class RouteOutput(BaseModel):
    """路线规划输出"""
    origin: str = Field(description="出发地")
    destination: str = Field(description="目的地")
    route_type: str = Field(description="路线类型")
    duration: str = Field(description="预计时间")
    daily_cost: int = Field(description="每日费用")
    total_cost: int = Field(description="总费用")
    tips: List[str] = Field(description="路线提示")


class AgentResponse(BaseModel):
    """完整的 Agent 响应"""
    plan: Optional[PlannerOutput] = Field(default=None, description="行程规划")
    checklist: Optional[ChecklistOutput] = Field(default=None, description="打包清单")
    budget: Optional[BudgetOutput] = Field(default=None, description="预算计算")
    weather: Optional[WeatherOutput] = Field(default=None, description="天气查询")
    route: Optional[RouteOutput] = Field(default=None, description="路线规划")


def get_llm():
    """初始化 LLM"""
    api_key = get_api_key()
    model_name = get_llm_model()
    
    return OpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0.7,
        timeout=60
    )


def create_memory():
    """创建记忆管理"""
    return ConversationBufferMemory(
        llm=get_llm(),
        memory_key="agent_memory",
        return_messages=True,
        max_token_limit=2000
    )


# ====== 子 Agent 定义 ======

def create_planning_agent(llm, memory):
    """创建行程规划 Agent"""
    
    planning_prompt = PromptTemplate.from_template("""
    你是一位专业的日本旅行规划师。请根据以下信息规划一份详细的行程：

    目的地：{destination}
    旅行天数：{days} 天
    总预算：{budget} 人民币
    旅行偏好：{preference}

    请按照以下要求规划：
    1. 每天的行程要丰富但不要过于紧张
    2. 根据偏好合理安排活动类型（古迹、自然景观、购物）
    3. 每天建议 1-2 个主要景点，预留自由活动时间
    4. 推荐交通便利的交通方式（新干线是首选）
    5. 推荐性价比高的住宿
    6. 预留购物和纪念品预算

    输出 JSON 格式的行程规划。
    """)
    
    planning_chain = planning_prompt | llm
    
    return AgentExecutor(
        llm=llm,
        memory=memory,
        verbose=True,
        agent_type="planner",
        name="行程规划专家"
    )


def create_checklist_agent(llm, memory):
    """创建打包清单 Agent"""
    
    checklist_prompt = PromptTemplate.from_template("""
    你是一位专业的旅行顾问。请根据以下行程规划生成一份详细的{days}天旅行打包清单：

    目的地：{destination}
    旅行天数：{days} 天
    总预算：{budget} 人民币
    旅行偏好：{preference}

    旅行行程概览：
    {itinerary}

    请根据行程和偏好生成打包清单，要求如下：

    1. 📚 本品必需品
       - 身份证件、护照、签证、机票、酒店预订确认单
       - 现金和银行卡
       - 手机和充电器（适配日本电压 100V）
       - 相机和备用电池

    2. 👕 衣物（7天）
       - 内衣（7套）
       - 外套（根据天气）
       - 袜子（2条）
       - 袜子（3条）
       - 袜子（3双）
       - 袜子（5双）
       - 额带（3条）
       - 袜子（3双）
       - 围巾（2条）
       - 毛帽（1顶）
       - 太阳镜（1顶）
       - 一次性内衣（3条）

    3. 🧴 洗护用品
       - 牙膏套装（2套）
       - 毛巾（3条）
       - 洗发水（小瓶装）
       - 洗发液（小瓶装）
       - 围巾（1条）
       - 洗发液（小瓶装）
       - 剃须刀（1把）
       - 拇须刀（1把）
       - 拖鞋（1双）
       - 拖鞋（1双）
       - 袜子（3双）
       - 袜子（3双）
       - 袜子（3双）

    4. 📱 电子设备
       - 移动电源（20000mAh 充电宝）
       - 相机（推荐微单或卡片机）
       - 手机支架

    5. 🧻 医疗用品
       - 常用感冒药
       - 创可贴
       - 晕车药（日本品牌）
       - 避晒霜（SPF50+）
       - 蚊虫药（避蚊虫）
       - 体温计
       - 晕车药（预防晕车）

    6. 📦 其他必需品
       - 保温杯
       - 小零食
       - 真镜
       - 行李箱
       - 锁具箱

    重要物品提醒：
    💡 不要忘记带护照和签证原件！
    💡 确保充电器支持日本电压（100V）
    💡 相机内存和存储卡提前准备充足

    输出 JSON 格式的打包清单。
    """)
    
    checklist_chain = checklist_prompt | llm
    
    return AgentExecutor(
        llm=llm,
        memory=memory,
        verbose=True,
        agent_type="checklist",
        name="打包清单专家"
    )


def create_budget_agent(llm, memory):
    """创建预算计算 Agent"""
    
    budget_prompt = PromptTemplate.from_template("""
    你是一位专业的旅行财务顾问。请根据以下信息计算详细的{days}天旅行预算：

    目的地：{destination}
    旅行天数：{days} 天
    总预算：{budget} 人民币
    旅行偏好：{preference}

    当前汇率：1 人民币 = 0.21 日元（仅供参考）

    请按照以下要求计算预算：

    1. 💱 交通费用
       - 往返机票：约占总预算的 25-35%
       - 日本国内交通：约占总预算的 15-20%
       - 推荐使用 JR Pass（7 天通票）

    2. 🏨 住宿费用
       - 酒店：约占总预算的 25-35%
       - 推荐预订商务酒店或经济型酒店
       - 平均费用：1500-3000 人民币/晚

    3. 🍜 餐饮费用
       - 早餐 + 晚餐：约占总预算的 20-25%
       - 建议：便利店早餐 + 拉面晚餐
       - 平均费用：2000-3000 人民币/天

    4. 🎫 门票和娱乐
       - 约占总预算的 10-15%
       - 门票：寺庙、神社、环球影城、迪士尼（根据选择）
       - 平均费用：1000-2000 人民币/天

    5. 🛍 购物
       - 约占总预算的 5-10%
       - 建议：药妆店、电器店、百元店
       - 平均费用：根据购物计划而定

    6. 💳 其他费用
       - 电话卡：约 500 人民币/月
       - 旅游保险：约 3000-1000 人民币/次
       - 应急备用金：建议预留 10,000 人民币

    7. 📊 预算分析
       - 总计：汇总所有费用
       - 人民币对日元转换：显示金额换算
       - 节约建议：优化交通和住宿选择

    输出 JSON 格式的预算分析报告。
    """)
    
    budget_chain = budget_prompt | llm
    
    return AgentExecutor(
        llm=llm,
        memory=memory,
        verbose=True,
        agent_type="budget",
        name="预算计算专家"
    )


# ====== 工具集成 ======

def create_weather_tool(llm):
    """创建天气查询工具"""
    
    async def get_weather(destination: str) -> WeatherOutput:
        """获取目的地的天气信息"""
        return weather.get_weather(destination)
    
    # 转换为 StructuredTool
    return Tool(
        name="获取天气",
        func=get_weather,
        description="获取目的地的天气预报信息",
        args_schema=WeatherOutput.schema()
    )


def create_currency_tool(llm):
    """创建汇率查询工具"""
    
    async def get_exchange_info(destination: str, budget: int) -> Dict[str, Any]:
        """获取汇率信息"""
        return currency.get_exchange_rate()
    
    return Tool(
        name="汇率查询",
        func=get_exchange_info,
        description="获取当前汇率和货币转换建议",
        args_schema="需要 destination 和 budget 参数"
    )


def create_route_tool(llm):
    """创建路线规划工具"""
    
    async def get_route_recommendation(origin: str, destination: str, days: int) -> RouteOutput:
        """获取路线推荐"""
        return maps.get_route_recommendation(origin, destination)
    
    return Tool(
        name="路线规划",
        func=get_route_recommendation,
        description="获取主要城市间的交通路线和费用估算",
        args_schema="需要 origin, destination 和 days 参数"
    )


# ====== 创建 Multi-Agent Executor ======

def create_multi_agent_executor():
    """创建多 Agent 执行器"""
    
    # 获取 LLM
    llm = get_llm()
    
    # 创建记忆
    memory = create_memory()
    
    # 创建子 Agent
    planning_agent = create_planning_agent(llm, memory)
    checklist_agent = create_checklist_agent(llm, memory)
    budget_agent = create_budget_agent(llm, memory)
    
    # 创建工具列表
    tools = [
        create_weather_tool(llm),
        create_currency_tool(llm),
        create_route_tool(llm)
    ]
    
    # 创建 Multi-Agent Executor
    # AgentExecutor 将自动调用相应的工具
    agent_executor = AgentExecutor(
        llm=llm,
        memory=memory,
        tools=tools,
        verbose=True,
        max_iterations=5,
        early_stopping_method="generate"
    )
    
    return agent_executor


async def plan_travel(input_data: Dict[str, Any]) -> AgentResponse:
    """规划旅行（主入口）"""
    
    # 创建 Multi-Agent Executor
    agent_executor = create_multi_agent_executor()
    
    # 构建完整的输入
    user_input = AgentInput(**input_data)
    
    # 构建提示词
    full_prompt = f"""
    你是一个智能旅行规划助手，请根据用户的需求提供最合适的建议和服务。

    用户需求：
    - 目的地：{user_input.destination}
    - 旅行天数：{user_input.days} 天
    - 预算：{user_input.budget} 人民币
    - 偏好：{user_input.preference}

    可用服务：
    1. 行程规划（生成详细日程）
    2. 打包清单（根据行程生成物品列表）
    3. 预算计算（费用估算和汇率转换）
    4. 天气查询（了解目的地天气）
    5. 路线规划（推荐最佳交通方式）

    请智能选择合适的服务，为用户提供全面的旅行规划支持。
    """
    
    try:
        # 使用 Multi-Agent Executor 执行
        result = await agent_executor.ainvoke(full_prompt)
        
        # 解析输出
        agent_response = AgentResponse(**result)
        
        print("\n" + "="*60)
        print("🎯 智能旅行规划完成！")
        print("="*60)
        print()
        
        return agent_response
        
    except Exception as e:
        print(f"\n❌ 规划失败: {e}")
        print("="*60)
        print()
        
        return AgentResponse(
            message=f"抱歉，规划过程中出现了问题：{str(e)}"
        )


# ====== 辅助函数 ======

def format_agent_response(response: AgentResponse) -> str:
    """格式化 Agent 响应为 JSON 字符串"""
    import json
    
    if response.message:
        # 有错误消息，直接返回
        return json.dumps({
            "error": True,
            "message": response.message
        })
    
    # 格式化成功响应
    result = {
        "error": False,
        "message": "规划完成",
        "data": {
            "destination": response.plan.destination if response.plan else "",
            "days": response.plan.days if response.plan else 0,
            "budget": response.budget.total_cost if response.budget else 0
        }
    }
    
    # 如果有子计划，添加到数据中
    if response.plan:
        result["data"]["plan"] = response.plan
    
    # 如果有打包清单，添加到数据中
    if response.checklist:
        result["data"]["checklist"] = response.checklist
    
    # 如果有预算，添加到数据中
    if response.budget:
        result["data"]["budget"] = {
            "daily": response.budget.daily_costs,
            "total": response.budget.total_cost,
            "suggestions": response.budget.suggestions
        }
    
    # 如果有天气，添加到数据中
    if response.weather:
        result["data"]["weather"] = response.weather
    
    # 如果有路线，添加到数据中
    if response.route:
        result["data"]["route"] = response.route
    
    return json.dumps(result, ensure_ascii=False, indent=2)
