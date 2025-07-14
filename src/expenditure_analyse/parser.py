import csv
from datetime import datetime

class CsvParser:
    def parse(self, file_path: str, csv_mapping: dict) -> list[dict]:
        """
        解析CSV文件，提取原始数据。
        :param file_path: CSV文件路径
        :param csv_mapping: 包含列名映射的字典，例如 {"date_col": "日期", "amount_col": "交易金额"}
        :return: 包含每行数据的字典列表
        :raises ValueError: 如果文件不存在、为空或缺少必要的列
        """
        if not file_path:
            raise ValueError("File path cannot be empty.")
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise ValueError("CSV file is empty or has no header.")

                # 检查所有必要的列是否存在
                required_cols = [
                    csv_mapping["date_col"],
                    csv_mapping["amount_col"],
                    csv_mapping["description_col"],
                    csv_mapping["type_col"]
                ]
                for col in required_cols:
                    if col not in reader.fieldnames:
                        raise ValueError(f"Missing required column '{col}' in CSV header.")

                transactions_data = []
                for row in reader:
                    transactions_data.append(row)
                return transactions_data
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {e}")
