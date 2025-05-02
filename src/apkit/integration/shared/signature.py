from typing import Any, Optional

from ...config import Config

from apsig import ProofVerifier, LDSignature, KeyUtil
from apsig.exceptions import MissingSignature, VerificationFailed, UnknownSignature
from apsig.draft.verify import Verifier
from apmodel import Activity, Actor, Link, StreamsLoader
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

from ...actor.fetch import ActorGetter
from ...x.tools import get_keys
from ...exceptions import APTypeError


class SignatureLib:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.getter = ActorGetter(config=self.config)
        self.loader = StreamsLoader()

    async def __fetch_actor(self, activity: Activity):
        if isinstance(activity.actor, str):
            actor = await self.getter.fetch(url=activity.actor)
        elif isinstance(activity.actor, Link):
            actor = await self.getter.fetch(url=activity.actor.href)
        elif isinstance(activity.actor, Actor):
            actor = activity.actor
        else:
            raise Exception
        if actor and isinstance(actor, Actor):
            keys = await get_keys(actor)
            return keys
        return {}

    async def __get_signature_from_kv(self, key_id: str) -> tuple[Optional[str], bool]:
        cache = False
        public_key = await self.config.kv.get(f"signature:{key_id}")
        if public_key:
            self.config.logger.debug("Use existing cached keys")
            cache = True
        return public_key, cache

    def __get_draft_signature_parts(self, signature: str) -> dict[Any, Any]:
        signature_parts = {}
        for item in signature.split(","):
            key, value = item.split("=", 1)
            signature_parts[key.strip()] = value.strip().strip('"')
        return signature_parts

    async def __verify_draft(
        self, body, url, method, headers: dict, no_check_cache: bool = False
    ) -> bool:
        signature_header = headers.get("signature")
        if signature_header:
            signature_parts = self.__get_draft_signature_parts(signature_header)
            key_id = signature_parts.get("keyId")
            if not key_id:
                raise MissingSignature("keyId does not exist.")
            cache = False
            if not no_check_cache:
                public_key, cache = await self.__get_signature_from_kv(key_id)
            activity = self.loader.load(body)
            if isinstance(activity, Activity):
                if not cache:
                    public_keys = await self.__fetch_actor(activity)
                    public_key = public_keys.get(key_id)
                if public_key:
                    verifier = Verifier(public_key, method, url, headers, body)
                    try:
                        verifier.verify(raise_on_fail=True)
                        if isinstance(public_key, rsa.RSAPublicKey):
                            await self.config.kv.set(
                                f"signature:{key_id}",
                                public_key.public_bytes(
                                    serialization.Encoding.PEM,
                                    serialization.PublicFormat.SubjectPublicKeyInfo,
                                ),
                            )
                        return True
                    except Exception as e:
                        if not cache:
                            raise VerificationFailed(f"{str(e)}")
                        else:
                            return await self.__verify_draft(
                                body, url, method, headers, no_check_cache=True
                            )
                else:
                    raise VerificationFailed("publicKey does not exist.")
            else:
                raise APTypeError("unsupported model type")
        else:
            raise MissingSignature("this is not http signed activity.")

    async def __verify_proof(self, body: dict, no_check_cache: bool = False) -> bool:
        proof_key = body.get("proof")
        if isinstance(proof_key, dict):
            verification_method = proof_key.get("verificationMethod")
            if verification_method:
                activity = self.loader.load(body)
                cache = False
                if isinstance(activity, Activity):
                    if not no_check_cache:
                        public_key, cache = await self.__get_signature_from_kv(verification_method)
                    if not cache:
                        public_keys = await self.__fetch_actor(activity)
                        public_key = public_keys.get(verification_method)
                    if public_key:
                        proof = ProofVerifier(public_key)
                        try:
                            proof.verify(body)
                            if not cache:
                                if isinstance(public_key, ed25519.Ed25519PublicKey):
                                    ku = KeyUtil(public_key)
                                    await self.config.kv.set(
                                        f"signature:{verification_method}",
                                        ku.encode_multibase(),
                                    )
                            return True
                        except Exception as e:
                            if not cache:
                                raise VerificationFailed(f"{str(e)}")
                            else:
                                return await self.__verify_proof(
                                    body, no_check_cache=True
                                )
                    else:
                        raise VerificationFailed("publicKey does not exist.")
                else:
                    raise APTypeError("unsupported model type")
            else:
                raise MissingSignature("verificationMethod does not exist.")
        else:
            raise MissingSignature("this is not signed activity.")

    async def __verify_ld(self, body: dict, no_check_cache: bool = False) -> bool:
        ld = LDSignature()
        signature = body.get("signature")
        creator: Optional[str] = None
        if isinstance(signature, dict):
            creator: Optional[str] = signature.get("creator")
            if creator is None:
                raise MissingSignature("creator does not exist.")
        cache = False
        if not no_check_cache:
            if creator:
                public_key, cache = await self.__get_signature_from_kv(creator)
        activity = self.loader.load(body)
        if isinstance(activity, Activity):
            if not cache:
                public_keys = await self.__fetch_actor(activity)
                public_key = public_keys.get(creator)
            if public_key:
                try:
                    ld.verify(body, public_key, raise_on_fail=True)
                    if not cache:
                        if isinstance(public_key, rsa.RSAPublicKey):
                            await self.config.kv.set(
                                f"signature:{creator}",
                                public_key.public_bytes(
                                    serialization.Encoding.PEM,
                                    serialization.PublicFormat.SubjectPublicKeyInfo,
                                ),
                            )
                    return True
                except (UnknownSignature, MissingSignature, VerificationFailed) as e:
                    if not cache:
                        raise VerificationFailed(f"{str(e)}")
                    else:
                        return await self.__verify_ld(body, no_check_cache=True)
            else:
                raise VerificationFailed("publicKey does not exist.")
        else:
            raise APTypeError("unsupported model type")

    async def verify(self, body, url, method, headers: dict) -> bool:
        try:
            proof = await self.__verify_proof(body)
            if proof:
                return True
        except Exception as e:
            self.config.logger.debug(
                f"Object Integrity Proofs verification failed; {str(e)}"
            )
        try:
            ld = await self.__verify_ld(body)
            if ld:
                return True
        except Exception as e:
            pass
            self.config.logger.debug(f"LDSignature verification failed; {str(e)}")
        try:
            draft = await self.__verify_draft(body, url, method, headers)
            if draft:
                return True
        except Exception as e:
            self.config.logger.debug(
                f"Draft HTTP signature verification failed; {str(e)}"
            )
        return False
