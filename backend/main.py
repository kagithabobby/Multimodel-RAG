from fastapi import FastAPI

app = FastAPI(title="Bilingual Technical Sensei API")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
