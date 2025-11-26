from typing import List, Dict
try:
    from rapidfuzz import fuzz
    _HAS_RAPIDFUZZ = True
except Exception:
    _HAS_RAPIDFUZZ = False
    from difflib import SequenceMatcher

class SkillNormalizer:
    """Normalizes and standardizes skill names with graceful fallback if rapidfuzz missing"""
    
    def __init__(self):
        self.skill_dictionary = {
            "python": ["py", "python 3", "python3", "anaconda"],
            "javascript": ["js", "node.js", "nodejs", "react", "vue"],
            "java": ["j2ee", "spring boot", "jvm"],
            "sql": ["mysql", "postgresql", "postgres", "oracle", "t-sql"],
            "cpp": ["c++", "cpp", "c plus plus"],
            "csharp": ["c#", "dotnet", ".net", "asp.net"],
            "react": ["reactjs", "react.js"],
            "angular": ["angularjs", "angular.js"],
            "html": ["html5", "html 5"],
            "css": ["css3", "sass", "scss"],
            "aws": ["amazon web services", "amazon aws"],
            "gcp": ["google cloud", "google cloud platform"],
            "azure": ["microsoft azure", "azure cloud"],
            "docker": ["dockerization", "containerization"],
            "kubernetes": ["k8s", "container orchestration"],
            "mongodb": ["mongo", "nosql"],
            "redis": ["caching", "cache"],
            "elasticsearch": ["elastic search", "search engine"],
            "machine learning": ["ml", "machine-learning"],
            "tensorflow": ["tensor flow", "tensorflow.js"],
            "pytorch": ["torch", "pytorch"],
            "scikit-learn": ["sklearn", "scikit learn"],
            "pytest": ["python testing"],
            "junit": ["java testing"],
            "git": ["github", "gitlab", "bitbucket", "version control"],
            "jira": ["agile", "scrum", "kanban"],
            "jenkins": ["ci/cd", "continuous integration"],
        }
    
    def _fuzzy_score(self, a: str, b: str) -> float:
        if _HAS_RAPIDFUZZ:
            return fuzz.ratio(a, b)
        else:
            return int(SequenceMatcher(None, a, b).ratio() * 100)
    
    def normalize_skill(self, skill: str) -> str:
        skill_lower = skill.lower().strip()
        if skill_lower in self.skill_dictionary:
            return skill_lower
        # check aliases
        for standard_skill, aliases in self.skill_dictionary.items():
            # exact alias match
            for alias in aliases:
                if skill_lower == alias:
                    return standard_skill
            # fuzzy match using available method
            for alias in aliases + [standard_skill]:
                score = self._fuzzy_score(skill_lower, alias)
                if score >= 85:
                    return standard_skill
        return skill.strip()
    
    def normalize_skills_list(self, skills: List[str]) -> List[str]:
        normalized = []
        seen = set()
        for skill in skills:
            normalized_skill = self.normalize_skill(skill)
            if normalized_skill not in seen:
                normalized.append(normalized_skill)
                seen.add(normalized_skill)
        return normalized
    
    def get_skill_category(self, skill: str) -> str:
        categories = {
            "programming_languages": ["python", "javascript", "java", "sql", "cpp", "csharp"],
            "web_frameworks": ["react", "angular", "html", "css", "vue"],
            "cloud_platforms": ["aws", "gcp", "azure"],
            "devops": ["docker", "kubernetes", "jenkins", "git"],
            "databases": ["mongodb", "redis", "elasticsearch", "sql"],
            "ml_ai": ["machine learning", "tensorflow", "pytorch", "scikit-learn"],
            "testing": ["pytest", "junit"],
        }
        normalized = self.normalize_skill(skill)
        for category, skills_list in categories.items():
            if normalized in skills_list:
                return category
        return "other"