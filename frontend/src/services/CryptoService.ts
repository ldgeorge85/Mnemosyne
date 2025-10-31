/**
 * Cryptographic Service - Client-Side Key Management
 *
 * Handles Ed25519 key generation and signing entirely client-side.
 * Private keys NEVER leave the browser - they are encrypted with a user passphrase.
 * Server only stores encrypted blobs and public keys.
 */

import * as ed from '@noble/ed25519';

interface KeyPairResult {
    publicKey: string; // Base64-encoded
    encryptedBlob: {
        algorithm: 'Ed25519';
        encryptedKey: string; // Base64-encoded AES-256-GCM encrypted private key
        salt: string; // Base64-encoded
        iv: string; // Base64-encoded
        iterations: number;
        encryption: 'AES-256-GCM';
    };
}

interface DecryptedKey {
    privateKey: Uint8Array;
    publicKey: Uint8Array;
}

export class CryptoService {
    private static instance: CryptoService;
    private cachedPassphrase: string | null = null;
    private passphraseTimeout: NodeJS.Timeout | null = null;

    private constructor() {}

    static getInstance(): CryptoService {
        if (!this.instance) {
            this.instance = new CryptoService();
        }
        return this.instance;
    }

    /**
     * Generate a new Ed25519 keypair client-side
     */
    async generateKeyPair(): Promise<KeyPairResult> {
        try {
            // Generate Ed25519 keypair (cryptographically secure)
            const privateKey = ed.utils.randomPrivateKey();
            const publicKey = await ed.getPublicKey(privateKey);

            // Get passphrase from user
            const passphrase = await this.promptForPassphrase(
                'Enter a passphrase to protect your signing key:',
                true
            );

            if (!passphrase || passphrase.length < 8) {
                throw new Error('Passphrase must be at least 8 characters');
            }

            // Generate random salt for key derivation
            const salt = crypto.getRandomValues(new Uint8Array(32));

            // Derive encryption key from passphrase using PBKDF2
            const encryptionKey = await this.deriveKey(passphrase, salt);

            // Generate random IV for AES-GCM
            const iv = crypto.getRandomValues(new Uint8Array(12));

            // Encrypt private key
            const encryptedPrivateKey = await this.encryptData(
                privateKey,
                encryptionKey,
                iv
            );

            // Clear sensitive data from memory
            privateKey.fill(0);

            // Return keys for server storage
            return {
                publicKey: this.base64Encode(publicKey),
                encryptedBlob: {
                    algorithm: 'Ed25519',
                    encryptedKey: this.base64Encode(encryptedPrivateKey),
                    salt: this.base64Encode(salt),
                    iv: this.base64Encode(iv),
                    iterations: 100000,
                    encryption: 'AES-256-GCM'
                }
            };
        } catch (error) {
            console.error('Key generation failed:', error);
            throw new Error(`Failed to generate keypair: ${error.message}`);
        }
    }

    /**
     * Sign data with user's private key (decrypted client-side)
     */
    async signData(data: string, encryptedBlob: any): Promise<string> {
        try {
            // Get passphrase (use cached if available and not expired)
            if (!this.cachedPassphrase) {
                this.cachedPassphrase = await this.promptForPassphrase(
                    'Enter your passphrase to sign:',
                    false
                );

                // Auto-clear passphrase after 5 minutes
                this.schedulePassphraseClear();
            }

            // Decrypt private key
            const privateKey = await this.decryptPrivateKey(
                encryptedBlob,
                this.cachedPassphrase
            );

            // Sign data
            const messageBytes = new TextEncoder().encode(data);
            const signature = await ed.sign(messageBytes, privateKey);

            // Clear private key from memory immediately
            privateKey.fill(0);

            return this.base64Encode(signature);
        } catch (error) {
            // Clear cached passphrase on error (might be wrong)
            this.clearPassphrase();
            console.error('Signing failed:', error);
            throw new Error(`Failed to sign data: ${error.message}`);
        }
    }

