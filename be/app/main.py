from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(title="Paid Newsletter API")


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
