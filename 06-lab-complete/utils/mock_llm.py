"""
Mock LLM used by the final Day 12 lab.
Keeps the lab self-contained so it can run and build from this folder alone.
"""
import random
import time


MOCK_RESPONSES = {
    "default": [
        "Day 12 final agent is responding with a mock answer while local deployment is being validated.",
        "The production-ready lab agent is up and handling your request with the bundled mock LLM.",
        "Your question reached the deployed-style agent successfully. This is a mock response for the lab.",
    ],
    "docker": ["Docker packages the app and its dependencies so the same build runs consistently across environments."],
    "deploy": ["Deployment publishes your application to a server or platform so other users can access it."],
    "health": ["The service reports healthy and ready to accept traffic."],
    "redis": ["Redis helps the app stay stateless by storing shared state outside individual processes."],
}


def ask(question: str, delay: float = 0.1) -> str:
    """Return a short mock response with a small delay to simulate LLM latency."""
    time.sleep(delay + random.uniform(0, 0.05))

    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)

    return random.choice(MOCK_RESPONSES["default"])


def ask_stream(question: str):
    """Yield a mock response word by word."""
    response = ask(question)
    for word in response.split():
        time.sleep(0.05)
        yield word + " "
