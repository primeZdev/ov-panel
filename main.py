import uvicorn
from backend.config import config


def main():
    uvicorn.run(
        "backend.app:api",
        host=str(config.HOST),
        port=config.PORT,
        reload=True,
        ssl_keyfile=config.SSL_KEYFILE,
        ssl_certfile=config.SSL_CERTFILE,
    )


if __name__ == "__main__":
    main()
