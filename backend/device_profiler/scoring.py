"""
Scoring and Evaluation module for GreenMind.
Computes the Available Computational Score (S_avail)
and evaluates local model suitability.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List



@dataclass
class DeviceProfile:

    timestamp: str

    os_info: Dict[str, Any]

    cpu_info: Dict[str, Any]

    memory_info: Dict[str, Any]

    gpu_info: List[Dict[str, Any]]

    power_info: Dict[str, Any]

    benchmark_info: Dict[str, Any]


    # Scores

    c_base_score: float

    m_headroom_score: float

    load_factor: float

    battery_factor: float

    s_available: float


    calculation_details: Dict[str, Any]


    supported_tier: str

    suitable_models: List[str]

    routing_recommendation: str



    def to_dict(self):

        return asdict(self)





class ComputeScoreCalculator:


    @staticmethod
    def calculate(
        telemetry: Dict[str, Any],
        benchmark: Dict[str, Any],
        timestamp_str: str
    ) -> DeviceProfile:



        cpu = telemetry["cpu"]

        mem = telemetry["memory"]

        gpus = telemetry["gpu"]

        power = telemetry["power"]




        # ==================================
        # 1. COMPUTE BASE SCORE (40 POINTS)
        # ==================================


        physical_cores = cpu.get(
            "physical_cores",
            1
        )


        # Laptop friendly scaling

        core_score = min(
            15.0,
            (physical_cores / 8.0) * 15.0
        )



        clock_mhz = (

            cpu.get(
                "max_frequency_mhz"
            )

            or

            cpu.get(
                "current_frequency_mhz"
            )

            or

            2500

        )



        clock_score = min(

            10.0,

            (clock_mhz / 3500.0) * 10.0

        )





        # Benchmark score

        gflops = benchmark.get(
            "gflops",
            0.0
        )


        benchmark_score = min(

            8.0,

            (gflops / 250.0) * 8.0

        )





        # GPU score

        has_discrete = any(

            g.get(
                "type",
                ""
            ).startswith("Discrete")

            for g in gpus

        )


        max_vram = max(

            [

                g.get(
                    "dedicated_vram_gb",
                    0.0
                )

                for g in gpus

            ],

            default=0.0

        )



        if has_discrete and max_vram >= 6:

            gpu_score = 7.0


        elif has_discrete or max_vram >= 2:

            gpu_score = 5.0


        else:

            gpu_score = 3.0





        c_base = round(

            core_score

            +

            clock_score

            +

            benchmark_score

            +

            gpu_score,

            2

        )


        c_base = min(
            40.0,
            c_base
        )





        # ==================================
        # 2. MEMORY SCORE (35 POINTS)
        # ==================================


        total_ram_gb = mem.get(
            "total_gb",
            0.0
        )


        # Use realistic usable memory estimation

        avail_ram_gb = round(

            total_ram_gb * 0.5,

            2

        )



        if avail_ram_gb >= 16:

            m_score = 35.0


        elif avail_ram_gb >= 8:

            m_score = 30.0


        elif avail_ram_gb >= 6:

            m_score = 25.0


        elif avail_ram_gb >= 4:

            m_score = 18.0


        elif avail_ram_gb >= 2:

            m_score = 10.0


        else:

            m_score = 0.0






        # ==================================
        # 3. SYSTEM LOAD FACTOR
        # ==================================


        cpu_load = cpu.get(
            "utilization_pct",
            0.0
        )


        ram_load = mem.get(
            "utilization_pct",
            0.0
        )


        combined_load = (

            cpu_load * 0.65

            +

            ram_load * 0.35

        )



        if combined_load <= 25:


            load_factor = round(

                1.0 -
                (combined_load / 25)
                * 0.05,

                2

            )


        elif combined_load <= 70:


            load_factor = round(

                0.95 -

                ((combined_load - 25)
                 / 45)
                * 0.35,

                2

            )


        else:


            load_factor = round(

                max(

                    0.20,

                    0.60 -

                    ((combined_load - 70)
                    / 30)
                    * 0.40

                ),

                2

            )







        # ==================================
        # 4. BATTERY FACTOR
        # ==================================


        plugged = power.get(
            "power_plugged",
            True
        )


        battery = power.get(
            "percent",
            100
        )



        if plugged:


            battery_factor = 1.0


        else:


            if battery >= 70:

                battery_factor = 0.85


            elif battery >= 40:

                battery_factor = 0.65


            elif battery >= 20:

                battery_factor = 0.40


            else:

                battery_factor = 0.15






        # ==================================
        # 5. FINAL AVAILABLE SCORE
        # ==================================


        raw_potential = (

            c_base

            +

            m_score

        ) * (100 / 75)



        s_available = round(

            raw_potential

            *

            load_factor

            *

            battery_factor,

            1

        )






        calculation_details = {


            "physical_cores":
            physical_cores,


            "core_score":
            round(core_score,2),


            "clock_mhz":
            clock_mhz,


            "clock_score":
            round(clock_score,2),


            "gflops":
            round(gflops,2),


            "benchmark_score":
            round(benchmark_score,2),


            "gpu_score":
            gpu_score,


            "c_base":
            c_base,


            "total_ram_gb":
            total_ram_gb,


            "usable_ram_estimate":
            avail_ram_gb,


            "m_score":
            m_score,


            "raw_potential":
            round(raw_potential,2),


            "cpu_load":
            cpu_load,


            "ram_load":
            ram_load,


            "combined_load":
            round(combined_load,2),


            "load_factor":
            load_factor,


            "battery_factor":
            battery_factor,


            "s_available":
            s_available

        }





        tier, models, recommendation = (

            ComputeScoreCalculator._classify_capability(

                s_available,

                avail_ram_gb

            )

        )






        return DeviceProfile(


            timestamp=timestamp_str,


            os_info=telemetry["system"],


            cpu_info=cpu,


            memory_info=mem,


            gpu_info=gpus,


            power_info=power,


            benchmark_info=benchmark,


            c_base_score=c_base,


            m_headroom_score=m_score,


            load_factor=load_factor,


            battery_factor=battery_factor,


            s_available=s_available,


            calculation_details=calculation_details,


            supported_tier=tier,


            suitable_models=models,


            routing_recommendation=recommendation

        )







    @staticmethod
    def _classify_capability(score, ram):


      if score >= 75 and ram >= 7:


        return (

            "Tier 3: Standard Local LLM Capable",

            [

                "Llama-3.1-8B-Q4",

                "Mistral-7B-Instruct-Q4",

                "Qwen2.5-7B-Instruct-Q4"

            ],

            "Strong edge capability for large local models"

        )



      elif score >= 45 and ram >= 3.5:


        return (

            "Tier 2: Compact SLM Capable",

            [

                "Llama-3.2-3B-Q4",

                "Phi-3.5-mini",

                "Gemma-2-2B",

                "Qwen2.5-1.5B"

            ],

            "Suitable for compact local AI models"

        )



      elif score >= 25 and ram >= 1.5:


        return (

            "Tier 1: Micro SLM Capable",

            [

                "Qwen2.5-0.5B",

                "SmolLM",

                "BERT classifiers"

            ],

            "Suitable for lightweight AI tasks"

        )



      else:


        return (

            "Tier 0: Cloud Offloading Recommended",

            [

                "Cloud API Models"

            ],

            "Device resource limited"

        )