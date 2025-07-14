import os
from expenditure_analyse.main import ExpenseAnalysisManager
from expenditure_analyse.config import ConfigManager

# 1. 定义或加载配置
config_manager = ConfigManager()
config = config_manager.get_default_config()

# 实例化分析管理器
manager = ExpenseAnalysisManager(config)

# 2. 指定银行流水文件路径
csv_file_path = "bank_statement_sample.csv"

# 创建一个虚拟的CSV文件，用于示例运行
if not os.path.exists(csv_file_path):
    with open(csv_file_path, "w", encoding="utf-8") as f:
        f.write("""日期,交易时间,交易金额,余额,交易类型,交易描述,对方账户名,备注
2023-10-01,10:00:00,-50.00,1950.00,支出,午餐_外卖,饿了么,
2023-10-01,15:30:00,-15.00,1935.00,支出,公交卡充值,公共交通,
2023-10-02,08:00:00,-120.00,1815.00,支出,超市购物_日常用品,沃尔玛,
2023-10-02,18:00:00,-88.50,1726.50,支出,晚餐_火锅,海底捞,
2023-10-03,09:30:00,200.00,1926.50,收入,工资_兼职,ABC公司,
2023-10-03,14:00:00,-35.00,1891.50,支出,咖啡,星巴克,
2023-10-04,11:00:00,-250.00,1641.50,支出,网购_电子产品,京东,
2023-10-05,20:00:00,-60.00,1581.50,支出,电影票_娱乐,万达影院,
""")
    print(f"Created dummy CSV file: {csv_file_path}")

# 3. 执行分析
print(f"正在分析文件: {csv_file_path}...")
try:
    monthly_report, llm_insights = manager.analyze_bank_statement(csv_file_path)

    # 4. 打印分析结果和来自大模型的洞察
    print("\n--- 月度花销报告 ---")
    print(f"总收入: {monthly_report['total_income']:.2f} 元")
    print(f"总支出: {monthly_report['total_expense']:.2f} 元")
    print(f"净结余: {monthly_report['net_balance']:.2f} 元")

    print("\n--- 支出类别分布 ---")
    for category, details in monthly_report['expense_by_category'].items():
        print(f"- {category}: {details['amount']:.2f} 元 ({details['percentage']:.2f}%)")

    print("\n--- 大模型消费洞察与建议 (V1.0为模拟输出) ---")
    if llm_insights:
        print(f"行为洞察: {llm_insights.get('llm_advice', '（未提供具体建议，请检查LLM配置）')}")
        print(f"消费预测: {llm_insights.get('llm_prediction', '（未提供具体预测，请检查LLM配置）')}")
    else:
        print("（大模型集成模块尚未配置或返回结果）")

except ValueError as e:
    print(f"分析失败: {e}")
except Exception as e:
    print(f"发生未知错误: {e}")

finally:
    # 清理示例文件 (可选)
    # if os.path.exists(csv_file_path):
    #     os.remove(csv_file_path)
    pass
