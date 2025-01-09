import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist

# Load your CSV (ensure correct encoding and path)
df = pd.read_csv("filtered_csv.csv", encoding='utf-8')  # Adjust encoding if needed

# Load a multilingual sentence embedding model that supports Kazakh
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-xlm-r-multilingual-v1')

# Precompute embeddings for all questions
questions = df['question'].tolist()
question_embeddings = embedding_model.encode(questions, convert_to_numpy=True, show_progress_bar=True)

def find_most_similar_context(user_question: str, top_k=1):
    """Find the context of the question most similar to the user's input question."""
    user_embedding = embedding_model.encode([user_question], convert_to_numpy=True)
    distances = cdist(user_embedding, question_embeddings, metric='cosine')[0]
    most_similar_idx = np.argmin(distances)

    matched_question = df.iloc[most_similar_idx]["question"]
    context = df.iloc[most_similar_idx]["context"]
    return context, matched_question

def get_random_question():
    """Return a random question and context."""
    random_row = df.sample(n=1).iloc[0]
    question_id = int(random_row.name)
    question = random_row["question"]
    context = random_row["context"]
    return question_id, question, context

def get_context_by_id(question_id: int):
    """Fetch a question and context by numeric ID."""
    if question_id < 0 or question_id >= len(df):
        return None, None
    row = df.iloc[question_id]
    return row["question"], row["context"]
