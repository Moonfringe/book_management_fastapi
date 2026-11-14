from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel , Field

app = FastAPI()
books = {}
next_id = 1

class BookCreate(BaseModel):
    title: str = Field(... , min_length=1 , max_length=100)
    author: str = Field(... , min_length=1 , max_length=100)
    isbn: str = Field(... , min_length=1 , max_length=100)
    price: float = Field(... , ge=0 , le=10000)
    stock: int = Field(... , ge=0 , le=500)

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    price: float
    stock: int

@app.post("/books", response_model=BookOut, status_code=201)
async def create_book(book : BookCreate):
    global next_id
    book_out_id = BookOut(id=next_id, **book.model_dump())
    books[next_id] = book_out_id
    next_id += 1
    return book_out_id

@app.get("/books", response_model=list[BookOut])
async def get_books(keyword : str | None = Query(None, min_length=1, max_length=255),
    page : int = Query(1, ge = 1, le = 1000),
    size : int = Query(10, ge = 1, le = 1000)):
    items = list(books.values())
    if keyword:
        items = [item for item in items if keyword.lower() in item.title.lower()
            or keyword.lower() in item.author.lower()]
    start = (page - 1) * size
    return items[start:start + size]

@app.get("/books/{book_id}", response_model=BookOut)
async def get_books_id(book_id : int = Path(..., ge = 1, le = 10000000)):
    found_book = books.get(book_id)
    if found_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return found_book

@app.put("/books/{book_id}", response_model=BookOut)
async def update_book(book_id : int, book : BookCreate):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    books[book_id] = BookOut(id=book_id, **book.model_dump())
    return books[book_id]


@app.delete("/books/{book_id}")
async def delete_book(book_id : int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    del books[book_id]
    return {"message": "Book deleted"}