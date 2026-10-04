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
    role prompting, instruction design, and variable interpolation tailored for Data & AI Engineering.
    """

    def __init__(self) -> None:
        self._templates: Dict[str, PromptTemplate] = {}
        self._register_default_templates()

    def _register_default_templates(self) -> None:
        self._templates["sql_pipeline_architect"] = PromptTemplate(
            id="sql_pipeline_architect",
            name="SQL & Data Pipeline Architect",
            category="Data Engineering",
            description="Role prompt instructing the model to generate optimized SQL queries with CTEs, window functions, and partitioning.",
            template_text=(
                "You are a Principal Data Engineer and SQL Architect specializing in PostgreSQL, Snowflake, and BigQuery.\n"
                "Write an optimized, production-ready SQL query based on the following requirement:\n"
                "'{input_text}'\n"
                "Include window functions, CTEs where appropriate, partition filter strategies, and indexing recommendations."
            ),
            variables=["input_text"],
        )

        self._templates["data_quality_inspector"] = PromptTemplate(
            id="data_quality_inspector",
            name="Data Quality & Schema Drift Inspector",
            category="Data Governance",
            description="Role prompt instructing model to evaluate datasets for schema validation, missing fields, and null rates.",
            template_text=(
                "You are a Data Quality Engineer specializing in Great Expectations, PySpark, and Data Lake Governance.\n"
                "Analyze the following schema or data record payload:\n"
                "'{input_text}'\n"
                "Highlight schema drift issues, null value rates, data type mismatches, and data validation rules."
            ),
            variables=["input_text"],
        )

        self._templates["async_python_expert"] = PromptTemplate(
            id="async_python_expert",
            name="Async Python & Pydantic v2 Architect",
            category="Development",
            description="Role prompt instructing model to refactor Python data pipelines using Pydantic v2, strict typing, and AsyncIO.",
            template_text=(
                "You are a Principal Python Engineer expert in AsyncIO, Pydantic v2, strict type hinting, and FastAPI.\n"
                "Refactor the following code snippet into clean, production-grade Python:\n"
                "```python\n{input_text}\n```\n"
                "Ensure strict Pydantic v2 validators, clear exception handling, and optimal async execution."
            ),
            variables=["input_text"],
        )

        self._templates["executive_summarizer"] = PromptTemplate(
            id="executive_summarizer",
            name="Executive Summary & Document Analyzer",
            category="AI Analytics",
            description="Role prompt instructing model to condense complex text into key executive bullets and action items.",
            template_text=(
                "You are an AI Analytics Specialist.\n"
                "Summarize the following document or data report into key executive bullet points, core findings, and action items:\n"
                "'{input_text}'"
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
