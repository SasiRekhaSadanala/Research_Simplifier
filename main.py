import os
import json
import fitz  
from fastapi import FastAPI, File, UploadFile, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from mistralai import Mistral

# Load the .env file
load_dotenv()

# Initialize the Mistral Client
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
client = None
if MISTRAL_API_KEY:
    client = Mistral(api_key=MISTRAL_API_KEY)
else:
    print("Warning: MISTRAL_API_KEY not found in .env file.")

# Create the FastAPI app
app = FastAPI(title="Research Paper Simplifier")

# Tell FastAPI to use the 'templates' folder for HTML files
templates = Jinja2Templates(directory="templates")



# Route 1: The Homepage (GET /)
@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



# Route 2: The Upload Handler (POST /upload)
@app.post("/upload")
async def upload_paper(request: Request, paper: UploadFile = File(...)): 
    temp_pdf_path = f"temp_{paper.filename}"  
    try:
        # Save the uploaded file
        with open(temp_pdf_path, 'wb') as f:
            f.write(await paper.read())
            
        # Core PDF Extraction
        doc = fitz.open(temp_pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        # Extract just the abstract
        raw_abstract = "Could not automatically find abstract."
        try:
            start_marker = "abstract"
            end_marker = "introduction"
            start_index = full_text.lower().find(start_marker)
            end_index = full_text.lower().find(end_marker, start_index)
            if start_index != -1 and end_index != -1:
                raw_abstract = full_text[start_index + len(start_marker) : end_index].strip()
            elif start_index != -1:
                raw_abstract = full_text[start_index + len(start_marker) : start_index + 3000].strip()
        except Exception:
            raw_abstract = full_text[:3000]

        # Call Mistral API for Summary
        summary = "Could not generate summary."
        if client:
            try:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant. Your task is to summarize the following academic abstract into one simple, easy-to-understand paragraph for a non-expert."},
                    {"role": "user", "content": f"Please summarize this abstract:\n\n{raw_abstract}"}
                ]
                
                chat_response = client.chat.complete(
                    model="mistral-small-latest",
                    messages=messages,
                )
                summary = chat_response.choices[0].message.content
            except Exception as e:
                summary = f"Mistral API error: {e}"
        else:
            summary = "Mistral API client not configured. Please set MISTRAL_API_KEY in .env"

        # Return the STYLED results page
        return templates.TemplateResponse("results.html", {
            "request": request,
            "filename": paper.filename,
            "summary": summary,
            "raw_abstract": raw_abstract  # We pass the abstract to the template
        })

    except Exception as e:
        return RedirectResponse(url="/", status_code=303)

    finally:
        # Clean up the temp file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        await paper.close()




# Route 3: The Quiz Generator (GET /quiz)
def generate_quiz_from_text(text: str, num_questions: int, difficulty: str):
    if not client:
        print("Error: Mistral client is not initialized.")
        return []

    prompt = f"""
    You are an expert at creating educational quizzes from academic text.
    Your task is to generate a quiz with {num_questions} unique, high-quality questions based on the provided text.

    Rules:
    - Output ONLY a valid JSON object with a single key "questions".
    - Each item must have keys: "question", "options" (an array of 4 strings), "answer" ("A", "B", "C", or "D"), and "explanation".
    - The difficulty level should be: {difficulty}.
    - Base all questions STRICTLY on the text provided below.
    
    ### Provided Text ###
    {text}
    """
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that strictly follows instructions to generate a quiz in a JSON format."},
            {"role": "user", "content": prompt}
        ]

        chat_response = client.chat.complete(
            model="mistral-small-latest",
            response_format={"type": "json_object"},
            messages=messages
        )
        
        content_str = chat_response.choices[0].message.content
        parsed_json = json.loads(content_str)
        q_list = parsed_json.get('questions', [])
        
        if not isinstance(q_list, list):
            print("Error: The 'questions' key did not contain a list.")
            return []
            
        return q_list

    except Exception as e:
        print(f"An unexpected error occurred with the Mistral API call: {e}")
        return []
    


@app.get('/quiz')
async def get_quiz_questions(
    request: Request,
    abstract: str = Query(...),
    difficulty: str = Query("medium", enum=["easy", "medium", "hard"]),
    num_questions: int = Query(3, ge=1, le=5)
):
    questions = generate_quiz_from_text(
        text=abstract, 
        num_questions=num_questions, 
        difficulty=difficulty
    )
    
    if not questions:
        error_message = "Failed to generate quiz from the model. It might be too busy or the abstract was too complex. Please try again."
        return templates.TemplateResponse("quiz.html", {
            "request": request,
            "questions": [],
            "error": error_message
        })
        
    return templates.TemplateResponse("quiz.html", {
        "request": request,
        "questions": questions,
        "error": None
    })



# Route 4: The Flashcard Generator (GET /flashcards)
def generate_flashcards_from_text(text: str, num_cards: int):
    if not client:
        print("Error: Mistral client is not initialized.")
        return []

    prompt = f"""
    You are an expert at creating educational study materials.
    Your task is to generate {num_cards} key-term flashcards based on the provided text.

    Rules:
    - Output ONLY a valid JSON object with a single key "flashcards".
    - Each item must have two keys: "term" (a key concept or name) and "definition" (a clear, concise explanation).
    - Base all flashcards STRICTLY on the text provided below.
    
    ### Provided Text ###
    {text}
    """
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that strictly follows instructions to generate flashcards in a JSON format."},
            {"role": "user", "content": prompt}
        ]

        chat_response = client.chat.complete(
            model="mistral-small-latest",
            response_format={"type": "json_object"},
            messages=messages
        )
        
        content_str = chat_response.choices[0].message.content
        parsed_json = json.loads(content_str)
        card_list = parsed_json.get('flashcards', [])
        
        if not isinstance(card_list, list):
            print("Error: The 'flashcards' key did not contain a list.")
            return []
            
        return card_list

    except Exception as e:
        print(f"An unexpected error occurred with the Mistral API call: {e}")
        return []
    


@app.get('/flashcards')
async def get_flashcards(
    request: Request,
    abstract: str = Query(...),
    num_cards: int = Query(5, ge=1, le=10) # Default to 5 cards
):
    flashcards = generate_flashcards_from_text(
        text=abstract, 
        num_cards=num_cards
    )
    
    if not flashcards:
        error_message = "Failed to generate flashcards from the model. It might be too busy or the abstract was too complex. Please try again."
        return templates.TemplateResponse("flashcards.html", {
            "request": request,
            "flashcards": [],
            "error": error_message
        })
        
    return templates.TemplateResponse("flashcards.html", {
        "request": request,
        "flashcards": flashcards,
        "error": None
    })