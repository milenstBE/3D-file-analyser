from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from stl import mesh
import tempfile
import numpy as np
import os

app = FastAPI()

# CORS-configuratie
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_volume(m: mesh.Mesh) -> float:
    volume = 0.0
    for i in range(len(m.vectors)):
        p1, p2, p3 = m.vectors[i]
        v = np.dot(p1, np.cross(p2, p3)) / 6
        volume += v
    return abs(volume)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        filename = file.filename.lower()
        if not filename.endswith(".stl"):
            raise ValueError("Enkel STL-bestanden worden ondersteund.")

        suffix = "." + filename.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        stl_mesh = mesh.Mesh.from_file(tmp_path)

        if stl_mesh.vectors.size == 0:
            raise ValueError("Ongeldig of leeg STL-bestand.")

        volume_mm3 = calculate_volume(stl_mesh)
        size = stl_mesh.max_ - stl_mesh.min_

        os.remove(tmp_path)

        return {
            "volume_cm3": float(volume_mm3 / 1000),
            "dimensions_mm": [float(dim) for dim in size]
        }

    except Exception as e:
        print(f"Fout bij verwerken STL-bestand: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Kon bestand niet verwerken. Upload een geldig binair STL-bestand."}
        )
