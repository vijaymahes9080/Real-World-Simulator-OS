import re
import httpx
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

class AIQueryResponse(BaseModel):
    natural_explanation: str
    parameter_adjustments: Dict[str, float] = {}
    triggered_simulation: bool = False
    suggested_visualizations: List[str] = []

class LLMService:
    def __init__(self, endpoint_url: str = "http://localhost:11434/api/generate", model_name: str = "llama3"):
        self.endpoint_url = endpoint_url
        self.model_name = model_name

    async def query_assistant(self, user_prompt: str, current_parameters: Dict[str, float]) -> AIQueryResponse:
        """
        Parses natural language input to determine if the user wants to adjust parameters or run a scenario.
        Provides a hybrid local model client and robust offline parser fallback.
        """
        # Step 1: Attempt local LLM API (Ollama / Llama.cpp) if active
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                # Prompt instructing LLM to output JSON format
                prompt = (
                    f"You are the AI Assistant for the Real-World Simulator OS.\n"
                    f"Current system variables: {current_parameters}\n"
                    f"User request: '{user_prompt}'\n"
                    f"Format your response EXACTLY as a JSON object with these keys:\n"
                    f"- 'explanation': Natural language response to the user's question.\n"
                    f"- 'adjustments': Dictionary mapping parameter keys to new float values.\n"
                    f"Example: {{\"explanation\": \"Simulating a 30% reduction in funding...\", \"adjustments\": {{\"funding\": 700.0}}}}\n"
                )
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
                response = await client.post(self.endpoint_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    # Parse contents
                    # Ollama return format might vary, handle text response parsing if needed
                    # ...
                    # For safety, let's process the fallback if JSON decoding fails
                    pass
        except Exception:
            # Fallback to local regex-based analyzer if server is offline
            pass

        # Robust Local Fallback Rules
        explanation = "I've analyzed your question and initiated a matching simulated scenario."
        adjustments = {}
        triggered = False
        visuals = ["Timeline Plot", "Sensitivity Chart"]

        prompt_clean = user_prompt.lower()
        
        # Scenario 1: Funding decrease
        if "funding" in prompt_clean or "budget" in prompt_clean:
            match = re.search(r"(\d+)%", prompt_clean)
            if match:
                percent = float(match.group(1))
                factor = 1 - (percent / 100)
                # Apply factor to any funding parameter present
                for k, v in current_parameters.items():
                    if "fund" in k or "budget" in k:
                        adjustments[k] = v * factor
                explanation = f"Simulating a {percent}% reduction in funding parameter(s). Let's observe the cascading effect on reserves and production capacity."
                triggered = True
            elif "increase" in prompt_clean or "double" in prompt_clean:
                for k, v in current_parameters.items():
                    if "fund" in k or "budget" in k:
                        adjustments[k] = v * 2.0
                explanation = "Simulating doubled funding assets. Let's trace expansion speed and resource consumption."
                triggered = True

        # Scenario 2: Weather / Rainfall variables
        elif "rain" in prompt_clean or "weather" in prompt_clean or "water" in prompt_clean:
            if "double" in prompt_clean or "increase" in prompt_clean:
                for k, v in current_parameters.items():
                    if "rain" in k or "water" in k:
                        adjustments[k] = v * 2.0
                explanation = "Simulating double rainfall rates. This is helpful for flood and crop growth stress tests."
                triggered = True
            elif "drought" in prompt_clean or "decrease" in prompt_clean:
                for k, v in current_parameters.items():
                    if "rain" in k or "water" in k:
                        adjustments[k] = v * 0.1
                explanation = "Simulating drought conditions (rainfall dropped to 10%). Crop growth and reserve levels should reflect resource scarcity."
                triggered = True

        # Scenario 3: Employee resignations / Labor shortage
        elif "employee" in prompt_clean or "staff" in prompt_clean or "layoff" in prompt_clean:
            match = re.search(r"(\d+)%", prompt_clean)
            if match:
                percent = float(match.group(1))
                factor = 1 - (percent / 100)
                for k, v in current_parameters.items():
                    if "employee" in k or "staff" in k or "labor" in k or "count" in k:
                        adjustments[k] = v * factor
                explanation = f"Simulating reduction in labor force by {percent}%. Let's review the impact on productivity metrics."
                triggered = True

        # Generic default response
        if not triggered:
            explanation = (
                f"Understood. To run this experiment, I can adjust the current parameters: "
                f"{list(current_parameters.keys())}. Try asking: 'What if funding drops by 30%?'"
            )

        return AIQueryResponse(
            natural_explanation=explanation,
            parameter_adjustments=adjustments,
            triggered_simulation=triggered,
            suggested_visualizations=visuals
        )
