from fastapi import FastAPI
from app.api.v1.endpoints import interaction
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(interaction.router, prefix=settings.API_V1_STR, tags=["Interaction"])

@app.get("/")
async def root():
    return {"message": "AI VRO API is running. Go to /docs for API documentation."} #no hay docs todavía