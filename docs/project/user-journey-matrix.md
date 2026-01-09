# TTA (Therapeutic Text Adventure) User Journey Matrix

## Overview
This comprehensive matrix maps detailed interaction flows for six distinct user categories in the TTA system, based on the demonstrated platform capabilities including authentication, character creation, world selection, therapeutic settings, and AI model management.

## User Categories Matrix

### 1. PLAYERS - End Users Seeking Therapeutic Storytelling

#### Primary Goals
- Experience therapeutic storytelling for personal growth and healing
- Create meaningful characters that reflect their therapeutic journey
- Engage in safe, guided therapeutic adventures
- Track personal progress and emotional development
- Build coping skills through interactive narratives

#### Entry Points
- **Direct Registration**: Self-signup via website/app
- **Referral Links**: Shared by friends, social media, or support groups
- **Therapeutic Recommendations**: Suggested by mental health professionals
- **Marketing Campaigns**: Ads, content marketing, wellness platforms

#### Authentication Flow
```
1. Landing Page → Sign Up/Login
2. Account Creation:
   - Username/Email/Password
   - Basic demographic info (optional)
   - Therapeutic goals assessment (optional)
3. Email Verification (if required)
4. Welcome Onboarding:
   - Platform tour
   - Safety guidelines
   - Privacy settings
5. Profile Setup:
   - Therapeutic preferences
   - Comfort level settings
   - Trigger warnings configuration
```

#### Core Workflows

**Character Creation Journey:**
```
Dashboard → Characters → Create Character
├── Step 1: Basic Info
│   ├── Character Name (required, 50 char limit)
│   ├── Appearance Description (required)
│   └── Real-time Preview
├── Step 2: Background & Personality
│   ├── Background Story (required)
│   ├── Personality Traits (add/remove interface)
│   └── Character Goals (add/remove interface)
└── Step 3: Therapeutic Profile
    ├── Comfort Level (1-10 slider)
    ├── Therapeutic Intensity (Low/Medium/High)
    ├── Therapeutic Goals (add/remove)
    └── Character Summary Review
```

**World Selection & Session Flow:**
```
Dashboard → Worlds → Browse/Filter
├── World Discovery
│   ├── Search by theme/difficulty/duration
│   ├── Compatibility ratings (requires character)
│   └── World details and descriptions
├── Character-World Matching
│   ├── Therapeutic compatibility check
│   ├── Safety assessment
│   └── Personalized recommendations
└── Session Initiation
    ├── Character selection
    ├── World entry confirmation
    └── Therapeutic session begins
```

#### Data Interactions
- **Input**: Character details, therapeutic preferences, session responses, progress feedback
- **View**: Personal dashboard, character profiles, session history, progress analytics
- **Manage**: Account settings, privacy controls, therapeutic preferences, character modifications

#### Permission Levels
- **Full Access**: Own characters, worlds, sessions, settings
- **Limited Access**: Public worlds, community features (if enabled)
- **No Access**: Other users' private data, administrative functions, clinical tools

#### Success Metrics
- **Engagement**: Session completion rates, return visits, time spent
- **Therapeutic Progress**: Self-reported mood improvements, goal achievement
- **Platform Adoption**: Character creation completion, world exploration, feature usage
- **Safety**: Successful trigger warning handling, crisis intervention effectiveness

#### Exit Points
- **Natural Completion**: Session ends, goals achieved, therapeutic milestone reached
- **Voluntary Pause**: Save progress, schedule next session, take break
- **Safety Exit**: Crisis support activation, immediate help resources
- **Technical Issues**: Error recovery, support contact, session restoration

---

### 2. PATIENTS - Clinical Users in Formal Therapeutic Settings

#### Primary Goals
- Participate in structured therapeutic interventions
- Complete assigned therapeutic exercises and adventures
- Collaborate with clinical staff on treatment goals
- Track progress within clinical treatment plans
- Maintain therapeutic engagement between sessions

#### Entry Points
- **Clinical Referral**: Therapist creates account or provides access code
- **Treatment Plan Integration**: Part of formal therapy program
- **Hospital/Clinic Portal**: Integrated with existing healthcare systems
- **Therapist Invitation**: Direct invitation with pre-configured settings

