def estimate_tokens(prompt):

    words = len(prompt.split())

    tokens = int(words * 1.3)

    return tokens