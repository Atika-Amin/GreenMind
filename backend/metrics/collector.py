"""
Metrics Collector for GreenMind's feedback layer.

Computes what BOTH engines would have cost (energy, carbon) for a given
request, using energy_decision()'s existing formulas plus PromptAnalyzer's
own tier classification and WorkloadRouter's own device tier - regardless
of which engine actually ran. This is how the response optimizer can show
"if this had gone the other way" without ever calling a second model.
"""

from workload_router.energy_decision import energy_decision

# PromptAnalyzer's tiers -> the Low/Medium/High buckets energy_decision()
# expects. Kept here rather than in energy_decision.py so that file stays
# untouched and this mapping is easy to find/adjust in one place.
TIER_TO_COMPLEXITY = {
    "Micro SLM": "Low",
    "Compact SLM (1.5B-3.8B)": "Medium",
    "Standard Local LLM (7B-8B)": "High",
}

# DeviceProfile's supported_tier -> the low/medium/high buckets
# energy_decision() expects for device capability.
DEVICE_TIER_TO_CAPABILITY = {
    "Tier 0: Cloud Offloading Recommended": "low",
    "Tier 1: Micro SLM Capable": "low",
    "Tier 2: Compact SLM Capable": "medium",
    "Tier 3: Standard Local LLM Capable": "high",
}


def collect(prompt_profile, device_profile, decision, execution_result, engine_used=None):
    """
    prompt_profile: PromptComplexityProfile from PromptAnalyzer.analyze()
    device_profile: DeviceProfile from DeviceProfiler.profile()
    decision: RoutingDecision from WorkloadRouter.route()
    execution_result: dict - the .to_dict() output from whichever
                       Local/CloudExecutionResult actually ran
    engine_used: "local" or "cloud" - the engine that ACTUALLY produced
                 execution_result. Pass this explicitly when the feedback
                 loop may have escalated past decision.can_execute_locally;
                 falls back to the decision's own call if omitted.

    Returns a metrics dict comparing the engine that ran against the one
    that didn't - both computed from energy_decision()'s existing formulas,
    not measured, since only one engine actually executed.
    """

    if engine_used is None:
        engine_used = "local" if decision.can_execute_locally else "cloud"

    complexity = TIER_TO_COMPLEXITY.get(prompt_profile.complexity_tier, "Medium")
    capability = DEVICE_TIER_TO_CAPABILITY.get(device_profile.supported_tier, "medium")

    energy = energy_decision(
        task_analysis={"complexity": complexity},
        device_info={"device_capability": capability, "network_cost": 0.2},
    )

    other_engine = "cloud" if engine_used == "local" else "local"

    used_energy = energy["local_energy"] if engine_used == "local" else energy["cloud_energy"]
    other_energy = energy["cloud_energy"] if engine_used == "local" else energy["local_energy"]
    used_carbon = energy["local_carbon"] if engine_used == "local" else energy["cloud_carbon"]
    other_carbon = energy["cloud_carbon"] if engine_used == "local" else energy["local_carbon"]

    energy_savings_pct = (
        round((other_energy - used_energy) / other_energy * 100, 1)
        if other_energy
        else 0.0
    )

    carbon_savings_pct = (
        round((other_carbon - used_carbon) / other_carbon * 100, 1)
        if other_carbon
        else 0.0
    )

    # Response time is only real for the engine that actually ran - local
    # and cloud results store it under different keys.
    real_response_time_s = (
        execution_result.get("total_duration_s")
        if engine_used == "local"
        else execution_result.get("latency_s")
    )

    return {
        "engine_used": engine_used,
        "alternative_engine": other_engine,
        "response_time_s": real_response_time_s,
        "energy_wh": used_energy,
        "carbon_g": used_carbon,
        "alternative_energy_wh": other_energy,
        "alternative_carbon_g": other_carbon,
        "energy_savings_pct": energy_savings_pct,
        "carbon_savings_pct": carbon_savings_pct,
        "network_cost_wh": energy["network_cost"],
        "score_margin": decision.score_margin,
        "routing_reasons": decision.reasons,
    }
