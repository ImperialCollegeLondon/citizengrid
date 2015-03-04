from Crypto.Cipher import AES
from citizengrid import DATA_K
import bz2
import base64


PADDING = '{'
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING


def decrypt_cred(encrypted_cred):
    """
    decrypts credentials
    :param encrypted_cred:
    :return: decrypted_cred
    """
    key = base64.decodestring(bz2.decompress(base64.decodestring(DATA_K)))

    cipher = AES.new(key, AES.MODE_CBC, "enw4d2e3w66dugh2")
    decoded_cred = base64.decodestring(encrypted_cred)
    decrypted_cred = cipher.decrypt(decoded_cred)
    decrypted_cred = decrypted_cred.rstrip(PADDING)

    return decrypted_cred


def decrypt_cred_pair(encrypted_access_cred, encrypted_secret_cred):
    """
    decrypts credential pairs, using AES.MODE_CBS
    :param encrypted_access_cred:
    :param encrypted_secret_cred:
    :return: (decrypted_access_cred, decrypted_secret_cred)
    """
    key = base64.decodestring(bz2.decompress(base64.decodestring(DATA_K)))

    cipher = AES.new(key, AES.MODE_CBC, "enw4d2e3w66dugh2")
    decoded_cred = base64.decodestring(encrypted_access_cred)
    decrypted_access_cred = cipher.decrypt(decoded_cred)
    decrypted_access_cred = decrypted_access_cred.rstrip(PADDING)

    decoded_cred = base64.decodestring(encrypted_secret_cred)
    decrypted_secret_cred = cipher.decrypt(decoded_cred)
    decrypted_secret_cred = decrypted_secret_cred.rstrip(PADDING)

    return(decrypted_access_cred, decrypted_secret_cred)
