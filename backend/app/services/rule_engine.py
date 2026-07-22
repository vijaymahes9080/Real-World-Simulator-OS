import re
import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Define a safe built-in namespace for rule evaluation
SAFE_BUILTINS = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "int": int,
    "float": float,
    "str": str,
    "len": len,
    "bool": bool,
    "sum": sum,
    "math": math,
    # Safe list/dict constructors
    "dict": dict,
    "list": list,
    "set": set,
}

class Rule(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    domain: str = "general"
    condition: str  # e.g., "agent.budget > 1000 and global.market_status == 'bull'"
    action: str     # e.g., "agent.budget -= 500; agent.status = 'invested'"
    priority: int = 0  # Higher means executes first
    probability: float = 1.0  # Execution probability (0.0 to 1.0)
    version: int = 1

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __getitem__(self, key):
        return self.__dict__[key]
        
    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, key):
        return key in self.__dict__

    def to_dict(self):
        res = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Namespace):
                res[k] = v.to_dict()
            else:
                res[k] = v
        return res

def make_namespaces(d: Any) -> Any:
    if isinstance(d, dict):
        return Namespace(**{k: make_namespaces(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [make_namespaces(x) for x in d]
    return d

class RuleEngine:
    @staticmethod
    def sanitize_expression(expr: str) -> str:
        """
        Performs basic sanitization of input Python strings to avoid obvious exploits.
        In production, a full AST validator is recommended.
        """
        # Block double underscores (e.g., __import__, __class__)
        if "__" in expr:
            raise ValueError("Double underscores are not permitted in expressions.")
        # Block import keywords
        if re.search(r"\b(import|eval|exec|open|globals|locals|getattr|setattr|delattr)\b", expr):
            raise ValueError("Forbidden Python keywords detected in rule expression.")
        return expr

    @staticmethod
    def preprocess_expression(expr: str) -> str:
        """
        Replaces the Python keyword 'global' with 'global_vars' to avoid syntax errors.
        """
        return re.sub(r"\bglobal\b", "global_vars", expr)

    @classmethod
    def evaluate_condition(cls, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluates a condition in a sandboxed environment.
        """
        if not condition or condition.strip().lower() == "true":
            return True
        
        sanitized = cls.sanitize_expression(condition)
        preprocessed = cls.preprocess_expression(sanitized)
        
        # Build evaluation local scope with Namespace wrappers
        local_scope = {}
        for key, val in context.items():
            ns_val = make_namespaces(val)
            local_scope[key] = ns_val
            if key == "global":
                local_scope["global_vars"] = ns_val

        # Evaluate
        try:
            # Inject SAFE_BUILTINS
            global_scope = {"__builtins__": SAFE_BUILTINS}
            result = eval(preprocessed, global_scope, local_scope)
            return bool(result)
        except Exception as e:
            # In case of rule parsing errors, return False
            return False

    @classmethod
    def execute_action(cls, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes assignments or state changes defined in the action string.
        Actions are expected to be semicolon-separated statements.
        Example action: "agent.budget -= 500; global.revenue += 500"
        """
        if not action or action.strip() == "":
            return context

        sanitized = cls.sanitize_expression(action)
        preprocessed = cls.preprocess_expression(sanitized)
        
        # Execute each statement
        statements = [s.strip() for s in preprocessed.split(";") if s.strip()]
        
        local_scope = {}
        for key, val in context.items():
            ns_val = make_namespaces(val)
            local_scope[key] = ns_val
            if key == "global":
                local_scope["global_vars"] = ns_val

        global_scope = {"__builtins__": SAFE_BUILTINS}
        
        try:
            for statement in statements:
                # Execute in the namespace
                exec(statement, global_scope, local_scope)
        except Exception as e:
            raise RuntimeError(f"Failed to execute rule action statement '{action}': {str(e)}")

        # Convert namespaces back to dictionary
        result_context = {}
        for key, val in local_scope.items():
            if key == "global_vars":
                continue
            if isinstance(val, Namespace):
                result_context[key] = val.to_dict()
            elif isinstance(val, list):
                result_context[key] = [
                    x.to_dict() if isinstance(x, Namespace) else x for x in val
                ]
            else:
                result_context[key] = val
                
        return result_context

    @classmethod
    def run_ruleset(
        cls, 
        rules: List[Rule], 
        context: Dict[str, Any], 
        max_chain_depth: int = 5,
        rng: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Runs a ruleset against a context with Forward Chaining and Priority conflict resolution.
        """
        import random
        random_gen = rng or random.Random()
        
        # Sort rules by priority descending
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        
        current_context = context
        chain_depth = 0
        state_changed = True
        
        while state_changed and chain_depth < max_chain_depth:
            state_changed = False
            chain_depth += 1
            
            for rule in sorted_rules:
                # Check probability first
                if rule.probability < 1.0:
                    if random_gen.random() > rule.probability:
                        continue
                        
                # Check condition
                if cls.evaluate_condition(rule.condition, current_context):
                    # Execute action
                    prev_context = str(current_context)
                    current_context = cls.execute_action(rule.action, current_context)
                    
                    # If context changed, we trigger next cycle of chaining
                    if str(current_context) != prev_context:
                        state_changed = True
                        break  # Break to start priority scan again (Forward Chaining)
                        
        return current_context
