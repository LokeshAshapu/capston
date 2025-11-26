import json
import logging
import math
from typing import Dict, List, Any
from config.settings import LLM_CONFIG

logger = logging.getLogger(__name__)

# simple LLM handler with YouTube fallback
class LLMHandler:
    def __init__(self, provider: str = None):
        self.provider = provider or LLM_CONFIG.get("provider", "webui")
        self.client = None
        self.available = False
        self._init_error = None
        self.setup_llm()

    def setup_llm(self):
        """Try to init clients; non-fatal if missing."""
        self.client = None
        self.available = False
        self._init_error = None

        if self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=LLM_CONFIG.get("openai_api_key"))
                self.available = True
            except Exception as e:
                self._init_error = str(e)
                logger.exception("OpenAI init failed")
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=LLM_CONFIG.get("gemini_api_key"))
                self.client = genai
                # do not call any model now; mark available
                self.available = True
            except Exception as e:
                self._init_error = str(e)
                logger.exception("Gemini init failed")
        elif self.provider == "webui":
            try:
                import requests
                resp = requests.get("http://localhost:5000/api/v1/model", timeout=3)
                if resp.status_code == 200:
                    self.client = "webui"
                    self.available = True
                else:
                    self._init_error = f"webui responded {resp.status_code}"
            except Exception as e:
                self._init_error = str(e)
                logger.info("WebUI not available: %s", e)
        elif self.provider == "huggingface":
            # we don't pre-check model availability here
            try:
                key = LLM_CONFIG.get("huggingface_api_key")
                if not key:
                    raise RuntimeError("Missing huggingface api key")
                self.client = {"type": "huggingface"}
                self.available = True
            except Exception as e:
                self._init_error = str(e)
                logger.exception("HuggingFace init failed")

    def check_available(self) -> Dict[str, Any]:
        return {"available": self.available, "provider": self.provider, "init_error": self._init_error}

    # minimal wrappers (not full implementations shown earlier)
    def _call_openai(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=LLM_CONFIG.get("model_name", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
            )
            return str(response)
        except Exception as e:
            logger.exception("OpenAI call failed")
            return f"Error calling OpenAI: {e}"

    def _call_gemini(self, prompt: str) -> str:
        try:
            genai = self.client
            model = genai.GenerativeModel(LLM_CONFIG.get("gemini_model", "gemini-1.5-flash"))
            resp = model.generate_content(prompt)
            return getattr(resp, "text", str(resp))
        except Exception as e:
            logger.exception("Gemini call failed")
            return f"Error calling Gemini: {e}"

    def _call_webui(self, prompt: str) -> str:
        try:
            import requests
            url = "http://localhost:5000/api/v1/generate"
            payload = {"prompt": prompt, "max_new_tokens": 512}
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
            j = r.json()
            return j.get("results", [{}])[0].get("text", str(j))
        except Exception as e:
            logger.exception("WebUI call failed")
            return f"Error calling WebUI: {e}"

    def _call_huggingface(self, prompt: str) -> str:
        try:
            import requests
            model = LLM_CONFIG.get("huggingface_model", "gpt2")
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {LLM_CONFIG.get('huggingface_api_key')}"}
            payload = {"inputs": prompt, "options": {"wait_for_model": True}}
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            out = r.json()
            if isinstance(out, list) and out and "generated_text" in out[0]:
                return out[0]["generated_text"]
            if isinstance(out, dict) and "generated_text" in out:
                return out["generated_text"]
            return str(out)
        except Exception as e:
            logger.exception("HuggingFace call failed")
            return f"Error calling HuggingFace: {e}"

    def _parse_learning_plan(self, raw: str) -> Dict:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
            return {"raw": parsed}
        except Exception:
            # return wrapper so caller can decide
            return {"raw_plan": raw}

    def generate_learning_plan_with_videos(self, missing_skills: List[str], job_title: str, current_level: str, weekly_hours: int = 5) -> Dict:
        """
        Try to generate with LLM; if not available or parse fails, generate simple heuristic plan
        and enrich each week with YouTube videos using your YOUTUBE_API_KEY.
        """
        # attempt LLM if available
        raw = None
        if self.available:
            try:
                if self.provider == "openai":
                    raw = self._call_openai(self._create_prompt(missing_skills, job_title, current_level, weekly_hours))
                elif self.provider == "gemini":
                    raw = self._call_gemini(self._create_prompt(missing_skills, job_title, current_level, weekly_hours))
                elif self.provider == "webui":
                    raw = self._call_webui(self._create_prompt(missing_skills, job_title, current_level, weekly_hours))
                elif self.provider == "huggingface":
                    raw = self._call_huggingface(self._create_prompt(missing_skills, job_title, current_level, weekly_hours))
            except Exception as e:
                logger.exception("LLM generation failed")

        parsed = self._parse_learning_plan(raw) if raw else {"raw_plan": None}

        # If LLM parse failed or LLM not available -> build deterministic fallback plan
        if "weeks" not in parsed:
            plan = self._build_fallback_plan(missing_skills, weekly_hours)
        else:
            plan = parsed

        # enrich with YouTube videos
        try:
            from backend.youtube_search import search_youtube
            for week in plan.get("weeks", []):
                focus = week.get("focus_skill") or week.get("focus") or ""
                if focus:
                    q = f"{focus} tutorial for {current_level}"
                    week["videos"] = search_youtube(q, max_results=2)
        except Exception:
            logger.exception("Failed to enrich plan with YouTube videos")

        # compute total time
        total_hours = sum(w.get("hours", weekly_hours) for w in plan.get("weeks", []))
        plan.setdefault("total_time_hours", total_hours)
        return plan

    def _create_prompt(self, missing_skills, job_title, current_level, weekly_hours):
        skills_str = ", ".join(missing_skills) if missing_skills else "general"
        return (
            f"You are an expert career coach. Create a 12-week learning plan for the target job: {job_title}.\n"
            f"Missing skills: {skills_str}\n"
            f"Current level: {current_level}\n"
            f"Weekly hours: {weekly_hours}\n"
            "Return valid JSON with keys: weeks (list of 12 objects with week, focus_skill, topics, resources, practice_project, milestone), total_time_hours, success_metrics, prerequisites."
        )

    def _build_fallback_plan(self, missing_skills: List[str], weekly_hours: int) -> Dict:
        """Deterministic simple 12-week plan splitting skills across weeks."""
        skills = missing_skills[:] or ["Core fundamentals"]
        weeks = []
        n_skills = max(1, len(skills))
        # distribute skills across 12 weeks
        for i in range(12):
            idx = i % n_skills
            focus = skills[idx]
            topics = [f"Intro to {focus}", f"Core concepts of {focus}", f"Practice: {focus} exercises"]
            resources = [{"name": f"{focus} tutorial", "type": "video", "url": "", "duration": "30-90m"}]
            weeks.append({
                "week": i + 1,
                "focus_skill": focus,
                "topics": topics,
                "resources": resources,
                "practice_project": f"Build a small {focus} mini-project",
                "milestone": f"Understand core {focus} concepts",
                "hours": weekly_hours,
            })
        return {"weeks": weeks, "prerequisites": [], "success_metrics": ["Complete weekly milestones", "Build final projects"]}

# end of file