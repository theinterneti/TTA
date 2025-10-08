# TTA Master Glossary

## Overview
This master glossary defines all terms used across TTA documentation to ensure consistency and clarity. All documentation must use these standardized definitions.

## Core System Terms

### **TTA (Therapeutic Text Adventure)**
The complete platform providing AI-powered therapeutic storytelling experiences through interactive text-based adventures.

### **Player**
End users who access the TTA system for personal therapeutic storytelling experiences. Players create characters, explore worlds, and engage in therapeutic sessions independently.

### **Patient**
Clinical users who access the TTA system as part of formal therapeutic treatment under clinical supervision. Patients work with clinical staff in structured therapeutic interventions.

### **Clinical Staff**
Licensed healthcare professionals (therapists, counselors, psychologists, psychiatrists) who use the TTA system to provide therapeutic interventions to patients.

### **Public User**
General audience members exploring the TTA platform to understand its capabilities, evaluate suitability, or access educational content before committing to use.

### **Developer**
Technical team members responsible for building, maintaining, and enhancing the TTA system infrastructure, features, and integrations.

### **Administrator**
System managers responsible for overall platform operations, user management, security, compliance, and institutional relationships.

## Character and World Terms

### **Character**
A therapeutic persona created by users to represent themselves in therapeutic adventures. Characters have:
- **Basic Info**: Name, appearance description
- **Background**: Personal story, personality traits, character goals
- **Therapeutic Profile**: Comfort level, therapeutic intensity preferences, therapeutic goals

### **Character Archetype**
Pre-defined character templates with specific therapeutic focuses (e.g., "The Resilient Survivor", "The Anxious Achiever") that users can customize.

### **World**
Therapeutic environments where characters engage in storytelling adventures. Worlds have specific themes, difficulty levels, and therapeutic approaches.

### **Therapeutic Session**
An interactive storytelling experience where a character engages with a world to achieve therapeutic goals through guided narrative progression.

### **Session Progress**
Real-time tracking of user engagement, therapeutic milestones, and outcome measurements during therapeutic sessions.

## Therapeutic Terms

### **Therapeutic Approach**
Specific evidence-based therapeutic methodologies integrated into the system:
- **CBT**: Cognitive Behavioral Therapy
- **Mindfulness-Based Therapy**: Mindfulness and meditation-focused interventions
- **Narrative Therapy**: Story-based therapeutic approach
- **Solution-Focused Brief Therapy**: Goal-oriented, solution-focused interventions
- **ACT**: Acceptance and Commitment Therapy
- **DBT**: Dialectical Behavior Therapy
- **Humanistic Therapy**: Person-centered therapeutic approach
- **Psychodynamic Therapy**: Insight-oriented therapeutic approach

### **Therapeutic Intensity**
User-configurable level of therapeutic intervention:
- **Low**: Gentle guidance with minimal therapeutic intervention
- **Medium**: Balanced therapeutic approach with moderate intervention
- **High**: Intensive therapeutic work with frequent interventions

### **Comfort Level**
User-defined scale (1-10) indicating their comfort with therapeutic exploration and intervention intensity.

### **Therapeutic Goals**
Specific, measurable objectives users want to achieve through their therapeutic journey (e.g., "Reduce anxiety and stress through mindfulness").

### **Trigger Warnings**
User-defined topics or content that might cause distress or discomfort, used to customize content filtering and safety protocols.

### **Safety Protocols**
Automated and manual systems designed to protect user wellbeing, including crisis intervention, content filtering, and emergency support activation.

## Technical Terms

### **API (Application Programming Interface)**
RESTful web services that enable communication between system components and external integrations. All API endpoints use the `/api/v1/` prefix.

### **Authentication**
User identity verification system using JWT (JSON Web Tokens) for secure access control and session management.

### **Authorization**
Role-based access control system that determines what features and data users can access based on their user type and permissions.

### **JWT (JSON Web Token)**
Secure token format used for user authentication and session management across the TTA system.

### **RBAC (Role-Based Access Control)**
Security model that restricts system access based on user roles (Player, Patient, Clinical Staff, Administrator, Developer).

### **Neo4j**
Graph database system used for storing and managing character relationships, world connections, and therapeutic progress data.

### **Redis**
In-memory data structure store used for session management, caching, and real-time data processing.

### **OpenRouter**
External AI model provider integration that provides access to multiple AI models for therapeutic content generation.

## User Interface Terms

### **Dashboard**
Main user interface showing personalized information, statistics, and quick actions relevant to each user type.

### **Character Creation Wizard**
Three-step guided process for creating therapeutic characters:
1. **Basic Info**: Name and appearance
2. **Background**: Story, traits, and goals
3. **Therapeutic Profile**: Comfort level, intensity, and therapeutic goals

