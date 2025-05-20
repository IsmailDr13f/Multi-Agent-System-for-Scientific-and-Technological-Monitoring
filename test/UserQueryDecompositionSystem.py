"""
this script is just a test for the question generation system
and the question similarity system, it's not a part of the main system
and it's not used in the main system.
"""


from transformers import pipeline
import json
from sentence_transformers import SentenceTransformer, util
import torch
import time

# Vérifier si un GPU est dispo
device = 0 if torch.cuda.is_available() else -1
print(f"Using device: {device}")
# Charger le modèle de phrase pour l'encodage

def generate_multiple_questions(question: str, 
                                model_hf = "google/flan-t5-small",
                                task = "text2text-generation",
                                num_questions: int = 3,
                                token_hf:str = "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",
                                device:int = device, 
                                original_prompt = True, 
                                prompt_: str = "You are a question rewriter") -> list:
    
    # Charger le pipeline avec le  modèle flan-t5-small
    generator = pipeline(task, model=model_hf,token=token_hf,device=device)
    format
    # Préparer un prompt qui insiste sur la nécessité de générer des questions distinctes et variées.
    prompt = (f"Generate {num_questions} distinct and diverse questions from the following input. "
              f"Each question should be different in wording and perspective. Input: {question}, follow the nex format: ")
    
    start_time = time.time()
    if original_prompt == False:
        # Utiliser le prompt original pour la génération de questions
        prompt = prompt_ 
    # Générer les questions en ajustant les paramètres de sampling pour favoriser la diversité
    outputs = generator(
        prompt, 
        max_length=128, 
        num_return_sequences=num_questions, 
        do_sample=True,           # active le sampling
        temperature=1.5,          # augmente la température pour plus de diversité
        top_k=50,                 # restreint le nombre de tokens à considérer
        top_p=0.95,               # utilise le nucleus sampling pour une diversité contrôlée
        early_stopping=True
    )
    end_time = time.time()
    time_taken = end_time - start_time
    # Extraire et nettoyer les questions générées
    questions = [output["generated_text"].strip() for output in outputs]
    
    return questions, time_taken    

# Load the pre-trained Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

def calculate_similarity(main_query, subqueries):
    # Encode main query and subqueries into embeddings
    query_embedding = model.encode(main_query, convert_to_tensor=True)
    subquery_embeddings = model.encode(subqueries, convert_to_tensor=True)

    # Calculate cosine similarity
    similarities = util.cos_sim(query_embedding, subquery_embeddings)

    return similarities