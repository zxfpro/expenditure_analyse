import pandas as pd
import os

def load_csv(file_path: str, column_mapping: dict) -> pd.DataFrame:
    """
    Loads a CSV file from the specified path and maps column names.

    Args:
        file_path (str): The path to the CSV file.
        column_mapping (dict): A dictionary mapping internal standard column names
                               to the actual column names in the CSV file.
                               Example: {"date_col": "日期", "amount_col": "金额", ...}

    Returns:
        pd.DataFrame: The loaded DataFrame with mapped column names.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing in the CSV.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"无法读取CSV文件，请检查文件格式: {e}")

    # Reverse mapping for easier lookup from CSV column to standard name
    reverse_mapping = {v: k for k, v in column_mapping.items()}
    
    # Check for required columns
    required_csv_cols = [column_mapping["date_col"], column_mapping["amount_col"], column_mapping["description_col"]]
    for col in required_csv_cols:
        if col not in df.columns:
            raise ValueError(f"CSV文件中缺少必要列: '{col}'。请检查您的列映射配置。")

    # Rename columns to standard internal names
    df = df.rename(columns={
        column_mapping["date_col"]: "date",
        column_mapping["amount_col"]: "amount",
        column_mapping["description_col"]: "description"
    })
    
    # If '时间' column exists, rename it to 'time_str'
    if "时间" in df.columns:
        df = df.rename(columns={"时间": "time_str"})

    return df

def preprocess_data(df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
    """
    Preprocesses the loaded DataFrame:
    - Converts 'date' column to datetime objects.
    - Converts 'amount' column to numeric, handling negative values for expenses.
    - Creates an 'is_income' column (True for income, False for expense).

    Args:
        df (pd.DataFrame): The DataFrame loaded from CSV with standard column names.
        column_mapping (dict): The column mapping used during loading (needed for amount column check).

    Returns:
        pd.DataFrame: The preprocessed DataFrame.

    Raises:
        ValueError: If date or amount columns cannot be processed.
    """
    # Convert 'date' to datetime, combining with 'time_str' if available
    try:
        if 'time_str' in df.columns:
            df['date'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time_str'].astype(str))
            df = df.drop(columns=['time_str']) # Drop the original time string column
        else:
            df['date'] = pd.to_datetime(df['date'])
        
        # Extract hour for prediction purposes
        df['hour'] = df['date'].dt.hour
    except Exception as e:
        raise ValueError(f"日期列 '{column_mapping['date_col']}' 格式不正确，无法转换为日期类型: {e}")

    # Convert 'amount' to numeric and create 'is_income'
    try:
        # Ensure amount is numeric. If it's already numeric, this does nothing.
        # If it's string like "-100.00", it will convert to -100.00
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        if df['amount'].isnull().any():
            raise ValueError("金额列包含无法转换为数字的值。")
        
        # Determine if it's income or expense.
        # Assuming positive amounts are income, negative are expenses.
        # If the original CSV uses positive for both and a separate 'transaction_type' column,
        # this logic would need adjustment. For now, based on LLD example, amount is signed.
        df['is_income'] = df['amount'] > 0
        df['expense_amount'] = df['amount'].apply(lambda x: abs(x) if x < 0 else 0)
        df['income_amount'] = df['amount'].apply(lambda x: x if x > 0 else 0)

    except Exception as e:
        raise ValueError(f"金额列 '{column_mapping['amount_col']}' 格式不正确，无法转换为数字类型或处理收入/支出: {e}")

    return df