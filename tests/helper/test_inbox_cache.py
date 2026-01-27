import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec
from apkit.config import AppConfig
from apkit.kv.inmemory import InMemoryKV
from apkit.helper.inbox import InboxVerifier

@pytest.fixture
def app_config():
    kv = InMemoryKV()
    return AppConfig(kv=kv)

@pytest.fixture
def verifier(app_config):
    return InboxVerifier(app_config)

@pytest.mark.asyncio
async def test_save_and_get_rsa_key_der(verifier, app_config):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    key_id = "https://example.com/actor#main-key"

    await verifier._InboxVerifier__save_signature_to_kv(key_id, public_key)

    stored_data = await app_config.kv.async_get(f"signature:{key_id}")
    assert isinstance(stored_data, bytes)
    
    loaded_key_direct = serialization.load_der_public_key(stored_data)
    assert isinstance(loaded_key_direct, rsa.RSAPublicKey)
    assert loaded_key_direct.public_numbers() == public_key.public_numbers()

    retrieved_key, is_cache = await verifier._InboxVerifier__get_signature_from_kv(key_id)
    
    assert is_cache is True
    assert isinstance(retrieved_key, rsa.RSAPublicKey)
    assert retrieved_key.public_numbers() == public_key.public_numbers()

@pytest.mark.asyncio
async def test_save_and_get_ed25519_key_der(verifier, app_config):
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    key_id = "https://example.com/actor#ed-key"

    await verifier._InboxVerifier__save_signature_to_kv(key_id, public_key)

    stored_data = await app_config.kv.async_get(f"signature:{key_id}")
    assert isinstance(stored_data, bytes)

    loaded_key_direct = serialization.load_der_public_key(stored_data)
    assert isinstance(loaded_key_direct, ed25519.Ed25519PublicKey)
    
    retrieved_key, is_cache = await verifier._InboxVerifier__get_signature_from_kv(key_id)

    assert is_cache is True
    assert isinstance(retrieved_key, ed25519.Ed25519PublicKey)
    assert retrieved_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ) == public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

@pytest.mark.asyncio
async def test_get_signature_invalid_data(verifier, app_config):
    key_id = "https://example.com/actor#invalid"
    
    await app_config.kv.async_set(f"signature:{key_id}", b"invalid-der-data")

    retrieved_key, is_cache = await verifier._InboxVerifier__get_signature_from_kv(key_id)
    
    assert retrieved_key is None
    assert is_cache is False

@pytest.mark.asyncio
async def test_get_signature_not_found(verifier):
    key_id = "https://example.com/actor#missing"
    
    retrieved_key, is_cache = await verifier._InboxVerifier__get_signature_from_kv(key_id)
    
    assert retrieved_key is None
    assert is_cache is False
