#!/usr/bin/env python3
import sys
import crypto
import os

def encrypt_value(value: str) -> str:
    key = os.getenv('SECRET_KEY', 'dev-secret-key')[:32]
    encrypted = crypto.encrypt(value, key)
    return f"ENC:{encrypted}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python encrypt_credentials.py <value_to_encrypt>")
        print("\nExample:")
        print("  python encrypt_credentials.py 'my-secret-token'")
        print("\nOutput will be prefixed with 'ENC:' for automatic decryption")
        sys.exit(1)
    
    value = sys.argv[1]
    encrypted = encrypt_value(value)
    
    print(f"\nEncrypted value:")
    print(encrypted)
    print("\nAdd this to your .env file or environment variables.")
    print("The system will automatically decrypt it when loaded.")

if __name__ == '__main__':
    main()
