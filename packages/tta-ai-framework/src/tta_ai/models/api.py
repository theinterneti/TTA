"""
Model Management API Endpoints.

This module provides FastAPI endpoints for model management functionality.
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

# TODO: Implement component_registry module
# from src.orchestration.component_registry import get_component
from .interfaces import TaskType
from .model_management_component import ModelManagementComponent

logger = logging.getLogger(__name__)


# API Models
class GenerationRequest(BaseModel):
    prompt: str
    task_type: TaskType | None = TaskType.GENERAL_CHAT
    max_tokens: int | None = 2048
    temperature: float | None = 0.7
    top_p: float | None = 0.9
    stream: bool | None = False
    max_latency_ms: int | None = 5000
    min_quality_score: float | None = 6.0


class GenerationResponse(BaseModel):
    text: str
    model_id: str
    provider: str
    latency_ms: float
    usage: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class ModelTestRequest(BaseModel):
    model_id: str
    provider_name: str


class ModelTestResponse(BaseModel):
    model_id: str
    provider: str
    healthy: bool
    latency_ms: float | None = None
    test_response: str | None = None
    error: str | None = None
    status: str


class ModelRecommendationRequest(BaseModel):
    task_type: TaskType
    max_cost_per_token: float | None = None
    max_latency_ms: int | None = None
    therapeutic_safety_required: bool | None = None


class SystemStatusResponse(BaseModel):
    initialized: bool
    active_models: int
    providers: dict[str, Any]
    system_resources: dict[str, Any] | None = None
    last_health_check: str | None = None


# Router
router = APIRouter(prefix="/api/v1/models", tags=["Model Management"])


# Dependency to get model management component
async def get_model_management() -> ModelManagementComponent:
    """Get the model management component instance."""
    # TODO: Implement component_registry module and get_component function
    # This would typically be injected from the main application
    # For now, raise an error as the registry is not implemented
    # component = get_component("model_management")
    component = None  # Placeholder until component_registry is implemented
    if not component:
        raise HTTPException(status_code=503, detail="Model management component not available")

    if not component.initialized:
        raise HTTPException(status_code=503, detail="Model management component not initialized")

    return component


@router.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Generate text using the model management system."""
    try:
        response = await model_mgmt.generate_text(
            prompt=request.prompt,
            task_type=request.task_type or TaskType.GENERAL_CHAT,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stream=request.stream,
            max_latency_ms=request.max_latency_ms,
            min_quality_score=request.min_quality_score,
        )

        if not response:
            raise HTTPException(status_code=503, detail="No suitable model available")

        metadata = response.metadata or {}
        return GenerationResponse(
            text=response.text,
            model_id=response.model_id,
            provider=metadata.get("provider", "unknown"),
            latency_ms=response.latency_ms or 0,
            usage=response.usage,
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/available", response_model=list[dict[str, Any]])
async def get_available_models(
    provider: str | None = None,
    free_only: bool = False,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get available models from all or specific providers with optional free filter."""
    try:
        models = await model_mgmt.get_available_models(provider, free_only=free_only)

        # Convert ModelInfo objects to dictionaries
        return [
            {
                "model_id": model.model_id,
                "name": model.name,
                "provider": model.provider_type.value,
                "description": model.description,
                "context_length": model.context_length,
                "cost_per_token": model.cost_per_token,
                "is_free": model.is_free,
                "capabilities": model.capabilities,
                "therapeutic_safety_score": model.therapeutic_safety_score,
                "performance_score": model.performance_score,
            }
            for model in models
        ]

    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/free", response_model=list[dict[str, Any]])
async def get_free_models(
    provider: str | None = None,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get only free models from all or specific providers."""
    try:
        models = await model_mgmt.get_free_models(provider)

        # Convert ModelInfo objects to dictionaries
        return [
            {
                "model_id": model.model_id,
                "name": model.name,
                "provider": model.provider_type.value,
                "description": model.description,
                "context_length": model.context_length,
                "cost_per_token": model.cost_per_token,
                "is_free": model.is_free,
                "capabilities": model.capabilities,
                "therapeutic_safety_score": model.therapeutic_safety_score,
                "performance_score": model.performance_score,
            }
            for model in models
        ]

    except Exception as e:
        logger.error(f"Failed to get free models: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/affordable", response_model=list[dict[str, Any]])
async def get_affordable_models(
    max_cost_per_token: float = 0.001,
    provider: str | None = None,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get models within the specified cost threshold."""
    try:
        models = await model_mgmt.get_affordable_models(max_cost_per_token, provider)

        # Convert ModelInfo objects to dictionaries
        return [
            {
                "model_id": model.model_id,
                "name": model.name,
                "provider": model.provider_type.value,
                "description": model.description,
                "context_length": model.context_length,
                "cost_per_token": model.cost_per_token,
                "is_free": model.is_free,
                "capabilities": model.capabilities,
                "therapeutic_safety_score": model.therapeutic_safety_score,
                "performance_score": model.performance_score,
            }
            for model in models
        ]

    except Exception as e:
        logger.error(f"Failed to get affordable models: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/openrouter/free", response_model=list[dict[str, Any]])
async def get_openrouter_free_models(
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get free models specifically from OpenRouter provider."""
    try:
        models = await model_mgmt.get_openrouter_free_models()

        # Convert ModelInfo objects to dictionaries
        return [
            {
                "model_id": model.model_id,
                "name": model.name,
                "provider": model.provider_type.value,
                "description": model.description,
                "context_length": model.context_length,
                "cost_per_token": model.cost_per_token,
                "is_free": model.is_free,
                "capabilities": model.capabilities,
                "therapeutic_safety_score": model.therapeutic_safety_score,
                "performance_score": model.performance_score,
            }
            for model in models
        ]

    except Exception as e:
        logger.error(f"Failed to get OpenRouter free models: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/recommendations", response_model=list[str])
async def get_model_recommendations(
    task_type: TaskType,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get model recommendations for a specific task type."""
    try:
        return await model_mgmt.get_model_recommendations(task_type)

    except Exception as e:
        logger.error(f"Failed to get model recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/test", response_model=ModelTestResponse)
async def test_model_connectivity(
    request: ModelTestRequest,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Test connectivity and performance of a specific model."""
    try:
        result = await model_mgmt.test_model_connectivity(request.model_id, request.provider_name)

        return ModelTestResponse(**result)

    except Exception as e:
        logger.error(f"Model test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get comprehensive system status."""
    try:
        status = await model_mgmt.get_system_status()
        return SystemStatusResponse(**status)

    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/load/{provider_name}/{model_id}")
async def load_model(
    provider_name: str,
    model_id: str,
    background_tasks: BackgroundTasks,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Load a specific model."""
    try:
        # Load model in background to avoid timeout
        background_tasks.add_task(model_mgmt.load_model, model_id, provider_name)

        return {
            "message": f"Loading model {model_id} from provider {provider_name}",
            "model_id": model_id,
            "provider": provider_name,
            "status": "loading",
        }

    except Exception as e:
        logger.error(f"Failed to load model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/unload/{model_id}")
async def unload_model(
    model_id: str,
    provider_name: str | None = None,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Unload a specific model."""
    try:
        success = await model_mgmt.unload_model(model_id, provider_name)

        if success:
            return {
                "message": f"Successfully unloaded model {model_id}",
                "model_id": model_id,
                "status": "unloaded",
            }
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found or not loaded")

    except Exception as e:
        logger.error(f"Failed to unload model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/performance/{model_id}")
async def get_model_performance(
    model_id: str,
    timeframe_hours: int = 24,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get performance metrics for a specific model."""
    try:
        if not model_mgmt.performance_monitor:
            raise HTTPException(status_code=503, detail="Performance monitoring not available")

        return await model_mgmt.performance_monitor.get_model_performance(model_id, timeframe_hours)

    except Exception as e:
        logger.error(f"Failed to get performance metrics for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/performance")
async def get_system_performance(
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get overall system performance metrics."""
    try:
        if not model_mgmt.performance_monitor:
            raise HTTPException(status_code=503, detail="Performance monitoring not available")

        return await model_mgmt.performance_monitor.get_system_performance()

    except Exception as e:
        logger.error(f"Failed to get system performance: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/fallback/statistics")
async def get_fallback_statistics(
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get fallback handler statistics."""
    try:
        if not model_mgmt.fallback_handler:
            raise HTTPException(status_code=503, detail="Fallback handler not available")

        return model_mgmt.fallback_handler.get_failure_statistics()

    except Exception as e:
        logger.error(f"Failed to get fallback statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fallback/reset/{model_id}")
async def reset_model_failures(
    model_id: str, model_mgmt: ModelManagementComponent = Depends(get_model_management)
):
    """Reset failure count for a model."""
    try:
        if not model_mgmt.fallback_handler:
            raise HTTPException(status_code=503, detail="Fallback handler not available")

        success = model_mgmt.fallback_handler.reset_model_failures(model_id)

        if success:
            return {
                "message": f"Reset failure count for model {model_id}",
                "model_id": model_id,
                "status": "reset",
            }
        raise HTTPException(
            status_code=404, detail=f"Model {model_id} not found in failure records"
        )

    except Exception as e:
        logger.error(f"Failed to reset failures for model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# OpenRouter Filter Management Endpoints
@router.post("/openrouter/filter")
async def set_openrouter_filter(
    show_free_only: bool = False,
    prefer_free: bool = True,
    max_cost_per_token: float = 0.001,
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Set OpenRouter free models filter settings."""
    try:
        await model_mgmt.set_openrouter_filter(show_free_only, prefer_free, max_cost_per_token)

        return {
            "message": "OpenRouter filter settings updated",
            "settings": {
                "show_free_only": show_free_only,
                "prefer_free": prefer_free,
                "max_cost_per_token": max_cost_per_token,
            },
        }

    except Exception as e:
        logger.error(f"Failed to set OpenRouter filter: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/openrouter/filter")
async def get_openrouter_filter(
    model_mgmt: ModelManagementComponent = Depends(get_model_management),
):
    """Get current OpenRouter filter settings."""
    try:
        settings = model_mgmt.get_openrouter_filter_settings()

        if settings is None:
            raise HTTPException(status_code=404, detail="OpenRouter provider not available")

        return {"provider": "openrouter", "settings": settings}

    except Exception as e:
        logger.error(f"Failed to get OpenRouter filter settings: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Health check endpoint
@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "model_management"}
