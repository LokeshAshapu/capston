# ...existing code...
import re
from typing import List, Dict

# lazy flags
_EMBEDDINGS_AVAILABLE = False
_SPACY_AVAILABLE = False

try:
    import spacy
    from sentence_transformers import SentenceTransformer
    _SPACY_AVAILABLE = True
    _EMBEDDINGS_AVAILABLE = True
except Exception:
    # allow module to load without heavy libs
    _SPACY_AVAILABLE = False
    _EMBEDDINGS_AVAILABLE = False

class SkillExtractor:
    """Extracts skills from resume text using lightweight fallback when heavy libs missing"""
    def __init__(self, embeddings_model_name: str = "all-MiniLM-L6-v2"):
        self._embeddings_model_name = embeddings_model_name
        self.nlp = None
        self.embeddings_model = None

        if _SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = None

        if _EMBEDDINGS_AVAILABLE:
            try:
                self.embeddings_model = SentenceTransformer(self._embeddings_model_name)
            except Exception:
                self.embeddings_model = None

    def extract_skills(self, text: str, job_skills: List[str] = None) -> List[str]:
        """Extract skills: use spaCy NER when available, otherwise regex tokenization"""
        if not text:
            return []

        if self.nlp:
            doc = self.nlp(text)
            ents = [ent.text for ent in doc.ents if ent.label_ in ("ORG", "PRODUCT", "NORP", "TECHNOLOGY")]
            # also fallback to noun chunks
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
            candidates = set(ents + noun_chunks)
        else:
            # simple fallback: collect capitalized words and common skill tokens
            tokens = re.findall(r"[A-Za-z+#\.\+]{2,}", text)
            candidates = set([t for t in tokens if len(t) <= 30])

        # simple dedupe and clean
        skills = [c.strip() for c in candidates if len(c.strip()) > 1]
        return sorted(list(set(skills)), key=lambda s: -len(s))  # prefer longer phrases first

    def match_skills_to_job(self, extracted_skills: List[str], job_skills: List[str]) -> Dict:
        """
        If embeddings available use semantic matching, otherwise do a conservative exact / fuzzy match.
        Returns dict with matched/weak/missing.
        """
        from rapidfuzz import fuzz

        if not job_skills:
            return {"matched": [], "weak_match": [], "missing": []}

        matched = []
        weak = []
        missing = job_skills.copy()

        # embeddings path
        if self.embeddings_model:
            try:
                import numpy as np
                ext_emb = self.embeddings_model.encode(extracted_skills, convert_to_numpy=True) if extracted_skills else np.array([])
                job_emb = self.embeddings_model.encode(job_skills, convert_to_numpy=True)
                for i, job_skill in enumerate(job_skills):
                    if ext_emb.size == 0:
                        break
                    sim = np.dot(ext_emb, job_emb[i]) / (np.linalg.norm(ext_emb, axis=1) * np.linalg.norm(job_emb[i]) + 1e-10)
                    best_idx = int(np.argmax(sim))
                    best_sim = float(sim[best_idx])
                    if best_sim >= 0.7:
                        matched.append({"job_skill": job_skill, "resume_skill": extracted_skills[best_idx], "score": best_sim})
                        if job_skill in missing: missing.remove(job_skill)
                    elif best_sim >= 0.5:
                        weak.append({"job_skill": job_skill, "similarity": best_sim})
                        if job_skill in missing: missing.remove(job_skill)
            except Exception:
                pass

        # fallback fuzzy matching for any unmatched job skills
        for job_skill in missing.copy():
            best = None
            best_score = 0
            for s in extracted_skills:
                score = fuzz.token_set_ratio(s.lower(), job_skill.lower())
                if score > best_score:
                    best_score = score
                    best = s
            if best_score >= 85:
                matched.append({"job_skill": job_skill, "resume_skill": best, "score": best_score})
                missing.remove(job_skill)
            elif best_score >= 60:
                weak.append({"job_skill": job_skill, "candidate": best, "score": best_score})
                if job_skill in missing: missing.remove(job_skill)

        return {"matched": matched, "weak_match": weak, "missing": missing}
# ...existing code...