    /**
     * Verify a signature (public operation, no passphrase needed)
     */
    async verifySignature(
        publicKeyB64: string,
        message: string,
        signatureB64: string
    ): Promise<boolean> {
        try {
            const publicKey = this.base64Decode(publicKeyB64);
            const signature = this.base64Decode(signatureB64);
            const messageBytes = new TextEncoder().encode(message);

            return await ed.verify(signature, messageBytes, publicKey);
        } catch (error) {
            console.error('Signature verification failed:', error);
            return false;
        }
    }

    /**
     * Clear cached passphrase from memory
     */
    clearPassphrase(): void {
        if (this.cachedPassphrase) {
            // Overwrite with random data before clearing
            this.cachedPassphrase = crypto.getRandomValues(new Uint8Array(this.cachedPassphrase.length))
                .reduce((acc, val) => acc + String.fromCharCode(val), '');
            this.cachedPassphrase = null;
        }

        if (this.passphraseTimeout) {
            clearTimeout(this.passphraseTimeout);
            this.passphraseTimeout = null;
        }
    }

    // Private helper methods

    private schedulePassphraseClear(): void {
        if (this.passphraseTimeout) {
            clearTimeout(this.passphraseTimeout);
        }

        // Auto-clear after 5 minutes
        this.passphraseTimeout = setTimeout(() => {
            this.clearPassphrase();
            console.log('Passphrase cache cleared due to timeout');
        }, 5 * 60 * 1000);
    }

    private async promptForPassphrase(
        message: string,
        confirm: boolean
    ): Promise<string> {
        // In a real implementation, this would show a secure modal dialog
        // For now, using browser prompt (NOT secure for production)
        const passphrase = prompt(message);

        if (!passphrase) {
            throw new Error('Passphrase required');
        }

        if (confirm) {
            const confirmation = prompt('Confirm passphrase:');
            if (passphrase !== confirmation) {
                throw new Error('Passphrases do not match');
            }
        }

        return passphrase;
    }

    private async deriveKey(
        passphrase: string,
        salt: Uint8Array
    ): Promise<CryptoKey> {
        const encoder = new TextEncoder();

        // Import passphrase as key material
        const keyMaterial = await crypto.subtle.importKey(
            'raw',
            encoder.encode(passphrase),
            'PBKDF2',
            false,
            ['deriveKey']
        );

        // Derive AES-GCM key from passphrase
        return crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: salt,
                iterations: 100000,
                hash: 'SHA-256'
            },
            keyMaterial,
            {
                name: 'AES-GCM',
                length: 256
            },
            false,
            ['encrypt', 'decrypt']
        );
    }

    private async encryptData(
        data: Uint8Array,
        key: CryptoKey,
        iv: Uint8Array
    ): Promise<Uint8Array> {
        const encrypted = await crypto.subtle.encrypt(
            {
                name: 'AES-GCM',
                iv: iv
            },
            key,
            data
        );

        return new Uint8Array(encrypted);
    }

    private async decryptPrivateKey(
        encryptedBlob: any,
        passphrase: string
    ): Promise<Uint8Array> {
        // Decode salt and IV
        const salt = this.base64Decode(encryptedBlob.salt);
        const iv = this.base64Decode(encryptedBlob.iv);
        const encryptedKey = this.base64Decode(encryptedBlob.encryptedKey);

        // Derive decryption key from passphrase
        const decryptionKey = await this.deriveKey(passphrase, salt);

        // Decrypt private key
        const decrypted = await crypto.subtle.decrypt(
            {
                name: 'AES-GCM',
                iv: iv
            },
            decryptionKey,
            encryptedKey
        );

        return new Uint8Array(decrypted);
    }

    private base64Encode(data: Uint8Array): string {
        return btoa(String.fromCharCode(...data));
    }

    private base64Decode(str: string): Uint8Array {
        return Uint8Array.from(atob(str), c => c.charCodeAt(0));
    }
}

// Export singleton instance
export const cryptoService = CryptoService.getInstance();
