import yaml
from autoevals.llm import LLMClassifier


class CustomClassifier(LLMClassifier):
    prompt = ""  # Placeholder to be overridden in subclasses

    def __new__(cls):
        """
        Customize the instantiation of the LLMClassifier by loading the prompt from the subclass.
        """
        kwargs = {}
        cls_name = cls.__name__  # Derive class name for identification
        cls._SPEC_FILE_CONTENTS = cls.prompt
        spec = yaml.safe_load(cls._SPEC_FILE_CONTENTS)
        return LLMClassifier(cls_name, spec['prompt'], spec['choice_scores'], **kwargs)

class ChecklistClassifier(CustomClassifier):
    """
    Evaluate whether an LLM-generated answer meets all criteria defined in a checklist.
    
    Inherits from CustomClassifier to utilize YAML-defined prompts and scoring.
    """
    prompt = """
prompt: |-
  You are assessing a submitted answer against a checklist on a given question. Here is the data:
  [BEGIN DATA]
  ************
  [Question]: {{{input}}}
  ************
  [Checklist]: {{{expected}}}
  ************
  [Submission]: {{{output}}}
  ************
  [END DATA]

  Assess the submitted answer against the checklist. Ignore any differences in style, grammar, or punctuation.
  Determine which case applies. Answer by selecting one of the following options:
  (A) The submitted answer passes some of the checklists.
  (B) The submitted answer passes most of the checklists.
  (C) The submitted answer passes all the checklists.
  (D) The submitted answer does not pass any of the checklists.
choice_scores:
  "A": 0.4
  "B": 0.6
  "C": 1
  "D": 0
"""
