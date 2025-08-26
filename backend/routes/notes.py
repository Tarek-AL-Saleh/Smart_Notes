from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from typing import List, Optional
from database import notes_collection
from models import Note, NoteCreate, NoteUpdate
from summarizer import summarize_text
from rapidfuzz import fuzz

router=APIRouter()

def normalize_note(note):
    return Note(
        id=str(note["_id"]),
        title=note["title"],
        content=note["content"],
        tags=note.get("tags", []),
        summary=note.get("summary"),
        created_at=note["created_at"],
        updated_at=note.get("updated_at")
        )

def call_ai_summary_api(note_id: str) -> str:
    note_doc = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note_doc:
        raise HTTPException(status_code=404, detail="Note not found")

    ai_summary = summarize_text(note_doc["content"])
    if ai_summary == "0":
        raise HTTPException(status_code=400, detail="Note content is empty")
    elif ai_summary == "1":
        raise HTTPException(status_code=500, detail="AI failed to generate summary")
    elif ai_summary == "2":
        raise HTTPException(status_code=502, detail="Gemini API error")

    notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {"summary": ai_summary, "updated_at": datetime.now(timezone.utc)}}
    )

    updated_doc = notes_collection.find_one({"_id": ObjectId(note_id)})
    return normalize_note(updated_doc)


#####################################################################################################
# Create a new note
#####################################################################################################

@router.post("/notes/", response_model=Note)
async def create_note(note: NoteCreate):
    note_dict = note.model_dump()
    note_dict["created_at"] = datetime.utcnow()
    note_dict["updated_at"] = None
    result = notes_collection.insert_one(note_dict)
    note_dict["id"] = str(result.inserted_id)
    return normalize_note(note_dict)


#####################################################################################################
# Get a note by ID
#####################################################################################################

@router.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return normalize_note(note)


#####################################################################################################
# Get all notes
#####################################################################################################

@router.get("/notes", response_model=List[Note])
async def get_all_notes():
    notes = notes_collection.find()
    return [normalize_note(note) for note in notes]


#####################################################################################################
# Update a note by ID
#####################################################################################################

@router.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, note_update: NoteUpdate):
    update_data = {k: v for k, v in note_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.now(timezone.utc)
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = notes_collection.find_one({"_id": ObjectId(note_id)})
    return normalize_note(updated_note)


#####################################################################################################
# Delete a note by ID
#####################################################################################################

@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}


#####################################################################################################
# Search notes by title, content, or tags
#####################################################################################################

@router.get("/notes/filter/", response_model=List[Note])
async def filter_notes(query: Optional[str] = None, tag: Optional[str] = None, threshold: int = 80):
    
    if not query:
        raise HTTPException(status_code=404, detail="No Query was provided")
    
    query_words = query.lower().split()
    notes_list=list(notes_collection.find())
    filtered_notes = []

    for note in notes_list:
        for word in query_words:
            title_score = fuzz.partial_ratio(word.lower(), note["title"].lower())
            content_score = fuzz.partial_ratio(word.lower(), note["content"].lower())
            tag_score = max( [fuzz.partial_ratio(word.lower(), tag.lower()) for tag in note.get("tags", [])] + [0])
            if max(title_score, content_score, tag_score) >= threshold:
                filtered_notes.append(note)
                break

    return [normalize_note(note) for note in filtered_notes]


#####################################################################################################
# Get recent notes
#####################################################################################################

@router.get("/notes/recent/", response_model=List[Note])
async def get_recent_notes(limit: int = 25):
    notes = notes_collection.find().sort("created_at", -1).limit(limit)
    return [normalize_note(note) for note in notes]


#####################################################################################################
# Summarize note content using AI
#####################################################################################################

@router.put("/notes/{note_id}/summarize", response_model=Note)
async def summarize_note(note_id: str):
    note_doc = normalize_note(notes_collection.find_one({"_id": ObjectId(note_id)}))
    if not note_doc:
        raise HTTPException(status_code=404, detail="Note not found")

    ai_summary = summarize_text(note_doc.content)

    if ai_summary == "0":
        raise HTTPException(status_code=400, detail="No content to summarize")
    elif ai_summary == "1":
        raise HTTPException(status_code=500, detail="Could not generate summary")
    elif ai_summary == "2":
        raise HTTPException(status_code=502, detail="AI API failed")

    notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {"summary": ai_summary}}
    )

    updated_doc = notes_collection.find_one({"_id": ObjectId(note_id)})
    return normalize_note(updated_doc)


#####################################################################################################
# Get note summary
#####################################################################################################

@router.get("/notes/{note_id}/summary", response_model=str)
async def get_note_summary(note_id: str):
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if "summary" not in note or not note["summary"]:
        raise HTTPException(status_code=404, detail="Summary not found")
    return note["summary"]


#####################################################################################################
# Delete all notes
#####################################################################################################

@router.delete("/notes/")
async def delete_all_notes():
    result = notes_collection.delete_many({})
    return {"message": f"Deleted {result.deleted_count} notes successfully"}