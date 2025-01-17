import pathlib
import time
from db import get_db
from fastapi import FastAPI, Depends, HTTPException, status, Path, Request, File, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from middleware import CustomHeaderMiddleware
from models import Owner, Cat
from schemas import OwnerResponse, Owner_schema, CatsResponse, Cat_schema

app = FastAPI()

@app.middleware('http')
async def add_proccess_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

app.add_middleware(CustomHeaderMiddleware)  

@app.get('/')
def root():
    return {"message": "API! v.0.0.1"}

@app.get('/owners', response_model=list[OwnerResponse], tags=['owners'])
async def get_owners(db: Session = Depends(get_db)):
    owners = db.query(Owner).all()
    return owners

@app.get('/owners/{owner_id}', response_model=OwnerResponse, tags=['owners']  )
async def gey_owner_by_id(body: Owner_schema, owner_id: int = Path(ge=1), db: Session = Depends(get_db)):
    owner = db.query(Owner).filter_by(id=owner_id).first()
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    return owner 

@app.post('/owners', response_model=OwnerResponse, tags=['owners']  )
async def create_owner(body: Owner_schema, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter_by(email=body.email).first()
    if owner:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Owner is existing")
    
    owner = Owner(fullname=body.fullname, email=body.email)
    db.add(owner)
    db.commit()
    return owner 


@app.put('/owners/{owner_id}', response_model=OwnerResponse, tags=['owners']  )
async def update_owner(body: Owner_schema, owner_id: int = Path(ge=1), db: Session = Depends(get_db)):
    owner = db.query(Owner).filter_by(id=owner_id).first()
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    
    owner.email = body.email 
    owner.fullname = body.fullname
    db.commit()
    return owner 


@app.delete('/owners/{owner_id}', response_model=OwnerResponse, tags=['owners']  )
async def delete_owner(owner_id: int = Path(ge=1), db: Session = Depends(get_db)):
    owner = db.query(Owner).filter_by(id=owner_id).first()
    if owner is  None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    db.delete(owner)
    db.commit()
    return owner 

@app.get('/cats', response_model=list[CatsResponse], tags=['cats'])
async def get_cats(db: Session = Depends(get_db)):
    cats = db.query(Cat).all()
    return cats

@app.get('/cats/{cat_id}', response_model=CatsResponse, tags=['cats']  )
async def gey_cats_by_id(body: Cat_schema, owner_id: int = Path(ge=1), db: Session = Depends(get_db)):
    cat = db.query(Cat).filter_by(id=owner_id).first()
    if cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found")
    return cat 

@app.post('/cats', response_model=CatsResponse, tags=['cats']  )
async def create_cat(body: Cat_schema, db: Session = Depends(get_db)):
    cat = Cat(**body.model_dump())
    db.add(cat)
    db.commit()
    return cat 


@app.put('/cats/{cat_id}', response_model=CatsResponse, tags=['cats'])
async def update_cat(body: Cat_schema, cat_id: int = Path(ge=1), db: Session = Depends(get_db)):
    cat = db.query(Cat).filter_by(id=cat_id).first()
    if cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found")
    
    cat.nick = body.nick
    cat.age = body.age
    cat.vaccinated = body.vaccinated
    cat.owner_id = body.owner_id
    db.commit() 
    return cat 


@app.delete('/cats/{cat_id}', response_model=CatsResponse, tags=['cats'])
async def delete_cat(cat_id: int = Path(ge=1), db: Session = Depends(get_db)):
    cat = db.query(Cat).filter_by(id=cat_id).first()
    if cat is  None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    db.delete(cat)
    db.commit()
    return cat  


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    
MAX_SIZE = 1_000_000
@app.post('/upload-file/')
async def create_upload_file(file: UploadFile = File(...)):
    # Убедимся, что директория 'uploads' существует
    uploads_dir = pathlib.Path('uploads')
    uploads_dir.mkdir(exist_ok=True)

    
    file_path = uploads_dir / file.filename
    file_size = 0
    # Записываем файл
    with open(file_path, 'wb') as f:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > MAX_SIZE:
                f.close()
                pathlib.Path(file_path).unlink()
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
                                    detail= f'to big, is over of limit: {MAX_SIZE}')
            f.write(chunk)
    
    return {"file_path": str(file_path)}
