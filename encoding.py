import base64
from PyPDF2  import PdfReader, PdfWriter

import getpass

# Correct dictionary mapping
ENCODE_MAP = {
    16: base64.b16encode,
    32: base64.b32encode,
    64: base64.b64encode,
    85: base64.b85encode,
}

DECODE_MAP = {
    16: base64.b16decode,
    32: base64.b32decode,
    64: base64.b64decode,
    85: base64.b85decode,
}

def file_to_base(user_input, output_user, base_type=64):
    """Encodes a binary file into a base-encoded text file."""
    try:
        if base_type not in ENCODE_MAP:
            print(f"Unsupported base: {base_type}")
            return
        
        with open(user_input, "rb") as f:
            raw_bytes = f.read()

        encoded_bytes = ENCODE_MAP[base_type](raw_bytes)

        # Explicit keyword argument for text writing
        with open(output_user, "w", encoding="utf-8") as f:
            f.write(encoded_bytes.decode("utf-8"))

        print(f"Saved Base{base_type} text: {output_user}")
    except Exception as e:
        print(f"Error encoding file: {e}")


def base_to_file(user_input, output_user, base_type=64):
    """Decodes a base-encoded text file back into a binary file."""
    try:
        if base_type not in DECODE_MAP:
            print(f"Unsupported base: {base_type}")
            return
        
        with open(user_input, "r", encoding="utf-8") as f:
            raw_bytes = f.read().strip().encode("utf-8")

        # Base16 decode requires uppercase hex characters
        if base_type == 16:
            raw_bytes = raw_bytes.upper()

        decoded_bytes = DECODE_MAP[base_type](raw_bytes)

        # Binary mode does NOT use an encoding argument
        with open(output_user, "wb") as f:
            f.write(decoded_bytes)

        print(f"Saved binary file: {output_user}")
    except Exception as e:
        print(f"Error decoding file: {e}")


def file_to_base(user_input, output_user, base_type=64):
    """Encodes a binary file into a base-encoded text file."""
    try:
        if base_type not in ENCODE_MAP:
            print(f"Unsupported base: {base_type}")
            return
        
        with open(user_input, "rb") as f:
            raw_bytes = f.read()

        encoded_bytes = ENCODE_MAP[base_type](raw_bytes)

        # Explicit keyword argument for text writing
        with open(output_user, "w", encoding="utf-8") as f:
            f.write(encoded_bytes.decode("utf-8"))

        print(f"Saved Base{base_type} text: {output_user}")
    except Exception as e:
        print(f"Error encoding file: {e}")


def protect_pdf(user_input, output_user):
    try:

        reader = PdfReader(user_input)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)


        password = getpass.getpass("Enter Password : ")
        writer.encrypt(password, algorithm = "AES-256")
        with open(output_user,"wb") as output_file:
            writer.write(output_file)
        print(f"the pdf has password")

        print(f"Saved file: with password {output_user}")
    except Exception as e:
        print(f"Error encrypting file: {e}")


def unlock_pdf(user_input, output_user):
    try:

        reader = PdfReader(user_input)

        if not reader.is_encrypted:
            print("this pdf is not password protected")
            return 


        password = getpass.getpass("Enter Password : ")
        if not reader.decrypt(password,algorithm = "AES-256"):
            print("wrong password")
            return

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        with open(output_user,"wb") as output_file:
            writer.write(output_file)

        print(f"Unlocked file {output_user}")
    except Exception as e:
        print(f"Error unlocking file: {e}")
