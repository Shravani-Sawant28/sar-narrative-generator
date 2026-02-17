from fastapi import APIRouter
from pydantic import BaseModel
import json

from app.services.sar_service import generate_sar, retrieve_knowledge
from app.services.audit_service import (
    get_latest_sar_version,
    save_sar_version
)

router = APIRouter()

class UpdateRequest(BaseModel):
    case_id: str
    sar_type: str
    case_data: dict


@router.post("/update")
def update_sar(request: UpdateRequest):

    previous = get_latest_sar_version(request.case_id)

    if not previous:
        return {"error": "No existing SAR found for this case_id"}

    context = retrieve_knowledge()

    enriched_case_data = {
        "previous_sar": previous.sar_narrative,
        "updated_case_data": request.case_data
    }

    raw_output = generate_sar(
        enriched_case_data,
        request.sar_type,
        context
    )

    try:
        parsed = json.loads(raw_output)
    except:
        return {"error": "Model output not valid JSON", "raw_output": raw_output}

    version = save_sar_version(
        request.case_id,
        parsed["sar_narrative"],
        json.dumps(parsed["explanation"])
    )

    return {
        "case_id": request.case_id,
        "version": version,
        "updated_sar": parsed
    }
