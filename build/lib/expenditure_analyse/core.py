import pandas as pd
from .data_loader import load_csv, preprocess_data
from .categorizer import apply_category
from .analyzer import analyze_statements, generate_report
from .adviser import generate_advice
from .question_answering import answer_query, predict_activity
from .config import DEFAULT_COLUMN_MAPPING, DEFAULT_CATEGORY_RULES, DEFAULT_ADVICE_RULES
from .log import setup_logging # 假设log.py提供setup_logging

logger = setup_logging() # 初始化日志

_processed_df_cache = None # 用于缓存已处理的DataFrame，供问答模块使用

def analyze_bank_statement(csv_file_path: str, config: dict = None) -> str:
    """
    Analyzes a bank statement CSV file, categorizes transactions,
    generates a financial report, and provides intelligent advice.
    This function loads, preprocesses, and categorizes the data,
    then caches it internally for subsequent queries.

    Args:
        csv_file_path (str): The path to the bank statement CSV file.
        config (dict, optional): A dictionary to override default
                                 column mappings, category rules, and advice rules.
                                 Defaults to None.

    Returns:
        str: A formatted string containing the financial analysis report and advice.

    Raises:
        FileNotFoundError: If the specified CSV file does not exist.
        ValueError: If the CSV file format is unexpected or
                    required columns are missing.
        Exception: For other unexpected errors during processing.
    """
    global _processed_df_cache
    logger.info(f"Starting comprehensive analysis for: {csv_file_path}")

    # Deep copy default configurations to avoid modification
    current_config = {
        "column_mapping": DEFAULT_COLUMN_MAPPING.copy(),
        "category_rules": DEFAULT_CATEGORY_RULES.copy(),
        "advice_rules": DEFAULT_ADVICE_RULES.copy()
    }
    # Update configurations with user-provided settings
    if config:
        current_config["column_mapping"].update(config.get("column_mapping", {}))
        current_config["category_rules"].update(config.get("category_rules", {}))
        current_config["advice_rules"].update(config.get("advice_rules", {}))

    try:
        # 1. Load and Preprocess Data
        logger.debug(f"Loading CSV from {csv_file_path} with mapping: {current_config['column_mapping']}")
        df = load_csv(csv_file_path, current_config["column_mapping"])
        df = preprocess_data(df, current_config["column_mapping"])
        _processed_df_cache = df.copy() # Cache the processed DataFrame for query module
        logger.info("Data loaded and preprocessed successfully.")

        # 2. Apply Categorization
        logger.debug(f"Applying categories with rules: {current_config['category_rules']}")
        df = apply_category(df, current_config["category_rules"])
        logger.info("Transactions categorized.")

        # 3. Analyze Data
        logger.debug("Performing financial analysis.")
        analysis_result = analyze_statements(df)
        logger.info("Financial analysis completed.")

        # 4. Generate Report
        report = generate_report(analysis_result)
        logger.debug("Analysis report generated.")

        # 5. Generate Advice
        advice = generate_advice(analysis_result, current_config["advice_rules"])
        logger.debug("Intelligent advice generated.")

        full_report = report + "\n\n--- 智能建议 ---\n" + advice
        logger.info("Full analysis report with advice generated successfully.")
        return full_report
    except FileNotFoundError:
        logger.error(f"Error: The file '{csv_file_path}' was not found.", exc_info=True)
        raise FileNotFoundError(f"文件未找到: {csv_file_path}")
    except ValueError as ve:
        logger.error(f"Error processing CSV data: {ve}", exc_info=True)
        raise ValueError(f"CSV数据处理错误: {ve}. 请检查文件格式和配置。")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred during analysis: {e}", exc_info=True)
        raise RuntimeError(f"分析过程中发生未知错误: {e}")

def query_bank_statement(query: str) -> str:
    """
    Answers natural language questions or provides preliminary predictions
    based on the cached bank statement data. This function relies on
    _processed_df_cache, which must be populated by a prior call to
    analyze_bank_statement.

    Args:
        query (str): The natural language query or prediction request.
                     Examples: "我的总支出是多少?", "上周我花了多少钱?",
                               "我每天中午12点通常会做什么?"

    Returns:
        str: A natural language answer or prediction result.

    Raises:
        RuntimeError: If no bank statement data has been loaded and processed yet.
        Exception: For other unexpected errors during query processing.
    """
    if _processed_df_cache is None:
        logger.warning("No bank statement data loaded. Please run analyze_bank_statement first.")
        raise RuntimeError("抱歉，目前没有可供查询的银行流水数据。请先加载并分析您的银行流水。")

    logger.info(f"Processing query: '{query}'")
    try:
        # Simple keyword-based intent detection for prediction vs. answering
        if any(p_word in query for p_word in ["预测", "通常会", "经常会", "可能做", "习惯"]):
            import re
            # Attempt to extract time from query, e.g., "中午12点", "下午3点"
            time_match = re.search(r'(\d{1,2})[点时]', query)
            if time_match:
                time_str = time_match.group(1) # Extracts "12" from "12点"
                logger.debug(f"Detected prediction intent for time: {time_str}")
                return predict_activity(_processed_df_cache, time_str)
            else:
                logger.info("Prediction query but no specific time found.")
                return "请提供具体的时间点以便我进行更准确的预测（例如：'中午12点'）。"
        else:
            logger.debug(f"Detected general question intent for query: {query}")
            return answer_query(_processed_df_cache, query)
    except Exception as e:
        logger.error(f"An error occurred during query processing: {e}", exc_info=True)
        return f"抱歉，处理您的查询时发生错误：{e}"