from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import random
import os

app = FastAPI()

# ✅ Ensure CSV files are always found, using absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get script's directory
CHARACTERS_FILE = os.path.join(BASE_DIR, "characters.csv")
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.csv")


# ✅ Define Pydantic model for character input
class Character(BaseModel):
    name: str
    description: str


class Quote(BaseModel):
    text: str
    author: str


# ✅ Helper function to read CSV files
def read_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")  # Debugging
        return []
    
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data = list(reader)  # Convert to list for debugging
        print(f"Data read from {file_path}: {data}")  # Debugging
        return data


# ✅ Initialize CSV files if they don’t exist
def initialize_csv(file_path, fieldnames):
    if not os.path.exists(file_path):
        with open(file_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()


# Initialize both CSV files
initialize_csv(CHARACTERS_FILE, ["name", "description"])
initialize_csv(QUOTES_FILE, ["text", "author"])


# ✅ GET all characters
@app.get("/characters")
async def get_characters():
    characters = read_csv(CHARACTERS_FILE)
    if not characters:
        raise HTTPException(status_code=404, detail="No characters found")
    return {"characters": characters}


# ✅ GET specific character by name
@app.get("/characters/{name}")
async def get_character(name: str):
    characters = read_csv(CHARACTERS_FILE)
    for character in characters:
        if character["name"].lower() == name.lower():
            return {"character": character}
    raise HTTPException(status_code=404, detail="Character not found")


# ✅ POST - Create a new character
@app.post("/create_character")
async def create_character(character: Character):
    try:
        with open(CHARACTERS_FILE, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "description"])
            writer.writerow({"name": character.name, "description": character.description})

        return {"message": f"Character '{character.name}' added successfully"}

    except PermissionError:
        raise HTTPException(status_code=500, detail="Permission denied: Unable to write to characters.csv")


# ✅ POST - Create a new quote
@app.post("/create_quote")
async def create_quote(quote: Quote):
    try:
        with open(QUOTES_FILE, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["text", "author"])
            writer.writerow({"text": quote.text, "author": quote.author})

        return {"message": f"Quote added: '{quote.text}' by {quote.author}"}

    except PermissionError:
        raise HTTPException(status_code=500, detail="Permission denied: Unable to write to quote.csv")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# ✅ GET a random quote
@app.get("/quote")
async def get_quote():
    quotes = read_csv(QUOTES_FILE)
    if not quotes:
        raise HTTPException(status_code=404, detail="No quotes available")

    random_quote = random.choice(quotes)  # Select a random quote
    return {"quote": random_quote["text"], "author": random_quote["author"]}


# ✅ GET all quotes by a specific author
@app.get("/quote/{author}")
async def get_quote_by_author(author: str):
    quotes = read_csv(QUOTES_FILE)
    if not quotes:
        raise HTTPException(status_code=404, detail="No quotes available")

    # Find all quotes by the given author (case insensitive)
    author_quotes = [q for q in quotes if q["author"].lower() == author.lower()]

    if not author_quotes:
        raise HTTPException(status_code=404, detail=f"No quotes found for author: {author}")

    return {"author": author, "quotes": [q["text"] for q in author_quotes]}
