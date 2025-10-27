# app_gradio.py
# ------------------------------------------------------------
# Demo web app (Gradio) for the Chatbot RAG IA GEN project.
# ------------------------------------------------------------

import os
import numpy as np
import gradio as gr
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import openai

# --- Load API key from .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Text utilities ---
def split_into_chunks(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def generate_embeddings(text):
    # For openai==0.28.x
    resp = openai.Embedding.create(model="text-embedding-ada-002", input=text)
    return resp["data"][0]["embedding"]

def cosine_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) or 1e-9
    return float(np.dot(v1, v2) / denom)

def scrape_website(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return " ".join(soup.stripped_strings)
    except Exception as e:
        return f"Error scraping website: {e}"

def extract_pdf_content(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages)
    except Exception as e:
        return f"Error processing PDF: {e}"

# --- Core RAG ---
class RAGChatbot:
    def __init__(self):
        self.chunks_with_embeddings = []

    def _process_content(self, content):
        chunks = split_into_chunks(content)
        self.chunks_with_embeddings = [
            {"content": ch, "embedding": generate_embeddings(ch)} for ch in chunks if ch.strip()
        ]

    def load_from_pdf(self, pdf_path):
        content = extract_pdf_content(pdf_path)
        if content.startswith("Error"):
            raise RuntimeError(content)
        self._process_content(content)

    def load_from_url(self, url):
        content = scrape_website(url)
        if content.startswith("Error"):
            raise RuntimeError(content)
        self._process_content(content)

    def find_relevant_chunk(self, query):
        if not self.chunks_with_embeddings:
            return ""
        q_emb = generate_embeddings(query)
        scored = [
            (item["content"], cosine_similarity(q_emb, item["embedding"]))
            for item in self.chunks_with_embeddings
        ]
        best_chunk, _ = max(scored, key=lambda x: x[1])
        return best_chunk

    def ask(self, query, model="gpt-3.5-turbo", max_tokens=200):
        if not self.chunks_with_embeddings:
            return "Please load content first (PDF or URL)."
        context = self.find_relevant_chunk(query)
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers using the given context."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            return resp["choices"][0]["message"]["content"]
        except Exception as e:
            return f"OpenAI error: {e}"

# --- Gradio UI ---
class RAGChatbotInterface:
    def __init__(self):
        self.chatbot = RAGChatbot()

    def process_file(self, file_path):
        try:
            self.chatbot.load_from_pdf(file_path)
            return "✅ PDF loaded. You can now ask questions."
        except Exception as e:
            return f"❌ {e}"

    def process_url(self, url):
        try:
            self.chatbot.load_from_url(url)
            return "✅ Website content loaded. You can now ask questions."
        except Exception as e:
            return f"❌ {e}"

    def chat(self, message, history):
        reply = self.chatbot.ask(message)
        history = history + [(message, reply)]
        return "", history

    def launch(self, share=False):
        with gr.Blocks(title="RAG Chatbot") as demo:
            gr.Markdown("# 📚 RAG Chatbot — Ask your documents")
            with gr.Tab("PDF"):
                pdf = gr.File(label="Upload PDF", type="filepath", file_types=[".pdf"])
                pdf_status = gr.Textbox(label="Status", interactive=False)
                pdf.upload(self.process_file, pdf, pdf_status)

            with gr.Tab("URL"):
                url = gr.Textbox(label="Website URL", placeholder="https://example.com")
                url_status = gr.Textbox(label="Status", interactive=False)
                load_btn = gr.Button("Load URL")
                load_btn.click(self.process_url, url, url_status)

            chatbot = gr.Chatbot(height=420)
            msg = gr.Textbox(label="Your question", placeholder="Ask something about the document...")
            submit = gr.Button("Send")
            clear = gr.Button("Clear")

            submit.click(self.chat, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: (None, []), None, [msg, chatbot], queue=False)

        demo.launch(share=share)


if __name__ == "__main__":
    RAGChatbotInterface().launch(share=True)
