from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from stl import mesh
import numpy as np
import tempfile
import os

app = FastAPI()

# CORS-ondersteuning zodat je HTML tool op makernaut.be verbinding kan maken
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in productie strakker instellen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResult(BaseModel):
    volume_cm3: float
    dimensions_mm: list[float]

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".stl"):
        return JSONResponse(content={"error": "Enkel STL ondersteund in deze testfase."}, status_code=400)

    try:
        contents = await file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        part_mesh = mesh.Mesh.from_file(temp_path)

        # Volumeberekening
        volume_mm3, _, _ = part_mesh.get_mass_properties()
        volume_cm3 = float(volume_mm3) / 1000.0

        # Dimensies berekenen
        mins = np.min(part_mesh.vectors, axis=(0, 1))
        maxs = np.max(part_mesh.vectors, axis=(0, 1))
        size_mm = maxs - mins

        os.remove(temp_path)

        return AnalysisResult(volume_cm3=volume_cm3, dimensions_mm=[float(x) for x in size_mm])

    except Exception as e:
        return JSONResponse(content={"error": f"Verwerking mislukt: {str(e)}"}, status_code=500)
