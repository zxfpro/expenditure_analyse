import pandas as pd

def analyze_statements(df: pd.DataFrame) -> dict:
    """
    Performs financial analysis on the categorized transaction data.

    Args:
        df (pd.DataFrame): The DataFrame with 'amount', 'is_income', and 'category' columns.

    Returns:
        dict: A dictionary containing the analysis results, including:
              - total_income
              - total_expense
              - net_balance
              - category_expenses (dict of category to total expense)
              - category_expense_percentages (dict of category to percentage of total expense)
              - largest_expense
              - smallest_expense (excluding zero)
              - largest_income
    """
    analysis_result = {}

    # Calculate total income and expense
    total_income = df[df['is_income']]['amount'].sum()
    total_expense = df[~df['is_income']]['amount'].sum() # Expenses are negative, so sum them directly
    net_balance = total_income + total_expense # total_expense is already negative

    analysis_result['total_income'] = total_income
    analysis_result['total_expense'] = abs(total_expense) # Report as positive value
    analysis_result['net_balance'] = net_balance

    # Category-wise expenses
    expense_df = df[~df['is_income']].copy()
    category_expenses = expense_df.groupby('category')['amount'].sum().abs().to_dict()
    analysis_result['category_expenses'] = category_expenses

    # Category expense percentages
    category_expense_percentages = {}
    if analysis_result['total_expense'] > 0:
        for category, amount in category_expenses.items():
            percentage = (amount / analysis_result['total_expense']) * 100
            category_expense_percentages[category] = percentage
    analysis_result['category_expense_percentages'] = category_expense_percentages

    # Largest/Smallest transactions
    if not expense_df.empty:
        analysis_result['largest_expense'] = expense_df['amount'].min() # min() will give largest negative
        analysis_result['smallest_expense'] = expense_df[expense_df['amount'] != 0]['amount'].max() # max() will give smallest negative (closest to zero)
    else:
        analysis_result['largest_expense'] = 0
        analysis_result['smallest_expense'] = 0

    income_df = df[df['is_income']].copy()
    if not income_df.empty:
        analysis_result['largest_income'] = income_df['amount'].max()
    else:
        analysis_result['largest_income'] = 0

    return analysis_result

def generate_report(analysis_result: dict) -> str:
    """
    Generates a formatted text report from the analysis results.

    Args:
        analysis_result (dict): The dictionary containing analysis results from analyze_statements.

    Returns:
        str: A formatted string representing the financial report.
    """
    report_lines = [] # Initialize report_lines here
    report_lines.append("--- 银行流水分析报告 ---")
    report_lines.append(f"总收入: {analysis_result['total_income']:.2f}")
    report_lines.append(f"总支出: -{analysis_result['total_expense']:.2f}")
    report_lines.append(f"净结余: {analysis_result['net_balance']:.2f}")
    report_lines.append("\n--- 各类别支出明细 ---")

    if analysis_result['category_expenses']:
        # Sort categories by expense amount in descending order
        sorted_categories = sorted(analysis_result['category_expenses'].items(), key=lambda item: item[1], reverse=True)
        for category, amount in sorted_categories:
            percentage = analysis_result['category_expense_percentages'].get(category, 0)
            report_lines.append(f"{category}: {amount:10.2f} ({percentage:.2f}%)")
    else:
        report_lines.append("没有发现支出数据。")

    report_lines.append("\n--- 交易概览 ---")
    report_lines.append(f"最大单笔支出: -{abs(analysis_result['largest_expense']):.2f}")
    report_lines.append(f"最小单笔支出: -{abs(analysis_result['smallest_expense']):.2f}")
    report_lines.append(f"最大单笔收入: {analysis_result['largest_income']:.2f}")

    return "\n".join(report_lines)