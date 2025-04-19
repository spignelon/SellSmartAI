import base64

def safe_b64decode(s):
    """
    Safely decode a base64 string by adding padding if necessary
    """
    # Add padding '=' characters if the length is not a multiple of 4
    s_padded = s + "=" * (4 - len(s) % 4) if len(s) % 4 else s
    return base64.b64decode(s_padded)
