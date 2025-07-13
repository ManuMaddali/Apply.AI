#!/usr/bin/env python3
"""
SSL/HTTPS Configuration for ApplyAI
Handles SSL certificate generation and HTTPS setup
"""

import os
import ssl
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSLConfig:
    """SSL Configuration Manager"""
    
    def __init__(self, cert_dir: str = "certs"):
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(exist_ok=True)
        
        # Certificate paths
        self.cert_file = self.cert_dir / "server.crt"
        self.key_file = self.cert_dir / "server.key"
        self.ca_cert_file = self.cert_dir / "ca.crt"
        
        # SSL context
        self.ssl_context = None
    
    def generate_self_signed_cert(self, 
                                 hostname: str = "localhost",
                                 days: int = 365) -> bool:
        """Generate self-signed SSL certificate"""
        
        try:
            # Generate private key
            key_cmd = [
                "openssl", "genrsa", 
                "-out", str(self.key_file), 
                "2048"
            ]
            
            subprocess.run(key_cmd, check=True, capture_output=True)
            logger.info(f"✅ Generated private key: {self.key_file}")
            
            # Generate certificate signing request
            csr_file = self.cert_dir / "server.csr"
            csr_cmd = [
                "openssl", "req", 
                "-new", "-key", str(self.key_file),
                "-out", str(csr_file),
                "-subj", f"/C=US/ST=State/L=City/O=ApplyAI/CN={hostname}"
            ]
            
            subprocess.run(csr_cmd, check=True, capture_output=True)
            logger.info(f"✅ Generated certificate signing request: {csr_file}")
            
            # Generate self-signed certificate
            cert_cmd = [
                "openssl", "x509", 
                "-req", "-days", str(days),
                "-in", str(csr_file),
                "-signkey", str(self.key_file),
                "-out", str(self.cert_file)
            ]
            
            subprocess.run(cert_cmd, check=True, capture_output=True)
            logger.info(f"✅ Generated self-signed certificate: {self.cert_file}")
            
            # Cleanup CSR file
            csr_file.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to generate SSL certificate: {e}")
            return False
    
    def generate_ca_cert(self, days: int = 365) -> bool:
        """Generate Certificate Authority certificate"""
        
        try:
            # Generate CA private key
            ca_key_file = self.cert_dir / "ca.key"
            ca_key_cmd = [
                "openssl", "genrsa", 
                "-out", str(ca_key_file), 
                "2048"
            ]
            
            subprocess.run(ca_key_cmd, check=True, capture_output=True)
            logger.info(f"✅ Generated CA private key: {ca_key_file}")
            
            # Generate CA certificate
            ca_cert_cmd = [
                "openssl", "req", 
                "-new", "-x509", "-days", str(days),
                "-key", str(ca_key_file),
                "-out", str(self.ca_cert_file),
                "-subj", "/C=US/ST=State/L=City/O=ApplyAI-CA/CN=ApplyAI-CA"
            ]
            
            subprocess.run(ca_cert_cmd, check=True, capture_output=True)
            logger.info(f"✅ Generated CA certificate: {self.ca_cert_file}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to generate CA certificate: {e}")
            return False
    
    def create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for HTTPS"""
        
        if not self.cert_file.exists() or not self.key_file.exists():
            logger.warning("⚠️  SSL certificates not found. Generating self-signed certificates...")
            if not self.generate_self_signed_cert():
                logger.error("❌ Failed to generate SSL certificates")
                return None
        
        try:
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(str(self.cert_file), str(self.key_file))
            
            # Security settings
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
            # Enable OCSP stapling and other security features
            context.check_hostname = False  # For self-signed certificates
            context.verify_mode = ssl.CERT_NONE  # For development
            
            self.ssl_context = context
            logger.info("✅ SSL context created successfully")
            return context
            
        except Exception as e:
            logger.error(f"❌ Failed to create SSL context: {e}")
            return None
    
    def get_uvicorn_ssl_config(self) -> dict:
        """Get SSL configuration for Uvicorn"""
        
        if not self.ssl_context:
            self.create_ssl_context()
        
        if not self.ssl_context:
            return {}
        
        return {
            "ssl_keyfile": str(self.key_file),
            "ssl_certfile": str(self.cert_file),
            "ssl_version": ssl.PROTOCOL_TLS_SERVER,
            "ssl_cert_reqs": ssl.CERT_NONE,
            "ssl_ca_certs": str(self.ca_cert_file) if self.ca_cert_file.exists() else None,
        }
    
    def validate_certificates(self) -> bool:
        """Validate SSL certificates"""
        
        if not self.cert_file.exists() or not self.key_file.exists():
            logger.error("❌ SSL certificate files not found")
            return False
        
        try:
            # Test certificate loading
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(str(self.cert_file), str(self.key_file))
            
            logger.info("✅ SSL certificates validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ SSL certificate validation failed: {e}")
            return False
    
    def get_cert_info(self) -> dict:
        """Get SSL certificate information"""
        
        if not self.cert_file.exists():
            return {"error": "Certificate file not found"}
        
        try:
            # Get certificate information
            cert_cmd = [
                "openssl", "x509", 
                "-in", str(self.cert_file),
                "-text", "-noout"
            ]
            
            result = subprocess.run(cert_cmd, capture_output=True, text=True, check=True)
            
            # Extract key information
            cert_text = result.stdout
            
            info = {
                "cert_file": str(self.cert_file),
                "key_file": str(self.key_file),
                "exists": True,
                "details": cert_text
            }
            
            return info
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to get certificate info: {e}")
            return {"error": str(e)}

# Global SSL configuration instance
ssl_config = SSLConfig()

def setup_https(hostname: str = "localhost", port: int = 8443) -> dict:
    """Setup HTTPS configuration"""
    
    logger.info(f"🔒 Setting up HTTPS for {hostname}:{port}")
    
    # Generate certificates if needed
    if not ssl_config.validate_certificates():
        logger.info("📋 Generating SSL certificates...")
        ssl_config.generate_self_signed_cert(hostname=hostname)
    
    # Create SSL context
    ssl_context = ssl_config.create_ssl_context()
    
    if ssl_context:
        logger.info("✅ HTTPS setup completed successfully")
        logger.info(f"🔗 Access your application at: https://{hostname}:{port}")
        logger.info("⚠️  Note: You may need to accept the self-signed certificate in your browser")
        
        return {
            "ssl_enabled": True,
            "ssl_config": ssl_config.get_uvicorn_ssl_config(),
            "hostname": hostname,
            "port": port,
            "url": f"https://{hostname}:{port}"
        }
    else:
        logger.error("❌ HTTPS setup failed")
        return {
            "ssl_enabled": False,
            "error": "Failed to create SSL context"
        }

if __name__ == "__main__":
    # Test SSL configuration
    print("🔒 Testing SSL Configuration")
    print("=" * 40)
    
    # Setup HTTPS
    result = setup_https()
    
    if result["ssl_enabled"]:
        print("✅ HTTPS setup successful!")
        print(f"🔗 URL: {result['url']}")
        
        # Show certificate info
        cert_info = ssl_config.get_cert_info()
        if "error" not in cert_info:
            print("📋 Certificate Information:")
            print(f"   📄 Certificate file: {cert_info['cert_file']}")
            print(f"   🔑 Key file: {cert_info['key_file']}")
        else:
            print(f"❌ Certificate info error: {cert_info['error']}")
    else:
        print("❌ HTTPS setup failed")
        print(f"Error: {result.get('error', 'Unknown error')}") 