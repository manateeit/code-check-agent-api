import json
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel
from .clients import PerplexityClient, LLMClient
from .models import (
    CodeCheckForm,
    LocationInformation,
    WallSigns,
    ProjectingSigns,
    FreestandingSigns,
    DirectionalsRegulatory,
    InformationalSigns,
    Awnings,
    UndercanopySigns,
    WindowSigns,
    TemporarySigns,
    ApprovalProcess,
    PermitRequirements,
    VarianceProcedures,
    ResearchedField
)

class CodeCheckAgent:
    def __init__(self, llm_provider: str = "openai"):
        self.perplexity = PerplexityClient()
        self.llm = LLMClient(provider=llm_provider)

    def _resolve_citations(self, content: str, citations: list) -> str:
        """
        Helper to append citation URLs to the content for the LLM to reference.
        """
        citation_text = "\n\nCitations:\n"
        for i, url in enumerate(citations, 1):
            citation_text += f"[{i}]: {url}\n"
        return content + citation_text

    def research_jurisdiction(self, address: str) -> LocationInformation:
        """
        Step 1: Identify Jurisdiction and Zoning.
        """
        query = f"What is the official municipality, zoning jurisdiction, and specific zoning designation for the address: {address}? Also provide the URL for the municipal code or zoning ordinance."
        result = self.perplexity.search(query)
        full_content = self._resolve_citations(result["content"], result["citations"])

        system_instructions = (
            "Extract the location details. identify the 'Jurisdiction' (City/County name) "
            "and 'Zoning' (specific code like 'C-1' or 'Residential'). "
            "For 'municipal_website', find the link to the code/ordinance. "
            "For every field, find the specific source URL from the provided Citations list."
        )

        return self.llm.extract_data(full_content, LocationInformation, system_instructions)

    def research_section(self, section_name: str, model: Type[BaseModel], address: str, jurisdiction_info: LocationInformation) -> BaseModel:
        """
        Generic step to research a specific section of the code.
        """
        jurisdiction = jurisdiction_info.jurisdiction.value or "the local municipality"
        zoning = jurisdiction_info.zoning.value or ""

        query = f"For the address {address} in {jurisdiction} (Zoning: {zoning}), what are the specific regulations for '{section_name}'? "

        if section_name == "Wall Signs":
            query += "Include details on allowed wall signs, square footage formulas, max height, illumination, materials, and calculation methods."
        elif section_name == "Freestanding Signs":
            query += "Include details on allowed freestanding/pylon signs, setbacks, max area, height, quantity, and multi-tenant rules."

        result = self.perplexity.search(query)
        if not result["content"]:
            return model()

        full_content = self._resolve_citations(result["content"], result["citations"])

        system_instructions = (
            f"You are researching {section_name}. Extract the specific regulations. "
            "For every field, you MUST provide the 'source_url' from the citation list that supports your answer. "
            "If a field is not explicitly mentioned in the text, leave it null/empty."
        )

        return self.llm.extract_data(full_content, model, system_instructions)

    def run(self, address: str) -> CodeCheckForm:
        """
        Main orchestration method.
        """
        # 1. Location & Jurisdiction
        location_info = self.research_jurisdiction(address)

        form = CodeCheckForm()
        form.location_information = location_info

        # 2. Research each section
        sections = [
            ("Wall Signs", WallSigns, "wall_signs"),
            ("Projecting Signs", ProjectingSigns, "projecting_signs"),
            ("Freestanding Signs", FreestandingSigns, "freestanding_signs"),
            ("Directionals / Regulatory / Parking Lot", DirectionalsRegulatory, "directionals_regulatory"),
            ("Informational Signs", InformationalSigns, "informational_signs"),
            ("Awnings", Awnings, "awnings"),
            ("Undercanopy Signs", UndercanopySigns, "undercanopy_signs"),
            ("Window Signs", WindowSigns, "window_signs"),
            ("Temporary Signs", TemporarySigns, "temporary_signs"),
            ("Approval Process", ApprovalProcess, "approval_process"),
            ("Permit Requirements", PermitRequirements, "permit_requirements"),
            ("Variance Procedures", VarianceProcedures, "variance_procedures"),
        ]

        for name, model_cls, field_name in sections:
            section_data = self.research_section(name, model_cls, address, location_info)
            setattr(form, field_name, section_data)

        return form
