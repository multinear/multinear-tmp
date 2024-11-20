from .checklist import ChecklistClassifier

                # result = loop.run_until_complete(run_test(company_name, test_case))
                
                # input_case = result['input']
                # answer = result['answer']
                # passed = result['passed']
                # score = result['score']
                # metadata = result['metadata']



def evaluate(spec: dict, input: any, output: any):
    """Evaluate an output against a specification"""

    min_score = spec.get('min_score', 1.0)

    evaluator = None
    if 'checklist' in spec:
        evaluator = ChecklistClassifier()
        result = evaluator(output, spec['checklist'], input=input)
    else:
        raise ValueError("No evaluator specified")

    return {
        'score': result.score,
        'passed': result.score >= min_score,
        'details': result.metadata
    }
