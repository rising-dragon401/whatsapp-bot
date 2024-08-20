from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import base64
from datetime import datetime

router = APIRouter()

@router.websocket("/ws/data/upload")
async def handle_upload_pdf(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            metadata = json.loads(data)

            filename = metadata.get('filename')
            file_data = metadata.get('data')

            if filename and file_data:
                file_data = base64.b64decode(file_data)
                path_name = "./embedding/" + str(datetime.utcnow()) + ".pdf"
                with open(path_name, "wb") as f:
                    f.write(file_data)
                await websocket.send_json({
                    "status": "success",
                    "filename": filename,
                    "size": len(file_data),
                    "pathname": path_name,
                    "created_at": str(datetime.utcnow()),
                })
            else:
                await websocket.send_text("Invalid data received.")
    except WebSocketDisconnect:
        print("WebSocket disconnected")