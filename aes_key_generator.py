import os

def generate_aes_key(key_length):
    return os.urandom(key_length // 8)

# Example: Generate a 256-bit (32-byte) AES key
aes_key = generate_aes_key(256)

if __name__ == "__main__":
    print("Generated AES Key:", aes_key)
