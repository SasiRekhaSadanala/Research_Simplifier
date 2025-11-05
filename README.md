# Research_Simplifier

A web application built with FastAPI and Mistral AI to help users understand complex research papers. Upload a PDF to get a simple summary, an interactive quiz, and flashcards of key terms.

## ✨ Features

* **AI-Powered Summary:** Uses the Mistral API to generate a simple, easy-to-read summary of any paper's abstract.
* **Interactive Quiz Generation:** Creates a robust, multi-question quiz with selectable difficulty (Easy, Medium, Hard). The app uses Mistral's JSON mode for reliable results.
* **Flashcard-Based Learning:** Generates a set of key terms and definitions as flippable flashcards. The user can select how many cards to generate.
* **Modern Frontend:** A clean, multi-page, responsive UI built with Tailwind CSS and Alpine.js.
* **PDF Parsing:** Extracts text directly from uploaded PDF documents.

## 🛠️ Tech Stack

* **Backend:** FastAPI, Uvicorn
* **AI:** Mistral AI (La Plateforme)
* **PDF Parsing:** PyMuPDF (fitz)
* **Frontend:** Tailwind CSS, Alpine.js
* **Dependencies:** `python-dotenv`, `mistralai`

## 🚀 How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/research-simplifier.git](https://github.com/your-username/research-simplifier.git)
    cd research-simplifier
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (or .\venv\Scripts\activate on Windows)
    ```

3.  **Install dependencies:**
    This will read the `requirements.txt` file and install everything.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create your .env file:**
    Create a file named `.env` in the root folder and add your Mistral API key:
    ```
    MISTRAL_API_KEY="your-mistral-api-key-goes-here"
    ```

5.  **Run the app:**
    ```bash
    uvicorn main:app --reload
    ```

6.  Open your browser and go to `http://127.0.0.1:8000`
