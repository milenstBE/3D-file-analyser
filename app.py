from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from stl import mesh
import tempfile
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        ext = file.filename.split('.')[-1].lower()
        if ext != "stl":
            raise ValueError("Bestand is geen STL")

        suffix = "." + ext
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Validatie: probeer STL te openen
        try:
            stl_mesh = mesh.Mesh.from_file(tmp_path)
        except Exception:
            raise ValueError("Geen geldig binair STL-bestand")

        volume = np.sum(stl_mesh.get_volumes())
        size = stl_mesh.max_ - stl_mesh.min_

        return {
            "volume_cm3": float(volume / 1000),
            "dimensions_mm": [float(x) for x in size]
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Kon bestand niet verwerken. Upload een geldig binair STL-bestand."}
        )
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
