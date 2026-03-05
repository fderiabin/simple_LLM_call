import json
import os
from datetime import datetime

class Conversation:
    """Keeps track of the back-and-forth messages."""

    SAVE_DIR = "conversations"

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
    
    def save(self):
        """Save conversation to a timestamped JSON file."""
        if not self.history:
            print("Nothing to save.")
            return
        
        os.makedirs(self.SAVE_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use the first user message as a preview in the filename
        first_msg = self.history[0]["parts"][0]["text"][:30]
        #Remove problematic characters from filename
        safe_msg = "".join(c if c.isalnum() or c in " -_" else "" for c in first_msg).strip()

        filename = f"{timestamp}_{safe_msg}.json"
        filepath = os.path.join(self.SAVE_DIR, filename)
        
        with open (filepath, "w", encoding='utf-8') as f:
            json.dump(self.history, f, indent = 2, ensure_ascii=False)

        print(f"Saved to {filepath}")

    def load(self):
        """List saved conversations and load one."""
        if not os.path.exists(self.SAVE_DIR):
            print("No saved conversations found.")
            return
        
        files = sorted(os.listdir(self.SAVE_DIR))
        json_files = [f for f in files if f.endswith(".json")]

        if not json_files:
            print("No saved convesations found.")
            return
        
        print("\nSaved Conversations:")
        for i, name in enumerate(json_files, start = 1):
            print(f"  {i}. {name}")

        choice = input("Enter number to load (or press Enter to cancel): ").strip()

        if not choice:
            return
        
        try:
            index = int(choice) - 1
            filepath = os.path.join(self.SAVE_DIR, json_files[index])
        except (ValueError, IndexError):
            print("Invalid choice.")
            return
        
        with open(filepath, "r", encoding="utf-8") as f:
            self.history = json.load(f)

        print(f"loaded {len(self.history)} messages from {json_files[index]}")