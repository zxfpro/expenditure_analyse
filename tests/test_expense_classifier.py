import pytest
from expenditure_analyse.classifier import ExpenseClassifier

@pytest.fixture
def classifier():
    return ExpenseClassifier()

@pytest.fixture
def classification_rules():
    return {
        "餐饮": ["午餐", "晚餐", "外卖", "咖啡", "餐"],
        "交通": ["公交", "地铁", "打车"],
        "购物": ["超市", "网购", "电子产品", "日用"],
        "娱乐": ["电影", "KTV"],
        "收入": ["工资", "兼职"] # 尽管是支出分类器，规则中也可以有收入关键词
    }

def test_classify_known_category(classifier, classification_rules):
    assert classifier.classify("午餐_外卖", classification_rules) == "餐饮"
    assert classifier.classify("打车去机场", classification_rules) == "交通"
    assert classifier.classify("京东网购了耳机", classification_rules) == "购物"
    assert classifier.classify("看电影", classification_rules) == "娱乐"
    assert classifier.classify("公司食堂午餐", classification_rules) == "餐饮"


def test_classify_case_insensitivity(classifier, classification_rules):
    assert classifier.classify("Coffee break", classification_rules) == "餐饮"
    assert classifier.classify("网购笔记本", classification_rules) == "购物"

def test_classify_unknown_category(classifier, classification_rules):
    assert classifier.classify("捐款", classification_rules) == "Uncategorized"
    assert classifier.classify("水电费", classification_rules) == "Uncategorized"
    assert classifier.classify("理财产品赎回", classification_rules) == "Uncategorized"


def test_classify_empty_description(classifier, classification_rules):
    assert classifier.classify("", classification_rules) == "Uncategorized"

def test_classify_with_no_rules(classifier):
    assert classifier.classify("随便什么", {}) == "Uncategorized"

def test_classify_with_complex_description(classifier, classification_rules):
    # 描述包含多个关键词，验证优先级或匹配逻辑
    assert classifier.classify("超市购物并吃午餐", classification_rules) == "购物" # 默认按第一个匹配到
    assert classifier.classify("买咖啡坐地铁", classification_rules) == "餐饮" # 默认按第一个匹配到