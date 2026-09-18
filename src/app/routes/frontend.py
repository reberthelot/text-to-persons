"""Frontend page routes rendering HTML templates."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.app.config import settings
from src.app.utils.dataset import TEST_DATASET

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory=str(settings.template_dir))


@router.get("/", response_class=HTMLResponse)
async def get_index_page(request: Request) -> HTMLResponse:
    """Serve the demo UI dashboard.

    Renders the semantic HTML template configured with the current runtime
    environment variables and the built-in benchmark dataset.

    Parameters
    ----------
    request : Request
        Incoming HTTP request object required by Starlette/FastAPI Jinja2Templates.

    Returns
    -------
    HTMLResponse
        Rendered HTML page.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "service_base_url": settings.service_base_url,
            "service_endpoint": settings.service_endpoint,
            "service_timeout_seconds": settings.service_timeout_seconds,
            "dataset_size": len(TEST_DATASET),
            "test_dataset_texts": [item["text"] for item in TEST_DATASET],
        },
    )

