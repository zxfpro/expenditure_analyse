def generate_advice(analysis_result: dict, advice_rules: dict) -> str:
    """
    Generates financial advice based on analysis results and predefined rules.

    Args:
        analysis_result (dict): The analysis results from analyzer.py.
        advice_rules (dict): Rules for generating advice, e.g., spending thresholds.

    Returns:
        str: A string containing the generated financial advice.
    """
    advice_messages = []

    total_income = analysis_result.get('total_income', 0)
    total_expense = analysis_result.get('total_expense', 0)
    net_balance = analysis_result.get('net_balance', 0)
    category_expenses = analysis_result.get('category_expenses', {})
    category_expense_percentages = analysis_result.get('category_expense_percentages', {})

    # Advice based on high dining threshold
    dining_percentage = category_expense_percentages.get('餐饮', 0)
    high_dining_threshold = advice_rules.get('high_dining_threshold', 0.20) * 100 # Convert to percentage
    if dining_percentage > high_dining_threshold:
        advice_messages.append(
            f"您的餐饮支出占总支出的 {dining_percentage:.2f}%，高于建议的 {high_dining_threshold:.0f}%。考虑适当控制餐饮消费，例如尝试在家做饭或减少外卖频率。"
        )

    # Advice based on low saving threshold
    if total_income > 0:
        saving_ratio = net_balance / total_income
        low_saving_threshold = advice_rules.get('low_saving_threshold', 0.10)
        if saving_ratio < low_saving_threshold:
            advice_messages.append(
                f"您的净结余占总收入的 {saving_ratio:.2%}，低于建议的 {low_saving_threshold:.0%}。建议您审视支出，制定更积极的储蓄计划。"
            )
    else:
        if net_balance < 0:
            advice_messages.append("本期没有收入，但有支出，请注意您的资金状况。")

    # General advice if no specific issues found
    if not advice_messages:
        advice_messages.append("您的财务状况良好，支出结构合理。继续保持！")
    
    return "\n".join(advice_messages)