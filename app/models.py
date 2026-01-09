from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class ResearchedField(BaseModel, Generic[T]):
    """
    Wrapper for a field that includes the value and its source citation.
    """
    value: Optional[T] = None
    source_url: Optional[str] = None
    source_quote: Optional[str] = None
    notes: Optional[str] = None

class LocationInformation(BaseModel):
    site_name: ResearchedField[str] = Field(default_factory=ResearchedField)
    site_address: ResearchedField[str] = Field(default_factory=ResearchedField)
    city: ResearchedField[str] = Field(default_factory=ResearchedField)
    state: ResearchedField[str] = Field(default_factory=ResearchedField)
    zip: ResearchedField[str] = Field(default_factory=ResearchedField)
    jurisdiction: ResearchedField[str] = Field(default_factory=ResearchedField)
    zoning: ResearchedField[str] = Field(default_factory=ResearchedField)
    pud_overlays: ResearchedField[bool] = Field(default_factory=ResearchedField)
    approved_csp: ResearchedField[bool] = Field(default_factory=ResearchedField)
    csp_required: ResearchedField[bool] = Field(default_factory=ResearchedField)
    municipal_website: ResearchedField[str] = Field(default_factory=ResearchedField)
    completed_by: Optional[str] = None
    date_completed: Optional[str] = None

    class MunicipalContact(BaseModel):
        name: ResearchedField[str] = Field(default_factory=ResearchedField)
        title: ResearchedField[str] = Field(default_factory=ResearchedField)
        phone: ResearchedField[str] = Field(default_factory=ResearchedField)
        fax: ResearchedField[str] = Field(default_factory=ResearchedField)
        email: ResearchedField[str] = Field(default_factory=ResearchedField)

    municipal_contact: MunicipalContact = Field(default_factory=MunicipalContact)

class WallSigns(BaseModel):
    wall_signs_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    square_footage_based_on: ResearchedField[str] = Field(default_factory=ResearchedField)
    maximum_sf_allowed: ResearchedField[float] = Field(default_factory=ResearchedField)
    sf_allowed_front: ResearchedField[float] = Field(default_factory=ResearchedField)
    maximum_height_from_grade: ResearchedField[float] = Field(default_factory=ResearchedField)
    can_project_above_roofline: ResearchedField[bool] = Field(default_factory=ResearchedField)
    project_above_roofline_amount: ResearchedField[str] = Field(default_factory=ResearchedField)
    illumination_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    material_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    color_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    sign_area_calculation_formula: ResearchedField[str] = Field(default_factory=ResearchedField)
    per_site: ResearchedField[str] = Field(default_factory=ResearchedField)
    max_letter_height: ResearchedField[float] = Field(default_factory=ResearchedField)
    max_logo_height: ResearchedField[float] = Field(default_factory=ResearchedField)
    max_sign_width: ResearchedField[float] = Field(default_factory=ResearchedField)

    class NumberOfSignsAllowed(BaseModel):
        secondary: ResearchedField[int] = Field(default_factory=ResearchedField)
        side: ResearchedField[int] = Field(default_factory=ResearchedField)
        rear: ResearchedField[int] = Field(default_factory=ResearchedField)

    number_of_signs_allowed_per_elevation: NumberOfSignsAllowed = Field(default_factory=NumberOfSignsAllowed)
    maximum_projection: ResearchedField[float] = Field(default_factory=ResearchedField)
    is_area_transferable_to_another_elevation: ResearchedField[bool] = Field(default_factory=ResearchedField)
    permits_required_for_repaint_signage: ResearchedField[bool] = Field(default_factory=ResearchedField)
    permits_required_for_non_illuminated_wall_signs: ResearchedField[bool] = Field(default_factory=ResearchedField)
    notes_wall_signs: ResearchedField[str] = Field(default_factory=ResearchedField)

class ProjectingSigns(BaseModel):
    projecting_signs_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    allowed_over_public_row: ResearchedField[bool] = Field(default_factory=ResearchedField)
    maximum_projection: ResearchedField[float] = Field(default_factory=ResearchedField)
    maximum_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    color_font_logo_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    height_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    minimum_clearance: ResearchedField[float] = Field(default_factory=ResearchedField)
    illumination_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    maximum_number: ResearchedField[int] = Field(default_factory=ResearchedField)
    feet_from_property_line: ResearchedField[float] = Field(default_factory=ResearchedField)
    clearance_to_grade: ResearchedField[float] = Field(default_factory=ResearchedField)
    sf_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    notes_projecting_signs: ResearchedField[str] = Field(default_factory=ResearchedField)