### **Settings Management**
User interface for configuring:
- **Therapeutic Preferences**: Intensity, approaches, comfort topics
- **AI Model Management**: Model selection and authentication
- **Privacy Settings**: Data protection and sharing preferences
- **Accessibility Settings**: Interface customization for different needs

### **World Browser**
Interface for discovering, filtering, and selecting therapeutic worlds based on compatibility, theme, and user preferences.

## Data and Privacy Terms

### **HIPAA (Health Insurance Portability and Accountability Act)**
US healthcare privacy law governing the protection of patient health information in clinical settings.

### **GDPR (General Data Protection Regulation)**
European privacy regulation governing personal data protection and user privacy rights.

### **PHI (Protected Health Information)**
Any health information that can be linked to a specific individual, requiring special protection under HIPAA.

### **Data Encryption**
Security measure ensuring data is protected both "in transit" (during transmission) and "at rest" (when stored).

### **Audit Trail**
Complete record of all user actions and system events for security, compliance, and troubleshooting purposes.

### **Data Retention**
Policies governing how long user data is stored and when it is automatically deleted or archived.

## Testing and Quality Terms

### **User Journey**
Complete path a user takes through the system from entry point to exit point, including all interactions and decision points.

### **Test Case**
Specific scenario with defined steps, expected results, and validation criteria used to verify system functionality.

### **Happy Path**
Ideal user flow with no errors, obstacles, or unusual conditions - the expected normal usage pattern.

### **Edge Case**
Boundary conditions, error states, or unusual user behaviors that test system resilience and error handling.

### **Load Testing**
Performance testing with multiple concurrent users to validate system scalability and response times.

### **Security Testing**
Validation of authentication, authorization, data protection, and vulnerability prevention measures.

### **Accessibility Testing**
Verification that the system meets WCAG 2.1 AA standards for users with disabilities.

## Integration Terms

### **EHR (Electronic Health Record)**
External healthcare systems that may integrate with TTA for clinical data exchange and treatment coordination.

### **API Integration**
Connection between TTA and external systems for data exchange, authentication, or service provision.

### **Webhook**
Automated HTTP callbacks that notify external systems of events or changes within the TTA system.

### **SSO (Single Sign-On)**
Authentication method allowing users to access TTA using credentials from other systems (e.g., hospital login systems).

## Performance and Monitoring Terms

### **Response Time**
Time between user action and system response, with targets of <2 seconds for page loads and <500ms for API calls.

### **Uptime**
Percentage of time the system is operational and accessible, with a target of 99.9% availability.

### **Scalability**
System's ability to handle increased load, with targets supporting 1000+ concurrent users.

### **Monitoring**
Real-time tracking of system performance, user behavior, and error rates for operational awareness.

### **Alerting**
Automated notifications when system metrics exceed defined thresholds or errors occur.

## Clinical and Therapeutic Outcome Terms

### **Therapeutic Effectiveness**
Measurable improvement in user wellbeing, symptom reduction, or goal achievement through TTA engagement.

### **Clinical Outcome**
Quantifiable results of therapeutic intervention measured through standardized assessments and progress tracking.

### **Progress Tracking**
Systematic monitoring of user advancement toward therapeutic goals through session engagement and outcome measurement.

### **Crisis Intervention**
Immediate support protocols activated when users indicate distress, suicidal ideation, or need emergency assistance.

### **Therapeutic Alliance**
Collaborative relationship between patient and clinical staff facilitated through the TTA platform.

## Compliance and Regulatory Terms

### **Clinical Validation**
Process of verifying that therapeutic interventions meet evidence-based standards and produce expected outcomes.

### **Regulatory Compliance**
Adherence to healthcare regulations, privacy laws, and professional standards governing therapeutic technology platforms.

### **Quality Assurance**
Systematic processes ensuring the TTA system meets defined standards for safety, effectiveness, and user experience.

### **Risk Management**
Identification, assessment, and mitigation of potential risks to user safety, data security, and system reliability.

## Version Control and Documentation Terms

### **Documentation Audit**
Systematic review of all documentation for accuracy, completeness, consistency, and alignment with system implementation.

### **Version Control**
System for tracking changes to documentation and code, ensuring all modifications are recorded and reversible.

### **Traceability Matrix**
Document linking user requirements to implemented features, test cases, and validation results.

### **Gap Analysis**
Identification of differences between documented requirements and actual system implementation.

---

**Usage Guidelines:**
- All TTA documentation must use these standardized definitions
- When introducing new terms, add them to this glossary first
- Ensure consistent capitalization and formatting across all documents
- Link to this glossary from other documentation when using technical terms

**Maintenance:**
- Glossary reviewed and updated with each major system release
- New terms added as system capabilities expand
- Deprecated terms marked and eventually removed
- User feedback incorporated to improve clarity and completeness

**Last Updated**: 2025-01-23
**Version**: 2.0
**Status**: ✅ Audited and Aligned with Demonstrated System
