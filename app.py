from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from stl import mesh
import tempfile
import numpy as np

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
        suffix = "." + file.filename.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        stl_mesh = mesh.Mesh.from_file(tmp_path)
        volume = np.sum(stl_mesh.get_volumes())
        min_bounds = stl_mesh.min_
        max_bounds = stl_mesh.max_
        size = (max_bounds - min_bounds)

        return {
            "volume_cm3": float(volume / 1000),
            "dimensions_mm": [float(dim) for dim in size]
        }
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Kon bestand niet verwerken. Upload een geldig STL- of STEP-bestand."}
        )
