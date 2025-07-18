import os
import pytest
import pandas as pd
import datetime # Added for mocking datetime
from expenditure_analyse import utils
from expenditure_analyse.core import analyze_bank_statement, query_bank_statement
from expenditure_analyse.config import DEFAULT_COLUMN_MAPPING, DEFAULT_CATEGORY_RULES

# Import core module to access its internal cache
import expenditure_analyse.core

@pytest.fixture(autouse=True)
def clear_processed_df_cache():
    """Fixture to clear the _processed_df_cache before each test."""
    expenditure_analyse.core._processed_df_cache = None
    yield
    expenditure_analyse.core._processed_df_cache = None # Ensure it's cleared after test too

# Mock CSV content for testing
MOCK_CSV_CONTENT_BASIC = """日期,时间,交易类型,金额,商户/摘要
2023-10-01,10:00,收入,1000.00,工资入账
2023-10-02,11:00,支出,-50.00,星巴克咖啡
2023-10-03,12:00,支出,-120.00,麻辣烫午餐
2023-10-04,13:00,支出,-30.00,公交卡充值
2023-10-05,14:00,支出,-200.00,超市购物
2023-10-06,15:00,支出,-15.00,便利店零食
2023-10-07,16:00,支出,-80.00,电影票
2023-10-08,12:30,支出,-60.00,KTV
2023-10-09,09:00,支出,-500.00,健身房年费
"""

MOCK_CSV_CONTENT_PREDICTION = """日期,时间,交易类型,金额,商户/摘要
2023-09-01,12:05,支出,-30.00,兰州拉面
2023-09-08,12:10,支出,-28.00,沙县小吃
2023-09-15,12:00,支出,-35.00,黄焖鸡
2023-09-22,18:30,支出,-100.00,火锅
2023-09-29,12:00,支出,-32.00,肉夹馍
2023-10-01,10:00,收入,1000.00,工资入账
"""


@pytest.fixture
def mock_basic_csv_file(tmp_path):
    """Fixture to create a temporary basic CSV file for testing analyze_bank_statement."""
    file_path = tmp_path / "test_basic_statement.csv"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(MOCK_CSV_CONTENT_BASIC)
    return str(file_path)

@pytest.fixture
def mock_prediction_csv_file(tmp_path):
    """Fixture to create a temporary CSV file for prediction testing."""
    file_path = tmp_path / "test_prediction_statement.csv"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(MOCK_CSV_CONTENT_PREDICTION)
    return str(file_path)

def test_analyze_bank_statement_success(mock_basic_csv_file):
    """Test that analyze_bank_statement runs successfully and returns a string report with advice."""
    report = analyze_bank_statement(mock_basic_csv_file)
    assert isinstance(report, str)
    assert "总收入: 1000.00" in report
    assert "总支出: -1055.00" in report # 50+120+30+200+15+80+60+500 = 1055
    assert "餐饮: -    170.00" in report # 50+120 (Adjusted for actual report format)
    assert "交通: -     30.00" in report
    assert "购物: -    215.00" in report # 200+15
    assert "娱乐: -    140.00" in report # 80+60
    assert "其他: -    500.00" in report # 健身房
    assert "智能建议" in report # Check for advice section

def test_analyze_bank_statement_file_not_found():
    """Test that analyze_bank_statement raises FileNotFoundError for non-existent file."""
    with pytest.raises(FileNotFoundError):
        analyze_bank_statement("non_existent_file.csv")

def test_analyze_bank_statement_custom_config(tmp_path):
    """Test analyze_bank_statement with custom column mapping and category rules."""
    custom_csv_content = """TxnDate,AmountUSD,ItemDescription
2023-11-01,200.00,Salary Payment
2023-11-02,-75.00,Restaurant Dinner
2023-11-03,-25.00,Bus Ticket
"""
    custom_file_path = tmp_path / "custom_statement.csv"
    with open(custom_file_path, "w", encoding="utf-8") as f:
        f.write(custom_csv_content)

    custom_config = {
        "column_mapping": {
            "date_col": "TxnDate",
            "amount_col": "AmountUSD",
            "description_col": "ItemDescription"
        },
        "category_rules": {
            "Food": ["Restaurant"],
            "Transport": ["Bus"],
            "Income": ["Salary"]
        }
    }
    report = analyze_bank_statement(str(custom_file_path), config=custom_config)
    assert "总收入: 200.00" in report
    assert "总支出: -100.00" in report
    assert "Food" in report # Should use custom category name
    assert "Transport" in report
    assert "餐饮" not in report # Should not use default categories for these

