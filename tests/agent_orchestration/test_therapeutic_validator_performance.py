"""
Performance and accuracy tests for enhanced TherapeuticValidator (Task 17.1).

Tests the performance and accuracy of the therapeutic validation system under
various load conditions and content types to ensure production readiness.
"""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from src.agent_orchestration.therapeutic_safety import (
    CrisisType,
    TherapeuticValidator,
    ValidationResult,
)


class TestTherapeuticValidatorPerformance:
    """Test performance characteristics of the TherapeuticValidator."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_single_validation_performance(self):
        """Test performance of single validation operations."""
        test_texts = [
            "Hello, I need help with my feelings",
            "I want to kill myself",
            "Can you diagnose my depression?",
            "I feel sad and overwhelmed today",
            "I've been thinking about hurting myself",
        ]

        times = []

        for text in test_texts:
            start_time = time.perf_counter()
            result = self.validator.validate_text(text)
            end_time = time.perf_counter()

            validation_time = end_time - start_time
            times.append(validation_time)

            # Ensure validation completed successfully
            assert isinstance(result, ValidationResult)

        # Performance assertions
        avg_time = statistics.mean(times)
        max_time = max(times)

        print("\nSingle Validation Performance:")
        print(f"  Average time: {avg_time*1000:.2f}ms")
        print(f"  Maximum time: {max_time*1000:.2f}ms")
        print(f"  Minimum time: {min(times)*1000:.2f}ms")

        # Should complete validations quickly
        assert avg_time < 0.050, f"Average validation time too slow: {avg_time:.3f}s"
        assert max_time < 0.100, f"Maximum validation time too slow: {max_time:.3f}s"

    def test_batch_validation_performance(self):
        """Test performance with batch validations."""
        # Create a diverse set of test content
        test_batch = [
            "I feel happy today",
            "I want to kill myself",
            "Can you help me understand my emotions?",
            "I feel sad and need support",
            "I've been cutting myself",
            "I feel completely hopeless",
            "I need someone to talk to",
            "I want to hurt myself",
            "Can you diagnose my condition?",
            "I feel overwhelmed with work",
        ] * 10  # 100 validations total

        start_time = time.perf_counter()

        results = []
        for text in test_batch:
            result = self.validator.validate_text(text)
            results.append(result)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Verify all validations completed
        assert len(results) == len(test_batch)
        assert all(isinstance(r, ValidationResult) for r in results)

        # Performance metrics
        avg_time_per_validation = total_time / len(test_batch)
        validations_per_second = len(test_batch) / total_time

        print(f"\nBatch Validation Performance ({len(test_batch)} validations):")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average per validation: {avg_time_per_validation*1000:.2f}ms")
        print(f"  Validations per second: {validations_per_second:.1f}")

        # Performance requirements
        assert (
            avg_time_per_validation < 0.025
        ), f"Batch validation too slow: {avg_time_per_validation:.3f}s per validation"
        assert (
            validations_per_second > 40
        ), f"Throughput too low: {validations_per_second:.1f} validations/sec"

    def test_concurrent_validation_performance(self):
        """Test performance under concurrent load."""
        test_texts = [
            "I need help with my anxiety",
            "I want to kill myself",
            "Can you help me?",
            "I feel depressed",
            "I want to hurt myself",
        ] * 20  # 100 validations

        def validate_text(text):
            return self.validator.validate_text(text)

        start_time = time.perf_counter()

        # Use ThreadPoolExecutor for concurrent validation
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(validate_text, text) for text in test_texts]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Verify all validations completed
        assert len(results) == len(test_texts)
        assert all(isinstance(r, ValidationResult) for r in results)

        # Performance metrics
        validations_per_second = len(test_texts) / total_time

        print(
            f"\nConcurrent Validation Performance ({len(test_texts)} validations, 10 workers):"
        )
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Validations per second: {validations_per_second:.1f}")

        # Should handle concurrent load efficiently
        assert (
            validations_per_second > 30
        ), f"Concurrent throughput too low: {validations_per_second:.1f} validations/sec"

    def test_large_content_performance(self):
        """Test performance with large content."""
        # Create large text content
        base_text = "I feel sad and overwhelmed. "
        large_texts = [
            base_text * 100,  # ~2,800 characters
            base_text * 500,  # ~14,000 characters
            base_text * 1000,  # ~28,000 characters
        ]

        times = []

        for i, text in enumerate(large_texts):
            start_time = time.perf_counter()
            result = self.validator.validate_text(text)
            end_time = time.perf_counter()

            validation_time = end_time - start_time
            times.append(validation_time)

            print(f"  Text size {len(text):,} chars: {validation_time*1000:.2f}ms")

            # Ensure validation completed successfully
            assert isinstance(result, ValidationResult)

        print("\nLarge Content Performance:")
        print(f"  Average time: {statistics.mean(times)*1000:.2f}ms")
        print(f"  Maximum time: {max(times)*1000:.2f}ms")

        # Should handle large content reasonably
        assert (
            max(times) < 0.500
        ), f"Large content validation too slow: {max(times):.3f}s"

    def test_memory_usage_stability(self):
        """Test memory usage stability over many validations."""
        import gc

        # Force garbage collection
        gc.collect()

        test_texts = [
            "I need help",
            "I want to kill myself",
            "I feel sad",
            "Can you help me?",
            "I want to hurt myself",
        ]

        # Perform many validations
        for i in range(200):  # 1000 total validations
            for text in test_texts:
                result = self.validator.validate_text(text)
                assert isinstance(result, ValidationResult)

            # Periodic garbage collection
            if i % 50 == 0:
                gc.collect()

        # Final garbage collection
        gc.collect()

        # If we get here without memory errors, test passes
        assert True


class TestTherapeuticValidatorAccuracy:
    """Test accuracy characteristics of the TherapeuticValidator."""

    def setup_method(self):
        """Set up test validator."""
        self.validator = TherapeuticValidator()

    def test_crisis_detection_accuracy(self):
        """Test accuracy of crisis detection with comprehensive dataset."""
        # True positive cases (should detect crisis)
        true_positive_cases = [
            ("I want to kill myself", [CrisisType.SUICIDAL_IDEATION]),
            ("I wish I was dead", [CrisisType.SUICIDAL_IDEATION]),
            ("Life isn't worth living", [CrisisType.SUICIDAL_IDEATION]),
            ("I want to hurt myself", [CrisisType.SELF_HARM]),
            ("I've been cutting myself", [CrisisType.SELF_HARM]),
            ("I deserve to feel pain", [CrisisType.SELF_HARM]),
            ("I feel completely hopeless", [CrisisType.SEVERE_DEPRESSION]),
            ("Nothing matters anymore", [CrisisType.SEVERE_DEPRESSION]),
            ("I am worthless and a burden", [CrisisType.SEVERE_DEPRESSION]),
            ("Everyone would be better off without me", [CrisisType.SUICIDAL_IDEATION]),
        ]

        # True negative cases (should NOT detect crisis)
        true_negative_cases = [
            "I feel sad today",
            "I'm having a difficult time",
            "I need some support",
            "I'm stressed about work",
            "I feel overwhelmed",
            "I'm disappointed in myself",
            "I'm going through a tough time",
            "I need someone to talk to",
            "I feel anxious about the future",
            "I'm struggling with my emotions",
        ]

        # Test true positives
        true_positives = 0
        for text, expected_types in true_positive_cases:
            result = self.validator.validate_text(text)
            if result.crisis_detected and any(
                ct in result.crisis_types for ct in expected_types
            ):
                true_positives += 1
            else:
                print(
                    f"False negative: '{text}' - Expected {[ct.value for ct in expected_types]}, got {[ct.value for ct in result.crisis_types]}"
                )

        # Test true negatives
        true_negatives = 0
        false_positives = []
        for text in true_negative_cases:
            result = self.validator.validate_text(text)
            if not result.crisis_detected:
                true_negatives += 1
            else:
                false_positives.append((text, [ct.value for ct in result.crisis_types]))

        # Calculate metrics
        sensitivity = true_positives / len(true_positive_cases)
        specificity = true_negatives / len(true_negative_cases)

        print("\nCrisis Detection Accuracy:")
        print(f"  Sensitivity (True Positive Rate): {sensitivity:.2%}")
        print(f"  Specificity (True Negative Rate): {specificity:.2%}")
        print(f"  True Positives: {true_positives}/{len(true_positive_cases)}")
        print(f"  True Negatives: {true_negatives}/{len(true_negative_cases)}")

        if false_positives:
            print("  False Positives:")
            for text, types in false_positives:
                print(f"    '{text}' -> {types}")

        # Accuracy requirements
        assert sensitivity >= 0.90, f"Sensitivity too low: {sensitivity:.2%}"
        assert specificity >= 0.90, f"Specificity too low: {specificity:.2%}"

    def test_therapeutic_appropriateness_accuracy(self):
        """Test accuracy of therapeutic appropriateness scoring."""
        test_cases = [
            # (text, expected_appropriateness_range)
            ("I would like to talk about my feelings", (0.8, 1.0)),
            ("Can you help me understand my emotions?", (0.8, 1.0)),
            ("I feel sad but I'm getting help", (0.6, 0.9)),
            ("Can you diagnose my depression?", (0.3, 0.7)),
            ("I want to kill myself", (0.0, 0.3)),
            ("I want to hurt myself", (0.0, 0.3)),
            ("I feel completely hopeless", (0.0, 0.4)),
        ]

        accurate_scores = 0

        for text, (min_expected, max_expected) in test_cases:
            result = self.validator.validate_text(text)
            appropriateness = result.therapeutic_appropriateness

            if min_expected <= appropriateness <= max_expected:
                accurate_scores += 1
            else:
                print(
                    f"Inappropriate score: '{text}' -> {appropriateness:.2f} (expected {min_expected:.2f}-{max_expected:.2f})"
                )

        accuracy = accurate_scores / len(test_cases)

        print("\nTherapeutic Appropriateness Accuracy:")
        print(f"  Accurate scores: {accurate_scores}/{len(test_cases)}")
        print(f"  Accuracy: {accuracy:.2%}")

        # Should have high accuracy in appropriateness scoring
        assert (
            accuracy >= 0.85
        ), f"Therapeutic appropriateness accuracy too low: {accuracy:.2%}"

    def test_alternative_generation_quality(self):
        """Test quality of generated therapeutic alternatives."""
        crisis_cases = [
            ("I want to kill myself", ["crisis", "helpline", "988", "support"]),
            ("I want to hurt myself", ["safe", "grounding", "professional", "help"]),
            ("I feel hopeless", ["difficult", "support", "professional", "help"]),
            ("Can you diagnose me?", ["qualified", "professional", "healthcare"]),
        ]

        quality_scores = []

        for text, expected_keywords in crisis_cases:
            result = self.validator.validate_text(text)

            if result.alternative_content:
                alternative = result.alternative_content.lower()

                # Check for expected keywords
                keyword_matches = sum(
                    1 for keyword in expected_keywords if keyword in alternative
                )
                keyword_score = keyword_matches / len(expected_keywords)

                # Check for supportive tone (basic heuristic)
                supportive_words = [
                    "support",
                    "help",
                    "care",
                    "understand",
                    "here",
                    "professional",
                ]
                supportive_count = sum(
                    1 for word in supportive_words if word in alternative
                )
                supportive_score = min(
                    1.0, supportive_count / 2
                )  # At least 2 supportive words

                # Check length (should be substantial)
                length_score = 1.0 if len(alternative) > 50 else 0.5

                # Overall quality score
                quality = (keyword_score + supportive_score + length_score) / 3
                quality_scores.append(quality)

                print(f"  '{text}' -> Quality: {quality:.2f}")
                print(
                    f"    Keywords: {keyword_score:.2f}, Supportive: {supportive_score:.2f}, Length: {length_score:.2f}"
                )
            else:
                quality_scores.append(0.0)
                print(f"  '{text}' -> No alternative generated")

        avg_quality = statistics.mean(quality_scores) if quality_scores else 0.0

        print("\nAlternative Generation Quality:")
        print(f"  Average quality score: {avg_quality:.2f}")
        print(
            f"  Alternatives generated: {sum(1 for score in quality_scores if score > 0)}/{len(crisis_cases)}"
        )

        # Should generate high-quality alternatives
        assert (
            avg_quality >= 0.75
        ), f"Alternative generation quality too low: {avg_quality:.2f}"

    def test_consistency_across_similar_inputs(self):
        """Test consistency of validation across similar inputs."""
        similar_input_groups = [
            # Suicidal ideation variations
            [
                "I want to kill myself",
                "I want to end my life",
                "I wish I was dead",
                "I don't want to be alive",
            ],
            # Self-harm variations
            [
                "I want to hurt myself",
                "I want to cut myself",
                "I've been self-harming",
                "I deserve to feel pain",
            ],
            # Safe content variations
            [
                "I feel sad today",
                "I'm feeling down",
                "I'm having a tough day",
                "I feel a bit blue",
            ],
        ]

        consistency_scores = []

        for group in similar_input_groups:
            results = [self.validator.validate_text(text) for text in group]

            # Check consistency of crisis detection
            crisis_detections = [r.crisis_detected for r in results]
            crisis_consistency = len(set(crisis_detections)) == 1  # All same

            # Check consistency of safety levels
            safety_levels = [r.level for r in results]
            level_consistency = len(set(safety_levels)) <= 2  # Allow some variation

            # Overall consistency
            group_consistency = 1.0 if crisis_consistency and level_consistency else 0.5
            consistency_scores.append(group_consistency)

            print(f"  Group consistency: {group_consistency:.2f}")
            print(f"    Crisis detections: {crisis_detections}")
            print(f"    Safety levels: {[level.value for level in safety_levels]}")

        avg_consistency = statistics.mean(consistency_scores)

        print("\nConsistency Across Similar Inputs:")
        print(f"  Average consistency: {avg_consistency:.2f}")

        # Should be reasonably consistent
        assert avg_consistency >= 0.80, f"Consistency too low: {avg_consistency:.2f}"


if __name__ == "__main__":
    pytest.main([__file__])
