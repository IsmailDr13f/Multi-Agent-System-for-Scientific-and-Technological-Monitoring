# Define a structure to hold person profiles
profiles = [
    {
    "name": "KHALID BOUSSAROUAL",
    "laboratory": "DATA-LAB, DICE",
    "role": "AI Engineer",
    "preferences": [
        "LLMs",
        "Transformers",
        "Reinforcement Learning",
        "Causal Inference",
        "Graph Neural Networks",
        "Generative AI",
        "AI Ethics",
        "Few-shot Learning",
        "Prompt Engineering",
        "Foundation Models",
        "Knowledge Graphs",
        "AI for Healthcare",
        "Multimodal Learning",
        "Explainable AI (XAI)",
        "Transfer Learning",
        "Natural Language Understanding",
        "Neurosymbolic AI"
    ],
    "email": "KHALID.BOUSSAROUAL-EXT@um6p.ma",
    "availability": "Full-time"
    },
    {
    "name": "GHITA HATIMI",
    "laboratory": "DATA-LAB, DICE",
    "role": "Computer Vision Engineer",
    "preferences": [
        "Image Classification",
        "Object Detection",
        "Image Segmentation",
        "Video Analysis",
        "3D Reconstruction",
        "Pose Estimation",
        "SLAM (Simultaneous Localization and Mapping)",
        "Optical Flow",
        "Image Super-Resolution",
        "Computer Vision for Autonomous Vehicles",
        "Face Recognition",
        "Medical Image Analysis",
        "Instance Segmentation",
        "Scene Understanding",
        "Self-supervised Learning in Vision",
        "Vision Transformers (ViT)",
        "Multi-view Geometry",
        "Edge Computing for Vision"
    ],
    "email": "GHITA.HATIMI-EXT@um6p.ma",
    "availability": "Full-time"
    },
    {
    "name": "ISMAIL DRIEF",
    "laboratory": "DATA-LAB, DICE",
    "role": "Data Scientist",
    "preferences": [
        "GenAI",
        "AI Agents",
        "Predictive Modeling",
        "Time Series Analysis",
        "Data Wrangling",
        "Big Data Analytics",
        "Business Intelligence",
        "Causal Inference",
        "LLMs",
        "Clustering Techniques",
        "Hypothesis Testing",
        "Data Storytelling",
        "Data Visualization",
        "Data Quality Management",
        "Feature Selection",
        "A/B Testing",
        "Statistical Modeling",
        "Natural Language Processing (NLP)",
        "Reinforcement Learning",
        "Deep Learning",
        "Machine Learning",
    ],
    "email": "ISMAIL.DRIEF-EXT@um6p.ma",
    "availability": "Full-time"
}



]

from pymongo import MongoClient

# Connect to MongoDB (change the URI if you're using MongoDB Atlas)
client = MongoClient("mongodb://localhost:27017/")  

# Create or use a database
db = client["vst_db"]

# Create or use a collection
collection = db["profiles"]


# Insert the profiles into the collection
result = collection.insert_many(profiles)

# Output inserted IDs
print("Inserted profile IDs:", result.inserted_ids)
