# from rapidfuzz import fuzz
# from typing import List, Dict, Tuple
# from sentence_transformers import SentenceTransformer
# import numpy as np

# class SkillMatcher:
#     """Matches extracted skills with job requirements"""
    
#     def __init__(self):
#         self.embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
    
#     def fuzzy_match(self, skill: str, job_skills: List[str], threshold: int = 80) -> Tuple[str, int]:
#         """
#         Fuzzy match a skill against job skills
        
#         Args:
#             skill: Extracted skill
#             job_skills: List of job required skills
#             threshold: Matching threshold (0-100)
            
#         Returns:
#             Tuple of (matched_skill, score)
#         """
#         if not job_skills:
#             return (None, 0)
        
#         best_match = None
#         best_score = 0
        
#         for job_skill in job_skills:
#             score = fuzz.token_set_ratio(skill.lower(), job_skill.lower())
#             if score > best_score:
#                 best_score = score
#                 best_match = job_skill
        
#         return (best_match, best_score) if best_score >= threshold else (None, best_score)
    
#     def semantic_match(self, skill: str, job_skills: List[str], threshold: float = 0.7) -> Tuple[str, float]:
#         """
#         Semantic match using embeddings
        
#         Args:
#             skill: Extracted skill
#             job_skills: List of job required skills
#             threshold: Similarity threshold (0-1)
            
#         Returns:
#             Tuple of (matched_skill, similarity_score)
#         """
#         if not job_skills:
#             return (None, 0)
        
#         skill_embedding = self.embeddings_model.encode(skill)
#         job_embeddings = self.embeddings_model.encode(job_skills)
        
#         # Cosine similarity
#         similarities = np.dot(job_embeddings, skill_embedding) / (
#             np.linalg.norm(job_embeddings, axis=1) * np.linalg.norm(skill_embedding) + 1e-10
#         )
        
#         best_idx = np.argmax(similarities)
#         best_score = similarities[best_idx]
        
#         return (job_skills[best_idx], float(best_score)) if best_score >= threshold else (None, float(best_score))
    
#     def match_all_skills(self, extracted_skills: List[str], job_skills: List[str]) -> Dict:
#         """
#         Match all extracted skills against job requirements
        
#         Args:
#             extracted_skills: Skills from resume
#             job_skills: Required job skills
            
#         Returns:
#             Comprehensive matching results
#         """
#         matched = []
#         weak_matches = []
#         missing = list(job_skills)
        
#         for skill in extracted_skills:
#             fuzzy_result = self.fuzzy_match(skill, job_skills, threshold=75)
#             semantic_result = self.semantic_match(skill, job_skills, threshold=0.6)
            
#             # Use fuzzy match if strong, otherwise semantic
#             if fuzzy_result[1] >= 80:
#                 matched.append({
#                     "skill": skill,
#                     "matched_to": fuzzy_result[0],
#                     "score": fuzzy_result[1],
#                     "method": "fuzzy"
#                 })
#                 if fuzzy_result[0] in missing:
#                     missing.remove(fuzzy_result[0])
#             elif semantic_result[1] >= 0.65:
#                 matched.append({
#                     "skill": skill,
#                     "matched_to": semantic_result[0],
#                     "score": float(semantic_result[1]),
#                     "method": "semantic"
#                 })
#                 if semantic_result[0] in missing:
#                     missing.remove(semantic_result[0])
#             elif fuzzy_result[1] >= 60 or semantic_result[1] >= 0.5:
#                 weak_matches.append({
#                     "skill": skill,
#                     "potential_match": fuzzy_result[0] or semantic_result[0],
#                     "fuzzy_score": fuzzy_result[1],
#                     "semantic_score": float(semantic_result[1])
#                 })
        
#         return {
#             "matched": matched,
#             "weak_matches": weak_matches,
#             "missing": missing,
#             "match_percentage": round((len(matched) / len(job_skills) * 100), 2) if job_skills else 0
#         }

# ...existing code...
from rapidfuzz import fuzz
from typing import List, Dict, Tuple

# lazy import for embeddings
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _EMBEDDINGS_OK = True
except Exception:
    _EMBEDDINGS_OK = False

class SkillMatcher:
    """Matches extracted skills with job requirements using fuzzy or semantic matching if available."""
    def __init__(self, embeddings_model_name: str = "all-MiniLM-L6-v2"):
        self.embeddings_model = None
        if _EMBEDDINGS_OK:
            try:
                self.embeddings_model = SentenceTransformer(embeddings_model_name)
            except Exception:
                self.embeddings_model = None

    def fuzzy_match(self, skill: str, job_skills: List[str], threshold: int = 80) -> Tuple[str, int]:
        if not job_skills:
            return (None, 0)
        best_match, best_score = None, 0
        for js in job_skills:
            score = fuzz.token_set_ratio(skill.lower(), js.lower())
            if score > best_score:
                best_score, best_match = score, js
        return (best_match, best_score) if best_score >= threshold else (None, best_score)

    def semantic_match(self, skill: str, job_skills: List[str], threshold: float = 0.7) -> Tuple[str, float]:
        if not self.embeddings_model or not job_skills:
            return (None, 0.0)
        try:
            skill_emb = self.embeddings_model.encode(skill, convert_to_numpy=True)
            job_embs = self.embeddings_model.encode(job_skills, convert_to_numpy=True)
            sims = np.dot(job_embs, skill_emb) / (np.linalg.norm(job_embs, axis=1) * np.linalg.norm(skill_emb) + 1e-10)
            best_idx = int(np.argmax(sims))
            best_score = float(sims[best_idx])
            return (job_skills[best_idx], best_score) if best_score >= threshold else (None, best_score)
        except Exception:
            return (None, 0.0)

    def match_all_skills(self, extracted_skills: List[str], job_skills: List[str]) -> Dict:
        matched = []
        weak_matches = []
        missing = job_skills.copy()

        for s in extracted_skills:
            f_match, f_score = self.fuzzy_match(s, job_skills, threshold=75)
            sem_match, sem_score = self.semantic_match(s, job_skills, threshold=0.65)

            if f_match and f_score >= 80:
                matched.append({"skill": s, "matched_to": f_match, "score": f_score, "method": "fuzzy"})
                if f_match in missing: missing.remove(f_match)
            elif sem_match and sem_score >= 0.65:
                matched.append({"skill": s, "matched_to": sem_match, "score": sem_score, "method": "semantic"})
                if sem_match in missing: missing.remove(sem_match)
            elif f_score >= 60 or sem_score >= 0.5:
                weak_matches.append({"skill": s, "potential_match": f_match or sem_match, "fuzzy_score": f_score, "semantic_score": sem_score})

        match_percentage = round((len(matched) / len(job_skills) * 100), 2) if job_skills else 0
        return {"matched": matched, "weak_matches": weak_matches, "missing": missing, "match_percentage": match_percentage}
# ...existing code...