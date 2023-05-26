from decimal import Decimal
import hashlib
import hmac

def ordinal_fmt(n):
    if n is None:
        return ''
    elif n % 10 == 1 and n % 100 != 11:
        suffix = 'st'
    elif (n % 10 == 2 and n % 100 != 12) or n % 100 == 72:
        suffix = 'nd'
    elif n % 10 == 3 and n % 100 != 13:
        suffix = 'rd'
    else:
        suffix = 'th'
    return str(n) + suffix

def money_fmt(number):
    quantized = number.quantize(Decimal('.01'))
    return f'${quantized:,.2f}'

def verify_signature(secret_token, signature_header, data):
    """Verify that the webhook payload was sent from GitHub by validating SHA256.

    Args:
        data: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    encoded_key = secret_token.encode()
    hash_object = hmac.new(encoded_key, msg=data, digestmod=hashlib.sha256)
    hash_algorithm, github_signature = signature_header.split('=', 1)
    return hmac.compare_digest(hash_object.hexdigest(), github_signature)
