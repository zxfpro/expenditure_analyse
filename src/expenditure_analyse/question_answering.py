import pandas as pd
from datetime import datetime, timedelta
from .utils import get_date_range_from_query, extract_date_from_query
from .log import setup_logging

logger = setup_logging()

def answer_query(df: pd.DataFrame, query: str) -> str:
    """
    Answers natural language questions based on the transaction data.

    Args:
        df (pd.DataFrame): The processed DataFrame with transaction data.
        query (str): The natural language query.

    Returns:
        str: A natural language answer.
    """
    query_lower = query.lower()

    # --- General Expense/Income Queries ---
    if "总支出" in query_lower or "一共花了多少钱" in query_lower:
        total_expense = df[~df['is_income']]['amount'].sum()
        return f"您的总支出是 {abs(total_expense):.2f} 元。"
    elif "总收入" in query_lower or "一共赚了多少钱" in query_lower:
        total_income = df[df['is_income']]['amount'].sum()
        return f"您的总收入是 {total_income:.2f} 元。"
    elif "净结余" in query_lower or "还剩多少钱" in query_lower:
        net_balance = df['amount'].sum()
        return f"您的净结余是 {net_balance:.2f} 元。"

    # --- Category-specific Queries ---
    for category in ["餐饮", "交通", "购物", "生活缴费", "娱乐", "其他"]: # Assuming these are the main categories
        if f"{category}支出" in query_lower or f"在{category}上花了多少" in query_lower:
            category_expense = df[(df['category'] == category) & (~df['is_income'])]['amount'].sum()
            return f"您在{category}上的支出是 {abs(category_expense):.2f} 元。"
        elif f"{category}收入" in query_lower:
            category_income = df[(df['category'] == category) & (df['is_income'])]['amount'].sum()
            return f"您在{category}上的收入是 {category_income:.2f} 元。"

    # --- Time-based Queries ---
    start_date, end_date = get_date_range_from_query(query)
    if start_date and end_date:
        filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        if "花了多少钱" in query_lower or "支出" in query_lower:
            time_expense = filtered_df[~filtered_df['is_income']]['amount'].sum()
            return f"从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}，您的总支出是 {abs(time_expense):.2f} 元。"
        elif "赚了多少钱" in query_lower or "收入" in query_lower:
            time_income = filtered_df[filtered_df['is_income']]['amount'].sum()
            return f"从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}，您的总收入是 {time_income:.2f} 元。"
        elif "花钱最多的地方" in query_lower:
            expense_in_range = filtered_df[~filtered_df['is_income']]
            if not expense_in_range.empty:
                most_expensive_category = expense_in_range.groupby('category')['amount'].sum().abs().idxmax()
                return f"从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}，您花钱最多的地方是 {most_expensive_category}。"
            else:
                return f"从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}，没有发现支出数据。"
        elif "做了什么" in query_lower or "活动" in query_lower:
            # Specific date activity
            specific_date = extract_date_from_query(query)
            if specific_date:
                daily_transactions = df[df['date'].dt.date == specific_date.date()]
                if not daily_transactions.empty:
                    transactions_summary = "\n".join([
                        f"- {row['date'].strftime('%H:%M')} {row['description']} ({row['amount']:.2f}元)"
                        for index, row in daily_transactions.iterrows()
                    ])
                    return f"{specific_date.strftime('%Y年%m月%d日')} 的交易活动：\n{transactions_summary}"
                else:
                    return f"{specific_date.strftime('%Y年%m月%d日')} 没有发现交易活动。"
            else:
                return "请提供具体的日期以便我查询当天的活动。"


    return "抱歉，我无法理解您的问题。请尝试更具体的提问，例如：'我的总支出是多少？' 或 '上周我花钱最多的地方是哪里？'"

def predict_activity(df: pd.DataFrame, time_str: str) -> str:
    """
    Predicts common activities or spending patterns around a specific time of day.

    Args:
        df (pd.DataFrame): The processed DataFrame with transaction data.
        time_str (str): The time of day to predict for (e.g., "12", "18").

    Returns:
        str: A natural language prediction.
    """
    try:
        target_hour = int(time_str)
        if not (0 <= target_hour <= 23):
            return "请提供一个有效的24小时制时间（0-23）。"
    except ValueError:
        return "请提供一个有效的时间数字（例如：'12' 代表中午12点）。"

    # Filter transactions around the target hour (e.g., +/- 1 hour)
    df['hour'] = df['date'].dt.hour
    logger.debug(f"DataFrame date column type: {df['date'].dtype}")
    logger.debug(f"DataFrame hours: {df['hour'].tolist()}")
    logger.debug(f"Target hour: {target_hour}, Time window: {target_hour - 1}-{target_hour + 1}")
    time_window_df = df[(df['hour'] >= target_hour - 1) & (df['hour'] <= target_hour + 1)]
    logger.debug(f"Filtered time_window_df:\n{time_window_df.to_string()}")

    if time_window_df.empty:
        return f"在 {target_hour} 点前后没有发现历史交易数据，无法进行预测。"

    # Find most frequent categories and descriptions
    most_frequent_category = time_window_df['category'].mode().iloc[0] if not time_window_df['category'].empty else "未知"
    most_frequent_description = time_window_df['description'].mode().iloc[0] if not time_window_df['description'].empty else "未知"

    # Summarize spending in this period
    total_spending_in_window = time_window_df[~time_window_df['is_income']]['amount'].sum()

    prediction_messages = [
        f"根据您在 {target_hour} 点前后的历史交易数据，您通常会进行以下活动：",
        f"- 最常见的类别是：{most_frequent_category}",
        f"- 最常见的交易描述是：'{most_frequent_description}'",
    ]
    if total_spending_in_window < 0:
        prediction_messages.append(f"- 在此时间段内，您通常会支出 {abs(total_spending_in_window):.2f} 元。")
    
    if most_frequent_category == "餐饮":
        prediction_messages.append("这可能意味着您在这个时间段通常会用餐或购买饮品。")
    elif most_frequent_category == "交通":
        prediction_messages.append("这可能意味着您在这个时间段通常会通勤或出行。")

    return "\n".join(prediction_messages)