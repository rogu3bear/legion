"""API endpoints for middleware pipeline management and testing."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel

from interface import dependencies
from interface.models.user import User
from legion.middleware import run_middleware_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


class MiddlewareTestRequest(BaseModel):
    """Request model for testing middleware pipeline."""
    agent: str
    directive: str
    confidence: Optional[float] = None
    confidence_threshold: Optional[float] = 0.75


class MiddlewareTestResponse(BaseModel):
    """Response model for middleware pipeline test."""
    final_valid: bool
    reason: Optional[str] = None
    source: str
    directive: Optional[str] = None


@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Middleware Health Check"
)
def middleware_health_check() -> Dict[str, Any]:
    """
    Public health check for middleware components (no authentication required).
    
    Returns basic availability status of middleware pipeline components.
    """
    try:
        # Test imports to verify middleware components are available
        from legion.middleware.validator import validate_directive
        from legion.middleware.hallucination_guard import guard_response
        from legion.agents.therapist.validation import therapist_validate
        
        return {
            "status": "healthy",
            "components_available": True,
            "pipeline_ready": True
        }
        
    except ImportError as e:
        logger.warning(f"Middleware component import error during health check: {e}")
        return {
            "status": "degraded",
            "components_available": False,
            "pipeline_ready": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error during middleware health check: {e}")
        return {
            "status": "error",
            "components_available": False,
            "pipeline_ready": False,
            "error": str(e)
        }


@router.post(
    "/test",
    response_model=MiddlewareTestResponse,
    summary="Test Middleware Pipeline"
)
def test_middleware_pipeline(
    request: MiddlewareTestRequest,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> MiddlewareTestResponse:
    """
    Test the middleware pipeline with a given request payload.
    
    This endpoint allows testing the directive validation, hallucination guard,
    and therapist validation components of the middleware pipeline.
    
    - **agent**: The agent name to test with
    - **directive**: The directive to validate
    - **confidence**: Optional confidence score (defaults to None)
    - **confidence_threshold**: Threshold for hallucination guard (defaults to 0.75)
    
    Returns the middleware pipeline result including validation status and source.
    """
    logger.info(
        f"User '{current_user.username}' testing middleware pipeline for agent '{request.agent}'"
    )
    
    # Prepare the request payload for middleware
    middleware_payload = {
        "agent": request.agent,
        "directive": request.directive,
    }
    
    if request.confidence is not None:
        middleware_payload["confidence"] = request.confidence
    
    try:
        # Run the middleware pipeline
        result = run_middleware_pipeline(
            middleware_payload, 
            confidence_threshold=request.confidence_threshold
        )
        
        logger.info(
            f"Middleware test completed for user '{current_user.username}': {result}"
        )
        
        return MiddlewareTestResponse(
            final_valid=result.get("final_valid", False),
            reason=result.get("reason"),
            source=result.get("source", "unknown"),
            directive=result.get("directive")
        )
        
    except Exception as e:
        logger.error(
            f"Error testing middleware pipeline for user '{current_user.username}': {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Middleware pipeline test failed: {str(e)}"
        )


@router.get(
    "/status",
    response_model=Dict[str, Any],
    summary="Get Middleware Status"
)
def get_middleware_status(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Dict[str, Any]:
    """
    Get the current status and configuration of the middleware pipeline.
    
    Returns information about available middleware components and their status.
    """
    logger.info(f"User '{current_user.username}' requesting middleware status")
    
    try:
        # Import middleware components to check availability
        from legion.middleware.validator import validate_directive
        from legion.middleware.hallucination_guard import guard_response
        from legion.agents.therapist.validation import therapist_validate
        
        status_info = {
            "status": "operational",
            "components": {
                "directive_validator": {
                    "available": True,
                    "function": "validate_directive"
                },
                "hallucination_guard": {
                    "available": True,
                    "function": "guard_response"
                },
                "therapist_validator": {
                    "available": True,
                    "function": "therapist_validate"
                }
            },
            "pipeline_function": "run_middleware_pipeline",
            "default_confidence_threshold": 0.75
        }
        
        return status_info
        
    except ImportError as e:
        logger.error(f"Middleware component import error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Middleware components not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting middleware status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get middleware status: {str(e)}"
        )


@router.get(
    "/config",
    response_model=Dict[str, Any],
    summary="Get Middleware Configuration"
)
def get_middleware_config(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Dict[str, Any]:
    """
    Get the current middleware configuration settings.
    
    Returns configuration parameters used by the middleware pipeline.
    """
    logger.info(f"User '{current_user.username}' requesting middleware configuration")
    
    try:
        config = {
            "default_confidence_threshold": 0.75,
            "pipeline_steps": [
                "directive_validation",
                "hallucination_guard", 
                "therapist_validation"
            ],
            "validation_sources": [
                "validator",
                "hallucination_guard",
                "therapist",
                "all_middleware_approved"
            ],
            "required_payload_fields": [
                "agent",
                "directive"
            ],
            "optional_payload_fields": [
                "confidence"
            ]
        }
        
        return config
        
    except Exception as e:
        logger.error(f"Error getting middleware config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get middleware configuration: {str(e)}"
        ) 