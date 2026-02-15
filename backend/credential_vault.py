#!/usr/bin/env python3
"""
Credential Vault - Secure Encrypted Storage
AES-256-GCM encryption with Scrypt key derivation
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import sqlite3
from datetime import datetime

class CredentialVault:
    """Secure encrypted storage for sensitive credentials"""
    
    def __init__(self, master_password: str, db_path: str = "data/credentials.db"):
        """
        Initialize credential vault with master password
        
        Args:
            master_password: Master password for encryption/decryption
            db_path: Path to encrypted database
        """
        self.master_password = master_password
        self.db_path = db_path
        self._ensure_db()
        
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from master password using Scrypt"""
        kdf = Scrypt(
            salt=salt,
            length=32,  # 256 bits for AES-256
            n=16384,  # CPU/memory cost
            r=8,      # Block size
            p=1,      # Parallelization
            backend=default_backend()
        )
        return kdf.derive(self.master_password.encode())
    
    def _ensure_db(self):
        """Create database if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else "data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credential_type TEXT NOT NULL,
                identifier TEXT NOT NULL,
                encrypted_data BLOB NOT NULL,
                salt BLOB NOT NULL,
                nonce BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(credential_type, identifier)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def encrypt(self, data: str) -> tuple:
        """
        Encrypt data using AES-256-GCM
        
        Returns:
            tuple: (encrypted_data, salt, nonce)
        """
        # Generate random salt and nonce
        salt = os.urandom(16)
        nonce = os.urandom(12)  # 96 bits for GCM
        
        # Derive key from password
        key = self._derive_key(salt)
        
        # Encrypt data
        aesgcm = AESGCM(key)
        encrypted = aesgcm.encrypt(nonce, data.encode(), None)
        
        return encrypted, salt, nonce
    
    def decrypt(self, encrypted_data: bytes, salt: bytes, nonce: bytes) -> str:
        """
        Decrypt data using AES-256-GCM
        
        Returns:
            str: Decrypted data
        """
        # Derive key from password
        key = self._derive_key(salt)
        
        # Decrypt data
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, encrypted_data, None)
        
        return decrypted.decode()
    
    def store(self, credential_type: str, identifier: str, data: dict, metadata: dict = None):
        """
        Store encrypted credential
        
        Args:
            credential_type: Type (wallet, api_key, etc.)
            identifier: Unique identifier
            data: Sensitive data to encrypt
            metadata: Optional non-sensitive metadata
        """
        # Encrypt data
        encrypted_data, salt, nonce = self.encrypt(json.dumps(data))
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO credentials 
            (credential_type, identifier, encrypted_data, salt, nonce, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            credential_type,
            identifier,
            encrypted_data,
            salt,
            nonce,
            json.dumps(metadata) if metadata else None,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def retrieve(self, credential_type: str, identifier: str) -> dict:
        """Retrieve and decrypt credential"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT encrypted_data, salt, nonce, metadata 
            FROM credentials 
            WHERE credential_type = ? AND identifier = ?
        ''', (credential_type, identifier))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        encrypted_data, salt, nonce, metadata = result
        
        # Decrypt data
        decrypted_json = self.decrypt(encrypted_data, salt, nonce)
        data = json.loads(decrypted_json)
        
        # Add metadata if exists
        if metadata:
            data['metadata'] = json.loads(metadata)
        
        return data
    
    def list_credentials(self, credential_type: str = None) -> list:
        """List all credentials (metadata only, no decryption)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if credential_type:
            cursor.execute('''
                SELECT id, credential_type, identifier, metadata, created_at, updated_at
                FROM credentials 
                WHERE credential_type = ?
            ''', (credential_type,))
        else:
            cursor.execute('''
                SELECT id, credential_type, identifier, metadata, created_at, updated_at
                FROM credentials
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        credentials = []
        for row in results:
            credentials.append({
                'id': row[0],
                'type': row[1],
                'identifier': row[2],
                'metadata': json.loads(row[3]) if row[3] else {},
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        return credentials
    
    def delete(self, credential_type: str, identifier: str):
        """Delete credential"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM credentials 
            WHERE credential_type = ? AND identifier = ?
        ''', (credential_type, identifier))
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    # Example usage
    vault = CredentialVault("my_secure_master_password")
    
    # Store a wallet
    vault.store(
        "wallet",
        "my_eth_wallet",
        {
            "private_key": "0x1234567890abcdef...",
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        },
        metadata={"label": "Main Trading Wallet", "chain": "ethereum"}
    )
    
    # Retrieve wallet
    wallet = vault.retrieve("wallet", "my_eth_wallet")
    print(f"Retrieved wallet: {wallet['address']}")
    
    # List all wallets
    wallets = vault.list_credentials("wallet")
    print(f"Total wallets: {len(wallets)}")
