from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from stl import mesh
import numpy as np
import io
import os
import uvicorn

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # eventueel beperken tot jouw domein
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        # Load STL file into numpy-stl mesh object
        part_mesh = mesh.Mesh.from_buffer(io.BytesIO(contents))

        # Compute volume and bounding box
        volume = float(np.sum(part_mesh.areas * part_mesh.normals[:, 2]) / 3.0)
        volume_cm3 = abs(volume) / 1000  # mm³ → cm³

        min_corner = np.min(part_mesh.vectors, axis=(0, 1))
        max_corner = np.max(part_mesh.vectors, axis=(0, 1))
        dimensions_mm = [float(x) for x in (max_corner - min_corner)]

        return {
            "volume_cm3": float(volume_cm3),
            "dimensions_mm": dimensions_mm
        }

    except Exception as e:
        return { "error": "Kan bestand niet verwerken. Upload een geldig STL- of STEP-bestand." }

# Bind dynamic port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