class FreestandingSigns(BaseModel):
    freestanding_signs_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    square_footage_formula: ResearchedField[str] = Field(default_factory=ResearchedField)
    minimum_setback_from_other_freestanding: ResearchedField[float] = Field(default_factory=ResearchedField)
    how_is_sign_area_calculated: ResearchedField[str] = Field(default_factory=ResearchedField)
    max_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    max_height: ResearchedField[float] = Field(default_factory=ResearchedField)
    setback: ResearchedField[float] = Field(default_factory=ResearchedField)
    max_number: ResearchedField[int] = Field(default_factory=ResearchedField)
    measured_from: ResearchedField[str] = Field(default_factory=ResearchedField)
    restriction_on_placement: ResearchedField[str] = Field(default_factory=ResearchedField)
    color_font_logo_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    minimum_vision_clearance: ResearchedField[str] = Field(default_factory=ResearchedField)
    windload_requirements: ResearchedField[str] = Field(default_factory=ResearchedField)
    faces_counted_toward_total_area_allowance: ResearchedField[str] = Field(default_factory=ResearchedField)
    support_structure_counted_in_area: ResearchedField[bool] = Field(default_factory=ResearchedField)
    illumination_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    sight_triangle_requirements: ResearchedField[str] = Field(default_factory=ResearchedField)
    material_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    multi_tenant_panel_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    multi_tenant_space_tenant_will_occupy: ResearchedField[str] = Field(default_factory=ResearchedField)
    notes_freestanding_signs: ResearchedField[str] = Field(default_factory=ResearchedField)

class DirectionalsRegulatory(BaseModel):
    directionals_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    permits_required: ResearchedField[bool] = Field(default_factory=ResearchedField)
    number_of_signs_allowed: ResearchedField[int] = Field(default_factory=ResearchedField)
    maximum_sf_allowed: ResearchedField[float] = Field(default_factory=ResearchedField)
    style_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    maximum_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    material_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    maximum_overall_height: ResearchedField[float] = Field(default_factory=ResearchedField)
    directionals_count_towards_allowed_sf: ResearchedField[bool] = Field(default_factory=ResearchedField)
    customer_parking_signs_restricted: ResearchedField[bool] = Field(default_factory=ResearchedField)
    corporate_colors_logos_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    placement_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    notes_directionals: ResearchedField[str] = Field(default_factory=ResearchedField)

class InformationalSigns(BaseModel):
    informational_signs_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    permits_required: ResearchedField[bool] = Field(default_factory=ResearchedField)
    number_of_signs_allowed: ResearchedField[int] = Field(default_factory=ResearchedField)
    maximum_sf_allowed: ResearchedField[float] = Field(default_factory=ResearchedField)
    style_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    maximum_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    material_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    maximum_overall_height: ResearchedField[float] = Field(default_factory=ResearchedField)
    directionals_count_towards_allowed_sf: ResearchedField[bool] = Field(default_factory=ResearchedField)
    customer_parking_signs_restricted: ResearchedField[bool] = Field(default_factory=ResearchedField)
    corporate_colors_logos_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    placement_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    color_font_logo_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    notes_informational: ResearchedField[str] = Field(default_factory=ResearchedField)

class Awnings(BaseModel):
    awnings_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    allowed_above_first_story: ResearchedField[bool] = Field(default_factory=ResearchedField)
    height_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    corporate_colors_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    clearance_from_grade_to_bottom: ResearchedField[float] = Field(default_factory=ResearchedField)
    overhang_of_row_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    max_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    notes_awnings: ResearchedField[str] = Field(default_factory=ResearchedField)

class UndercanopySigns(BaseModel):
    undercanopy_signs_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    counts_toward_wall_sign_allowance: ResearchedField[bool] = Field(default_factory=ResearchedField)
    copy_area_counted_total_allotment: ResearchedField[bool] = Field(default_factory=ResearchedField)
    how_is_copy_area_measured: ResearchedField[str] = Field(default_factory=ResearchedField)
    minimum_clearance: ResearchedField[float] = Field(default_factory=ResearchedField)
    restrictions_on_placement_lettering_logos: ResearchedField[str] = Field(default_factory=ResearchedField)
    max_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    max_number: ResearchedField[int] = Field(default_factory=ResearchedField)
    copy_logo_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    illumination_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    notes_undercanopy: ResearchedField[str] = Field(default_factory=ResearchedField)

class WindowSigns(BaseModel):
    window_signs_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    illumination_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    minimum_clearance: ResearchedField[float] = Field(default_factory=ResearchedField)
    permits_required: ResearchedField[bool] = Field(default_factory=ResearchedField)
    max_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    area_counts_toward_total_allowance: ResearchedField[bool] = Field(default_factory=ResearchedField)
    color_logo_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    vinyl_graphics_application_considered: ResearchedField[bool] = Field(default_factory=ResearchedField)
    setback_from_glass_exempt: ResearchedField[bool] = Field(default_factory=ResearchedField)
    how_is_area_calculated: ResearchedField[str] = Field(default_factory=ResearchedField)
    how_far_away_must_they_be: ResearchedField[str] = Field(default_factory=ResearchedField)
    notes_window_signs: ResearchedField[str] = Field(default_factory=ResearchedField)

