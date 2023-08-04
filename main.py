from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import email.utils

from fastapi.middleware.cors import CORSMiddleware

from email.utils import formatdate

import logging



app = FastAPI(debug=True)


# CORS Configuration
origins = [
    "*",
    "http://localhost:3000",
    "http://172.24.128.1:3000/",  # 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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


class User(BaseModel):
    username: str
    email: str

class Note(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    content: str
    #owner: User 
    tags: List[str] = []
    created_at: datetime = None 


# class NoteInResponse(BaseModel):
#     _id: str  # Convert _id field to string

#     class Config:
#         from_attributes = True   



def get_all_notes() -> List[Note]:
    # Find all note documents in the collection
    all_notes = notes_collection.find({})

    # Convert each document to a Note object and store them in a list
    #notes_list = [Note(**note) for note in all_notes]
    #notes_list = [Note(**note, id=str(note["_id"])) for note in all_notes]
    notes_list = []
    for note in all_notes:
        # Create a new dictionary with **note unpacking and set the 'id' field separately
        #note_data = {**note, 'id': str(note["_id"])}
        note['_id'] = str(note['_id'])
        # Create a Note instance using the updated dictionary
        note_instance = Note(**note, exclude_unset=True)
        notes_list.append(note_instance)

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
        # Get the actual data from the Pydantic model
        note_dict = note_data.dict()

        # Set the created_at field using the current datetime in RFC 2822 format
        #note_dict["created_at"] = email.utils.formatdate()
        #note_data.created_at = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        current_datetime_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
        current_datetime = datetime.strptime(current_datetime_str, "%a, %d %b %Y %H:%M:%S %Z")

        # Set the created_at field with the datetime object
        note_dict["created_at"] = current_datetime


        # Insert the note data into the database
        result = db.notes.insert_one(note_dict)


        note_id = str(result.inserted_id)
        note_data.id = note_id  # Update the Pydantic model with the inserted _id

        return note_data
    except Exception as e:
        return {"message": f"Failed to create note: {str(e)}"}



    


@app.get("/notes/{note_id}", response_model=Note)
def read_note(note_id: str):
    print(f"vlezname v: {note_id}")
    note = get_note(note_id)
    return (note)




# @app.put("/notes/{note_id}", response_model=Note)
# def update_note(note_id: str, updated_data: Note):
#     try:
#         # Get the updated note data as a dictionary
#         updated_data_dict = updated_data.dict(exclude_unset=True)

#         # Convert the id from the path parameter to an ObjectId
#         note_object_id = ObjectId(note_id)

#         # Update the note in the database
#         result = notes_collection.update_one(
#             {"_id": note_object_id},
#             {"$set": updated_data_dict}
#         )

#         # Check if the note was successfully updated
#         if result.modified_count > 0:
#             # Fetch and return the updated note
#             updated_note = get_note(note_id)
#             return updated_note

#         # If the note was not found, return a 404 response
#         raise HTTPException(status_code=404, detail="Note not found")

#     except Exception as e:
#         logger.error(f"Error updating note: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")





@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, updated_data: Note):
    logger.debug(f"Note ID to be updated: {note_id}")
    result = update_note_in_db(note_id, updated_data.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = get_note(note_id)
    return updated_note

# @app.put("/notes/{note_id}", response_model=Note)
# def update_note(note_id: str, updated_data: Note):
#     try:
#         logger.debug(f"Note ID to be updated: {note_id}")
#         # Assuming Note is the Pydantic model representing the updated note data
#         result = update_note_in_db(note_id, updated_data.dict(exclude_unset=True))
#         if result:
#             return get_note(note_id)
#         return None
#     except Exception as e:
#         logger.error(f"Error updating note: {str(e)}")
#         raise e

@app.delete("/notes/{note_id}", response_model=bool)
def delete_note(note_id: str):
    return delete_note(note_id)




def update_note_in_db(note_id: str, updated_data: dict) -> bool:
    try:
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
    except Exception as e:
        logger.error(f"Error updating note in DB: {str(e)}")
        raise e




def delete_note(note_id: str) -> bool:
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    return result.deleted_count > 0






# @app.post("/notes/", response_model=Note)
# def create_note(note_data: Note):
#     try:
        
#         # Assuming Note is the Pydantic model representing the note data


#         note_dict = note_data.dict()

#         note_data.created_at = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

#         # result go ima dva puti
#         result = db.notes.insert_one(note_dict).inserted_id 
    
#         #note_id = result.inserted_id
#        # new_note["_id"] = note_id
#         return note_data
#     except Exception as e:
#         return {"message": f"Failed to create note: {str(e)}"}

