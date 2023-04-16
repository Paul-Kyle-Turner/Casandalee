import hashlib

# hash a message
def hash_message_sha_256(message):
    message = message.encode(encoding="ASCII", errors="ignore")
    return hashlib.sha256(bytes(message)).hexdigest()

# open a prompt
def get_prompt(file_name):
    with open(file_name) as open_file:
        return open_file.read()
    
def craft_prompt(prompt, message, rules, previous_messages):
    prompt = prompt.replace("<PREVIOUS_CONVERSATION>", previous_messages)
    prompt = prompt.replace("<MESSAGE>", message)
    return prompt.replace("<ADDITIONAL_INFORMATION>", rules)

def print_something():
    print("something")