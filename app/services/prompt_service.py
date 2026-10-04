from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    id: str
    name: str
    category: str
    description: str
    template_text: str
    variables: List[str] = Field(default_factory=list)


class PromptTemplateRegistry:
    """
    Prompt Engineering & Template Registry supporting reusable system prompt patterns,
    role prompting, instruction design, and variable interpolation.
    """

    def __init__(self) -> None:
        self._templates: Dict[str, PromptTemplate] = {}
        self._register_default_templates()

    def _register_default_templates(self) -> None:
        self._templates["security_auditor"] = PromptTemplate(
            id="security_auditor",
            name="Enterprise Security Auditor",
            category="Security & Audit",
            description="Role prompt instructing the model to act as a CISSP security auditor searching for OWASP risks.",
            template_text=(
                "You are an expert Chief Information Security Officer (CISO) and CISSP certified auditor.\n"
                "Analyze the provided code or architecture for OWASP Top 10 vulnerabilities, unauthorized access risks, "
                "and hardcoded secrets.\n"
                "Provide clear severity ratings (CRITICAL, HIGH, MEDIUM, LOW) and actionable remediation code.\n"
                "Target Input: {input_text}"
            ),
            variables=["input_text"],
        )

        self._templates["compliance_analyst"] = PromptTemplate(
            id="compliance_analyst",
            name="SOC2 & HIPAA Compliance Analyst",
            category="Governance",
            description="Role prompt instructing the model to evaluate compliance against SOC2, HIPAA, and GDPR frameworks.",
            template_text=(
                "You are a Senior Regulatory & Compliance Analyst specializing in SOC2 Type II, HIPAA, and GDPR.\n"
                "Evaluate the following policy or data workflow specification for compliance gaps:\n"
                "'{input_text}'\n"
                "List specific compliance control failures, risk severity, and recommended policy adjustments."
            ),
            variables=["input_text"],
        )

        self._templates["code_refactoring_expert"] = PromptTemplate(
            id="code_refactoring_expert",
            name="Async Python & Type Safety Expert",
            category="Development",
            description="Role prompt instructing model to refactor Python code using Pydantic v2, strict typing, and async patterns.",
            template_text=(
                "You are a Principal Python Architect expert in AsyncIO, Pydantic v2, strict type hinting, and FastAPI.\n"
                "Refactor the following Python snippet for production execution:\n"
                "```python\n{input_text}\n```\n"
                "Ensure clean exception handling, docstrings, and optimal performance."
            ),
            variables=["input_text"],
        )

        self._templates["structured_json_extractor"] = PromptTemplate(
            id="structured_json_extractor",
            name="Structured Data JSON Extractor",
            category="Data Extraction",
            description="Role prompt forcing model to return strict validated JSON schema format.",
            template_text=(
                "You are an automated JSON Data Extraction engine.\n"
                "Parse the following input text and output ONLY valid JSON matching the requested schema.\n"
                "Input Data: {input_text}"
            ),
            variables=["input_text"],
        )

    def list_templates(self) -> List[PromptTemplate]:
        return list(self._templates.values())

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        return self._templates.get(template_id)

    def render_template(self, template_id: str, kwargs: Dict[str, str]) -> str:
        tmpl = self.get_template(template_id)
        if not tmpl:
            raise ValueError(f"Prompt template '{template_id}' not found in registry.")

        rendered = tmpl.template_text
        for var in tmpl.variables:
            val = kwargs.get(var, f"[{var}]")
            rendered = rendered.replace(f"{{{var}}}", val)
        return rendered


# Global Prompt Service instance
prompt_service = PromptTemplateRegistry()
