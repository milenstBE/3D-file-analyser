from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from stl import mesh
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        # STL verwerken met numpy-stl
        part_mesh = mesh.Mesh.from_buffer(io.BytesIO(contents))

        volume = np.sum(part_mesh.areas * part_mesh.normals[:, 2]) / 3.0
        volume_cm3 = abs(float(volume)) / 1000  # mm³ → cm³

        min_corner = np.min(part_mesh.vectors, axis=(0, 1))
        max_corner = np.max(part_mesh.vectors, axis=(0, 1))
        dimensions_mm = (max_corner - min_corner).astype(float).tolist()

        return {
            "volume_cm3": round(volume_cm3, 2),
            "dimensions_mm": [round(d, 2) for d in dimensions_mm]
        }

    except Exception as e:
        return {"error": "Kan bestand niet verwerken. Upload een geldig STL- of STEP-bestand."}
