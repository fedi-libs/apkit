import base64
import datetime as dt
import email.utils
import json
from typing import Any, List, Tuple, cast

import pytz
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
from http_sf import parse
from http_sf.types import (
    BareItemType,
    InnerListType,
    ItemType,
    ParamsType,
)
from multiformats import multibase, multicodec

from apsig.draft.tools import calculate_digest
from apsig.exceptions import MissingSignature, VerificationFailed


class RFC9421Signer:
    def __init__(self, private_key: rsa.RSAPrivateKey, key_id: str):
        self.private_key = private_key
        self.key_id = key_id
        self.sign_headers = [
            "date",
            "@method",
            "@path",
            "@authority",
            "content-type",
            "content-length",
        ]

    def __build_signature_base(
        self, special_keys: dict[str, str], headers: dict[str, str]
    ) -> bytes:
        headers_new = []
        headers = headers.copy()
        for h in self.sign_headers:
            if h in ["@method", "@path", "@authority"]:
                v = special_keys.get(h)

                if v:
                    headers_new.append(f'"{h}": {v}')
                else:
                    raise ValueError(f"Missing Value: {h}")
            elif h == "@signature-params":
                v = special_keys.get(h)

                if v:
                    headers_new.append(f'"{h}": {self.__generate_sig_input()}')
                else:
                    raise ValueError(f"Missing Value: {h}")
            else:
                v_raw = headers.get(h)
                if v_raw is not None:
                    v = v_raw.strip()
                    headers_new.append(f'"{h}": {v}')
                else:
                    raise ValueError(f"Missing Header Value: {h}")
        headers_new.append(f'"@signature-params": {self.__generate_sig_input()}')
        return ("\n".join(headers_new)).encode("utf-8")

    def generate_signature_header(self, signature: bytes) -> str:
        return base64.b64encode(signature).decode("utf-8")

    def __generate_sig_input(self):
        param = "("
        target_len = len(self.sign_headers)
        timestamp = dt.datetime.now(dt.UTC)
        for p in self.sign_headers:
            param += f'"{p}"'
            if p != self.sign_headers[target_len - 1]:
                param += " "
        param += ");"
        param += f"created={int(timestamp.timestamp())};"
        param += 'alg="rsa-v1_5-sha256";'
        param += f'keyid="{self.key_id}"'
        return param

    def sign(
        self,
        method: str,
        path: str,
        host: str,
        headers: dict,
        body: bytes | dict = b"",
    ):
        if isinstance(body, dict):
            body = json.dumps(body).encode("utf-8")

        headers = {k.lower(): v for k, v in headers.items()}
        if not headers.get("date"):
            headers["date"] = email.utils.formatdate(usegmt=True)
        if not headers.get("content-length"):
            headers["content-length"] = str(len(body))

        special_keys = {
            "@method": method.upper(),
            "@path": path,
            "@authority": host,
        }

        base = self.__build_signature_base(special_keys, headers)
        signed = self.private_key.sign(base, padding.PKCS1v15(), hashes.SHA256())
        headers_req = headers.copy()
        headers_req["Signature"] = f"sig1=:{self.generate_signature_header(signed)}:"
        headers_req["content-digest"] = f"sha-256=:{calculate_digest(body)}:"
        headers_req["Signature-Input"] = f"sig1={self.__generate_sig_input()}"
        return headers_req


