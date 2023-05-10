"""Used to generate ids for messages sent to pinecone."""
import hashlib

def hash_message_to_sha_256(message):
    message = message.encode(encoding="ASCII", errors="ignore")
    return hashlib.sha256(bytes(message)).hexdigest()

