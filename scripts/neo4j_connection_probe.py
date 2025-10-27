# ruff: noqa: ALL
#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time
from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("neo4j_probe")


def attempt_connect(
    uri: str,
    username: str,
    password: str,
    initial_sleep: float | None = None,
    attempts: int = 5,
):
    """Replicate the project's connect() logic with retries and backoff.
    Returns True/False and a summary list of (attempt_idx, elapsed, outcome, err_str).
    """
    time.time()
    try:
        from neo4j import GraphDatabase
        from neo4j.exceptions import (
            AuthError,
            ClientError as _ClientError,
            ServiceUnavailable as _ServiceUnavailable,
        )
    except Exception as e:
        logger.error("neo4j package not installed: %s", e)
        return False, [(0, 0.0, "no-neo4j", str(e))]

    base_delay = 0.5
    results = []

    if initial_sleep:
        logger.debug("Initial sleep %.1fs before first attempt", initial_sleep)
        time.sleep(initial_sleep)

    driver = None
    for attempt in range(attempts):
        a_t0 = time.time()
        try:
            driver = GraphDatabase.driver(uri, auth=(username, password))
            with driver.session() as session:
                session.run("RETURN 1")
            dt = time.time() - a_t0
            results.append((attempt + 1, dt, "ok", ""))
            try:
                if driver:
                    driver.close()
            except Exception:
                pass
            return True, results
        except (AuthError, _ServiceUnavailable) as e:
            dt = time.time() - a_t0
            results.append((attempt + 1, dt, type(e).__name__, str(e)))
            delay = min(base_delay * (2**attempt), 8.0)
            logger.debug(
                "Attempt %d/%d failed (%s); retry in %.1fs",
                attempt + 1,
                attempts,
                type(e).__name__,
                delay,
            )
            try:
                if driver:
                    driver.close()
            except Exception:
                pass
            driver = None
            if attempt < attempts - 1:
                time.sleep(delay)
            else:
                break
        except _ClientError as e:
            # Retry only when AuthenticationRateLimit pattern observed
            emsg = str(e)
            dt = time.time() - a_t0
            if ("AuthenticationRateLimit" in emsg) or (
                "authentication details too many times" in emsg
            ):
                results.append((attempt + 1, dt, type(e).__name__, emsg))
                delay = min(base_delay * (2**attempt), 8.0)
                logger.debug(
                    "Attempt %d/%d hit AuthenticationRateLimit; retry in %.1fs",
                    attempt + 1,
                    attempts,
                    delay,
                )
                try:
                    if driver:
                        driver.close()
                except Exception:
                    pass
                driver = None
                if attempt < attempts - 1:
                    time.sleep(delay)
                else:
                    break
            else:
                results.append((attempt + 1, dt, type(e).__name__, emsg))
                try:
                    if driver:
                        driver.close()
                except Exception:
                    pass
                return False, results
        except Exception as e:
            dt = time.time() - a_t0
            results.append((attempt + 1, dt, type(e).__name__, str(e)))
            try:
                if driver:
                    driver.close()
            except Exception:
                pass
            return False, results
    # exhausted
    return False, results


@contextmanager
def ensure_container_if_needed(mode: str):
    """Context manager returning (uri, username, password) either from env/local or a Testcontainer."""
    if mode == "local":
        uri = os.environ.get("TEST_NEO4J_URI", "bolt://localhost:7687")
        username = os.environ.get("TEST_NEO4J_USERNAME", "neo4j")
        password = os.environ.get("TEST_NEO4J_PASSWORD", "password")
        yield uri, username, password
        return
    # container mode
    try:
        from testcontainers.neo4j import Neo4jContainer
    except Exception as e:
        logger.error("testcontainers not available: %s", e)
        raise
    with (
        Neo4jContainer("neo4j:5-community")
        .with_env("NEO4J_AUTH", "neo4j/testpassword")
        .with_env("NEO4J_ACCEPT_LICENSE_AGREEMENT", "yes")
    ) as neo4j:
        uri = neo4j.get_connection_url()
        username = "neo4j"
        password = "testpassword"
        yield uri, username, password


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["local", "container"], default="container")
    ap.add_argument(
        "--initial-sleep",
        type=float,
        default=0.0,
        help="initial sleep seconds before first attempt",
    )
    ap.add_argument("--attempts", type=int, default=5)
    args = ap.parse_args()

    with ensure_container_if_needed(args.mode) as (uri, username, password):
        logger.info("Testing Neo4j connect to %s with user=%s", uri, username)
        ok, results = attempt_connect(
            uri,
            username,
            password,
            initial_sleep=args.initial_sleep,
            attempts=args.attempts,
        )
        logger.info("Result: %s", "SUCCESS" if ok else "FAIL")
        for i, dt, outcome, msg in results:
            logger.info(
                "  attempt=%d elapsed=%.3fs outcome=%s msg=%s", i, dt, outcome, msg
            )
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
