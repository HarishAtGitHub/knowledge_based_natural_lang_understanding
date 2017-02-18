from knowledge_based_analyzer import KnowledgeBasedAnalyzer
from test_input import *

analyzer = KnowledgeBasedAnalyzer()

for text in what:
    print(analyzer.analyze(text))
