import brotli
import json


def deocde_br(encoded_bytes: bytes, to_dict=False):
    decoded = brotli.decompress(encoded_bytes).decode('utf-8')
    if to_dict:
        return dict(json.loads(decoded))
    return decoded
