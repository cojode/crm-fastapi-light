import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.web.application:get_app",
        host="0.0.0.0",
        factory=True,
        port=8000,
        reload=True,
        reload_dirs=["."],
        reload_includes=["*.py"],
    )
