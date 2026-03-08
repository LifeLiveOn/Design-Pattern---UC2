from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from context import Context
from handler import pipeline
from config import AIConfig, PromptTemplates

class RuleUpdater(ABC):

    def update(self, source):

        rules = self.load_rules(source)

        rules = self.process_rules(rules)

        return rules

    @abstractmethod
    def load_rules(self, source):
        raise NotImplementedError

    def process_rules(self, rules):
        return rules
    

class ManualRuleUpdater(RuleUpdater):
    """
    manually load rules from a list of rule strings
    """

    def load_rules(self, rules: str | Iterable[str]):
        if isinstance(rules, str):
            return pipeline.handle(rules)
        return pipeline.handle(list(rules))

class AIRuleUpdater(RuleUpdater):
    """
    Load rules from an AI-generated document using Langchain.
    Extracts business rules from unstructured text (discounts, shipping, etc.)
    and formats them for the handler pipeline.
    """

    def __init__(self, ai_client=None, use_langchain=None, api_key=None, model=None):
        self.ai_client = ai_client  # Generic AI service interface
        # Use config defaults if not specified
        self.use_langchain = use_langchain if use_langchain is not None else AIConfig.USE_LANGCHAIN
        self.api_key = api_key or AIConfig.OPENAI_API_KEY
        self.model = model or AIConfig.MODEL_NAME

    def load_rules(self, document: str):
        # Try Langchain integration first
        if self.use_langchain:
            try:
                structured_rules = self._extract_with_langchain(document)
                return pipeline.handle(structured_rules)
            except Exception as e:
                print(f"Langchain extraction failed: {e}. Trying fallback...")
        
        # Try generic AI client
        if self.ai_client:
            prompt = self._build_extraction_prompt(document)
            structured_rules = self.ai_client.generate(prompt)
            return pipeline.handle(structured_rules)
        
        # Fallback: assume document is already formatted
        return pipeline.handle(document)

    def _build_extraction_prompt(self, document: str) -> str:
        """Build comprehensive prompt for rule extraction using config template."""
        return PromptTemplates.EXTRACTION_PROMPT_TEMPLATE.format(document=document)

    def _extract_with_langchain(self, document: str) -> str:
        """Use Langchain with OpenAI to extract business rules."""
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
        except ImportError:
            raise ImportError(
                "Langchain not installed. Run: pip install langchain langchain-openai"
            )

        if not self.api_key:
            raise ValueError("OpenAI API key required for Langchain integration")

        llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=AIConfig.TEMPERATURE,
            max_tokens=AIConfig.MAX_TOKENS
        )

        system_msg = SystemMessage(content=PromptTemplates.SYSTEM_PROMPT)

        human_msg = HumanMessage(content=f"Extract rules from:\n\n{document}")

        response = llm.invoke([system_msg, human_msg])
        return response.content


class BusinessRuleController:

    def __init__(self, ruleset):
        self.ruleset = ruleset

    def update_rules_manual(self, rules: str | Iterable[str]):

        updater = ManualRuleUpdater()

        parsed_rules = updater.update(rules)

        for rule in parsed_rules:
            self.ruleset.add_rule(rule)

    def update_rules_ai(self, document: str):

        updater = AIRuleUpdater()

        parsed_rules = updater.update(document)

        for rule in parsed_rules:
            self.ruleset.add_rule(rule)

    def process_request(self, request_data):

        context = Context(request_data)

        return self.ruleset.evaluate(context)

    def list_rules(self):
        sorted_rules = sorted(self.ruleset.rules, key=lambda r: r.priority, reverse=True)
        return [f"{rule.rule_id}: {rule}" for rule in sorted_rules]