import pytest
from expenditure_analyse.llm_integrator import LlmIntegrator

def test_prepare_data_for_llm():
    integrator = LlmIntegrator()
    mock_report = {
        "total_income": 1000.0,
        "total_expense": 500.0,
        "net_balance": 500.0,
        "expense_by_category": {
            "餐饮": {"amount": 200.0, "percentage": 40.0},
            "购物": {"amount": 150.0, "percentage": 30.0},
            "娱乐": {"amount": 150.0, "percentage": 30.0}
        }
    }
    prepared_data = integrator.prepare_data_for_llm(mock_report)

    assert prepared_data["monthly_summary"]["total_expense"] == 500.0
    assert len(prepared_data["expense_breakdown"]) == 3
    assert prepared_data["request_type"] == "expense_analysis_and_advice"
    assert any(item['category'] == '餐饮' and item['amount'] == 200.0 for item in prepared_data['expense_breakdown'])

def test_process_llm_response_actual_data():
    integrator = LlmIntegrator()
    mock_llm_response = {
        "status": "success",
        "advice": "您的餐饮和娱乐支出占比较高，建议控制。",
        "prediction": "下月餐饮支出预计将增加5%。"
    }
    processed_insights = integrator.process_llm_response(mock_llm_response)

    assert processed_insights["llm_advice"] == "您的餐饮和娱乐支出占比较高，建议控制。"
    assert processed_insights["llm_prediction"] == "下月餐饮支出预计将增加5%。"

def test_process_llm_response_no_data_or_empty():
    integrator = LlmIntegrator()
    processed_insights_none = integrator.process_llm_response(None)
    assert "模拟建议" in processed_insights_none["llm_advice"]
    assert "模拟预测" in processed_insights_none["llm_prediction"]

    processed_insights_empty = integrator.process_llm_response({})
    assert processed_insights_empty["llm_advice"] == "No specific advice provided by LLM."
    assert processed_insights_empty["llm_prediction"] == "No specific prediction provided by LLM."