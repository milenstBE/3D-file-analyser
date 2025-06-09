from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import trimesh

app = FastAPI()

# Correcte CORS-middleware zodat je frontend (bijv. makernaut.be) verbinding mag maken
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # eventueel specifieker: ["https://www.makernaut.be"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        suffix = "." + file.filename.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Laad bestand met trimesh (ondersteunt STL, STEP, etc.)
        mesh = trimesh.load(tmp_path, force='mesh')

        if mesh.is_empty:
            raise ValueError("Leeg of ongeldig mesh-bestand")

        volume = mesh.volume / 1000  # mm³ → cm³
        dimensions = mesh.extents  # mm

        return {
            "volume_cm3": float(volume),
            "dimensions_mm": [float(dim) for dim in dimensions]
        }

    except Exception as e:
        print("Fout bij verwerken bestand:", e)
        return JSONResponse(
            status_code=400,
            content={"error": "Kon bestand niet verwerken. Upload een geldig STL- of STEP-bestand."}
        )
