import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(
        description="Run the FastAPI Video2MP3 application."
    )
    parser.add_argument(
        "-s", "--start", action="store_true", help="Start the FastAPI application"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8000, help="Specify the port (default: 8000)"
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=1,
        help="Specify the number of workers (default: 1)",
    )

    args = parser.parse_args()

    if args.start:
        # reference to the load_app function used by uvicorn to run the server
        from api.defaults.load_app import load_app

        # Uvicorn requires the app to be passed as an import string to enable reload and workers
        uvicorn.run(
            "api.defaults.load_app:load_app",  # module and function that returns the app
            host="0.0.0.0",
            port=args.port,
            workers=args.workers if args.workers > 0 else 1,
            reload=True,
            reload_dirs=["./api"],  # Only watch the api directory
            lifespan="off",  # Disable lifespan
            factory=True,
        )


if __name__ == "__main__":
    main()
