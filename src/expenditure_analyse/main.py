import os
from datetime import datetime
from expenditure_analyse.core import Transaction
from expenditure_analyse.parser import CsvParser
from expenditure_analyse.classifier import ExpenseClassifier
from expenditure_analyse.analyzer import ExpenseAnalyzer
from expenditure_analyse.llm_integrator import LlmIntegrator
from expenditure_analyse.config import ConfigManager

class ExpenseAnalysisManager:
    def __init__(self, config: dict = None):
        self.config = config if config is not None else ConfigManager().get_default_config()
        self.parser = CsvParser()
        self.classifier = ExpenseClassifier()
        self.analyzer = ExpenseAnalyzer()
        self.llm_integrator = LlmIntegrator(self.config.get("llm_config"))

    def analyze_bank_statement(self, file_path: str) -> tuple[dict, dict]:
        """
        分析银行流水文件，生成报告并获取LLM洞察。
        :param file_path: 银行流水CSV文件路径
        :return: (月度报告字典, LLM洞察字典)
        """
        # 1. 解析CSV文件
        raw_transactions_data = self.parser.parse(file_path, self.config["csv_mapping"])

        transactions = []
        for data in raw_transactions_data:
            try:
                date_str = data[self.config["csv_mapping"]["date_col"]]
                # 尝试多种日期格式
                date_obj = None
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                if date_obj is None:
                    raise ValueError(f"Could not parse date: {date_str}")

                amount_str = data[self.config["csv_mapping"]["amount_col"]]
                amount = float(amount_str)

                description = data[self.config["csv_mapping"]["description_col"]]
                transaction_type_str = data[self.config["csv_mapping"]["type_col"]]

                transaction_type = "expense"
                if self.config["csv_mapping"]["income_keyword"] in transaction_type_str:
                    transaction_type = "income"
                elif self.config["csv_mapping"]["expense_keyword"] in transaction_type_str:
                    transaction_type = "expense"
                elif amount > 0: # 如果没有明确的类型关键词，根据金额正负判断
                    transaction_type = "income"
                elif amount < 0:
                    transaction_type = "expense"

                # 分类
                category = self.classifier.classify(description, self.config["classification_rules"])

                transactions.append(Transaction(
                    date=date_obj,
                    amount=amount,
                    description=description,
                    transaction_type=transaction_type,
                    category=category,
                    original_data=data
                ))
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to data error: {data} - {e}")
                continue

        # 2. 生成分析报告
        monthly_report = self.analyzer.generate_monthly_report(transactions)

        # 3. LLM集成 (V1.0 模拟)
        prepared_data = self.llm_integrator.prepare_data_for_llm(monthly_report)
        # 模拟LLM响应，V1.0不进行实际API调用
        llm_insights = self.llm_integrator.process_llm_response(None) # 传入None模拟无实际LLM响应

        return monthly_report, llm_insights
