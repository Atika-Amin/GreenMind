"""
Task Analysis Engine for GreenMind (Phase 2)

Analyzes:
- User intent
- Task category
- Domain complexity
- Reasoning depth
- Output requirement
- Token workload

Calculates Required Computational Score (S_req)
"""

import re

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple



@dataclass
class PromptComplexityProfile:

    prompt: str

    input_tokens: int
    estimated_output_tokens: int
    total_tokens: int


    task_category: str
    complexity_tier: str


    action_type: str


    c_task_score: float
    c_token_score: float
    k_struct_score: float


    s_required: float


    min_ram_gb: float
    min_compute_gflops: float


    target_model_tier: str
    recommended_models: List[str]


    calculation_details: Dict[str,Any]


    def to_dict(self):

        return asdict(self)





class PromptAnalyzer:


    ACTION_PATTERNS = {


        "design":[
            r"\bdesign\b",
            r"\bcreate\b",
            r"\bdevelop\b",
            r"\bbuild\b",
            r"\bpropose\b",
            r"\barchitect\b"
        ],


        "evaluation":[
            r"\bevaluate\b",
            r"\banalyze\b",
            r"\bassess\b",
            r"\bvalidate\b",
            r"\bbenchmark\b",
            r"\breview\b"
        ],


        "comparison":[
            r"\bcompare\b",
            r"\bdifference\b",
            r"\bversus\b",
            r"\bvs\b",
            r"\btrade.?off\b"
        ],


        "optimization":[
            r"\boptimize\b",
            r"\bimprove\b",
            r"\btune\b",
            r"\breduce latency\b",
            r"\baccelerate\b"
        ],


        "implementation":[
            r"\bimplement\b",
            r"\bcode\b",
            r"\bprogram\b",
            r"\bdevelop code\b",
            r"\bscript\b"
        ],


        "explanation":[
            r"\bexplain\b",
            r"\bdescribe\b",
            r"\bwhat is\b",
            r"\bhow does\b"
        ],


        "research":[
            r"\bresearch\b",
            r"\bliterature\b",
            r"\bpaper\b",
            r"\bsurvey\b"
        ],

        "writing": [

    r"\bwrite\b",
    r"\bdraft\b",
    r"\bcompose\b",
    r"\bcreate an email\b",
    r"\bwrite an email\b",
    r"\bmessage\b",
    r"\bletter\b",
    r"\bparagraph\b",
    r"\bpost\b"

       ]

    }



    DOMAIN_PATTERNS={


        "general":[
            r"\bgeneral\b"
        ],


        "programming":[
            r"\bpython\b",
            r"\bjava\b",
            r"\bc\+\+\b",
            r"\bcode\b",
            r"\bsoftware\b"
        ],


        "machine_learning":[
            r"\bmachine learning\b",
            r"\bml\b"
        ],


        "deep_learning":[
            r"\bdeep learning\b",
            r"\bneural network\b",
            r"\btransformer\b"
        ],


        "medical_ai":[
            r"\bmedical\b",
            r"\bhealthcare\b",
            r"\bclinical\b",
            r"\bdiagnosis\b"
        ],


        "system_design":[
            r"\bsystem architecture\b",
            r"\bdistributed system\b",
            r"\bmicroservice\b"
        ]

    }



    REASONING_MARKERS=[


        (r"\bstep.?by.?step\b",
         4,
         "Step reasoning"),


        (r"\bwhy\b",
         2,
         "Causal reasoning"),


        (r"\bderive\b",
         4,
         "Mathematical derivation"),


        (r"\bcompare\b",
         3,
         "Comparison reasoning"),


        (r"\btrade.?off\b",
         3,
         "Tradeoff analysis"),


        (r"\bconstraint\b",
         3,
         "Constraint handling")

    ]



    HEAVY_DOMAINS=[

        "deep_learning",
        "medical_ai",
        "system_design"

    ]

    def detect_action(self, prompt):

     text = prompt.lower()


     scores = {

        "writing":0,
        "summarization":0,
        "translation":0,
        "rewriting":0,
        "explanation":0,
        "evaluation":0,
        "comparison":0,
        "design":0,
        "implementation":0,
        "optimization":0,
        "research":0

    }



    # User request has higher priority than background content

     patterns = {


        "writing":[
            r"\bwrite\b",
            r"\bdraft\b",
            r"\bcompose\b",
            r"\bemail\b",
            r"\bletter\b"
        ],


        "summarization":[
            r"\bsummarize\b",
            r"\bsummary\b",
            r"\bshorten\b",
            r"\bkey points\b"
        ],


        "translation":[
            r"\btranslate\b",
            r"\btranslation\b"
        ],


        "rewriting":[
            r"\brewrite\b",
            r"\bparaphrase\b",
            r"\bpolish\b"
        ],


        "design":[
            r"\bdesign\b",
            r"\bcreate architecture\b",
            r"\bpropose model\b"
        ],


        "evaluation":[
            r"\bevaluate\b",
            r"\bassess\b",
            r"\bbenchmark\b"
        ],


        "optimization":[
            r"\boptimize\b",
            r"\bimprove\b",
            r"\btune\b"
        ],


        "implementation":[
            r"\bimplement\b",
            r"\bcode\b",
            r"\bprogram\b"
        ],


        "research":[
            r"\bresearch\b",
            r"\bsurvey\b"
        ],


        "comparison":[
            r"\bcompare\b",
            r"\bversus\b",
            r"\bvs\b"
        ],


        "explanation":[
            r"\bexplain\b",
            r"\bdescribe\b",
            r"\bwhat is\b"
        ]

     }



     for action, words in patterns.items():

        for word in words:

            if re.search(word,text):

                scores[action]+=1



     return max(
        scores,
        key=scores.get
     )




    def detect_domain(self,prompt):

        text = prompt.lower()


        detected=[]


        for domain,patterns in self.DOMAIN_PATTERNS.items():

            for pattern in patterns:

                if re.search(pattern,text):

                    detected.append(domain)

                    break



        return detected




    def estimate_tokens(self,prompt):

        words=len(prompt.split())


        return max(
            1,
            int(words*1.3)
        )




    def estimate_output_tokens(
            self,
            prompt,
            action
    ):

        text=prompt.lower()



        if action=="explanation":

            return 500



        if action=="evaluation":

            return 900



        if action=="design":

            return 1200



        if action=="implementation":

            return 1500



        if action=="optimization":

            return 1300



        if action=="research":

            return 2000



        if "brief" in text:

            return 300



        return 600





    def calculate_reasoning_score(self,prompt):

        score=0


        markers=[]


        text=prompt.lower()



        for pattern,value,name in self.REASONING_MARKERS:


            if re.search(pattern,text):

                score += value

                markers.append(name)



        return min(
            15,
            score
        ),markers





    def calculate_task_score(
            self,
            action
    ):


        scores={

    "writing":10,

    "summarization":15,

    "translation":10,

    "rewriting":15,

    "explanation":25,

    "evaluation":40,

    "comparison":45,

    "design":50,

    "implementation":55,

    "optimization":60,

    "research":60

}



        return scores.get(
            action,
            20
        )





    def calculate_domain_score(
            self,
            domains
    ):

        score=0


        mapping={


            "general":5,


            "programming":10,


            "machine_learning":15,


            "deep_learning":20,


            "medical_ai":25,


            "system_design":20


        }



        for d in domains:

            score=max(
                score,
                mapping.get(d,5)
            )


        return score





    def analyze(
            self,
            prompt
    ):



        action=self.detect_action(prompt)


        domains=self.detect_domain(prompt)



        input_tokens=self.estimate_tokens(prompt)



        output_tokens=self.estimate_output_tokens(
            prompt,
            action
        )



        total_tokens=input_tokens+output_tokens




        task_score=self.calculate_task_score(
            action
        )


        domain_score=self.calculate_domain_score(
            domains
        )


        reasoning_score,markers=\
            self.calculate_reasoning_score(prompt)




        token_score=min(
    5,
    total_tokens/1000
        )



        structural_score=min(
            15,
            reasoning_score
        )




        s_required=round(

            task_score
            +
            domain_score
            +
            token_score
            +
            structural_score,

            1

        )



        s_required=min(
            100,
            s_required
        )





        if s_required>=75:


            tier="Standard Local LLM (7B-8B)"


            models=[

                "Llama-3.1-8B-Q4",

                "Mistral-7B-Instruct-Q4",

                "Qwen2.5-7B-Instruct-Q4"

            ]


            ram=7

            compute=120




        elif s_required>=45:


            tier="Compact SLM (1.5B-3.8B)"


            models=[

                "Llama-3.2-3B-Q4",

                "Phi-3.5-mini",

                "Qwen2.5-1.5B"

            ]


            ram=3.5

            compute=50





        else:


            tier="Micro SLM"


            models=[

                "SmolLM",

                "TinyBERT"

            ]


            ram=1.5

            compute=20






        return PromptComplexityProfile(


            prompt=prompt,


            input_tokens=input_tokens,


            estimated_output_tokens=output_tokens,


            total_tokens=total_tokens,



            task_category=
            f"{action.title()} Task",



            complexity_tier=tier,


            action_type=action,



            c_task_score=task_score,


            c_token_score=round(
                token_score,
                2
            ),



            k_struct_score=structural_score,



            s_required=s_required,



            min_ram_gb=ram,


            min_compute_gflops=compute,



            target_model_tier=tier,


            recommended_models=models,



            calculation_details={

                "detected_domains":domains,

                "reasoning_markers":markers,

                "formula":
                "Task + Domain + Token + Reasoning"

            }


        )