#### Authentication Flow
```
1. Clinical Access Code/Invitation
2. Guided Account Setup:
   - Patient ID verification
   - Clinical consent forms
   - HIPAA compliance acknowledgment
3. Therapist-Supervised Configuration:
   - Therapeutic goals alignment
   - Safety parameters setting
   - Progress tracking permissions
4. Clinical Profile Creation:
   - Treatment plan integration
   - Therapist communication preferences
   - Emergency contact information
```

#### Core Workflows

**Supervised Character Creation:**
```
Clinical Dashboard → Assigned Exercises → Character Creation
├── Therapist-Guided Setup
│   ├── Pre-approved character templates
│   ├── Clinical goal alignment
│   └── Safety parameter enforcement
├── Collaborative Development
│   ├── Patient input with therapist oversight
│   ├── Real-time clinical notes integration
│   └── Progress milestone tracking
└── Clinical Review & Approval
    ├── Therapist validation
    ├── Treatment plan alignment check
    └── Safety assessment completion
```

**Clinical Session Management:**
```
Patient Portal → Active Assignments → Session Entry
├── Pre-Session Preparation
│   ├── Mood/state check-in
│   ├── Session objectives review
│   └── Safety reminder acknowledgment
├── Guided Therapeutic Adventure
│   ├── Structured narrative progression
│   ├── Real-time clinical monitoring
│   └── Intervention point management
└── Post-Session Processing
    ├── Reflection and journaling
    ├── Progress assessment
    └── Therapist communication
```

#### Data Interactions
- **Input**: Clinical assessments, session responses, progress reports, mood tracking
- **View**: Assigned exercises, progress dashboards, therapist communications, treatment milestones
- **Manage**: Personal therapeutic goals, session scheduling, communication preferences

#### Permission Levels
- **Supervised Access**: Clinical exercises, approved worlds, monitored sessions
- **Collaborative Control**: Character development with therapist oversight
- **Restricted Areas**: Administrative functions, other patients' data, unsupervised content

#### Success Metrics
- **Clinical Outcomes**: Treatment goal achievement, symptom improvement, engagement levels
- **Compliance**: Assignment completion, session attendance, progress reporting
- **Therapeutic Alliance**: Patient-therapist collaboration, communication effectiveness
- **Safety**: Crisis prevention, appropriate intervention usage, risk management

#### Exit Points
- **Treatment Completion**: Clinical goals achieved, discharge planning
- **Session Transition**: Move to next treatment phase, referral to other services
- **Crisis Intervention**: Emergency support activation, clinical escalation
- **Technical Support**: Clinical IT assistance, session recovery, data backup

---

### 3. CLINICAL STAFF - Therapists, Counselors, Healthcare Providers

#### Primary Goals
- Monitor and guide patient therapeutic journeys
- Customize therapeutic interventions and content
- Track patient progress and clinical outcomes
- Manage caseloads and treatment plans
- Ensure patient safety and clinical compliance
- Generate clinical reports and documentation

#### Entry Points
- **Professional Registration**: Verified clinical credentials
- **Institutional Access**: Hospital/clinic system integration
- **Training Programs**: Professional development and certification
- **Colleague Referrals**: Professional network recommendations

#### Authentication Flow
```
1. Professional Credential Verification
2. Clinical Account Setup:
   - License verification
   - Institutional affiliation
   - Specialization areas
3. HIPAA/Privacy Training Completion
4. Clinical Dashboard Configuration:
   - Caseload management setup
   - Intervention preferences
   - Reporting requirements
5. Patient Assignment Permissions
```

#### Core Workflows

**Patient Management Dashboard:**
```
Clinical Portal → Patient Caseload → Individual Management
├── Patient Overview
│   ├── Treatment plan status
│   ├── Session progress tracking
│   └── Risk assessment monitoring
├── Intervention Customization
│   ├── Character template creation
│   ├── World content modification
│   └── Therapeutic goal setting
└── Progress Monitoring
    ├── Real-time session observation
    ├── Outcome measurement tracking
    └── Clinical note documentation
```

**Therapeutic Content Creation:**
```
Clinical Tools → Content Management → Custom Development
├── Character Template Design
│   ├── Therapeutic archetype creation
│   ├── Clinical goal integration
│   └── Safety parameter definition
├── World Customization
│   ├── Therapeutic scenario development
│   ├── Intervention point placement
│   └── Outcome pathway design
└── Assessment Integration
    ├── Progress measurement tools
    ├── Clinical outcome tracking
    └── Report generation setup
```

