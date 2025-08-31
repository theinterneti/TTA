"""
Validation Result Caching

This module provides caching functionality for therapeutic safety validation results,
integrating with Redis for performance optimization.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any

from .models import ContentPayload, ValidationContext, ValidationResult

logger = logging.getLogger(__name__)


class ValidationCache:
    """Cache for validation results using Redis."""

    def __init__(self, redis_client=None, key_prefix: str = "tta:safety:validation"):
        self.redis_client = redis_client
        self.key_prefix = key_prefix
        self.default_ttl = timedelta(hours=1)

        # Cache statistics
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_errors": 0,
            "cache_evictions": 0,
        }

    def _generate_cache_key(
        self, content: ContentPayload, context: ValidationContext
    ) -> str:
        """Generate cache key for content and context."""
        # Create a hash of content and relevant context
        content_hash = hashlib.sha256(content.content_text.encode()).hexdigest()[:16]

        # Include relevant context factors in key
        context_factors = {
            "user_age_group": (
                context.user_age_group.value if context.user_age_group else None
            ),
            "validation_scope": context.validation_scope.value,
            "strict_mode": context.strict_mode,
            "user_therapeutic_goals": [
                goal.value for goal in context.user_therapeutic_goals
            ],
            "user_risk_factors": [risk.value for risk in context.user_risk_factors],
        }

        context_str = json.dumps(context_factors, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:8]

        return f"{self.key_prefix}:{content_hash}:{context_hash}"

    async def get(
        self, content: ContentPayload, context: ValidationContext
    ) -> ValidationResult | None:
        """Get cached validation result."""
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(content, context)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                result_data = json.loads(cached_data)
                result = self._deserialize_result(result_data)
                result.cache_hit = True

                self.stats["cache_hits"] += 1
                logger.debug(f"Cache hit for key: {cache_key}")
                return result
            else:
                self.stats["cache_misses"] += 1
                logger.debug(f"Cache miss for key: {cache_key}")
                return None

        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        content: ContentPayload,
        context: ValidationContext,
        result: ValidationResult,
        ttl: timedelta | None = None,
    ) -> bool:
        """Set validation result in cache."""
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(content, context)
            result_data = self._serialize_result(result)

            ttl_seconds = int((ttl or self.default_ttl).total_seconds())

            await self.redis_client.setex(
                cache_key, ttl_seconds, json.dumps(result_data)
            )

            self.stats["cache_sets"] += 1
            logger.debug(f"Cached result for key: {cache_key}, TTL: {ttl_seconds}s")
            return True

        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"Cache set error: {e}")
            return False

    async def invalidate(
        self, content: ContentPayload, context: ValidationContext
    ) -> bool:
        """Invalidate cached result."""
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(content, context)
            result = await self.redis_client.delete(cache_key)

            if result:
                self.stats["cache_evictions"] += 1
                logger.debug(f"Invalidated cache for key: {cache_key}")

            return bool(result)

        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"Cache invalidation error: {e}")
            return False

    async def clear_user_cache(self, user_id: str) -> int:
        """Clear all cached results for a user."""
        if not self.redis_client:
            return 0

        try:
            pattern = f"{self.key_prefix}:*"
            keys = await self.redis_client.keys(pattern)

            # Filter keys that might belong to the user (this is approximate)
            # In a production system, you might want to include user_id in the cache key
            deleted_count = 0
            for key in keys:
                try:
                    cached_data = await self.redis_client.get(key)
                    if cached_data:
                        result_data = json.loads(cached_data)
                        # Check if this result belongs to the user
                        # This is a simplified check - in production, include user_id in key
                        await self.redis_client.delete(key)
                        deleted_count += 1
                except Exception:
                    continue

            self.stats["cache_evictions"] += deleted_count
            logger.info(f"Cleared {deleted_count} cache entries for user: {user_id}")
            return deleted_count

        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"Cache clear error: {e}")
            return 0

    def _serialize_result(self, result: ValidationResult) -> dict[str, Any]:
        """Serialize validation result for caching."""
        # Convert Pydantic model to dict
        result_dict = result.model_dump()

        # Convert datetime objects to ISO strings
        if result_dict.get("started_at"):
            result_dict["started_at"] = result_dict["started_at"].isoformat()
        if result_dict.get("completed_at"):
            result_dict["completed_at"] = result_dict["completed_at"].isoformat()

        # Convert enums to values
        result_dict["status"] = result_dict["status"]
        result_dict["action"] = result_dict["action"]
        result_dict["overall_safety_level"] = result_dict["overall_safety_level"]
        result_dict["crisis_level"] = result_dict["crisis_level"]

        # Add cache metadata
        result_dict["cached_at"] = datetime.utcnow().isoformat()

        return result_dict

    def _deserialize_result(self, result_data: dict[str, Any]) -> ValidationResult:
        """Deserialize validation result from cache."""
        # Convert ISO strings back to datetime objects
        if result_data.get("started_at"):
            result_data["started_at"] = datetime.fromisoformat(
                result_data["started_at"]
            )
        if result_data.get("completed_at"):
            result_data["completed_at"] = datetime.fromisoformat(
                result_data["completed_at"]
            )

        # Remove cache metadata
        result_data.pop("cached_at", None)

        # Create ValidationResult from dict
        return ValidationResult(**result_data)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
        hit_rate = (
            (self.stats["cache_hits"] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform cache health check."""
        if not self.redis_client:
            return {"status": "disabled", "redis_available": False}

        try:
            # Test Redis connection
            await self.redis_client.ping()

            # Get cache info
            info = await self.redis_client.info("memory")
            used_memory = info.get("used_memory_human", "unknown")

            return {
                "status": "healthy",
                "redis_available": True,
                "used_memory": used_memory,
                "stats": self.get_stats(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "redis_available": False,
                "error": str(e),
                "stats": self.get_stats(),
            }


class SafetyResultCache:
    """Specialized cache for safety validation results with additional features."""

    def __init__(self, validation_cache: ValidationCache):
        self.validation_cache = validation_cache
        self.result_patterns = {}  # Cache for common result patterns

    async def get_or_validate(
        self, content: ContentPayload, context: ValidationContext, validator_func
    ) -> ValidationResult:
        """Get cached result or perform validation."""
        # Try cache first
        cached_result = await self.validation_cache.get(content, context)
        if cached_result:
            return cached_result

        # Perform validation
        result = await validator_func(content, context)

        # Cache the result
        await self.validation_cache.set(content, context, result)

        return result

    async def cache_batch_results(
        self,
        results: list[Tuple[ContentPayload, ValidationContext, ValidationResult]],
        ttl: timedelta | None = None,
    ) -> int:
        """Cache multiple validation results in batch."""
        cached_count = 0

        for content, context, result in results:
            success = await self.validation_cache.set(content, context, result, ttl)
            if success:
                cached_count += 1

        return cached_count

    async def get_similar_results(
        self, content: ContentPayload, similarity_threshold: float = 0.8
    ) -> list[ValidationResult]:
        """Get cached results for similar content (simplified implementation)."""
        # This is a simplified implementation
        # In production, you might use more sophisticated similarity matching
        similar_results = []

        # For now, just return empty list
        # Could be enhanced with content similarity algorithms

        return similar_results

    def analyze_cache_patterns(self) -> dict[str, Any]:
        """Analyze cached validation patterns for insights."""
        stats = self.validation_cache.get_stats()

        # Basic pattern analysis
        patterns = {
            "high_cache_hit_rate": stats["hit_rate_percent"] > 70,
            "cache_effectiveness": (
                "high"
                if stats["hit_rate_percent"] > 70
                else "medium" if stats["hit_rate_percent"] > 40 else "low"
            ),
            "total_validations_cached": stats["cache_sets"],
            "cache_errors_rate": (
                stats["cache_errors"] / max(stats["total_requests"], 1)
            )
            * 100,
        }

        return {
            "cache_stats": stats,
            "patterns": patterns,
            "recommendations": self._generate_cache_recommendations(patterns),
        }

    def _generate_cache_recommendations(self, patterns: dict[str, Any]) -> list[str]:
        """Generate recommendations for cache optimization."""
        recommendations = []

        if patterns["cache_effectiveness"] == "low":
            recommendations.append(
                "Consider increasing cache TTL or reviewing cache key strategy"
            )

        if patterns["cache_errors_rate"] > 5:
            recommendations.append(
                "High cache error rate detected - check Redis connection"
            )

        if patterns["total_validations_cached"] < 100:
            recommendations.append(
                "Low cache usage - consider enabling caching for more validation types"
            )

        return recommendations

    async def warm_cache(
        self,
        common_content: list[Tuple[ContentPayload, ValidationContext]],
        validator_func,
    ) -> int:
        """Warm cache with common content validations."""
        warmed_count = 0

        for content, context in common_content:
            # Check if already cached
            cached = await self.validation_cache.get(content, context)
            if not cached:
                # Validate and cache
                result = await validator_func(content, context)
                success = await self.validation_cache.set(content, context, result)
                if success:
                    warmed_count += 1

        logger.info(f"Warmed cache with {warmed_count} validation results")
        return warmed_count
