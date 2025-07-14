import os
import pytest
from expenditure_analyse.parser import CsvParser

@pytest.fixture
def sample_csv_path(tmp_path):
    """创建临时CSV文件供测试使用"""
    csv_content = """日期,交易时间,交易金额,余额,交易类型,交易描述,对方账户名,备注
2023-10-01,10:00:00,-50.00,1950.00,支出,午餐_外卖,饿了么,
2023-10-02,08:00:00,100.00,2050.00,收入,兼职工资,ABC公司,
2023-10-03,09:00:00,-abc.00,1950.00,支出,错误金额,测试,
"""
    file_path = tmp_path / "test_bank_statement.csv"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    return file_path

@pytest.fixture
def csv_config():
    return {
        "date_col": "日期",
        "amount_col": "交易金额",
        "description_col": "交易描述",
        "type_col": "交易类型",
        "income_keyword": "收入",
        "expense_keyword": "支出"
    }

def test_parse_csv_basic(sample_csv_path, csv_config):
    parser = CsvParser()
    transactions_data = parser.parse(sample_csv_path, csv_config)

    assert len(transactions_data) == 3 # 包含错误行，但应被解析出来
    assert transactions_data[0]["日期"] == "2023-10-01"
    assert transactions_data[0]["交易金额"] == "-50.00" # 保持原始字符串，后续转换
    assert transactions_data[0]["交易描述"] == "午餐_外卖"

    assert transactions_data[2]["交易金额"] == "-abc.00" # 错误金额也应被读取

def test_parse_csv_missing_column(sample_csv_path, csv_config):
    parser = CsvParser()
    modified_config = csv_config.copy()
    modified_config["date_col"] = "不存在的日期" # 故意设置一个不存在的列
    with pytest.raises(ValueError, match="Missing required column '不存在的日期' in CSV header."):
        parser.parse(sample_csv_path, modified_config)

def test_parse_csv_empty_file(tmp_path, csv_config):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")
    parser = CsvParser()
    with pytest.raises(ValueError, match="CSV file is empty or has no header."):
        parser.parse(empty_file, csv_config)

def test_parse_csv_non_existent_file(csv_config):
    parser = CsvParser()
    with pytest.raises(ValueError, match="File not found: non_existent.csv"):
        parser.parse("non_existent.csv", csv_config)