class TemporarySigns(BaseModel):
    temporary_banner_signs_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    allowable_timeframe: ResearchedField[str] = Field(default_factory=ResearchedField)
    placement_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    permit_required: ResearchedField[bool] = Field(default_factory=ResearchedField)
    material_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    copy_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    size_coverage_allowed: ResearchedField[str] = Field(default_factory=ResearchedField)
    maximum_number: ResearchedField[int] = Field(default_factory=ResearchedField)
    maximum_area: ResearchedField[float] = Field(default_factory=ResearchedField)
    color_font_logo_restrictions: ResearchedField[str] = Field(default_factory=ResearchedField)
    temporary_text_allowed_on_windows: ResearchedField[bool] = Field(default_factory=ResearchedField)

class ApprovalProcess(BaseModel):
    design_review_required: ResearchedField[bool] = Field(default_factory=ResearchedField)
    design_review_handled_administratively_or_meeting: ResearchedField[str] = Field(default_factory=ResearchedField)
    meeting_required_must_attend: ResearchedField[bool] = Field(default_factory=ResearchedField)
    will_we_present_proposal: ResearchedField[bool] = Field(default_factory=ResearchedField)

class PermitRequirements(BaseModel):
    permits_can_be_applied_via: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    persons_who_can_apply_for_permits: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    license_required_for: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    signature_required_on_application_by: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    documents_required: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    number_of_document_copies: ResearchedField[int] = Field(default_factory=ResearchedField)
    document_size: ResearchedField[str] = Field(default_factory=ResearchedField)
    time_to_secure_permit: ResearchedField[str] = Field(default_factory=ResearchedField)
    documentation_required_for_emc: ResearchedField[str] = Field(default_factory=ResearchedField)
    cost_of_permit: ResearchedField[str] = Field(default_factory=ResearchedField)
    electrical_permit_required_for_illuminated_signs: ResearchedField[bool] = Field(default_factory=ResearchedField)
    notes_permit_requirements: ResearchedField[str] = Field(default_factory=ResearchedField)

class VarianceProcedures(BaseModel):
    variances_allowed: ResearchedField[bool] = Field(default_factory=ResearchedField)
    likelihood_of_variance_being_approved: ResearchedField[str] = Field(default_factory=ResearchedField)
    variance_can_be_applied_for_by: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    signature_required_on_application: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    must_attend_variance_hearing: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    documents_required: ResearchedField[List[str]] = Field(default_factory=ResearchedField)
    quantity_required: ResearchedField[str] = Field(default_factory=ResearchedField)
    document_color: ResearchedField[str] = Field(default_factory=ResearchedField)
    time_to_secure_variance: ResearchedField[str] = Field(default_factory=ResearchedField)
    board: ResearchedField[str] = Field(default_factory=ResearchedField)
    document_size: ResearchedField[str] = Field(default_factory=ResearchedField)
    cost_of_variance: ResearchedField[str] = Field(default_factory=ResearchedField)
    deadline: ResearchedField[str] = Field(default_factory=ResearchedField)
    meeting_date: ResearchedField[str] = Field(default_factory=ResearchedField)
    percent_approved: ResearchedField[str] = Field(default_factory=ResearchedField)
    notes_variance_procedures: ResearchedField[str] = Field(default_factory=ResearchedField)

class CodeCheckForm(BaseModel):
    form_name: str = "Code Check Form"
    location_information: LocationInformation = Field(default_factory=LocationInformation)
    wall_signs: WallSigns = Field(default_factory=WallSigns)
    projecting_signs: ProjectingSigns = Field(default_factory=ProjectingSigns)
    freestanding_signs: FreestandingSigns = Field(default_factory=FreestandingSigns)
    directionals_regulatory: DirectionalsRegulatory = Field(default_factory=DirectionalsRegulatory)
    informational_signs: InformationalSigns = Field(default_factory=InformationalSigns)
    awnings: Awnings = Field(default_factory=Awnings)
    undercanopy_signs: UndercanopySigns = Field(default_factory=UndercanopySigns)
    window_signs: WindowSigns = Field(default_factory=WindowSigns)
    temporary_signs: TemporarySigns = Field(default_factory=TemporarySigns)
    approval_process: ApprovalProcess = Field(default_factory=ApprovalProcess)
    permit_requirements: PermitRequirements = Field(default_factory=PermitRequirements)
    variance_procedures: VarianceProcedures = Field(default_factory=VarianceProcedures)
