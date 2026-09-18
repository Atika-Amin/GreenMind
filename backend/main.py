
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas.request import AIRequest

from device_profiler import DeviceProfiler

from workload_router.prompt_analyzer import PromptAnalyzer

from workload_router.workload_router import WorkloadRouter


import os
import sys

# local_engine/ and cloud_engine/ live one level up from backend/, at the
# project root - add that to the path so they're importable from here.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

# Your .env file lives at the project root, not inside backend/ - point
# load_dotenv at it explicitly rather than relying on auto-detection.
load_dotenv(dotenv_path=os.path.join(_PROJECT_ROOT, ".env"))

from local_engine import LocalExecutor
from cloud_engine import CloudExecutor

local_executor = LocalExecutor()
cloud_executor = CloudExecutor()

from metrics.collector import collect
from optimization.response_optimizer import optimize
from optimization.feedback_loop import run_with_feedback

app = FastAPI(
    title="GreenMind API",
    version="2.0"
)



# ============================
# CORS Configuration
# ============================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"]

)



# ============================
# Home Route
# ============================

@app.get("/")
def home():

    return {

        "message":
        "GreenMind AI Workload Router API Running",

        "version":
        "2.0"

    }





# ============================
# Main Processing Pipeline
# ============================

@app.post("/process")
def process(request: AIRequest):


    # ==================================
    # 1. DEVICE PROFILING
    # ==================================

    profiler = DeviceProfiler()


    device_profile = profiler.profile(

        run_benchmark=False

    )



    # ==================================
    # 2. PROMPT WORKLOAD ANALYSIS
    # ==================================

    analyzer = PromptAnalyzer()


    prompt_profile = analyzer.analyze(

        request.prompt

    )



    # ==================================
    # 3. ENERGY AWARE ROUTING DECISION
    # ==================================

    router = WorkloadRouter()


    decision = router.route(

        request.prompt,

        device_profile

    )
    # ==================================
    # 4. EXECUTION WITH FEEDBACK LOOP
    #    (verifies quality, retries truncation once,
    #    escalates local -> cloud if still failing)
    # ==================================

    execution_result_dict, engine_used, feedback_attempts = run_with_feedback(

        decision,

        local_executor,

        cloud_executor

    )



    # ==================================
    # 5. METRICS + RESPONSE OPTIMIZATION
    # ==================================

    metrics = collect(

        decision.prompt_profile,

        device_profile,

        decision,

        execution_result_dict,

        engine_used

    )


    optimized = optimize(

        execution_result_dict,

        metrics

    )



    # ==================================
    # FINAL RESPONSE
    # ==================================

    return {


        "greenmind_status":

        "Workload analysis completed",

        "execution": {
            "engine_used": engine_used,
            **execution_result_dict
        },

        "response_optimization": optimized,

        "metrics": metrics,

        "feedback_attempts": feedback_attempts,



        "prompt_analysis":{


            "task_category":

            prompt_profile.task_category,


            "target_model_tier":

            prompt_profile.target_model_tier,


            "input_tokens":

            prompt_profile.input_tokens,


            "estimated_output_tokens":

            prompt_profile.estimated_output_tokens,


            "total_tokens":

            prompt_profile.total_tokens,


            "required_score":

            prompt_profile.s_required,


            "required_ram_gb":

            prompt_profile.min_ram_gb,


            "required_compute_gflops":

            prompt_profile.min_compute_gflops,


            "recommended_models":

            prompt_profile.recommended_models

        },



        "device_profile":{


            "cpu":

            device_profile.cpu_info,


            "memory":

            device_profile.memory_info,


            "gpu":

            device_profile.gpu_info,


            "battery":

            device_profile.power_info,


            "available_score":

            device_profile.s_available,


            "supported_tier":

            device_profile.supported_tier

        },



        "routing_decision":{


            "decision":

            decision.decision_text,


            "can_execute_locally":

            decision.can_execute_locally,


            "score_margin":

            decision.score_margin,


            "ram_margin_gb":

            decision.ram_margin_gb,


            "reasons":

            decision.reasons

        }

    }