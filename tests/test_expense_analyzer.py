import pytest
from datetime import datetime
from expenditure_analyse.core import Transaction
from expenditure_analyse.analyzer import ExpenseAnalyzer

@pytest.fixture
def sample_transactions():
    return [
        Transaction(datetime(2023, 10, 1), 50.00, "午餐", "expense", "餐饮"),
        Transaction(datetime(2023, 10, 1), 150.00, "购物", "expense", "购物"),
        Transaction(datetime(2023, 10, 2), 200.00, "工资", "income", "收入"),
        Transaction(datetime(2023, 10, 2), 30.00, "咖啡", "expense", "餐饮"),
        Transaction(datetime(2023, 10, 3), 70.00, "娱乐", "expense", "娱乐"),
        Transaction(datetime(2023, 10, 3), 100.00, "奖金", "income", "收入"),
        Transaction(datetime(2023, 10, 4), 20.00, "公交", "expense", "交通"),
        Transaction(datetime(2023, 10, 5), 10.00, "未知消费", "expense", "Uncategorized"),
    ]

@pytest.fixture
def analyzer():
    return ExpenseAnalyzer()

def test_generate_monthly_report_totals(analyzer, sample_transactions):
    report = analyzer.generate_monthly_report(sample_transactions)

    assert report["total_income"] == 300.00
    assert report["total_expense"] == 330.00
    assert report["net_balance"] == -30.00

def test_generate_monthly_report_category_distribution(analyzer, sample_transactions):
    report = analyzer.generate_monthly_report(sample_transactions)
    expense_by_category = report["expense_by_category"]

    assert "餐饮" in expense_by_category
    assert expense_by_category["餐饮"]["amount"] == 80.00
    assert pytest.approx(expense_by_category["餐饮"]["percentage"]) == (80.00 / 330.00) * 100

    assert "购物" in expense_by_category
    assert expense_by_category["购物"]["amount"] == 150.00

    assert "娱乐" in expense_by_category
    assert expense_by_category["娱乐"]["amount"] == 70.00

    assert "交通" in expense_by_category
    assert expense_by_category["交通"]["amount"] == 20.00

    assert "Uncategorized" in expense_by_category
    assert expense_by_category["Uncategorized"]["amount"] == 10.00

    assert "收入" not in expense_by_category # 类别分布只针对支出

def test_generate_monthly_report_empty_transactions(analyzer):
    report = analyzer.generate_monthly_report([])
    assert report["total_income"] == 0.0
    assert report["total_expense"] == 0.0
    assert report["net_balance"] == 0.0
    assert report["expense_by_category"] == {}