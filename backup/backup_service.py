#!/usr/bin/env python3
"""
TTA Backup Service
Comprehensive backup and recovery system for TTA production environment
"""

import os
import sys
import time
import logging
import schedule
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
import redis
from neo4j import GraphDatabase
import psutil
from prometheus_client import start_http_server, Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/backup_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
backup_counter = Counter('tta_backups_total', 'Total number of backups performed', ['type', 'status'])
backup_duration = Histogram('tta_backup_duration_seconds', 'Time spent performing backups', ['type'])
backup_size = Gauge('tta_backup_size_bytes', 'Size of backup files', ['type'])
last_backup_timestamp = Gauge('tta_last_successful_backup_timestamp', 'Timestamp of last successful backup', ['type'])
backup_failures = Counter('tta_backup_failures_total', 'Total number of backup failures', ['type'])

class TTABackupService:
    """Comprehensive backup service for TTA production environment"""
    
    def __init__(self):
        self.config = self._load_config()
        self.s3_client = self._init_s3_client()
        self.redis_client = self._init_redis_client()
        self.neo4j_driver = self._init_neo4j_driver()
        
        # Backup directories
        self.neo4j_backup_dir = Path("/neo4j-backups")
        self.redis_backup_dir = Path("/redis-backups")
        self.logs_dir = Path("/app/logs")
        
        # Ensure directories exist
        for directory in [self.neo4j_backup_dir, self.redis_backup_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load configuration from environment variables"""
        return {
            'neo4j_uri': os.getenv('NEO4J_URI', 'bolt://neo4j:7687'),
            'neo4j_user': os.getenv('NEO4J_USER', 'neo4j'),
            'neo4j_password': os.getenv('NEO4J_PASSWORD', 'TTA_Neo4j_Prod_2024!'),
            'redis_host': os.getenv('REDIS_HOST', 'redis'),
            'redis_port': int(os.getenv('REDIS_PORT', '6379')),
            'redis_password': os.getenv('REDIS_PASSWORD', 'TTA_Redis_Prod_2024!'),
            's3_bucket': os.getenv('S3_BUCKET', 'tta-backups'),
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'backup_schedule': os.getenv('BACKUP_SCHEDULE', '0 2 * * *'),
            'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
            'compression_enabled': os.getenv('COMPRESSION_ENABLED', 'true').lower() == 'true',
            'encryption_enabled': os.getenv('ENCRYPTION_ENABLED', 'true').lower() == 'true'
        }
    
    def _init_s3_client(self):
        """Initialize S3 client for backup storage"""
        try:
            return boto3.client(
                's3',
                aws_access_key_id=self.config['aws_access_key_id'],
                aws_secret_access_key=self.config['aws_secret_access_key']
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            return None
    
    def _init_redis_client(self):
        """Initialize Redis client"""
        try:
            return redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                password=self.config['redis_password'],
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            return None
    
    def _init_neo4j_driver(self):
        """Initialize Neo4j driver"""
        try:
            return GraphDatabase.driver(
                self.config['neo4j_uri'],
                auth=(self.config['neo4j_user'], self.config['neo4j_password'])
            )
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            return None
    
    def backup_neo4j(self) -> bool:
        """Perform Neo4j database backup"""
        logger.info("Starting Neo4j backup...")
        
        with backup_duration.labels(type='neo4j').time():
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"neo4j_backup_{timestamp}"
                backup_path = self.neo4j_backup_dir / backup_name
                
                # Create backup using neo4j-admin
                cmd = [
                    'neo4j-admin', 'database', 'dump',
                    '--database=neo4j',
                    f'--to-path={backup_path}'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
                
                if result.returncode == 0:
                    # Compress backup if enabled
                    if self.config['compression_enabled']:
                        compressed_path = f"{backup_path}.tar.gz"
                        subprocess.run(['tar', '-czf', compressed_path, '-C', str(backup_path.parent), backup_path.name])
                        backup_path = Path(compressed_path)
                    
                    # Get backup size
                    backup_size_bytes = backup_path.stat().st_size
                    backup_size.labels(type='neo4j').set(backup_size_bytes)
                    
                    # Upload to S3 if configured
                    if self.s3_client:
                        self._upload_to_s3(backup_path, f"neo4j/{backup_path.name}")
                    
                    # Update metrics
                    backup_counter.labels(type='neo4j', status='success').inc()
                    last_backup_timestamp.labels(type='neo4j').set(time.time())
                    
                    logger.info(f"Neo4j backup completed successfully: {backup_path}")
                    return True
                else:
                    logger.error(f"Neo4j backup failed: {result.stderr}")
                    backup_failures.labels(type='neo4j').inc()
                    return False
                    
            except Exception as e:
                logger.error(f"Neo4j backup error: {e}")
                backup_failures.labels(type='neo4j').inc()
                return False
    
    def backup_redis(self) -> bool:
        """Perform Redis backup"""
        logger.info("Starting Redis backup...")
        
        with backup_duration.labels(type='redis').time():
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"redis_backup_{timestamp}.rdb"
                backup_path = self.redis_backup_dir / backup_name
                
                # Trigger Redis BGSAVE
                if self.redis_client:
                    self.redis_client.bgsave()
                    
                    # Wait for background save to complete
                    while self.redis_client.lastsave() == self.redis_client.lastsave():
                        time.sleep(1)
                    
                    # Copy RDB file
                    subprocess.run(['cp', '/data/dump.rdb', str(backup_path)])
                    
                    # Compress if enabled
                    if self.config['compression_enabled']:
                        compressed_path = f"{backup_path}.gz"
                        subprocess.run(['gzip', '-c', str(backup_path)], 
                                     stdout=open(compressed_path, 'wb'))
                        backup_path = Path(compressed_path)
                    
                    # Get backup size
                    backup_size_bytes = backup_path.stat().st_size
                    backup_size.labels(type='redis').set(backup_size_bytes)
                    
                    # Upload to S3 if configured
                    if self.s3_client:
                        self._upload_to_s3(backup_path, f"redis/{backup_path.name}")
                    
                    # Update metrics
                    backup_counter.labels(type='redis', status='success').inc()
                    last_backup_timestamp.labels(type='redis').set(time.time())
                    
                    logger.info(f"Redis backup completed successfully: {backup_path}")
                    return True
                else:
                    logger.error("Redis client not available")
                    backup_failures.labels(type='redis').inc()
                    return False
                    
            except Exception as e:
                logger.error(f"Redis backup error: {e}")
                backup_failures.labels(type='redis').inc()
                return False
    
    def _upload_to_s3(self, file_path: Path, s3_key: str) -> bool:
        """Upload backup file to S3"""
        try:
            logger.info(f"Uploading {file_path} to S3...")
            
            extra_args = {}
            if self.config['encryption_enabled']:
                extra_args['ServerSideEncryption'] = 'AES256'
            
            self.s3_client.upload_file(
                str(file_path),
                self.config['s3_bucket'],
                s3_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Successfully uploaded to S3: s3://{self.config['s3_bucket']}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Clean up old backup files based on retention policy"""
        logger.info("Cleaning up old backups...")
        
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        # Clean local backups
        for backup_dir in [self.neo4j_backup_dir, self.redis_backup_dir]:
            for backup_file in backup_dir.glob('*'):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file}")
        
        # Clean S3 backups if configured
        if self.s3_client:
            self._cleanup_s3_backups(cutoff_date)
    
    def _cleanup_s3_backups(self, cutoff_date: datetime):
        """Clean up old S3 backups"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.config['s3_bucket'])
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    self.s3_client.delete_object(
                        Bucket=self.config['s3_bucket'],
                        Key=obj['Key']
                    )
                    logger.info(f"Deleted old S3 backup: {obj['Key']}")
                    
        except ClientError as e:
            logger.error(f"S3 cleanup failed: {e}")
    
    def perform_full_backup(self):
        """Perform complete system backup"""
        logger.info("Starting full system backup...")
        
        success_count = 0
        total_backups = 2
        
        # Backup Neo4j
        if self.backup_neo4j():
            success_count += 1
        
        # Backup Redis
        if self.backup_redis():
            success_count += 1
        
        # Clean up old backups
        self.cleanup_old_backups()
        
        if success_count == total_backups:
            logger.info("Full backup completed successfully")
        else:
            logger.warning(f"Partial backup completed: {success_count}/{total_backups} successful")
    
    def health_check(self) -> Dict:
        """Perform health check and return status"""
        status = {
            'service': 'tta-backup-service',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check S3 connectivity
        if self.s3_client:
            try:
                self.s3_client.head_bucket(Bucket=self.config['s3_bucket'])
                status['checks']['s3'] = 'healthy'
            except Exception as e:
                status['checks']['s3'] = f'unhealthy: {e}'
                status['status'] = 'degraded'
        
        # Check Redis connectivity
        if self.redis_client:
            try:
                self.redis_client.ping()
                status['checks']['redis'] = 'healthy'
            except Exception as e:
                status['checks']['redis'] = f'unhealthy: {e}'
                status['status'] = 'degraded'
        
        # Check Neo4j connectivity
        if self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    session.run("RETURN 1")
                status['checks']['neo4j'] = 'healthy'
            except Exception as e:
                status['checks']['neo4j'] = f'unhealthy: {e}'
                status['status'] = 'degraded'
        
        return status
    
    def run(self):
        """Run the backup service"""
        logger.info("Starting TTA Backup Service...")
        
        # Start Prometheus metrics server
        start_http_server(8080)
        logger.info("Prometheus metrics server started on port 8080")
        
        # Schedule backups
        schedule.every().day.at("02:00").do(self.perform_full_backup)
        logger.info(f"Scheduled daily backups at 02:00")
        
        # Run initial backup
        self.perform_full_backup()
        
        # Main service loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Backup service shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in backup service: {e}")
                time.sleep(60)

if __name__ == "__main__":
    service = TTABackupService()
    service.run()