#### Data Interactions
- **Input**: Clinical assessments, treatment plans, intervention designs, progress notes
- **View**: Patient dashboards, session analytics, outcome reports, caseload summaries
- **Manage**: Patient assignments, therapeutic content, clinical protocols, safety parameters

#### Permission Levels
- **Full Clinical Access**: Assigned patients, clinical tools, content creation, reporting
- **Administrative Functions**: Caseload management, institutional reporting, compliance monitoring
- **Restricted Access**: Other clinicians' patients (unless shared), administrative settings

#### Success Metrics
- **Clinical Effectiveness**: Patient outcome improvements, treatment goal achievement
- **Efficiency**: Caseload management, documentation time, intervention customization
- **Safety**: Risk identification, crisis intervention, compliance maintenance
- **Professional Development**: Platform proficiency, content creation, outcome optimization

#### Exit Points
- **Session Completion**: Patient discharge, treatment plan completion
- **Shift Transition**: Handoff to colleagues, on-call coverage
- **Administrative Tasks**: Reporting completion, compliance documentation
- **Professional Development**: Training completion, certification updates

---

### 4. PUBLIC USERS - General Audience Exploring Platform

#### Primary Goals
- Explore therapeutic storytelling concepts
- Understand platform capabilities and benefits
- Evaluate suitability for personal or professional use
- Access educational content and resources
- Make informed decisions about platform engagement

#### Entry Points
- **Website Landing Page**: Organic search, direct navigation
- **Marketing Campaigns**: Social media, content marketing, advertisements
- **Educational Content**: Blog posts, webinars, research publications
- **Professional Referrals**: Healthcare providers, educators, researchers

#### Authentication Flow
```
1. Anonymous Browsing (Limited Access)
2. Optional Account Creation:
   - Basic registration for enhanced features
   - Email verification
   - Interest area selection
3. Demo Access:
   - Guided platform tour
   - Sample character creation
   - Limited world exploration
4. Conversion Pathways:
   - Player registration
   - Clinical inquiry
   - Professional interest
```

#### Core Workflows

**Platform Exploration:**
```
Landing Page → Platform Overview → Feature Discovery
├── Educational Content Access
│   ├── Therapeutic storytelling concepts
│   ├── Research and evidence base
│   └── Success stories and testimonials
├── Demo Experience
│   ├── Simplified character creation
│   ├── Sample world exploration
│   └── Basic therapeutic interaction
└── Information Gathering
    ├── Pricing and plans
    ├── Professional resources
    └── Contact and support options
```

**Evaluation and Decision Making:**
```
Demo Experience → Information Review → Decision Point
├── Personal Suitability Assessment
│   ├── Therapeutic needs evaluation
│   ├── Comfort level assessment
│   └── Goal alignment check
├── Professional Evaluation
│   ├── Clinical application review
│   ├── Integration possibilities
│   └── Training requirements
└── Conversion Actions
    ├── Player account creation
    ├── Clinical inquiry submission
    └── Professional consultation request
```

#### Data Interactions
- **Input**: Interest preferences, contact information, feedback surveys
- **View**: Public content, demo experiences, educational resources, pricing information
- **Manage**: Demo progress, information requests, communication preferences

#### Permission Levels
- **Public Access**: Marketing content, educational resources, basic platform information
- **Demo Access**: Limited character creation, sample worlds, basic interactions
- **No Access**: User data, clinical tools, administrative functions, full platform features

#### Success Metrics
- **Engagement**: Time on site, demo completion, content consumption
- **Conversion**: Account creation, inquiry submission, consultation requests
- **Education**: Understanding improvement, concept comprehension, benefit recognition
- **Satisfaction**: Feedback scores, recommendation likelihood, return visits

#### Exit Points
- **Information Gathering Complete**: Decision made, next steps identified
- **Conversion**: Account creation, professional inquiry, clinical consultation
- **Continued Exploration**: Bookmark for later, newsletter subscription
- **Disengagement**: Platform not suitable, needs not met, alternative solutions

---

### 5. DEVELOPERS - Technical Team Building and Maintaining System

#### Primary Goals
- Develop and maintain platform functionality
- Ensure system performance, security, and reliability
- Implement new features and therapeutic capabilities
- Monitor system health and user experience
- Integrate with external systems and APIs
- Maintain code quality and documentation

#### Entry Points
- **Team Onboarding**: New hire integration, role assignment
- **Project Assignment**: Feature development, bug fixes, maintenance tasks
- **System Monitoring**: Performance alerts, error notifications, user reports
- **Development Workflow**: Daily standups, sprint planning, code reviews

