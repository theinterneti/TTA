# TTA Authentication & Player Profile Monitoring

## Overview

This document describes the comprehensive monitoring metrics and dashboards for tracking authentication and player profile management in the TTA system.

## Metrics Collected

### JWT Token Generation Metrics

#### `tta_jwt_token_generation_total`
- **Type:** Counter
- **Labels:** `service`, `result` (success/failure)
- **Description:** Total number of JWT token generation attempts
- **Use Case:** Track authentication volume and identify token generation failures

#### `tta_jwt_token_generation_duration_seconds`
- **Type:** Histogram
- **Labels:** `service`
- **Buckets:** [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
- **Description:** JWT token generation duration in seconds
- **Use Case:** Monitor token generation performance and identify latency issues

#### `tta_jwt_token_verification_total`
- **Type:** Counter
- **Labels:** `service`, `result` (success/failure/missing_player_id)
- **Description:** Total number of JWT token verification attempts
- **Use Case:** Track token validation and identify missing player_id issues

### Player ID Field Presence Metrics

#### `tta_player_id_field_presence_total`
- **Type:** Counter
- **Labels:** `endpoint`, `has_player_id` (true/false)
- **Description:** Total requests with player_id field presence tracking
- **Use Case:** Monitor player_id field presence across different endpoints

#### `tta_player_id_presence_rate_percent`
- **Type:** Gauge
- **Labels:** `endpoint`
- **Description:** Percentage of requests with valid player_id field
- **Use Case:** Real-time monitoring of player_id presence rate per endpoint

### Player Profile Auto-Creation Metrics

#### `tta_player_profile_autocreation_total`
- **Type:** Counter
- **Labels:** `trigger` (oauth_signin/first_login/etc), `result` (success/failure)
- **Description:** Total player profile auto-creation attempts
- **Use Case:** Track profile creation volume and success rates by trigger type

#### `tta_player_profile_autocreation_duration_seconds`
- **Type:** Histogram
- **Labels:** `trigger`
- **Buckets:** [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
- **Description:** Player profile auto-creation duration in seconds
- **Use Case:** Monitor profile creation performance

#### `tta_player_profile_autocreation_errors_total`
- **Type:** Counter
- **Labels:** `error_category` (validation_error/database_error/duplicate_user/etc)
- **Description:** Total player profile auto-creation errors by category
- **Use Case:** Identify and categorize profile creation failures

## Grafana Dashboard

### Dashboard: TTA Authentication & Player Profile Monitoring
**UID:** `tta-auth-monitoring`
**Location:** `monitoring/grafana/dashboards/tta-authentication-monitoring.json`

### Dashboard Sections

#### 1. JWT Token Generation Monitoring
- **JWT Token Generation Success/Failure Rates:** Time series showing token generation success and failure rates over time
- **JWT Token Generation Latency (Percentiles):** p50, p95, p99 latency percentiles for token generation
- **Total JWT Tokens Issued:** Counter showing cumulative tokens issued
- **JWT Generation Success Rate:** Gauge with alert threshold (<99% triggers warning)

#### 2. Player ID Field Presence Validation
- **Player ID Field Presence Rate:** Gauge showing overall percentage of requests with valid player_id
- **Requests Missing Player ID (by Endpoint):** Time series breakdown of missing player_id by endpoint
- **Player ID Presence Rate by Endpoint:** Stacked bar chart showing presence rate per endpoint

#### 3. Player Profile Auto-Creation Metrics
- **Player Profile Auto-Creation Success/Failure Rates:** Time series showing creation success/failure by trigger type
- **Player Profile Auto-Creation Latency:** p50, p95, p99 latency percentiles for profile creation
- **Total Auto-Created Player Profiles:** Counter showing cumulative profiles created
- **Auto-Creation Triggers Breakdown:** Pie chart showing distribution of creation triggers
- **Auto-Creation Errors by Category:** Pie chart showing error distribution by category

## Alert Thresholds

### Recommended Alert Rules

#### JWT Token Generation Failure Rate
- **Threshold:** >1% failure rate over 5 minutes
- **Severity:** Warning
- **Action:** Investigate authentication service health and secret key configuration

#### JWT Token Generation Latency
- **Threshold:** p95 > 100ms
- **Severity:** Warning
- **Action:** Check CPU usage and optimize token generation code

#### Player ID Presence Rate
- **Threshold:** <95% presence rate for authenticated endpoints
- **Severity:** Warning
- **Action:** Investigate token generation and middleware configuration

#### Player Profile Auto-Creation Failure Rate
- **Threshold:** >5% failure rate over 5 minutes
- **Severity:** Critical
- **Action:** Check database connectivity and player profile manager logs

#### Player Profile Auto-Creation Latency
- **Threshold:** p95 > 1 second
- **Severity:** Warning
- **Action:** Investigate database performance and optimize profile creation

## Instrumentation Locations

### Backend Code Instrumentation

1. **JWT Token Generation:** `src/player_experience/services/auth_service.py`
   - Method: `create_access_token()`
   - Metrics: Token generation success/failure, latency

2. **JWT Token Verification:** `src/player_experience/services/auth_service.py`
   - Method: `verify_access_token()`
   - Metrics: Token verification success/failure, player_id presence

3. **Player ID Presence Tracking:** `src/player_experience/api/middleware.py`
   - Middleware: Request processing
   - Metrics: Player_id field presence by endpoint

4. **Player Profile Auto-Creation:** `src/player_experience/api/routers/auth.py`
   - Endpoint: `/login`
   - Metrics: Auto-creation success/failure, latency, trigger type, error category

## Accessing the Dashboard

### Local Development
1. Start monitoring stack: `docker-compose --profile monitoring up -d`
2. Access Grafana: http://localhost:3000
3. Navigate to: Dashboards → TTA → TTA Authentication & Player Profile Monitoring

### Homelab/Staging
1. Access Grafana: http://<homelab-ip>:3001
2. Login with configured credentials
3. Navigate to: Dashboards → TTA → TTA Authentication & Player Profile Monitoring

## Troubleshooting

### Metrics Not Appearing
1. Verify Prometheus is scraping the player-experience service
2. Check `/metrics` endpoint is accessible: `curl http://localhost:8000/metrics`
3. Verify metrics are being recorded in Prometheus: Query `tta_jwt_token_generation_total`

### Dashboard Not Loading
1. Verify dashboard JSON is valid
2. Check Grafana logs: `docker logs tta-grafana-dev`
3. Verify datasource configuration in Grafana

### Incorrect Metric Values
1. Check instrumentation code is being executed
2. Verify metric labels match dashboard queries
3. Check for exceptions in application logs

## Future Enhancements

- Add OAuth-specific metrics for third-party authentication
- Track MFA verification success rates
- Monitor session duration and activity patterns
- Add geographic distribution of authentication attempts
- Implement anomaly detection for unusual authentication patterns