def test_analyze_bank_statement_empty_csv(tmp_path):
    """Test handling of an empty CSV file (header only)."""
    empty_file_path = tmp_path / "empty.csv"
    with open(empty_file_path, "w", encoding="utf-8") as f:
        f.write("日期,时间,交易类型,金额,商户/摘要\n") # Only header
    report = analyze_bank_statement(str(empty_file_path))
    assert "总收入: 0.00" in report
    assert "总支出: 0.00" in report
    assert "没有发现支出数据。" in report # Or similar message from report generator

def test_query_bank_statement_before_analysis():
    """Test that query_bank_statement raises RuntimeError if no data is loaded."""
    with pytest.raises(RuntimeError) as excinfo:
        query_bank_statement("我的总支出是多少？")
    assert "没有可供查询的银行流水数据" in str(excinfo.value)

def test_query_bank_statement_total_expense(mock_basic_csv_file):
    """Test querying total expense."""
    analyze_bank_statement(mock_basic_csv_file) # Load data first
    answer = query_bank_statement("我的总支出是多少？")
    assert "1055.00" in answer
    assert "总支出" in answer

def test_query_bank_statement_category_expense(mock_basic_csv_file):
    """Test querying expense for a specific category."""
    analyze_bank_statement(mock_basic_csv_file)
    answer = query_bank_statement("我的餐饮支出是多少？")
    assert "170.00" in answer
    assert "餐饮" in answer

def test_query_bank_statement_recent_spending(mock_basic_csv_file, monkeypatch):
    """Test querying recent spending (e.g., last week)."""
    # Mock datetime.now() to a fixed date for consistent testing
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return cls(2023, 10, 9, 12, 0, 0) # Set a fixed date for the test

    monkeypatch.setattr(utils, 'datetime', MockDatetime)

    analyze_bank_statement(mock_basic_csv_file)
    answer = query_bank_statement("我上周花了多少钱？")
    # Last week from 2023-10-09 would be 2023-10-02 to 2023-10-08
    # 50(咖啡)+120(麻辣烫)+30(公交)+200(超市)+15(便利店)+80(电影)+60(KTV) = 555
    assert "555.00" in answer

def test_query_bank_statement_prediction_lunch(mock_prediction_csv_file, monkeypatch):
    """Test prediction for a specific time, like lunch."""
    # Mock datetime.now() to a fixed date for consistent testing
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return cls(2023, 9, 15, 12, 0, 0) # Set a fixed date for the test, closer to prediction data

    monkeypatch.setattr(utils, 'datetime', MockDatetime)

    analyze_bank_statement(mock_prediction_csv_file)
    answer = query_bank_statement("我每天中午12点通常会做什么？")
    assert "餐饮" in answer
    assert "兰州拉面" in answer or "沙县小吃" in answer or "黄焖鸡" in answer or "肉夹馍" in answer # Check for common lunch items
    assert "这可能意味着您在这个时间段通常会用餐或购买饮品。" in answer

def test_query_bank_statement_specific_date_activity(mock_basic_csv_file):
    """Test querying activity on a specific date."""
    analyze_bank_statement(mock_basic_csv_file)
    answer = query_bank_statement("我2023年10月05号做了什么？")
    assert "超市购物" in answer
    assert "200.00" in answer

def test_query_bank_statement_unrecognized_query(mock_basic_csv_file):
    """Test handling of a query that cannot be fully understood."""
    analyze_bank_statement(mock_basic_csv_file)
    answer = query_bank_statement("告诉我一些不寻常的事情。")
    assert "抱歉" in answer or "无法理解" in answer # Or similar polite fallback message