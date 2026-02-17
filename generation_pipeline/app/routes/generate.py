from fastapi import APIRouter
from pydantic import BaseModel
import json

from app.services.sar_service import generate_sar, retrieve_knowledge
from app.services.audit_service import save_sar_version

router = APIRouter()

class SARRequest(BaseModel):
    case_id: str
    sar_type: str
    case_data: dict


@router.post("/generate")
def generate(request: SARRequest):

    # Retrieve regulatory context
    context = retrieve_knowledge()

    # Generate SAR from LLM
    raw_output = generate_sar(
        request.case_data,
        request.sar_type,
        context
    )

    try:
        parsed = json.loads(raw_output)
    except:
        return {
            "error": "Model output not valid JSON",
            "raw_output": raw_output
        }

    # Save version
    version = save_sar_version(
        request.case_id,
        parsed["sar_narrative"],
        json.dumps(parsed["explanation"])
    )

    return {
        "case_id": request.case_id,
        "version": version,
        "sar": parsed["sar_narrative"],
        "explanation": parsed["explanation"]
    }