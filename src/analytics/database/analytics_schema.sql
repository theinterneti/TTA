-- Advanced Analytics Database Schema for TTA System
-- This schema supports privacy-compliant aggregate analytics and behavioral pattern analysis

-- Create analytics schema
CREATE SCHEMA IF NOT EXISTS analytics;

-- User Behavior Patterns Table
CREATE TABLE analytics.user_behavior_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL CHECK (pattern_type IN ('engagement', 'therapeutic_progress', 'session_behavior', 'outcome_prediction')),
    pattern_data JSONB NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    user_cohort VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Therapeutic Outcomes Table
CREATE TABLE analytics.therapeutic_outcomes (
    outcome_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_cohort VARCHAR(50) NOT NULL,
    session_count INTEGER NOT NULL CHECK (session_count >= 0),
    total_duration_hours FLOAT NOT NULL CHECK (total_duration_hours >= 0),
    engagement_score FLOAT NOT NULL CHECK (engagement_score >= 0.0 AND engagement_score <= 1.0),
    progress_markers_count INTEGER NOT NULL CHECK (progress_markers_count >= 0),
    therapeutic_goals_achieved INTEGER NOT NULL CHECK (therapeutic_goals_achieved >= 0),
    outcome_category VARCHAR(30) NOT NULL CHECK (outcome_category IN ('positive', 'neutral', 'needs_attention', 'excellent', 'good', 'moderate')),
    outcome_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cohort Analysis Table
CREATE TABLE analytics.cohort_analysis (
    cohort_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_name VARCHAR(50) NOT NULL UNIQUE,
    cohort_characteristics JSONB NOT NULL,
    user_count INTEGER NOT NULL CHECK (user_count >= 0),
    avg_engagement_score FLOAT CHECK (avg_engagement_score >= 0.0 AND avg_engagement_score <= 1.0),
    avg_progress_score FLOAT CHECK (avg_progress_score >= 0.0 AND avg_progress_score <= 1.0),
    success_rate FLOAT CHECK (success_rate >= 0.0 AND success_rate <= 1.0),
    analysis_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    analysis_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Predictive Models Table
CREATE TABLE analytics.predictive_models (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('engagement_prediction', 'outcome_prediction', 'intervention_recommendation', 'risk_assessment')),
    model_version VARCHAR(20) NOT NULL,
    model_parameters JSONB NOT NULL,
    training_data_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    training_data_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    accuracy_score FLOAT CHECK (accuracy_score >= 0.0 AND accuracy_score <= 1.0),
    precision_score FLOAT CHECK (precision_score >= 0.0 AND precision_score <= 1.0),
    recall_score FLOAT CHECK (recall_score >= 0.0 AND recall_score <= 1.0),
    f1_score FLOAT CHECK (f1_score >= 0.0 AND f1_score <= 1.0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Real-time Alerts Table
CREATE TABLE analytics.realtime_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('therapeutic_intervention', 'system_performance', 'user_engagement', 'anomaly_detection')),
    alert_severity VARCHAR(20) NOT NULL CHECK (alert_severity IN ('low', 'medium', 'high', 'critical')),
    alert_message TEXT NOT NULL,
    alert_data JSONB,
    user_cohort VARCHAR(50),
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Aggregate Metrics Table
CREATE TABLE analytics.aggregate_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50) NOT NULL CHECK (metric_category IN ('user_engagement', 'therapeutic_outcomes', 'system_performance', 'model_performance')),
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(20),
    aggregation_period VARCHAR(20) NOT NULL CHECK (aggregation_period IN ('hourly', 'daily', 'weekly', 'monthly')),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Privacy Audit Log Table
CREATE TABLE analytics.privacy_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(50) NOT NULL CHECK (operation_type IN ('data_access', 'data_aggregation', 'pattern_detection', 'report_generation')),
    user_cohorts_accessed TEXT[], -- Array of cohort identifiers
    data_anonymization_level VARCHAR(20) NOT NULL CHECK (data_anonymization_level IN ('low', 'medium', 'high', 'maximum')),
    differential_privacy_epsilon FLOAT,
    accessed_by VARCHAR(100) NOT NULL,
    access_purpose TEXT NOT NULL,
    data_retention_period INTERVAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_behavior_patterns_type_cohort ON analytics.user_behavior_patterns(pattern_type, user_cohort);
CREATE INDEX idx_behavior_patterns_created_at ON analytics.user_behavior_patterns(created_at DESC);
CREATE INDEX idx_behavior_patterns_confidence ON analytics.user_behavior_patterns(confidence_score DESC);

CREATE INDEX idx_therapeutic_outcomes_cohort ON analytics.therapeutic_outcomes(user_cohort);
CREATE INDEX idx_therapeutic_outcomes_category ON analytics.therapeutic_outcomes(outcome_category);
CREATE INDEX idx_therapeutic_outcomes_created_at ON analytics.therapeutic_outcomes(created_at DESC);

CREATE INDEX idx_cohort_analysis_name ON analytics.cohort_analysis(cohort_name);
CREATE INDEX idx_cohort_analysis_period ON analytics.cohort_analysis(analysis_period_start, analysis_period_end);

CREATE INDEX idx_predictive_models_type_active ON analytics.predictive_models(model_type, is_active);
CREATE INDEX idx_predictive_models_accuracy ON analytics.predictive_models(accuracy_score DESC);

CREATE INDEX idx_realtime_alerts_type_severity ON analytics.realtime_alerts(alert_type, alert_severity);
CREATE INDEX idx_realtime_alerts_unresolved ON analytics.realtime_alerts(is_resolved, created_at DESC);

CREATE INDEX idx_aggregate_metrics_category_period ON analytics.aggregate_metrics(metric_category, aggregation_period);
CREATE INDEX idx_aggregate_metrics_name_period ON analytics.aggregate_metrics(metric_name, period_start, period_end);

CREATE INDEX idx_privacy_audit_operation ON analytics.privacy_audit_log(operation_type, created_at DESC);

-- Views for Common Queries

-- Active High-Confidence Patterns View
CREATE VIEW analytics.v_active_high_confidence_patterns AS
SELECT
    pattern_id,
    pattern_type,
    pattern_data,
    confidence_score,
    user_cohort,
    created_at
FROM analytics.user_behavior_patterns
WHERE is_active = TRUE
  AND confidence_score >= 0.7
ORDER BY confidence_score DESC, created_at DESC;

-- Cohort Performance Summary View
CREATE VIEW analytics.v_cohort_performance_summary AS
SELECT
    user_cohort,
    COUNT(*) as total_outcomes,
    AVG(engagement_score) as avg_engagement,
    AVG(CASE WHEN outcome_category IN ('positive', 'excellent', 'good') THEN 1.0 ELSE 0.0 END) as success_rate,
    AVG(total_duration_hours) as avg_duration_hours,
    AVG(therapeutic_goals_achieved) as avg_goals_achieved
FROM analytics.therapeutic_outcomes
GROUP BY user_cohort
ORDER BY success_rate DESC;

-- Recent Alert Summary View
CREATE VIEW analytics.v_recent_alert_summary AS
SELECT
    alert_type,
    alert_severity,
    COUNT(*) as alert_count,
    COUNT(CASE WHEN is_resolved = FALSE THEN 1 END) as unresolved_count,
    MAX(created_at) as latest_alert
FROM analytics.realtime_alerts
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY alert_type, alert_severity
ORDER BY alert_severity DESC, alert_count DESC;

-- Functions for Data Management

-- Function to clean old patterns (data retention)
CREATE OR REPLACE FUNCTION analytics.cleanup_old_patterns(retention_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM analytics.user_behavior_patterns
    WHERE created_at < NOW() - (retention_days || ' days')::INTERVAL
      AND is_active = FALSE;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    INSERT INTO analytics.privacy_audit_log (
        operation_type,
        data_anonymization_level,
        accessed_by,
        access_purpose,
        data_retention_period
    ) VALUES (
        'data_cleanup',
        'high',
        'system',
        'Automated data retention cleanup',
        (retention_days || ' days')::INTERVAL
    );

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate cohort statistics
CREATE OR REPLACE FUNCTION analytics.calculate_cohort_stats(cohort_name VARCHAR(50))
RETURNS TABLE(
    total_patterns INTEGER,
    avg_confidence FLOAT,
    pattern_types TEXT[],
    latest_analysis TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INTEGER as total_patterns,
        AVG(confidence_score)::FLOAT as avg_confidence,
        ARRAY_AGG(DISTINCT pattern_type) as pattern_types,
        MAX(created_at) as latest_analysis
    FROM analytics.user_behavior_patterns
    WHERE user_cohort = cohort_name
      AND is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Triggers for Updated Timestamps
CREATE OR REPLACE FUNCTION analytics.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_behavior_patterns_updated_at
    BEFORE UPDATE ON analytics.user_behavior_patterns
    FOR EACH ROW EXECUTE FUNCTION analytics.update_updated_at_column();

CREATE TRIGGER update_therapeutic_outcomes_updated_at
    BEFORE UPDATE ON analytics.therapeutic_outcomes
    FOR EACH ROW EXECUTE FUNCTION analytics.update_updated_at_column();

CREATE TRIGGER update_cohort_analysis_updated_at
    BEFORE UPDATE ON analytics.cohort_analysis
    FOR EACH ROW EXECUTE FUNCTION analytics.update_updated_at_column();

CREATE TRIGGER update_predictive_models_updated_at
    BEFORE UPDATE ON analytics.predictive_models
    FOR EACH ROW EXECUTE FUNCTION analytics.update_updated_at_column();

-- Grant permissions (adjust as needed for your environment)
-- GRANT USAGE ON SCHEMA analytics TO analytics_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA analytics TO analytics_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA analytics TO analytics_user;

-- Initial data for testing
INSERT INTO analytics.cohort_analysis (
    cohort_name,
    cohort_characteristics,
    user_count,
    avg_engagement_score,
    avg_progress_score,
    success_rate,
    analysis_period_start,
    analysis_period_end
) VALUES (
    'high_engagement_users',
    '{"therapeutic_focus": "anxiety", "session_frequency": "high", "engagement_level": "high"}',
    0,
    0.85,
    0.78,
    0.82,
    NOW() - INTERVAL '30 days',
    NOW()
);

COMMENT ON SCHEMA analytics IS 'Advanced analytics schema for TTA system with privacy-compliant aggregate analysis';
COMMENT ON TABLE analytics.user_behavior_patterns IS 'Stores detected behavioral patterns with privacy protection';
COMMENT ON TABLE analytics.therapeutic_outcomes IS 'Aggregated therapeutic outcome data for analysis';
COMMENT ON TABLE analytics.cohort_analysis IS 'Cohort-based analysis results and statistics';
COMMENT ON TABLE analytics.predictive_models IS 'Machine learning models for predictive analytics';
COMMENT ON TABLE analytics.realtime_alerts IS 'Real-time alerts and notifications for therapeutic interventions';
COMMENT ON TABLE analytics.aggregate_metrics IS 'Time-series aggregate metrics for system and therapeutic performance';
COMMENT ON TABLE analytics.privacy_audit_log IS 'Audit trail for privacy compliance and data access tracking';