#### Authentication Flow
```
1. Developer Account Provisioning
2. Access Level Assignment:
   - Development environment access
   - Production monitoring permissions
   - Code repository access
3. Security Clearance:
   - Background checks (if required)
   - HIPAA compliance training
   - Security protocol acknowledgment
4. Development Environment Setup:
   - Local development configuration
   - Testing environment access
   - Deployment pipeline permissions
```

#### Core Workflows

**Feature Development Cycle:**
```
Requirements → Design → Implementation → Testing → Deployment
├── Requirement Analysis
│   ├── User story review
│   ├── Technical specification
│   └── Acceptance criteria definition
├── Development Process
│   ├── Code implementation
│   ├── Unit testing
│   └── Integration testing
├── Quality Assurance
│   ├── Code review
│   ├── Security assessment
│   └── Performance testing
└── Deployment Pipeline
    ├── Staging deployment
    ├── User acceptance testing
    └── Production release
```

**System Maintenance and Monitoring:**
```
Monitoring Dashboard → Issue Identification → Resolution → Documentation
├── Performance Monitoring
│   ├── System metrics tracking
│   ├── User experience monitoring
│   └── Error rate analysis
├── Issue Resolution
│   ├── Bug investigation
│   ├── Performance optimization
│   └── Security patch application
└── Documentation and Communication
    ├── Change log updates
    ├── Team communication
    └── User impact assessment
```

#### Data Interactions
- **Input**: Code commits, configuration changes, monitoring data, user feedback
- **View**: System metrics, error logs, user analytics, performance dashboards
- **Manage**: Codebase, deployment pipelines, system configurations, documentation

#### Permission Levels
- **Development Access**: Code repositories, development environments, testing systems
- **Production Monitoring**: System metrics, error logs, performance data
- **Administrative Functions**: Deployment controls, system configurations, user management (limited)
- **Restricted Access**: User personal data, clinical information, financial data

#### Success Metrics
- **Code Quality**: Test coverage, bug rates, code review scores
- **System Performance**: Uptime, response times, error rates
- **Feature Delivery**: Sprint completion, user satisfaction, adoption rates
- **Security**: Vulnerability assessments, compliance scores, incident response times

#### Exit Points
- **Task Completion**: Feature delivery, bug resolution, maintenance completion
- **Shift Handoff**: On-call rotation, team transitions, knowledge transfer
- **Project Milestones**: Release completion, sprint endings, milestone achievements
- **Emergency Response**: Critical issue resolution, system recovery, incident closure

---

### 6. ADMINISTRATORS - System Managers and Operations

#### Primary Goals
- Manage overall system operations and user accounts
- Ensure platform security, compliance, and data protection
- Monitor system performance and resource utilization
- Handle user support and issue escalation
- Manage institutional relationships and integrations
- Oversee platform governance and policy enforcement

#### Entry Points
- **Administrative Role Assignment**: Organizational hierarchy, responsibility delegation
- **System Alerts**: Performance issues, security incidents, user escalations
- **Scheduled Tasks**: Regular maintenance, reporting, compliance reviews
- **Strategic Planning**: Platform evolution, feature prioritization, resource allocation

#### Authentication Flow
```
1. Administrative Credential Verification
2. Multi-Factor Authentication Setup
3. Role-Based Access Control Assignment:
   - System administration permissions
   - User management capabilities
   - Compliance monitoring access
4. Security Clearance Validation:
   - Background verification
   - Compliance training completion
   - Policy acknowledgment
5. Administrative Dashboard Configuration
```

#### Core Workflows

**User Account Management:**
```
Admin Dashboard → User Management → Account Operations
├── Account Lifecycle Management
│   ├── User registration approval
│   ├── Account modification/suspension
│   └── Data retention/deletion
├── Access Control Management
│   ├── Permission level assignment
│   ├── Role-based access updates
│   └── Security policy enforcement
└── Support and Escalation
    ├── User issue resolution
    ├── Technical support coordination
    └── Clinical escalation management
```

**System Operations and Monitoring:**
```
Operations Center → System Health → Performance Management
├── Infrastructure Monitoring
│   ├── Server performance tracking
│   ├── Database optimization
│   └── Network security monitoring
├── Compliance Management
│   ├── HIPAA compliance monitoring
│   ├── Data protection audits
│   └── Policy enforcement tracking
└── Reporting and Analytics
    ├── Usage analytics generation
    ├── Performance reporting
    └── Compliance documentation
```

