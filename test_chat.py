from chatbot import get_response

print("Agneyra AI Assistant (Local Test)")
print("Type 'exit' to stop.\n")

phone_number = "test_user"

while True:
    query = input("You: ")

    if query.lower() == "exit":
        break

    response = get_response(query, phone_number)

    print("Bot:", response)

 