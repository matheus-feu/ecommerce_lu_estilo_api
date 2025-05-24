from src import app
from src.core.settings import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.app.APP_HOST, port=5000)