#### Data Interactions
- **Input**: System configurations, user account changes, policy updates, compliance data
- **View**: System-wide analytics, user management dashboards, compliance reports, performance metrics
- **Manage**: User accounts, system settings, security policies, institutional relationships

#### Permission Levels
- **Full System Access**: All user accounts, system configurations, administrative functions
- **Compliance Oversight**: Audit trails, policy enforcement, regulatory reporting
- **Emergency Powers**: System shutdown, security incident response, data protection measures
- **Restricted Clinical Access**: Clinical data only for compliance/support purposes

#### Success Metrics
- **System Reliability**: Uptime, performance consistency, error resolution times
- **User Satisfaction**: Support response times, issue resolution rates, user feedback scores
- **Compliance**: Audit success rates, policy adherence, regulatory requirement fulfillment
- **Security**: Incident response times, vulnerability management, access control effectiveness

#### Exit Points
- **Operational Completion**: Maintenance tasks finished, reports generated, issues resolved
- **Escalation Handoff**: Critical issues transferred to specialists, emergency response activation
- **Scheduled Transitions**: Shift changes, planned maintenance windows, update deployments
- **Strategic Reviews**: Performance assessments, policy updates, system evolution planning

---

## Cross-User Interaction Scenarios

### Patient-Clinician Collaboration
- **Shared Character Development**: Patient creates, clinician reviews and guides
- **Session Monitoring**: Real-time clinical oversight during therapeutic adventures
- **Progress Communication**: Automated reports and manual clinical notes
- **Crisis Intervention**: Immediate clinician notification and response protocols

### Developer-Administrator Coordination
- **Feature Deployment**: Developer implementation with administrator approval and monitoring
- **System Maintenance**: Coordinated downtime, update deployment, rollback procedures
- **Security Incidents**: Developer technical response with administrator policy enforcement
- **Performance Optimization**: Technical improvements with operational impact assessment

### Public-Player Conversion
- **Demo to Full Account**: Seamless transition from exploration to active use
- **Educational Continuity**: Information gathered during exploration informs player setup
- **Support Transition**: Public inquiry escalation to player onboarding support

---

## Testing Scenarios Matrix

### Happy Path Testing
- **Complete User Journeys**: End-to-end workflows for each user type
- **Feature Integration**: Cross-functional capabilities working together
- **Data Flow Validation**: Information correctly passed between system components
- **Permission Verification**: Appropriate access levels maintained throughout journeys

### Edge Case Testing
- **Boundary Conditions**: Maximum character limits, session timeouts, data volume limits
- **Error Recovery**: Network failures, server errors, data corruption scenarios
- **Unusual User Behavior**: Rapid clicking, browser back/forward, multiple tabs
- **System Limits**: Concurrent user limits, resource exhaustion, performance degradation

### Security Testing
- **Authentication Bypass Attempts**: Unauthorized access prevention
- **Data Access Violations**: Cross-user data protection verification
- **Privilege Escalation**: Role-based access control enforcement
- **Data Protection**: HIPAA compliance, privacy settings, data encryption

### Performance Testing
- **Load Scenarios**: Multiple concurrent users, high-volume data processing
- **Stress Testing**: System behavior under extreme conditions
- **Scalability Validation**: Performance maintenance as user base grows
- **Resource Optimization**: Memory usage, database performance, API response times

---

## Implementation Recommendations

### Monitoring and Analytics
- **User Journey Tracking**: Detailed analytics for each user type's path through the system
- **Conversion Funnel Analysis**: Public user to player/patient conversion optimization
- **Clinical Outcome Measurement**: Therapeutic effectiveness tracking and reporting
- **System Performance Metrics**: Real-time monitoring of technical and user experience indicators

### Continuous Improvement
- **User Feedback Integration**: Regular collection and analysis of user experience data
- **A/B Testing Framework**: Systematic testing of interface and workflow improvements
- **Clinical Efficacy Studies**: Ongoing research into therapeutic outcomes and optimization
- **Technical Debt Management**: Regular assessment and resolution of system maintenance needs

This comprehensive user journey matrix provides the foundation for thorough testing, user acceptance criteria development, and system validation across all user categories in the TTA platform.


---
**Logseq:** [[TTA.dev/Docs/Project/User-journey-matrix]]
