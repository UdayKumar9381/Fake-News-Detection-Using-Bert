"""
FastAPI Backend for Fake News Detection System
Main application entry point
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from api.prediction import get_predictor
from api.verification import get_verifier
from utils.file_extractor import extract_text_from_file
from utils.config import config

# ========================================
# Initialize FastAPI App
# ========================================
app = FastAPI(
    title="Fake News Detection API",
    description="BERT-based fake news detection with document and media verification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========================================
# CORS Middleware
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# Request/Response Models
# ========================================
class TextInput(BaseModel):
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Breaking news: Scientists discover new treatment for diseases."
            }
        }


class PredictionResponse(BaseModel):
    prediction: str
    label: int
    confidence: float
    confidence_level: str
    accuracy: float
    f1_score: float
    processing_time: float
    probabilities: dict
    parameters: dict


class FileUploadResponse(BaseModel):
    prediction: str
    confidence: float
    accuracy: float
    f1_score: float
    filename: str
    file_info: dict
    extracted_text_preview: str
    parameters: dict


class VerificationResponse(BaseModel):
    prediction: str
    confidence: float
    source_verification: dict
    credibility_score: float
    official_approval: bool
    verification_summary: str


# ========================================
# Startup Event
# ========================================
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    print("\n" + "="*50)
    print("🚀 Starting Fake News Detection API")
    print("="*50)
    
    try:
        # Initialize predictor (loads BERT model)
        predictor = get_predictor()
        model_info = predictor.get_model_info()
        
        print(f"✅ Model loaded: {model_info['model_type']}")
        print(f"✅ Device: {model_info['device']}")
        print(f"✅ Vocabulary size: {model_info['vocab_size']}")
        
        # Initialize verifier
        verifier = get_verifier()
        print(f"✅ Source verifier initialized")
        
        print("="*50)
        print(f"📍 Server running on: http://{config.HOST}:{config.PORT}")
        print(f"📚 API Documentation: http://{config.HOST}:{config.PORT}/docs")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        print("\n⚠️  Make sure you have:")
        print("   1. Trained the BERT model")
        print("   2. Placed it in the correct directory")
        print("   3. Updated MODEL_PATH in .env file")
        raise


# ========================================
# API ENDPOINTS
# ========================================

@app.get("/")
def root():
    """
    Health check endpoint
    
    Returns basic API information
    """
    predictor = get_predictor()
    model_info = predictor.get_model_info()
    
    return {
        "status": "online",
        "message": "Fake News Detection API",
        "version": "1.0.0",
        "model": model_info['model_type'],
        "device": model_info['device'],
        "endpoints": {
            "predict_text": "/predict-text",
            "upload_file": "/upload-file",
            "verify_source": "/verify-source",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """
    Detailed health check
    
    Returns system status and configuration
    """
    try:
        predictor = get_predictor()
        model_info = predictor.get_model_info()
        config_summary = config.get_summary()
        
        return {
            "status": "healthy",
            "model": model_info,
            "config": config_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/predict-text", response_model=PredictionResponse)
async def predict_text(input_data: TextInput):
    """
    Predict if text is fake or real news
    
    **Parameters:**
    - text: News text to classify (minimum 10 characters)
    
    **Returns:**
    - prediction: "Real" or "Fake"
    - confidence: Confidence percentage (0-100)
    - confidence_level: "High", "Medium", or "Low"
    - processing_time: Time taken for prediction
    - probabilities: Individual class probabilities
    """
    try:
        if not input_data.text or len(input_data.text.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Text must be at least 10 characters long"
            )
        
        predictor = get_predictor()
        result = predictor.predict(input_data.text)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/upload-file", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and analyze PDF, DOCX, or image file
    
    **Supported formats:**
    - PDF (.pdf)
    - Word Document (.docx)
    - Images (.jpg, .jpeg, .png)
    
    **Maximum file size:** 10MB
    
    **Returns:**
    - prediction: Classification result
    - confidence: Confidence percentage
    - filename: Original filename
    - file_info: File metadata
    - extracted_text_preview: First 500 characters
    """
    try:
        # Read file
        file_bytes = await file.read()
        
        # Check file size
        if len(file_bytes) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {config.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Extract text
        try:
            extracted_text, file_info = extract_text_from_file(file_bytes, file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # If extracted text is short, try additional OCR attempts for images
        extracted_text_clean = extracted_text.strip()
        if len(extracted_text_clean) < config.MIN_TEXT_LENGTH:
            # If file is image, attempt a more aggressive OCR pass
            if file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                try:
                    # re-run OCR with preprocessing (file_extractor handles preprocessing)
                    extracted_text_clean, _ = extract_text_from_file(file_bytes, file.filename)
                except Exception:
                    # ignore and fall back to using whatever text we have
                    pass

            # If still short, allow prediction with relaxed minimum length for images
            if len(extracted_text_clean) < config.MIN_TEXT_LENGTH:
                predictor = get_predictor()
                try:
                    result = predictor.predict(extracted_text_clean, min_length=1)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Could not extract sufficient text from file: {str(e)}")
            else:
                predictor = get_predictor()
                result = predictor.predict(extracted_text_clean)
        else:
            # Predict normally
            predictor = get_predictor()
            result = predictor.predict(extracted_text_clean)
        
        return {
            "prediction": result['prediction'],
            "confidence": result['confidence'],
            "accuracy": result['accuracy'],
            "f1_score": result['f1_score'],
            "filename": file.filename,
            "file_info": file_info,
            "extracted_text_preview": extracted_text[:500],
            "parameters": result['parameters']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.post("/verify-source", response_model=VerificationResponse)
async def verify_source(input_data: TextInput):
    """
    Predict and verify content against official sources
    
    Performs comprehensive verification including:
    - BERT-based fake news detection
    - Google News verification
    - Official source checking
    - Overall credibility scoring
    
    **Parameters:**
    - text: News text to verify
    
    **Returns:**
    - prediction: "Real" or "Fake"
    - confidence: Model confidence (0-100)
    - source_verification: Detailed verification results
    - credibility_score: Overall credibility (0-100)
    - official_approval: Boolean indicating official source approval
    - verification_summary: Human-readable summary
    """
    try:
        if not input_data.text or len(input_data.text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Text must be at least 10 characters long"
            )
        
        # Get prediction
        predictor = get_predictor()
        prediction = predictor.predict(input_data.text)
        
        # Verify sources
        verifier = get_verifier()
        result = verifier.comprehensive_verification(input_data.text, prediction)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )


@app.get("/model-info")
def get_model_info():
    """
    Get detailed model information
    
    Returns information about the loaded BERT model
    """
    try:
        predictor = get_predictor()
        return predictor.get_model_info()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve model info: {str(e)}"
        )


# ========================================
# Error Handlers
# ========================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors by returning a JSONResponse."""
    content = {
        "error": "Endpoint not found",
        "message": f"The endpoint {request.url.path} does not exist",
        "available_endpoints": [
            "/",
            "/health",
            "/predict-text",
            "/upload-file",
            "/verify-source",
            "/model-info",
            "/docs"
        ]
    }
    return JSONResponse(status_code=404, content=content)


# ========================================
# Run Server
# ========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Starting Fake News Detection API")
    print("="*50)
    print(f"📍 Server: http://{config.HOST}:{config.PORT}")
    print(f"📚 Documentation: http://{config.HOST}:{config.PORT}/docs")
    print(f"🔧 Device: {'CUDA' if config.MODEL_PATH else 'CPU'}")
    print("="*50 + "\n")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level="info"
    )