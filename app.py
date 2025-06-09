from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from stl import mesh
import numpy as np
import tempfile
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/analyze")
async def analyze(file: UploadFile):
    suffix = os.path.splitext(file.filename)[-1].lower()
    contents = await file.read()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(contents)
        temp_path = temp.name

    if suffix == ".stl":
        m = mesh.Mesh.from_file(temp_path)
        volume = m.get_mass_properties()[0]
        size = m.max_ - m.min_
    else:
        return {"error": "Ongeldig bestandstype"}

    return {
        "volume_cm3": round(volume, 2),
        "dimensions_mm": [round(s, 1) for s in size]
    }
