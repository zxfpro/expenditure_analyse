import pandas as pd
from .log import setup_logging

logger = setup_logging()

def apply_category(df: pd.DataFrame, category_rules: dict) -> pd.DataFrame:
    """
    Applies categories to transactions based on predefined rules.

    Args:
        df (pd.DataFrame): The DataFrame containing transaction data,
                           must have a 'description' column.
        category_rules (dict): A dictionary where keys are category names
                               and values are lists of keywords.
                               Example: {"餐饮": ["饭店", "外卖"], "交通": ["公交", "地铁"]}

    Returns:
        pd.DataFrame: The DataFrame with an added 'category' column.
                      Transactions not matching any rule are categorized as '其他'.
    """
    logger.debug(f"Applying categories with rules: {category_rules}")
    df['category'] = '其他' # Default category
    logger.debug(f"DataFrame before categorization:\n{df[['description', 'amount', 'is_income', 'category']].to_string()}")

    # Iterate through rules and apply categories
    for category, keywords in category_rules.items():
        # Special handling for '收入' category to ensure it's only applied to income transactions
        if category == '收入':
            for keyword in keywords:
                df.loc[df['description'].str.contains(keyword, case=False, na=False) & (df['is_income'] == True), 'category'] = category
        else:
            # For expense categories, apply only to expense transactions
            for keyword in keywords:
                mask = df['description'].str.contains(keyword, case=False, na=False) & (df['is_income'] == False)
                df.loc[mask & (df['category'] == '其他'), 'category'] = category
    
    logger.debug(f"DataFrame after categorization:\n{df[['description', 'amount', 'is_income', 'category']].to_string()}")
    return df