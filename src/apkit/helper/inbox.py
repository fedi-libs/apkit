import json
import logging
from typing import Any, Optional

import apmodel
from apmodel import Activity
from apmodel.core.link import Link
from apmodel.vocab.actor import Actor
from apsig import KeyUtil, LDSignature, ProofVerifier
from apsig.draft.verify import Verifier
from apsig.exceptions import (
    MissingSignature,
    UnknownSignature,
    VerificationFailed,
)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from ..client.asyncio.client import ActivityPubClient
from ..config import AppConfig


class InboxVerifier:
    def __init__(self, config: AppConfig) -> None:
        self.logger = logging.getLogger("activitypub.server.inbox.helper")
        self.config = config

    async def __fetch_actor(self, activity: Activity) -> Optional[Actor]:
        async with ActivityPubClient() as client:
            match activity.actor:
                case str() as url:
                    actor = await client.actor.fetch(url=url)
                case Link(href=str() as url):
                    actor = await client.actor.fetch(url=url)
                case Actor() as actor_obj:
                    actor = actor_obj
                case _:
                    raise Exception("Invalid actor type")
            if actor and isinstance(actor, Actor):
                return actor
            return None

    def __get_draft_signature_parts(self, signature: str) -> dict[Any, Any]:
        signature_parts = {}
        for item in signature.split(","):
            key, value = item.split("=", 1)
            signature_parts[key.strip()] = value.strip().strip('"')
        return signature_parts

    async def __get_signature_from_kv(self, key_id: str) -> tuple[Optional[str], bool]:
        cache = False
        public_key = await self.config.kv.async_get(f"signature:{key_id}")
        if public_key:
            self.logger.debug("Use existing cached keys")
            cache = True
        return public_key, cache

    async def __verify_draft(
        self,
        body: bytes,
        url,
        method,
        headers: dict,
        no_check_cache: bool = False,
    ) -> bool:
        signature_header = headers.get("signature")
        body_json = json.loads(body)
        if signature_header:
            signature_parts = self.__get_draft_signature_parts(signature_header)
            key_id = signature_parts.get("keyId")
            if not key_id:
                raise MissingSignature("keyId does not exist.")
            cache = False
            public_key = None
            if not no_check_cache:
                public_key, cache = await self.__get_signature_from_kv(key_id)
            activity = apmodel.load(body_json)
            if isinstance(activity, Activity):
                if not cache:
                    public_keys = await self.__fetch_actor(activity)
                    if public_keys:
                        public_key = public_keys.get_key(key_id)
                    else:
                        public_key = None
                if (
                    public_key
                    and not isinstance(public_key, str)
                    and isinstance(public_key.public_key, RSAPublicKey)
                ):
                    verifier = Verifier(
                        public_key.public_key, method, url, headers, body
                    )
                    try:
                        verifier.verify(raise_on_fail=True)
                        if isinstance(public_key, rsa.RSAPublicKey):
                            await self.config.kv.async_set(
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
                raise ValueError("unsupported model type")
        else:
            raise MissingSignature("this is not http signed activity.")

    async def __verify_proof(self, body: bytes, no_check_cache: bool = False) -> bool:
        body_json = json.loads(body)
        proof_key = body_json.get("proof")

        if isinstance(proof_key, dict):
            verification_method = proof_key.get("verificationMethod")
            if verification_method:
                activity = apmodel.load(body_json)
                cache = False
                public_key = None
                if isinstance(activity, Activity):
                    if not no_check_cache:
                        public_key, cache = await self.__get_signature_from_kv(
                            verification_method
                        )
                    if not cache:
                        public_keys = await self.__fetch_actor(activity)
                        if public_keys:
                            public_key = public_keys.get_key(verification_method)
                    if (
                        public_key
                        and not isinstance(public_key, str)
                        and isinstance(public_key, Ed25519PublicKey)
                    ):
                        proof = ProofVerifier(public_key)
                        try:
                            proof.verify(body_json)
                            if not cache:
                                if isinstance(public_key, ed25519.Ed25519PublicKey):
                                    ku = KeyUtil(public_key)
                                    await self.config.kv.async_set(
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
                    raise ValueError("unsupported model type")
            else:
                raise MissingSignature("verificationMethod does not exist.")
        else:
            raise MissingSignature("this is not signed activity.")

    async def __verify_ld(self, body: bytes, no_check_cache: bool = False) -> bool:
        ld = LDSignature()
        body_json = json.loads(body)
        signature = body_json.get("signature")
        creator: Optional[str] = None
        if isinstance(signature, dict):
            creator: Optional[str] = signature.get("creator")
            if creator is None:
                raise MissingSignature("creator does not exist.")
        cache = False
        public_key = None
        if not no_check_cache:
            if creator:
                public_key, cache = await self.__get_signature_from_kv(creator)
        activity = apmodel.load(body_json)
        if isinstance(activity, Activity):
            if not cache:
                public_keys = await self.__fetch_actor(activity)
                if public_keys and creator:
                    public_key = public_keys.get_key(creator)
            if public_key:
                try:
                    public_key = (
                        public_key.public_key
                        if not isinstance(public_key, str)
                        else public_key
                    )
                    if public_key and not isinstance(public_key, Ed25519PublicKey):
                        ld.verify(body_json, public_key, raise_on_fail=True)
                        if not cache:
                            if isinstance(public_key, rsa.RSAPublicKey):
                                await self.config.kv.async_set(
                                    f"signature:{creator}",
                                    public_key.public_bytes(
                                        serialization.Encoding.PEM,
                                        serialization.PublicFormat.SubjectPublicKeyInfo,
                                    ),
                                )
                        return True
                    raise VerificationFailed("publicKey does not exist.")
                except (
                    UnknownSignature,
                    MissingSignature,
                    VerificationFailed,
                ) as e:
                    if not cache:
                        raise VerificationFailed(f"{str(e)}")
                    else:
                        return await self.__verify_ld(body, no_check_cache=True)
            else:
                raise VerificationFailed("publicKey does not exist.")
        else:
            raise ValueError("unsupported model type")

    async def verify(self, body: bytes, url, method, headers: dict) -> bool:
        try:
            proof = await self.__verify_proof(body)
            if proof:
                return True
        except Exception as e:
            self.logger.debug(f"Object Integrity Proofs verification failed; {str(e)}")
        try:
            ld = await self.__verify_ld(body)
            if ld:
                return True
        except Exception as e:
            self.logger.debug(f"LDSignature verification failed; {str(e)}")
        try:
            draft = await self.__verify_draft(body, url, method, headers)
            if draft:
                return True
        except Exception as e:
            self.logger.debug(f"Draft HTTP signature verification failed; {str(e)}")
        return False