class RFC9421Verifier:
    def __init__(
        self,
        public_key: ed25519.Ed25519PublicKey
        | rsa.RSAPublicKey
        | ec.EllipticCurvePublicKey
        | str,
        method: str,
        path: str,
        host: str,
        headers: dict[str, str],
        body: bytes | dict | None = None,
        clock_skew: int = 300,
    ):
        self.public_key: (
            ed25519.Ed25519PublicKey | rsa.RSAPublicKey | ec.EllipticCurvePublicKey
        )

        if isinstance(public_key, str):
            codec, data = multicodec.unwrap(multibase.decode(public_key))
            match codec.name:
                case "ed25519-pub":
                    self.public_key: ed25519.Ed25519PublicKey = (
                        ed25519.Ed25519PublicKey.from_public_bytes(data)
                    )
                case "rsa-pub":
                    pubkey = serialization.load_pem_public_key(data)
                    if not isinstance(pubkey, rsa.RSAPublicKey):
                        raise TypeError("PublicKey must be ed25519 or RSA or ECDSA.")
                    self.public_key = pubkey
                case "p256-pub":
                    pubkey = serialization.load_pem_public_key(data)
                    if not isinstance(pubkey, ec.EllipticCurvePublicKey):
                        raise TypeError("PublicKey must be ed25519 or RSA or ECDSA.")
                    self.public_key = pubkey
                case "p384-pub":
                    pubkey = serialization.load_pem_public_key(data)
                    if not isinstance(pubkey, ec.EllipticCurvePublicKey):
                        raise TypeError("PublicKey must be ed25519 or RSA or ECDSA.")
                    self.public_key = pubkey
                case _:
                    raise TypeError("PublicKey must be ed25519 or RSA or ECDSA.")
        else:
            self.public_key: ed25519.Ed25519PublicKey | rsa.RSAPublicKey = public_key
        self.clock_skew = clock_skew
        self.method = method.upper()
        self.path = path
        self.host = host
        self.headers = {key.lower(): value for key, value in headers.items()}

    def __expect_value_and_params_member(
        self,
        member: Any,
    ) -> Tuple[ItemType | InnerListType, ParamsType]:
        if not isinstance(member, tuple) or len(member) != 2:
            raise ValueError("expected a (value, params) tuple")
        value, params = member
        if not isinstance(params, dict):
            raise ValueError("expected params to be a dict")
        return cast(Tuple[ItemType | InnerListType, ParamsType], (value, params))

    def __generate_sig_input(
        self, headers: List[BareItemType], params: ParamsType
    ) -> str:
        created = params.get("created")
        alg = params.get("alg")
        keyid = params.get("keyid")

        if isinstance(created, dt.datetime):
            created_timestamp = created
        elif isinstance(created, int):
            created_timestamp = dt.datetime.fromtimestamp(created)
        elif isinstance(created, str):
            created_timestamp = dt.datetime.fromtimestamp(int(created))
        else:
            raise ValueError("Unknown created value")
        request_time = created_timestamp.astimezone(pytz.utc)
        current_time = dt.datetime.now(dt.UTC)
        if abs((current_time - request_time).total_seconds()) > self.clock_skew:
            raise VerificationFailed(
                f"property created is too far from current time ({current_time}): {request_time}"
            )

        param = "("
        target_len = len(headers)
        for p in headers:
            param += f'"{p}"'
            if p != headers[target_len - 1]:
                param += " "
        param += ");"
        param += f"created={int(created_timestamp.timestamp())};"
        param += f'alg="{alg}";'
        param += f'keyid="{keyid}"'
        return param

    def __rebuild_sigbase(
        self, headers: List[BareItemType], params: ParamsType
    ) -> bytes:
        special_keys = {
            "@method": self.method,
            "@path": self.path,
            "@authority": self.host,
        }
        base = []
        for h in cast(List[str], headers):
            if h in ["@method", "@path", "@authority"]:
                base.append(f'"{h}": {special_keys.get(h)}')
            else:
                v_raw = self.headers.get(h)
                if v_raw is not None:
                    v = v_raw.strip()
                    base.append(f'"{h}": {v}')
                else:
                    raise ValueError(f"Missing Header Value: {h}")
        base.append(
            f'"@signature-params": {self.__generate_sig_input(headers=headers, params=params)}'
        )
        return ("\n".join(base)).encode("utf-8")

    def verify(self, raise_on_fail: bool = False) -> str | None:
        signature = self.headers.get("signature")
        if not signature:
            if raise_on_fail:
                raise MissingSignature("Signature header is missing")
            return None

        signature_input = self.headers.get("signature-input")
        if not signature_input:
            if raise_on_fail:
                raise MissingSignature("Signature-Input header is missing")
            return None

        signature_input_parsed = parse(
            signature_input.encode("utf-8"), tltype="dictionary"
        )
        signature_parsed = parse(signature.encode("utf-8"), tltype="dictionary")

        if not isinstance(signature_input_parsed, dict):
            raise VerificationFailed(
                f"Unsupported Signature-Input type: {type(signature_input_parsed)}"
            )

        if not isinstance(signature_parsed, dict):
            raise VerificationFailed(
                f"Unsupported Signature type: {type(signature_parsed)}"
            )

        for k, v in signature_input_parsed.items():
            try:
                value, params = self.__expect_value_and_params_member(v)
                if isinstance(value, list):
                    headers: List[BareItemType] = [
                        itm[0] if isinstance(itm, tuple) else itm for itm in value
                    ]
                else:
                    raise ValueError(
                        "expected the value to be an inner-list (list of items)"
                    )

                created = params.get("created")
                key_id = str(params.get("keyid"))
                alg = params.get("alg")

                if not created:
                    raise VerificationFailed("created not found.")
                if not key_id:
                    raise VerificationFailed("keyid not found.")
                if not alg:
                    raise VerificationFailed("alg not found.")
                if alg not in [
                    "ed25519",
                    "rsa-v1_5-sha256",
                    "rsa-v1_5-sha512",
                    "rsa-pss-sha512",
                ]:
                    raise VerificationFailed(f"Unsupported algorithm: {alg}")

                sigi = self.__rebuild_sigbase(headers, params)
                signature_bytes = signature_parsed.get(k)
                if not isinstance(signature_bytes, tuple):
                    raise VerificationFailed(
                        f"Unknown Signature: {type(signature_bytes)}"
                    )

                sig_val = None
                for sig in cast(InnerListType, signature_bytes):
                    if isinstance(sig, bytes):
                        sig_val = sig
                        break
                if sig_val is None:
                    raise ValueError("No Signature found.")
                try:
                    match alg:
                        case "ed25519":
                            if not isinstance(
                                self.public_key, ed25519.Ed25519PublicKey
                            ):
                                raise VerificationFailed("Algorithm missmatch.")
                            self.public_key.verify(sig_val, sigi)
                        case "rsa-v1_5-sha256":
                            if not isinstance(self.public_key, rsa.RSAPublicKey):
                                raise VerificationFailed("Algorithm missmatch.")
                            self.public_key.verify(
                                sig_val,
                                sigi,
                                padding.PKCS1v15(),
                                hashes.SHA256(),
                            )
                        case "rsa-v1_5-sha512":
                            if not isinstance(self.public_key, rsa.RSAPublicKey):
                                raise VerificationFailed("Algorithm missmatch.")
                            self.public_key.verify(
                                sig_val,
                                sigi,
                                padding.PKCS1v15(),
                                hashes.SHA512(),
                            )
                        case "rsa-pss-sha512":
                            if not isinstance(self.public_key, rsa.RSAPublicKey):
                                raise VerificationFailed("Algorithm missmatch.")
                            self.public_key.verify(
                                sig_val,
                                sigi,
                                padding.PSS(
                                    mgf=padding.MGF1(hashes.SHA512()),
                                    salt_length=hashes.SHA512().digest_size,
                                ),
                                hashes.SHA512(),
                            )
                        case "ecdsa-p256-sha256":
                            if not isinstance(
                                self.public_key, ec.EllipticCurvePublicKey
                            ):
                                raise VerificationFailed("Algorithm missmatch.")
                            self.public_key.verify(
                                sig_val,
                                sigi,
                                ec.ECDSA(hashes.SHA256()),
                            )
                        case "ecdsa-p384-sha384":
                            if not isinstance(
                                self.public_key, ec.EllipticCurvePublicKey
                            ):
                                raise VerificationFailed("Algorithm missmatch.")
                            self.public_key.verify(
                                sig_val,
                                sigi,
                                ec.ECDSA(hashes.SHA384()),
                            )
                    return key_id
                except Exception as e:
                    if raise_on_fail:
                        raise VerificationFailed(str(e))
                    return None
            except ValueError:
                continue

        if raise_on_fail:
            raise VerificationFailed("RFC9421 Signature verification failed.")
        return None
