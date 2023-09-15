import random
import string

def generate_password(length, include_lowercase, include_uppercase, include_digits, include_special_chars):
    chars = ''
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_special_chars:
        chars += string.punctuation

    if len(chars) == 0:
        print("Please select at least one character type.")
        return None

    password = ''.join(random.choice(chars) for _ in range(length))
    return password

def generate_dictionary():
    # Create a dictionary file with common English words
    common_words = [
        "apple", "banana", "cherry", "dog", "elephant", "flower", "grape", "happy", "ice", "juice", "king", "lemon",
        "mango", "night", "orange", "penguin", "queen", "rose", "strawberry", "tree", "umbrella", "violet", "water", "xylophone", "yellow", "zebra"
    ]

    with open('dictionary.txt', 'w') as f:
        f.write('\n'.join(common_words))

def main():
    print("Advanced Password Generator")

    length = int(input("Enter the desired password length: "))

    include_lowercase = input("Include lowercase letters? (y/n): ").strip().lower() == 'y'
    include_uppercase = input("Include uppercase letters? (y/n): ").strip().lower() == 'y'
    include_digits = input("Include digits? (y/n): ").strip().lower() == 'y'
    include_special_chars = input("Include special characters? (y/n): ").strip().lower() == 'y'

    # Additional options
    include_similar_chars = input("Include similar characters (e.g., 'I', 'l', '1', 'O', '0')? (y/n): ").strip().lower() == 'y'
    exclude_ambiguous_chars = input("Exclude ambiguous characters (e.g., '{}'/'{}', '{}'/'{}')? (y/n): ".format('l', '1', 'O', '0')).strip().lower() == 'y'

    if exclude_ambiguous_chars:
        chars = ''.join(filter(lambda c: c not in 'l1O0', string.ascii_letters + string.digits + string.punctuation))
        if not chars:
            print("Excluding ambiguous characters results in an empty character set. Please include more character types.")
            return
    else:
        chars = string.ascii_letters + string.digits + string.punctuation

    password = generate_password(length, include_lowercase, include_uppercase, include_digits, include_special_chars)

    if include_similar_chars:
        while all(c in 'Il10Oo' for c in password):
            password = generate_password(length, include_lowercase, include_uppercase, include_digits, include_special_chars)

    generate_dictionary()  # Create the dictionary file

    # Additional options
    exclude_dictionary_words = input("Exclude dictionary words? (y/n): ").strip().lower() == 'y'
    max_char_repeat = int(input("Maximum character repetition (0 for no restriction): "))

    if exclude_dictionary_words:
        # Load the created dictionary file and filter out words
        with open('dictionary.txt', 'r') as f:
            dictionary_words = set(word.strip().lower() for word in f.readlines())
        while password.lower() in dictionary_words:
            password = generate_password(length, include_lowercase, include_uppercase, include_digits, include_special_chars)

    if max_char_repeat > 0:
        # Check for character repetition
        repeated_chars = set()
        for char in password:
            if password.count(char) > max_char_repeat:
                repeated_chars.add(char)
        while repeated_chars:
            password = generate_password(length, include_lowercase, include_uppercase, include_digits, include_special_chars)
            repeated_chars = {char for char in password if password.count(char) > max_char_repeat}

    print("Generated Password:", password)

if __name__ == '__main__':
    main()
