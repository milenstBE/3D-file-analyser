from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import trimesh

app = FastAPI()

# CORS voor frontend toegang
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        # Bestand opslaan in tijdelijke map
        suffix = "." + file.filename.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Laad het 3D model met trimesh
        mesh = trimesh.load(tmp_path, force='mesh')

        # Bereken volume en bounding box
        volume = mesh.volume  # in mm³
        bounds = mesh.bounds  # min en max [[x1, y1, z1], [x2, y2, z2]]
        size = bounds[1] - bounds[0]  # dimensies in mm

        return {
            "volume_cm3": float(volume / 1000),
            "dimensions_mm": [float(d) for d in size]
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": "Kon bestand niet verwerken. Upload een geldig STL-bestand."})
