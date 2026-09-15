"""
Response Optimizer for GreenMind's feedback layer.

Takes the raw execution result plus metrics.collector's output and
produces the final response: the actual answer, plus honest
Fast / Accurate / Energy Efficient / Sustainable comparisons against the
engine that *wasn't* used. Everything here is reasoned from numbers
WorkloadRouter and energy_decision() already computed - no second model
call, no guessing.
"""

# Rough response-time ceilings per engine to call a result "fast".
# Heuristic, not measured against the alternative engine (we never ran it) -
# tune these against your own real test results as you gather more of them.
FAST_THRESHOLD_S = {"local": 10.0, "cloud": 8.0}

# Energy/carbon differences under this percent are treated as a wash
# rather than forcing a winner - this is the "cost might be the same"
# case: small margins shouldn't be dressed up as a decisive advantage.
COMPARABLE_THRESHOLD_PCT = 5.0


def _is_fast(engine_used, response_time_s):
    if response_time_s is None:
        return None
    return response_time_s <= FAST_THRESHOLD_S.get(engine_used, 10.0)


def _is_accurate(engine_used, score_margin):
    if engine_used == "cloud":
        # Cloud is the escalation target and is presumed capable of any
        # task GreenMind sends it - score_margin here reflects local's
        # capability gap, not cloud's, so it isn't the right signal for
        # cloud's own accuracy.
        return True
    # Local: WorkloadRouter only allows this path when S_avail >= S_req,
    # so a non-negative margin means the device comfortably met the
    # task's own required capability - not a marginal, underpowered call.
    return score_margin is not None and score_margin >= 0


def _energy_comparison_text(other_engine, savings_pct):
    if abs(savings_pct) < COMPARABLE_THRESHOLD_PCT:
        return f"Comparable energy use to {other_engine} ({savings_pct:+.1f}%)."
    if savings_pct > 0:
        return f"{savings_pct:.1f}% less energy than {other_engine} would have used."
    return f"{abs(savings_pct):.1f}% more energy than {other_engine} would have used."


def _accuracy_comparison_text(engine_used, metrics):
    if engine_used == "local":
        return (
            "Local model met this task's required capability "
            f"(score margin +{metrics['score_margin']:.1f}). Cloud would likely match "
            "or slightly exceed this, but that extra capability wasn't needed here."
        )
    reasons_text = "; ".join(metrics["routing_reasons"]) or "device capability limits"
    return f"Cloud was used because local execution didn't meet this task's requirements ({reasons_text})."


def optimize(execution_result, metrics):
    """
    execution_result: dict - the .to_dict() output from whichever engine ran
    metrics: dict - the output of metrics.collector.collect()
    """

    engine_used = metrics["engine_used"]
    other_engine = metrics["alternative_engine"]
    success = bool(execution_result.get("success"))

    energy_efficient = metrics["energy_wh"] <= metrics["alternative_energy_wh"]
    sustainable = metrics["carbon_g"] <= metrics["alternative_carbon_g"]

    return {
        "final_response": execution_result.get("response_text"),
        "status": "Optimized" if success else "Failed",
        "engine_used": engine_used,
        "badges": {
            # A failed execution earns no positive badges - there's no
            # real response to call fast, accurate, or anything else.
            "fast": _is_fast(engine_used, metrics["response_time_s"]) if success else False,
            "accurate": _is_accurate(engine_used, metrics["score_margin"]) if success else False,
            "energy_efficient": energy_efficient if success else False,
            "sustainable": sustainable if success else False,
        },
        # The actual numbers behind each badge above - so the UI (and the
        # paper) can show real figures, not just a pass/fail pill.
        "details": {
            "response_time_s": metrics["response_time_s"],
            "fast_threshold_s": FAST_THRESHOLD_S.get(engine_used, 10.0),
            "score_margin": metrics["score_margin"],
            "energy_wh": metrics["energy_wh"],
            "alternative_energy_wh": metrics["alternative_energy_wh"],
            "energy_savings_pct": metrics["energy_savings_pct"],
            "carbon_g": metrics["carbon_g"],
            "alternative_carbon_g": metrics["alternative_carbon_g"],
            "carbon_savings_pct": metrics["carbon_savings_pct"],
        },
        "comparison": {
            "alternative_engine": other_engine,
            "energy": _energy_comparison_text(other_engine, metrics["energy_savings_pct"]),
            "accuracy": _accuracy_comparison_text(engine_used, metrics),
            "alternative_energy_wh": metrics["alternative_energy_wh"],
            "alternative_carbon_g": metrics["alternative_carbon_g"],
        },
    }
