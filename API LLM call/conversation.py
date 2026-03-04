class Conversation:
    """Keeps track of the back-and-forth messages."""

    def __init__(self):
        self.history: list[dict] = []

    def add_user_message(self, text: str):
        self.history.append({
            "role": "user",
            "parts": [{"text": text}],
        })

    def add_model_message(self, text: str):
        self.history.append({
            "role": "model",
            "parts": [{"text": text}],
        })

    def clear(self):
        self.history.clear()
        print("Conversation cleared.")

    def get_history(self) -> list[dict]:
        return self.history