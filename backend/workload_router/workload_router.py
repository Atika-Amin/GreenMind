"""
Workload Router and Energy-Aware Decision Engine for GreenMind (Phase 2).
Compares device available score (S_avail) against prompt required score (S_req)
and generates routing decisions and requirement summaries.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

from device_profiler.scoring import DeviceProfile
from .prompt_analyzer import PromptAnalyzer, PromptComplexityProfile


@dataclass
class RoutingDecision:
    """Encapsulates the routing decision, comparison metrics, and prompt requirements."""
    decision_text: str          # Exactly "It can be executed locally " or "Cloud Computation needed"
    can_execute_locally: bool
    prompt_profile: PromptComplexityProfile
    device_profile: DeviceProfile
    
    # Comparison metrics
    s_available: float
    s_required: float
    score_margin: float         # S_avail - S_req (positive: surplus, negative: deficit)
    ram_available_gb: float
    ram_required_gb: float
    ram_margin_gb: float        # Available RAM - Required RAM
    
    # Decision rationale and prompt requirements
    reasons: List[str]
    prompt_requirements: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_text": self.decision_text,
            "can_execute_locally": self.can_execute_locally,
            "s_available": self.s_available,
            "s_required": self.s_required,
            "score_margin": self.score_margin,
            "ram_available_gb": self.ram_available_gb,
            "ram_required_gb": self.ram_required_gb,
            "ram_margin_gb": self.ram_margin_gb,
            "reasons": self.reasons,
            "prompt_requirements": self.prompt_requirements,
            "prompt_profile": self.prompt_profile.to_dict(),
            "device_profile": self.device_profile.to_dict(),
        }


class WorkloadRouter:
    """
    Evaluates prompt complexity against edge device capabilities to determine
    the optimal execution path (Local Edge vs Cloud Offload).
    """

    def __init__(self, analyzer: Optional[PromptAnalyzer] = None):
        self.analyzer = analyzer or PromptAnalyzer()

    def route(
        self,
        prompt: str,
        device_profile: DeviceProfile
    ) -> RoutingDecision:


        prompt_profile = self.analyzer.analyze(prompt)


        # ==============================
        # Device capability
        # ==============================

        s_avail = device_profile.s_available

        s_req = prompt_profile.s_required

        score_margin = round(
            s_avail - s_req,
            1
        )


        # ==============================
        # Memory estimation
        # ==============================

        total_ram = device_profile.memory_info.get(
            "total_gb",
            0.0
        )


        # Estimate AI usable RAM
        avail_ram = round(
            total_ram * 0.5,
            2
        )


        req_ram = prompt_profile.min_ram_gb


        ram_margin = round(
            avail_ram - req_ram,
            2
        )



        # ==============================
        # Power information
        # ==============================

        power_info = device_profile.power_info


        is_plugged = power_info.get(
            "power_plugged",
            True
        )


        battery_pct = power_info.get(
            "percent",
            100
        )



        reasons = []

        can_execute = True



        # ==============================
        # Rule 0:
        # Model Tier Compatibility
        # ==============================

        device_tier = device_profile.supported_tier

        required_tier = prompt_profile.target_model_tier



        if (

            "Standard Local LLM" in required_tier

            and

            "Tier 3" not in device_tier

        ):


            can_execute = False


            reasons.append(

                "Model Tier Mismatch: "
                "Requested 7B-8B model requires higher edge capability."

            )



        # ==============================
        # Rule 1:
        # Compute Score
        # ==============================

        if s_avail < s_req:


            can_execute = False


            reasons.append(

                f"Score Deficit: Device S_avail ({s_avail:.1f}) "
                f"is lower than required S_req ({s_req:.1f}) "
                f"by {abs(score_margin):.1f} pts."

            )


        else:


            reasons.append(

                f"Score Headroom: Device S_avail ({s_avail:.1f}) "
                f"meets required S_req ({s_req:.1f})."

            )



        # ==============================
        # Rule 2:
        # Memory
        # ==============================

        if avail_ram < req_ram:


            can_execute = False


            reasons.append(

                f"Memory Deficit: Available RAM ({avail_ram:.1f} GB) "
                f"is below required minimum ({req_ram:.1f} GB)."

            )


        else:


            reasons.append(

                f"Memory Headroom: Available RAM ({avail_ram:.1f} GB) "
                f"satisfies model requirement ({req_ram:.1f} GB)."

            )



        # ==============================
        # Rule 3:
        # Battery protection
        # ==============================

        if (

            not is_plugged

            and

            battery_pct < 20

            and

            s_req >= 50

        ):


            can_execute = False


            reasons.append(

                f"Battery Conservation: "
                f"Battery level {battery_pct}% is too low."

            )




        # Final decision

        if can_execute:


            decision_text = "It can be executed locally "


        else:


            decision_text = "Cloud Computation needed"





        prompt_requirements = {


            "required_computational_score":
            s_req,


            "minimum_ram_gb":
            req_ram,


            "minimum_compute_gflops":
            prompt_profile.min_compute_gflops,


            "target_model_tier":
            prompt_profile.target_model_tier,


            "recommended_models":
            prompt_profile.recommended_models,


            "task_category":
            prompt_profile.task_category,


            "input_tokens":
            prompt_profile.input_tokens,


            "estimated_output_tokens":
            prompt_profile.estimated_output_tokens,


            "total_tokens":
            prompt_profile.total_tokens

        }




        return RoutingDecision(

            decision_text=decision_text,

            can_execute_locally=can_execute,

            prompt_profile=prompt_profile,

            device_profile=device_profile,


            s_available=s_avail,

            s_required=s_req,

            score_margin=score_margin,


            ram_available_gb=avail_ram,

            ram_required_gb=req_ram,

            ram_margin_gb=ram_margin,


            reasons=reasons,

            prompt_requirements=prompt_requirements

        )


def format_progress_bar(val: float, max_val: float = 100.0, width: int = 24) -> str:
    """Renders a text progress bar."""
    filled = int((val / max_val) * width)
    filled = max(0, min(width, filled))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {val:5.1f} / {max_val:.0f}"


def print_routing_report(decision: RoutingDecision):
    """
    Renders a comprehensive terminal report highlighting the exact routing decision,
    comparison between device and prompt, and detailed prompt execution requirements.
    """
    p = decision.prompt_profile
    d = decision.device_profile
    req = decision.prompt_requirements
    calc = p.calculation_details

    print("\n" + "=" * 70)
    print("         GREENMIND: PROMPT COMPLEXITY & WORKLOAD ROUTING          ")
    print("=" * 70)

    # 1. PROMPT ANALYSIS & REQUIREMENTS
    print("\n[1] PROMPT EXECUTION REQUIREMENTS")
    print(f"  - Input Prompt      : \"{p.prompt[:60]}{'...' if len(p.prompt) > 60 else ''}\"")
    print(f"  - Task Category     : {p.task_category}")
    print(f"  - Target Model Tier : {p.target_model_tier}")
    print(f"  - Suitable Models   : {', '.join(p.recommended_models)}")
    print(f"  - Token Workload    : {p.input_tokens} Input + ~{p.estimated_output_tokens} Output = {p.total_tokens} Total Tokens")
    print(f"  - Required RAM      : {req['minimum_ram_gb']:.1f} GB Minimum Free RAM")
    print(f"  - Required Compute  : {req['minimum_compute_gflops']:.1f} GFLOPS Throughput")
    print(f"  - Required Score    : S_req = {p.s_required:.1f} / 100")
    if calc.get("detected_reasoning_markers"):
        print(f"  - Reasoning Markers : {', '.join(calc['detected_reasoning_markers'])}")

    # 2. CALCULATION BREAKDOWN FOR S_req
    print("\n[2] PROMPT SCORE CALCULATION (S_req)")
    print(f"    - Task Base Score (C_task)   : {p.c_task_score:4.1f} / 55 pts")
    print(f"    - Token Scale (C_token)      : {p.c_token_score:4.1f} / 30 pts ({p.total_tokens} tokens)")
    print(f"    - Structural Depth (K_struct): {p.k_struct_score:4.1f} / 15 pts")
    print(f"    -> Formula: S_req = min(100, {p.c_task_score} + {p.c_token_score} + {p.k_struct_score}) = {p.s_required:.1f} / 100")

    # 3. SCORE & RESOURCE COMPARISON
    print("\n[3] HARDWARE VS WORKLOAD COMPARISON")
    print(f"  - Device Available Score (S_avail) : {format_progress_bar(decision.s_available, 100.0, 20)}")
    print(f"  - Prompt Required Score (S_req)   : {format_progress_bar(decision.s_required, 100.0, 20)}")
    
    margin_symbol = "+" if decision.score_margin >= 0 else ""
    print(f"  - Score Margin                     : {margin_symbol}{decision.score_margin:.1f} pts {'(Feasible)' if decision.score_margin >= 0 else '(Deficit)'}")
    print(f"  - Memory Headroom                  : {decision.ram_available_gb:.1f} GB Available vs {decision.ram_required_gb:.1f} GB Required ({'+' if decision.ram_margin_gb >= 0 else ''}{decision.ram_margin_gb:.1f} GB)")

    print("\n[4] EVALUATION SUMMARY")
    for reason in decision.reasons:
        print(f"  • {reason}")

    # 5. FINAL DECISION (Exact string output required)
    print("\n" + "=" * 70)
    print(f"  ROUTING DECISION : {decision.decision_text}")
    print("=" * 70 + "\n")
