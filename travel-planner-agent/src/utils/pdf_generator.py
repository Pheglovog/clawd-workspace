"""
PDF 行程单生成器
生成美观的 PDF 行程单，供用户保存和打印
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from loguru import logger

# 检查 reportlab 库
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.lib.units import inch, mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # 注册中文字体（这里使用默认字体，实际应该下载并注册中文字体）
    try:
        font = TTFont('SimSun', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        pdfmetrics.registerFont(font)
        addMapping('SimSun', 0, 0, 'utf-8')
        CHINESE_FONT = 'SimSun'
    except:
        CHINESE_FONT = 'Helvetica'  # 如果中文字体加载失败，使用默认字体
except ImportError:
    logger.error("reportlab 未安装，请运行：pip install reportlab")
    CHINESE_FONT = 'Helvetica'


class ItineraryItem(BaseModel):
    """行程项目"""
    day: int = Field(description="天数")
    date: datetime = Field(description="日期")
    activities: List[str] = Field(default_factory=list, description="活动列表")
    meals: List[str] = Field(default_factory=list, description="餐饮")
    transportation: str = Field(default="", description="交通方式")
    notes: str = Field(default="", description="备注")


class BudgetBreakdown(BaseModel):
    """预算明细"""
    item: str = Field(description="项目")
    amount: float = Field(description="金额")
    currency: str = Field(default="CNY", description="货币")


class Itinerary(BaseModel):
    """行程单"""
    destination: str = Field(description="目的地")
    travel_dates: Dict[str, Any] = Field(description="旅行日期（start, end）")
    duration_days: int = Field(description="旅行天数")
    travelers: List[Dict[str, str]] = Field(description="旅行者信息")
    total_budget: float = Field(description="总预算")
    budget_breakdown: List[BudgetBreakdown] = Field(default_factory=list, description="预算明细")
    itinerary: List[ItineraryItem] = Field(description="行程安排")
    notes: str = Field(default="", description="其他备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class PDFGenerator:
    """PDF 生成器"""

    def __init__(self, output_dir: str = "./pdf_output"):
        """
        初始化 PDF 生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 样式
        self.styles = self._create_styles()

    def _create_styles(self) -> Dict[str, Any]:
        """创建 PDF 样式"""
        styles = getSampleStyleSheet()

        # 自定义样式
        styles.add(ParagraphStyle(
            name='Title',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=TA_CENTER
        ))

        styles.add(ParagraphStyle(
            name='Subtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkgray,
            alignment=TA_CENTER
        ))

        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue,
            alignment=TA_LEFT,
            fontName=CHINESE_FONT
        ))

        styles.add(ParagraphStyle(
            name='Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14,
            fontName=CHINESE_FONT
        ))

        styles.add(ParagraphStyle(
            name="Small",
            parent=styles['Normal'],
            fontSize=8,
            fontName=CHINESE_FONT
        ))

        return styles

    def generate_itinerary_pdf(
        self,
        itinerary: Itinerary,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        生成行程单 PDF

        Args:
            itinerary: 行程单对象
            filename: 文件名（可选，如果不提供，自动生成）

        Returns:
            PDF 文件路径（如果生成成功），否则返回 None
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"行程单_{itinerary.destination}_{timestamp}.pdf"

        pdf_path = self.output_dir / filename

        try:
            # 创建 PDF 文档
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)

            # 添加内容
            story = []
            
            # 1. 标题
            title = f"{itinerary.destination} 旅行行程单"
            story.append(Paragraph(title, self.styles['Title']))
            story.append(Spacer(1, 20))

            # 2. 基本信息
            story.append(Paragraph("基本信息", self.styles['Subtitle']))
            story.append(Spacer(1, 10))

            info_data = [
                ["目的地", itinerary.destination],
                ["旅行日期", f"{itinerary.travel_dates['start'].strftime('%Y年%m月%d日')} - {itinerary.travel_dates['end'].strftime('%Y年%m月%d日')}"],
                ["旅行天数", f"{itinerary.duration_days} 天"],
                ["旅行人数", f"{len(itinerary.travelers)} 人"]
            ]

            info_table = Table(info_data, colWidths=[100, 200])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 1), colors.whitesmoke),
                ('TEXTCOLOR', (0, 0), (1, 1), colors.black),
                ('ALIGN', (0, 0), (1, 1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, 0), CHINESE_FONT),
                ('FONTSIZE', (0, 0), (0, 0), 10),
                ('BOTTOMPADDING', (0, 0), (1, 1), 8),
                ('TOPPADDING', (0, 0), (1, 1), 8),
                ('LEFTPADDING', (0, 0), (1, 1), 8),
                ('RIGHTPADDING', (0, 0), (1, 1), 8),
            ]))

            story.append(info_table)
            story.append(Spacer(1, 20))

            # 3. 旅行者信息
            if itinerary.travelers:
                story.append(Paragraph("旅行者信息", self.styles['Subtitle']))
                story.append(Spacer(1, 10))

                for traveler in itinerary.travelers:
                    traveler_info = [
                        ["姓名", traveler['name']],
                        ["年龄", traveler.get('age', '')],
                        ["性别", traveler.get('gender', '')],
                        ["联系方式", traveler.get('contact', '')]
                    ]

                    traveler_table = Table(traveler_info, colWidths=[80, 120, 80, 120])
                    traveler_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 1), colors.whitesmoke),
                        ('TEXTCOLOR', (0, 0), (1, 1), colors.black),
                        ('ALIGN', (0, 0), (1, 1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, 0), CHINESE_FONT),
                        ('FONTSIZE', (0, 0), (0, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (1, 1), 8),
                        ('TOPPADDING', (0, 0), (1, 1), 8),
                        ('LEFTPADDING', (0, 0), (1, 1), 8),
                        ('RIGHTPADDING', (0, 0), (1, 1), 8),
                    ]))

                    story.append(traveler_table)
                    story.append(Spacer(1, 10))

            # 4. 行程安排
            if itinerary.itinerary:
                story.append(Paragraph("行程安排", self.styles['Subtitle']))
                story.append(Spacer(1, 10))

                for item in itinerary.itinerary:
                    day_info = f"第 {item.day} 天 - {item.date.strftime('%Y年%m月%d日')}"
                    story.append(Paragraph(day_info, self.styles['SectionHeader']))
                    story.append(Spacer(1, 8))

                    # 活动
                    if item.activities:
                        story.append(Paragraph("活动：", self.styles['Normal']))
                        for activity in item.activities:
                            story.append(Paragraph(f"  • {activity}", self.styles['Normal']))
                        story.append(Spacer(1, 4))

                    # 餐饮
                    if item.meals:
                        story.append(Paragraph("餐饮：", self.styles['Normal']))
                        for meal in item.meals:
                            story.append(Paragraph(f"  • {meal}", self.styles['Normal']))
                        story.append(Spacer(1, 4))

                    # 交通
                    if item.transportation:
                        story.append(Paragraph(f"交通：{item.transportation}", self.styles['Normal']))
                        story.append(Spacer(1, 6))

                    # 备注
                    if item.notes:
                        story.append(Paragraph(f"备注：{item.notes}", self.styles['Small']))
                        story.append(Spacer(1, 6))

                    story.append(Spacer(1, 15))

            # 5. 预算明细
            if itinerary.budget_breakdown:
                story.append(Paragraph("预算明细", self.styles['Subtitle']))
                story.append(Spacer(1, 10))

                total_amount = 0
                for budget in itinerary.budget_breakdown:
                    total_amount += budget.amount
                    budget_info = [
                        [budget.item, f"{budget.amount:.2f} {budget.currency}"]
                    ]

                    budget_table = Table(budget_info, colWidths=[200, 100])
                    budget_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 1), colors.whitesmoke),
                        ('TEXTCOLOR', (0, 0), (1, 1), colors.black),
                        ('ALIGN', (0, 0), (1, 1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, 0), CHINESE_FONT),
                        ('FONTSIZE', (0, 0), (0, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (1, 1), 8),
                        ('TOPPADDING', (0, 0), (1, 1), 8),
                        ('LEFTPADDING', (0, 0), (1, 1), 8),
                        ('RIGHTPADDING', (0, 0), (1, 1), 8),
                    ]))

                    story.append(budget_table)
                    story.append(Spacer(1, 10))

                # 总预算
                total_info = [
                    ["总预算", f"{itinerary.total_budget:.2f} {itinerary.budget_breakdown[0].currency if itinerary.budget_breakdown else 'CNY'}"],
                    ["实际预算", f"{total_amount:.2f} {itinerary.budget_breakdown[0].currency if itinerary.budget_breakdown else 'CNY'}"]
                ]

                total_table = Table(total_info, colWidths=[200, 200])
                total_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (1, 1), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (1, 1), colors.black),
                    ('ALIGN', (0, 0), (1, 1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, 0), CHINESE_FONT),
                    ('FONTSIZE', (0, 0), (0, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (1, 1), 10),
                    ('TOPPADDING', (0, 0), (1, 1), 10),
                    ('LEFTPADDING', (0, 0), (1, 1), 12),
                    ('RIGHTPADDING', (0, 0), (1, 1), 12),
                ]))

                story.append(total_table)
                story.append(Spacer(1, 20))

            # 6. 其他备注
            if itinerary.notes:
                story.append(Paragraph("其他备注", self.styles['Subtitle']))
                story.append(Spacer(1, 10))
                story.append(Paragraph(itinerary.notes, self.styles['Normal']))
                story.append(Spacer(1, 20))

            # 7. 页脚
            footer_text = f"生成时间：{itinerary.created_at.strftime('%Y年%m月%d日 %H:%M:%S')}"
            story.append(Paragraph(footer_text, self.styles['Small']))
            story.append(Spacer(1, 10))

            # 添加页码和版权信息
            def footer(canvas, doc):
                canvas.saveState()
                canvas.setFont(CHINESE_FONT, 8)
                canvas.drawRightString(200 * mm, 15 * mm, f"第 {doc.page} 页")
                canvas.drawString(20 * mm, 15 * mm, f"© 2026 Travel Planner Agent")
                canvas.restoreState()

            # 构建 PDF
            doc.build(story, onFirstPage=footer, onLaterPages=footer)

            logger.info(f"✅ PDF 已生成：{pdf_path}")

            return str(pdf_path)

        except Exception as e:
            logger.error(f"❌ PDF 生成失败: {e}")
            return None

    def generate_simple_itinerary_pdf(
        self,
        destination: str,
        days: int,
        start_date: datetime,
        activities: List[List[str]],
        budget: float,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        生成简化的行程单 PDF

        Args:
            destination: 目的地
            days: 天数
            start_date: 开始日期
            activities: 每天的活动列表
            budget: 预算
            filename: 文件名（可选）

        Returns:
            PDF 文件路径（如果生成成功），否则返回 None
        """
        # 创建行程单对象
        itinerary_items = []
        current_date = start_date

        for day, day_activities in enumerate(activities, 1):
            item = ItineraryItem(
                day=day,
                date=current_date,
                activities=day_activities
            )
            itinerary_items.append(item)
            current_date += timedelta(days=1)

        budget_breakdown = [
            BudgetBreakdown(item="住宿", amount=budget * 0.4),
            BudgetBreakdown(item="交通", amount=budget * 0.3),
            BudgetBreakdown(item="餐饮", amount=budget * 0.2),
            BudgetBreakdown(item="购物", amount=budget * 0.1)
        ]

        itinerary = Itinerary(
            destination=destination,
            travel_dates={
                'start': start_date,
                'end': start_date + timedelta(days=days - 1)
            },
            duration_days=days,
            travelers=[{'name': '旅行者1'}],  # 默认一个旅行者
            total_budget=budget,
            budget_breakdown=budget_breakdown,
            itinerary=itinerary_items
        )

        return self.generate_itinerary_pdf(itinerary, filename)


# 使用示例
def example_usage():
    """使用示例"""
    # 创建 PDF 生成器
    generator = PDFGenerator()

    # 示例 1: 使用完整的数据结构
    print("\n=== 示例 1: 生成完整的行程单 PDF ===")
    
    itinerary = Itinerary(
        destination="东京",
        travel_dates={
            'start': datetime(2024, 4, 1),
            'end': datetime(2024, 4, 7)
        },
        duration_days=7,
        travelers=[
            {'name': '张三', 'age': '30', 'gender': '男', 'contact': 'zhangsan@example.com'},
            {'name': '李四', 'age': '28', 'gender': '女', 'contact': 'lisi@example.com'}
        ],
        total_budget=20000.0,
        budget_breakdown=[
            BudgetBreakdown(item="住宿", amount=6000.0),
            BudgetBreakdown(item="交通", amount=5000.0),
            BudgetBreakdown(item="餐饮", amount=4000.0),
            BudgetBreakdown(item="购物", amount=3000.0),
            BudgetBreakdown(item="其他", amount=2000.0)
        ],
        itinerary=[
            ItineraryItem(
                day=1,
                date=datetime(2024, 4, 1),
                activities=[
                    "上午：抵达东京，办理酒店入住",
                    "下午：参观东京塔",
                    "晚上：在银座购物"
                ],
                meals=["早餐：酒店", "午餐：东京塔附近餐厅", "晚餐：银座餐厅"],
                transportation="地铁",
                notes="记得带护照和信用卡"
            ),
            ItineraryItem(
                day=2,
                date=datetime(2024, 4, 2),
                activities=[
                    "上午：浅草寺和金阁寺",
                    "下午：京都岚山",
                    "晚上：品尝怀石料理"
                ],
                meals=["早餐：酒店", "午餐：怀石料理", "晚餐：京都餐厅"],
                transportation="新干线",
                notes="新干线车票已购买"
            )
        ],
        notes="祝旅途愉快！有任何问题请联系：example@example.com"
    )

    pdf_path = generator.generate_itinerary_pdf(itinerary)
    print(f"PDF 路径: {pdf_path}")

    # 示例 2: 使用简化的接口
    print("\n=== 示例 2: 生成简化的行程单 PDF ===")
    
    activities = [
        ["上午：参观东京塔", "下午：银座购物", "晚上：晚餐"],
        ["浅草寺", "金阁寺", "岚山"],
        ["清水寺", "伏见稻荷大社", "祗园"],
        ["皇居", "二重桥", "明治神宫"],
        ["迪士尼乐园", "全天"],
        ["秋叶原", "电器街", "全天"],
        ["准备返程", "全天"]
    ]

    pdf_path = generator.generate_simple_itinerary_pdf(
        destination="东京",
        days=7,
        start_date=datetime(2024, 4, 1),
        activities=activities,
        budget=20000.0
    )
    print(f"PDF 路径: {pdf_path}")


if __name__ == "__main__":
    example_usage()
