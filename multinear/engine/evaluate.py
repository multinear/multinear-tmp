from .checklist import ChecklistClassifier2


def evaluate(spec: dict, input: any, output: any):
    """Evaluate an output against a specification"""

    min_score = spec.get('min_score', 1.0)

    evaluator = None
    if 'checklist' in spec:
        evaluator = ChecklistClassifier2()
        result = evaluator(output, spec['checklist'], input=input)
    else:
        raise ValueError("No evaluator specified")

    return {
        'score': result.score,
        'passed': result.score >= min_score,
        'details': result.metadata
    }
