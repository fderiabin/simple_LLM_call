import logging
from conversation import Conversation
from llm_client import send_message_stream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    print("Gemini Chat")
    print("Commands: 'quit', 'clear', '/save', '/load'\n")
    convo = Conversation()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "clear":
            convo.clear()
            continue
        if user_input.lower() == "/save":
            convo.save()
            continue
        if user_input.lower() == "/load":
            convo.load()
            continue

        convo.add_user_message(user_input)

        print("Gemini: ", end="", flush=True)
        reply = send_message_stream(convo.get_history())
        convo.add_model_message(reply)
        print()



if __name__ == "__main__":
    main()