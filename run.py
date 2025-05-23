from src import app, start_application
from src.core.config import settings

if __name__ == "__main__":
    start_application()
    import uvicorn

    uvicorn.run(app, host=settings.APP_HOST, port=5000)
