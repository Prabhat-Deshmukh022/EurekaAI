import os
import shutil
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from read_and_process import chunk_and_embed

app = FastAPI()

UPLOAD_DIR = "temp_uploads"

@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):


    print("IN /UPLOAD")
    for file in files:
        try:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a PDF")

            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"ERROR: {str(e)}")
        
        finally:
            await file.close()
    
    try:
        # read_and_process(UPLOAD_DIR)
        chunk_and_embed(UPLOAD_DIR)
        return {"message":"success"}, 200
    
    except Exception as e:
        return {"message":f"Exception in ingesting {e}"}, 500
