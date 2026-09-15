def classify_task(prompt):

    text = prompt.lower()


    categories = {

        "coding": [
            "code",
            "python",
            "java",
            "debug",
            "program"
        ],


        "summarization": [
            "summarize",
            "summary",
            "shorten",
            "overview"
        ],


        "analysis": [
            "analyze",
            "compare",
            "evaluate",
            "investigate"
        ],


        "design": [
            "design",
            "develop",
            "architecture",
            "create system"
        ],


        "translation": [
            "translate",
            "translation"
        ]

    }



    for task, keywords in categories.items():

        for keyword in keywords:

            if keyword in text:

                return task



    return "general"