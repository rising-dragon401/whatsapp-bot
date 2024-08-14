from fastapi import FastAPI
from routers import wabot, payment

app = FastAPI()

app.include_router(wabot.router)
app.include_router(payment.router)

# Root route
@app.get("/")
async def root():
    return {"message": "Hello World!"}
    
if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)