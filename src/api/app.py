import os
import sys
sys.path.insert(0, os.path.abspath("."))

import tempfile
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

from src.config import Config
from src.inference.predict import CancerPredictor
from src.explainability.grad_cam import GradCAM
from src.explainability.visualization import visualize_predictions

app = FastAPI(
    title="Explainable Hybrid AI Cancer Diagnosis",
    version="1.0.0",
    description="Conference Paper Prototype for Cancer Diagnosis"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.routes import router as api_v1_router
app.include_router(api_v1_router)


# Load configuration
config = Config()
device = config.device

# Initialize predictor
model_path = 'models/trained/best_model.pth'
if not os.path.exists(model_path):
    model_path = 'models/trained/final_model.pth'

predictor = CancerPredictor(model_path, config, device)

# Initialize Grad-CAM
grad_cam = GradCAM(predictor.model, config.xai.grad_cam_layer, device)

@app.get("/api/v1/info")
async def api_info():
    """API info endpoint"""
    return {
        "message": "Explainable Hybrid AI Cancer Diagnosis API",
        "status": "running",
        "version": "1.0.0",
        "device": str(device),
        "model": config.model.model_name,
        "classes": predictor.class_names,
        "endpoints": [
            "/",
            "/health",
            "/predict",
            "/predict/explain",
            "/predict/batch"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": os.path.exists(model_path),
        "device": device,
        "num_classes": config.model.num_classes
    }

@app.post("/predict")
async def predict(image: UploadFile = File(...)) -> Dict[str, Any]:
    """Predict cancer type and recommend treatment"""
    
    # Validate file
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        content = await image.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Make prediction
        result = predictor.predict(tmp_path)
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "prediction": result
        }
    
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(500, f"Prediction failed: {str(e)}")

@app.post("/predict/explain")
async def predict_with_explanation(image: UploadFile = File(...)):
    """Predict with Grad-CAM explanation"""
    
    # Validate and save file
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        content = await image.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Get prediction
        result = predictor.predict(tmp_path)
        
        # Generate Grad-CAM
        from torchvision import transforms
        from PIL import Image
        
        img = Image.open(tmp_path).convert('RGB')
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        cam, class_idx = grad_cam.generate(img_tensor, result['predicted_class'])
        
        # Save heatmap
        output_path = 'outputs/visualizations/grad_cam_temp.png'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        grad_cam.save_heatmap(tmp_path, cam, output_path)
        
        # Read heatmap as base64
        import base64
        with open(output_path, 'rb') as f:
            heatmap_base64 = base64.b64encode(f.read()).decode()
        
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
        
        return {
            "status": "success",
            "prediction": result,
            "explanation": {
                "grad_cam": heatmap_base64,
                "class_idx": class_idx
            }
        }
    
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(500, f"Prediction failed: {str(e)}")

@app.post("/predict/visualize")
async def predict_with_visualization(image: UploadFile = File(...)):
    """Predict and generate complete visualization"""
    
    # Validate and save file
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        content = await image.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Get prediction
        result = predictor.predict(tmp_path)
        
        # Generate Grad-CAM
        from torchvision import transforms
        from PIL import Image
        
        img = Image.open(tmp_path).convert('RGB')
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        cam, class_idx = grad_cam.generate(img_tensor, result['predicted_class'])
        overlay = grad_cam.overlay_heatmap(tmp_path, cam)
        
        # Save visualization
        output_path = 'outputs/visualizations/result.png'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fig = visualize_predictions(tmp_path, result, overlay, save_path=output_path)
        
        # Read visualization as base64
        import base64
        with open(output_path, 'rb') as f:
            viz_base64 = base64.b64encode(f.read()).decode()
        
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        return {
            "status": "success",
            "prediction": result,
            "visualization": viz_base64
        }
    
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(500, f"Prediction failed: {str(e)}")

frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

