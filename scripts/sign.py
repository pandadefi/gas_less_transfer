from ape import Contract

from eth_utils import encode_hex
from eth_account._utils.structured_data.hashing import hash_domain
from eth_account.messages import encode_structured_data
from ape import accounts
from random import randbytes

CIRCLE = "0x55fe002aeff02f77364de339a1292923a15844b8"
VALID_AFTER = 0
VALID_BEFORE = 1663100000

def build_permit(holder, spender, token, random_bytes):
    data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "domain": {
            "name": token.name(),
            "version": token.version(),
            "chainId": 1,
            "verifyingContract": str(token),
        },
        "primaryType": "TransferWithAuthorization",
        "message": {
            "from": str(holder),
            "to": str(spender),
            "value": token.balanceOf(holder),
            "validAfter": VALID_AFTER,
            "validBefore": VALID_BEFORE,
            "nonce": random_bytes,
        },
    }
    assert hash_domain(data) == token.DOMAIN_SEPARATOR()
    return encode_structured_data(data)


def main():
    from_account = accounts.load("ledger")
    to = accounts[1]
    gas_spent_by = accounts[0]
    random_bytes = randbytes(32)

    usdc = Contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    usdc.transfer(from_account, 10**6, sender=accounts[CIRCLE])
    permit = build_permit(from_account, to, usdc, random_bytes)
    signature = from_account.sign_message(permit)
    print(signature.r)
    print(signature.s)
    print(signature.v)
    usdc.transferWithAuthorization(
        from_account,
        to,
        usdc.balanceOf(from_account),
        VALID_AFTER,
        VALID_BEFORE,
        random_bytes,
        signature.v,
        signature.r,
        signature.s,
        sender = gas_spent_by
    )
