from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from stl import mesh
import tempfile
import numpy as np
import os

app = FastAPI()

# CORS-configuratie voor frontend toegang
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        filename = file.filename.lower()
        if not filename.endswith(".stl"):
            raise ValueError("Enkel STL-bestanden worden momenteel ondersteund.")

        suffix = "." + filename.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        print(f"Bestand opgeslagen op tijdelijke locatie: {tmp_path}")
        stl_mesh = mesh.Mesh.from_file(tmp_path)

        # Check of de mesh geldig is
        if stl_mesh.vectors.size == 0:
            raise ValueError("Geen geldige mesh gevonden in STL-bestand.")

        volume = np.sum(stl_mesh.get_volumes())  # in mm³
        min_bounds = stl_mesh.min_
        max_bounds = stl_mesh.max_
        size = max_bounds - min_bounds

        os.remove(tmp_path)

        return {
            "volume_cm3": float(volume / 1000),  # omzetten naar cm³
            "dimensions_mm": [float(dim) for dim in size]
        }

    except Exception as e:
        print(f"Fout bij verwerken STL-bestand: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Kon bestand niet verwerken. Upload een geldig binair STL-bestand."}
        )
