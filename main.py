from app import app
from routers.wabot import router as WabotRouter
from routers.payment import router as PaymentRouter
from routers.auth import router as AuthRouter
from routers.messaging import router as MessagingRouter
from routers.data import router as DataRouter
from routers.pdffile import router as PdffileRouter
from routers.botuser import router as UserRouter

app.include_router(WabotRouter)
app.include_router(PaymentRouter)
app.include_router(AuthRouter)
app.include_router(MessagingRouter)
app.include_router(PdffileRouter)
app.include_router(UserRouter)

app.include_router(DataRouter)

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)