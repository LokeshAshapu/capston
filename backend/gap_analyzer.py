from typing import List, Dict
from sklearn.cluster import KMeans
import numpy as np
from sentence_transformers import SentenceTransformer

class GapAnalyzer:
    """Analyzes skill gaps and clusters missing skills"""
    
    def __init__(self):
        self.embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.skill_importance = self._load_skill_importance()
    
    def _load_skill_importance(self) -> Dict[str, float]:
        """Load skill importance weights"""
        return {
            # Core technical skills (high importance)
            "python": 10, "javascript": 9, "java": 9, "sql": 9, "react": 9,
            "aws": 8, "docker": 8, "kubernetes": 8, "git": 9,
            
            # Mid-level importance
            "html": 7, "css": 7, "mongodb": 7, "api": 7, "testing": 7,
            
            # Soft skills
            "communication": 8, "leadership": 7, "problem solving": 8,
            
            # Default
            "default": 5
        }
    
    def analyze_gaps(self, matched: List, missing: List, weak_matches: List) -> Dict:
        """
        Comprehensive gap analysis
        
        Args:
            matched: Matched skills
            missing: Missing skills
            weak_matches: Weak matches
            
        Returns:
            Detailed gap analysis
        """
        total_required = len(matched) + len(missing) + len(weak_matches)
        
        gap_analysis = {
            "summary": {
                "total_required": total_required,
                "matched": len(matched),
                "missing": len(missing),
                "weak": len(weak_matches),
                "completion_percentage": round((len(matched) / total_required * 100), 2) if total_required > 0 else 0,
            },
            "missing_skills": self._rank_missing_skills(missing),
            "weak_skills": weak_matches,
            "skill_clusters": self._cluster_missing_skills(missing),
        }
        
        return gap_analysis
    
    def _rank_missing_skills(self, missing_skills: List[str]) -> List[Dict]:
        """
        Rank missing skills by importance and dependencies
        
        Args:
            missing_skills: List of missing skills
            
        Returns:
            Ranked list of missing skills with importance scores
        """
        ranked = []
        
        for skill in missing_skills:
            importance = self.skill_importance.get(skill.lower(), self.skill_importance["default"])
            dependencies = self._get_skill_dependencies(skill)
            
            ranked.append({
                "skill": skill,
                "importance": importance,
                "priority": "High" if importance >= 8 else "Medium" if importance >= 6 else "Low",
                "dependencies": dependencies,
            })
        
        # Sort by importance (descending)
        ranked.sort(key=lambda x: x["importance"], reverse=True)
        
        return ranked
    
    def _get_skill_dependencies(self, skill: str) -> List[str]:
        """Get prerequisite skills for a given skill"""
        dependencies_map = {
            "kubernetes": ["docker"],
            "django": ["python"],
            "tensorflow": ["python", "numpy"],
            "aws": ["linux"],
            "microservices": ["api", "docker"],
            "graphql": ["javascript", "api"],
        }
        
        return dependencies_map.get(skill.lower(), [])
    
    def _cluster_missing_skills(self, missing_skills: List[str], n_clusters: int = 3) -> Dict:
        """
        Cluster missing skills into categories for better planning
        
        Args:
            missing_skills: List of missing skills
            n_clusters: Number of clusters
            
        Returns:
            Clustered skills with categories
        """
        if len(missing_skills) < n_clusters:
            n_clusters = max(1, len(missing_skills) - 1)
        
        if n_clusters == 0 or len(missing_skills) == 0:
            return {"clusters": []}
        
        try:
            embeddings = self.embeddings_model.encode(missing_skills)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            
            clusters = {}
            for idx, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(missing_skills[idx])
            
            return {
                "clusters": [{"cluster_id": k, "skills": v} for k, v in clusters.items()],
                "n_clusters": n_clusters
            }
        except Exception as e:
            return {"clusters": [{"cluster_id": 0, "skills": missing_skills}], "error": str(e)}