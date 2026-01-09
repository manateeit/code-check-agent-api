import smartsheet
import logging
from typing import Optional
from .models import CodeCheckForm

def export_to_smartsheet(
    form: CodeCheckForm,
    access_token: str,
    workspace_name: str = "Code Research",
    workspace_id: Optional[int] = None
) -> dict:
    """
    Export code check form to Smartsheet.

    Args:
        form: CodeCheckForm with research data
        access_token: Smartsheet API access token (provided by caller)
        workspace_name: Name of workspace (default: "Code Research")
        workspace_id: Optional pre-defined workspace ID to skip lookup

    Returns:
        dict with sheet_url and sheet_id
    """
    smart = smartsheet.Smartsheet(access_token)
    smart.errors_as_exceptions(True)

    # 1. Find or verify workspace
    if workspace_id:
        ws_id = workspace_id
    else:
        response = smart.Workspaces.list_workspaces(include_all=True)
        ws_id = None
        for ws in response.data:
            if ws.name == workspace_name:
                ws_id = ws.id
                break

        if not ws_id:
            raise ValueError(f"Workspace '{workspace_name}' not found and no workspace_id provided")

    # 2. Get state/city for folder organization
    state_val = form.location_information.state.value or "Unspecified State"
    city_val = form.location_information.city.value or "Unspecified City"

    # 2a. Get/Create State Folder
    state_folder_id = _get_or_create_folder(smart, state_val, ws_id, 'workspace')

    # 2b. Get/Create City Folder inside State Folder
    city_folder_id = _get_or_create_folder(smart, city_val, state_folder_id, 'folder')

    # 3. Create Sheet
    full_address = form.location_information.site_address.value or "Unknown Address"
    sheet_name = full_address.split(",")[0].strip()

    if len(sheet_name) > 50:
        sheet_name = sheet_name[:47] + "..."

    sheet_spec = smartsheet.models.Sheet({
        'name': sheet_name,
        'columns': [
            {'title': 'Section', 'primary': True, 'type': 'TEXT_NUMBER'},
            {'title': 'Field', 'type': 'TEXT_NUMBER'},
            {'title': 'Value', 'type': 'TEXT_NUMBER'},
            {'title': 'Source URL', 'type': 'TEXT_NUMBER'},
            {'title': 'Notes', 'type': 'TEXT_NUMBER'}
        ]
    })

    new_sheet = smart.Folders.create_sheet_in_folder(city_folder_id, sheet_spec).result

    # 4. Prepare Rows
    rows = []

    # Header Row
    header_row = smartsheet.models.Row()
    header_row.to_bottom = True
    header_row.cells.append({'column_id': new_sheet.columns[0].id, 'value': "FULL ADDRESS"})
    header_row.cells.append({'column_id': new_sheet.columns[1].id, 'value': full_address})
    rows.append(header_row)

    sections = {
        "Location Info": form.location_information,
        "Wall Signs": form.wall_signs,
        "Projecting Signs": form.projecting_signs,
        "Freestanding Signs": form.freestanding_signs,
        "Directionals": form.directionals_regulatory,
        "Informational": form.informational_signs,
        "Awnings": form.awnings,
        "Undercanopy": form.undercanopy_signs,
        "Window Signs": form.window_signs,
        "Temporary Signs": form.temporary_signs,
        "Approval Process": form.approval_process,
        "Permit Requirements": form.permit_requirements,
        "Variance Procedures": form.variance_procedures
    }

    for section_name, model in sections.items():
        if not model:
            continue

        data_dict = model.model_dump()

        for field_key, field_val in data_dict.items():
            display_field = field_key.replace("_", " ").title()

            val_str = "N/A"
            source_url = ""
            notes = ""

            if isinstance(field_val, dict) and "value" in field_val:
                v = field_val.get("value")
                if v is True: val_str = "Yes"
                elif v is False: val_str = "No"
                elif v is not None: val_str = str(v)

                source_url = field_val.get("source_url") or ""
                notes = field_val.get("notes") or ""

            elif isinstance(field_val, dict):
                for sub_k, sub_v in field_val.items():
                    sub_display = f"{display_field} - {sub_k.replace('_', ' ').title()}"

                    sub_val_str = "N/A"
                    sub_url = ""
                    sub_notes = ""

                    if isinstance(sub_v, dict) and "value" in sub_v:
                        sv = sub_v.get("value")
                        if sv is True: sub_val_str = "Yes"
                        elif sv is False: sub_val_str = "No"
                        elif sv is not None: sub_val_str = str(sv)

                        sub_url = sub_v.get("source_url") or ""
                        sub_notes = sub_v.get("notes") or ""
                    elif isinstance(sub_v, dict):
                        sub_val_str = str(sub_v)
                    else:
                        sub_val_str = str(sub_v) if sub_v is not None else "N/A"

                    row = smartsheet.models.Row()
                    row.to_bottom = True
                    row.cells.append({'column_id': new_sheet.columns[0].id, 'value': section_name})
                    row.cells.append({'column_id': new_sheet.columns[1].id, 'value': sub_display})
                    row.cells.append({'column_id': new_sheet.columns[2].id, 'value': sub_val_str})

                    link_cell = {'column_id': new_sheet.columns[3].id, 'value': sub_url}
                    if sub_url and sub_url.startswith("http"):
                        link_cell['hyperlink'] = {'url': sub_url}
                    row.cells.append(link_cell)

                    row.cells.append({'column_id': new_sheet.columns[4].id, 'value': sub_notes})
                    rows.append(row)
                continue

            row = smartsheet.models.Row()
            row.to_bottom = True
            row.cells.append({'column_id': new_sheet.columns[0].id, 'value': section_name})
            row.cells.append({'column_id': new_sheet.columns[1].id, 'value': display_field})
            row.cells.append({'column_id': new_sheet.columns[2].id, 'value': val_str})

            link_cell = {'column_id': new_sheet.columns[3].id, 'value': source_url}
            if source_url and source_url.startswith("http"):
                link_cell['hyperlink'] = {'url': source_url}
            row.cells.append(link_cell)

            row.cells.append({'column_id': new_sheet.columns[4].id, 'value': notes})
            rows.append(row)

    # 5. Batch Add Rows
    smart.Sheets.add_rows(new_sheet.id, rows)

    return {
        "sheet_url": new_sheet.permalink,
        "sheet_id": new_sheet.id,
        "rows_created": len(rows)
    }


def _get_or_create_folder(smart, folder_name: str, parent_id: int, parent_type: str = 'workspace') -> int:
    """
    Finds a folder by name within a parent (workspace or folder).
    If not found, creates it.
    Returns the Folder ID.
    """
    found_id = None

    if parent_type == 'workspace':
        response = smart.Workspaces.list_folders(parent_id, include_all=True)
    else:
        response = smart.Folders.list_folders(parent_id, include_all=True)

    for folder in response.data:
        if folder.name.lower() == folder_name.lower():
            found_id = folder.id
            break

    if found_id:
        return found_id

    folder_spec = smartsheet.models.Folder({'name': folder_name})
    if parent_type == 'workspace':
        new_folder = smart.Workspaces.create_folder_in_workspace(parent_id, folder_spec).result
    else:
        new_folder = smart.Folders.create_folder_in_folder(parent_id, folder_spec).result

    return new_folder.id
