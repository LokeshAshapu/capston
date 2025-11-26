import os
from dotenv import load_dotenv

load_dotenv()

APP_CONFIG = {
    "app_name": "SkillGuide AI - Skill Gap Analyzer",
    "version": "1.0.0",
    "description": "AI-powered resume analysis and personalized learning path generation",
}

# LLM Configuration
LLM_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "openai"),  # openai, gemini, claude, huggingface
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "gemini_api_key": os.getenv("GEMINI_API_KEY"),
    "claude_api_key": os.getenv("CLAUDE_API_KEY"),
    "huggingface_api_key": os.getenv("HUGGINGFACE_API_KEY"),
    "huggingface_model": os.getenv("HUGGINGFACE_MODEL", "gpt2"),
    "model_name": os.getenv("LLM_MODEL", "gpt-4-turbo"),
}

# NLP Configuration
NLP_CONFIG = {
    "spacy_model": "en_core_web_sm",
    "embeddings_model": "all-MiniLM-L6-v2",
    "similarity_threshold": 0.7,
}

# Clustering Configuration
CLUSTERING_CONFIG = {
    "method": "kmeans",  # kmeans or hdbscan
    "n_clusters": 5,
    "min_cluster_size": 2,
}

# File Upload Configuration
FILE_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_formats": [".pdf", ".docx", ".doc"],
}

# Database Configuration (optional)
DATABASE_CONFIG = {
    "use_supabase": os.getenv("USE_SUPABASE", False),
    "supabase_url": os.getenv("SUPABASE_URL"),
    "supabase_key": os.getenv("SUPABASE_KEY"),
}

# Job Templates Path
JOB_TEMPLATES_PATH = "config/job_templates.json"
SKILL_TAXONOMY_PATH = "data/skill_taxonomy.json"