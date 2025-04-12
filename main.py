from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import csv

app = FastAPI()

# Enable CORS (Allows cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Define data models
class User(BaseModel):
    username: str
    password: str 

class Task(BaseModel):
    task: str
    deadline: str 
    user: str

# Define file paths
users_file = r"C:\Users\DS LAB PC 14\Downloads\exam-main\data\users.csv"
tasks_file = r"C:\Users\DS LAB PC 14\Downloads\exam-main\data\tasks.csv"

# Ensure the data directory exists
os.makedirs(os.path.dirname(users_file), exist_ok=True)

# Ensure CSV files exist with headers
if not os.path.exists(users_file):
    pd.DataFrame(columns=["username", "password"]).to_csv(users_file, index=False)

if not os.path.exists(tasks_file):
    pd.DataFrame(columns=["task", "deadline", "user"]).to_csv(tasks_file, index=False)

@app.post("/create_user/")
async def create_user(user: User):
    print(f"Trying to create user: {user.username}")

    # Check if user already exists
    with open(users_file, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            if row[0] == user.username:
                print("User already exists!")
                return {"status": "User already exists"}

    # Append new user to CSV
    with open(users_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user.username, user.password])
    
    print("User created successfully!")
    return {"status": "User created"}

@app.post("/login/")
async def user_login(user: User):
    print(f"Trying to log in: {user.username} - {user.password}")
    
    with open(users_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            print(f"Checking: {row[0]} - {row[1]}")  # Log what is in the CSV
            if row[0].strip() == user.username.strip() and row[1].strip() == user.password.strip():
                print("Login successful!")
                return {"status": "Logged in"}

    print("Login failed!")
    return {"status": "Invalid username or password"}

# Create a new task
@app.post("/create_task/")
async def create_task(task: Task):
    df = pd.read_csv(tasks_file)

    # Append new task
    new_task = pd.DataFrame([[task.task, task.deadline, task.user]], columns=["task", "deadline", "user"])
    df = pd.concat([df, new_task], ignore_index=True)
    df.to_csv(tasks_file, index=False)
    
    return {"status": "Task created"}

# Retrieve all tasks (ignoring username)
@app.get("/get_tasks/")
async def get_tasks(name: str):
    df = pd.read_csv(tasks_file)

    # Handle case when the file is empty
    if df.empty:
        return {"tasks": []}

    # Convert all tasks to a list of lists
    all_tasks = df.loc[df['user']==name].values.tolist()
    
    return {"tasks": all_tasks}