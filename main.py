from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import email.utils



app = FastAPI(debug=True)

client = MongoClient("mongodb://localhost:27017")
print(client)
db = client["First_DB"]
notes_collection = db["notes"]


@app.get("/check-mongodb-connection")
async def check_mongodb_connection():
    try:
        # Perform a simple query or operation to test the connection
        collection = db["test"]  
        document_count = collection.count_documents({})
        return {"message": f"Connected to MongoDB. Document count: {document_count}"}
    except Exception as e:
        return {"message": f"Failed to connect to MongoDB: {str(e)}"}



first_note = { " Pasta ": ["spageti, domaten sos, kaima, maslo, luk"] }
second_note = {"List": ["1, 2, 3, 4"]}
#notes = db.notes
#notes_id = notes.insert_one(first_note).inserted_id






@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/home")
async def home():
    n: int = 30
    return {"number": n}

class User(BaseModel):
    username: str
    email: str

class Note(BaseModel):
    title: str
    content: str
    #owner: User 
    #ags: list[str]
    created_at: datetime = None 



def get_all_notes() -> List[Note]:
    # Find all note documents in the collection
    all_notes = notes_collection.find()

    # Convert each document to a Note object and store them in a list
    notes_list = [Note(**note) for note in all_notes]

    return notes_list



def get_note(note_id: str) -> dict:
    
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    print(note)
    return note


@app.get("/all_notes/", response_model=List[Note])
def read_all_notes():
    return get_all_notes()



@app.post("/notes/", response_model=Note)
def create_note(note_data: Note):
    try:
        # Assuming Note is the Pydantic model representing the note data

        note_dict = note_data.dict()

        note_data.created_at = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

        # result go ima dva puti
        result = db.notes.insert_one(note_dict).inserted_id 
    
        #note_id = result.inserted_id
       # new_note["_id"] = note_id
        return note_data
    except Exception as e:
        return {"message": f"Failed to create note: {str(e)}"}
    


@app.get("/notes/{note_id}", response_model=Note)
def read_note(note_id: str):
    print(f"vlezname v: {note_id}")
    note = get_note(note_id)
    return note

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, updated_data: Note):
    # Assuming Note is the Pydantic model representing the updated note data
    result = update_note(note_id, updated_data.dict(exclude_unset=True))
    if result:
        return get_note(note_id)
    return None

@app.delete("/notes/{note_id}", response_model=bool)
def delete_note(note_id: str):
    return delete_note(note_id)




def update_note(note_id: str, updated_data: dict) -> bool:
    # Get the existing note document from the collection
    existing_note = notes_collection.find_one({"_id": ObjectId(note_id)})

    # Check if the note exists
    if existing_note:
        # Merge the existing note data with the updated data
        updated_note_data = {**existing_note, **updated_data}

        # Update the note document with the merged data
        result = notes_collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": updated_note_data}
        )

        return result.modified_count > 0

    return False  # Return False if the note does not exist





# def update_note(note_id: str, updated_data: dict) -> bool:
#     result = notes_collection.update_one(
#         {"_id": ObjectId(note_id)},
#         {"$set": updated_data}
#     )
#     return result.modified_count > 0


def delete_note(note_id: str) -> bool:
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    return result.deleted_count > 0








