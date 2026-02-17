from fastapi import FastAPI
from app.database.connection import Base, engine
from app.explainability.shap_style import compute_feature_importance, generate_shap_plot
from fastapi.responses import FileResponse
from app.routes import generate, update
from app.database import models

Base.metadata.create_all(bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(generate.router)
app.include_router(update.router)

@app.post("/shap-explanation/")
def shap_explanation(case_data: dict):

    scores = compute_feature_importance(case_data)
    image_path = generate_shap_plot(scores)

    return FileResponse(image_path, media_type="image/png")
