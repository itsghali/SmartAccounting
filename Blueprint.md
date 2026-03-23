# Accountech Blueprint
## Rewritten to Align with the GitHub Repo
### Accounting Platform First, AI Layer Second

---

## 1. Project Overview & Vision

### 1.1 Core Objective
Build a cloud-native accounting platform for Moroccan accounting firms that serves as the **system of record** for accounting operations, multi-dossier management, reporting, and compliance.

The platform starts by solving the most critical operational need: a modern, integrated accounting foundation designed for Moroccan workflows. Once this core is reliable and adopted, the product expands into payroll, commercial operations, and an AI automation layer.

### 1.2 Product Philosophy
The project is based on a simple principle:

**Accounting is the foundation. AI is the acceleration layer.**

The platform must first be trusted for:

- journal management
- accounting entries
- VAT handling
- fiscal years
- ledgers and trial balance
- balance sheet and CPC
- multi-dossier operations
- auditability and traceability

Only after this foundation is stable should AI automate document-heavy and repetitive workflows.

### 1.3 Target User
Primary target:

- Moroccan accounting firms
- fiduciaries
- multi-client accounting structures managing multiple dossiers

Secondary target over time:

- SMEs that need a localized accounting platform
- multi-entity businesses requiring centralized operations

### 1.4 Vision
The long-term vision is to become the **operating platform for accounting firms in Morocco**:

- first as the trusted accounting system of record
- then as the unified platform for payroll and operational workflows
- finally as an intelligent platform powered by specialized AI agents

### 1.5 Strategic Direction
The roadmap is intentionally phased:

- Phase 1: Core accounting platform
- Phase 2: Moroccan payroll integration
- Phase 3: Commercial and invoicing operations
- Phase 4: AI-powered automation and reporting assistance

This sequencing protects product quality, regulatory correctness, and user trust.

---

## 2. Strategic Partnership Model

### 2.1 Role of the Accounting Partner
The accounting firm partner is not only a future customer. It is a validation and workflow partner.

Its role is to provide:

- real accounting workflows
- dossier structures
- Moroccan accounting logic
- validation of screens, flows, and outputs
- feedback on adoption blockers
- test scenarios for real production-like conditions

### 2.2 What the Partner Helps Validate
The partner contributes to:

- how dossiers are structured
- how entries are created and reviewed
- how VAT and reporting are handled in practice
- how accountants navigate between clients and fiscal periods
- how documents are linked to accounting operations
- where future AI can remove repetitive work safely

### 2.3 What the Partner Does Not Replace
The partner is not a substitute for product design or engineering.

The product team remains responsible for:

- platform architecture
- workflow design
- product prioritization
- technical implementation
- infrastructure and security
- AI layer design

### 2.4 Commercial Value of the Partnership
The partnership provides:

- early workflow validation
- pilot deployment conditions
- product credibility
- a practical path to early adoption
- a foundation for future referrals to similar firms

---

## 3. Market Positioning & Opportunity

### 3.1 The Problem
Moroccan accounting firms still work across fragmented environments:

- accounting software
- payroll tools
- invoicing tools
- spreadsheets
- paper-based document flows

This creates:

- duplicate entry
- weak traceability
- poor cross-module consistency
- slow execution
- operational pressure during reporting periods

### 3.2 The Opportunity
Accounting firms sit at the center of business administration for a large part of the economy. Improving accountant productivity creates downstream efficiency across compliance, payroll, reporting, invoicing, and document handling.

### 3.3 Product Positioning
Accountech is positioned as:

- a vertical SaaS platform
- built for accounting firms first
- natively adapted to Moroccan workflows
- designed for multi-dossier operations
- capable of becoming the firm’s operational backbone

### 3.4 Strategic Differentiation
The differentiation is not just “AI”.

It is the combination of:

- Moroccan accounting logic
- unified workflows
- cloud-native architecture
- multi-dossier scalability
- future AI automation built on trusted accounting data

---

## 4. Product Scope

### 4.1 Platform Core
The platform core includes:

- user authentication
- role-based access control
- firm-level and dossier-level permissions
- multi-tenant architecture
- multi-dossier management
- multi-company support
- audit logs
- document linkage
- structured reporting
- reliable accounting database design

### 4.2 Core Accounting Scope
The first product scope is accounting.

This includes:

- chart of accounts support
- journals
- accounting entries
- fiscal years and periods
- VAT workflows
- fixed assets
- general ledger
- trial balance
- balance sheet
- CPC
- basic tax and reporting outputs
- exports and printable reports

### 4.3 Later Modules
After the accounting foundation is stable, the platform expands to include:

- payroll
- employee records
- declarations and deductions
- commercial operations
- quotations, orders, invoices, payments
- customer and product records
- basic stock support

### 4.4 AI Layer
AI is a later, structured extension that sits on top of platform data and workflows.

It should support:

- document intake
- OCR and extraction
- classification
- entry suggestions
- validation and anomaly detection
- reporting assistance

AI does not replace the accounting platform. It enhances it.

---

## 5. Regulatory & Domain Requirements

### 5.1 Compliance as Foundation
The product must be designed as regulated operational infrastructure, not as a lightweight business tool.

It must support Moroccan accounting requirements including:

- PCM / Moroccan accounting logic
- VAT handling
- fiscal reporting consistency
- payroll-related obligations in later phases
- auditability of operations
- traceable user actions and corrections

### 5.2 Domain Integrity
The product must ensure:

- accounting balance consistency
- traceable corrections
- clear review flows
- document-to-entry linkage where applicable
- controlled permissions
- reliable reporting outputs

### 5.3 Why This Matters
In accounting software, correctness is more important than novelty.

The product only earns trust if it is:

- legally coherent
- operationally stable
- understandable by accountants
- dependable during reporting cycles

---

## 6. Technical Architecture

### 6.1 Core Architecture Principle
The architecture must support the accounting platform first.

This means prioritizing:

- structured accounting data
- transactional integrity
- multi-tenant isolation
- auditability
- modular expansion
- future AI integration points

### 6.2 Recommended Architecture
A modern architecture can include:

- frontend for firm and dossier workflows
- backend API for accounting logic and platform operations
- PostgreSQL for core transactional data
- object/document storage for attachments
- background job processing for heavy tasks
- monitoring, backups, and observability
- modular AI services introduced progressively

### 6.3 AI Readiness Without AI Dependency
The system should be designed so that:

- documents can be stored and linked before OCR exists
- entries can be created manually before AI suggestions exist
- reports can be generated from structured accounting data without AI
- AI can later consume trusted platform data rather than substitute for it

That is the correct dependency order.

---

## 7. Data Model Strategy

### 7.1 Core Data Principles
The database must reflect accounting reality first.

Core entities should include:

- firms
- users
- roles and permissions
- dossiers
- fiscal years
- journals
- entries
- entry lines
- accounts
- VAT logic
- fixed assets
- reporting structures
- documents
- audit logs

### 7.2 Data Model Objective
The data model should allow the same data to serve multiple purposes:

- booking
- review
- reporting
- document traceability
- future payroll/commercial integration
- future AI automation

### 7.3 AI Layer Dependency
The AI layer should consume and enrich this data model, not define it.

That is why the accounting schema comes first.

---

## 8. Implementation Roadmap

### 8.1 Phase 1 - Core Accounting MVP
Goal: build a compliant accounting platform that accountants can actually use.

Deliverables:

- tenant and dossier setup
- user roles and access control
- journals and entries
- fiscal year workflows
- VAT handling
- ledger and trial balance
- balance sheet and CPC
- audit logs
- document attachment basics
- core reporting

### 8.2 Phase 2 - Stabilization & Adoption
Goal: strengthen product quality and real-world usability.

Deliverables:

- workflow refinements
- faster navigation across dossiers
- reporting improvements
- import/export helpers
- corrections and review flows
- stronger deployment and monitoring

### 8.3 Phase 3 - Payroll Module
Goal: expand into payroll while keeping accounting integration native.

Deliverables:

- employee records
- payroll calculations
- deductions and declarations
- payslips
- links between payroll and accounting

### 8.4 Phase 4 - Commercial Module
Goal: unify invoicing and operational flows.

Deliverables:

- customers
- products
- quotations
- invoices
- payments
- basic stock operations
- accounting linkage

### 8.5 Phase 5 - AI Layer Deployment
Goal: automate repetitive accounting workflows safely.

Deliverables:

- document intake
- OCR and extraction
- classification
- accounting suggestions
- validation checks
- reporting assistance

---

## 9. What to Build First

### 9.1 Immediate Build Priorities
Before anything AI-heavy, the first build priorities should be:

- dossier structure
- accounting data model
- journal and entry workflows
- VAT logic
- trial balance and reporting outputs
- audit logging
- document linkage
- role-based access

### 9.2 Why This Order Matters
Without a trusted platform core:

- AI has nowhere reliable to write
- suggested entries cannot be validated properly
- reporting outputs are not dependable
- the product remains a document tool, not a business platform

### 9.3 Success Condition
The first success milestone is not “the AI works”.

It is:

> accountants can manage real accounting workflows on the platform with confidence.

---

## 10. Requirements Gathering Framework

### 10.1 Functional Validation Areas
Requirements gathering should focus first on accounting platform workflows, not AI prompts.

Priority areas:

- dossier creation and lifecycle
- journal structure
- entry creation and validation
- VAT processing
- reporting expectations
- correction flows
- document attachment needs
- access permissions
- period closing practices

### 10.2 Secondary AI Discovery
Only after this should AI-specific requirements be structured around:

- document types
- extraction fields
- classification expectations
- common correction patterns
- confidence thresholds
- reviewer workflows

### 10.3 Principle
Do not ask firms what AI they want before understanding how they actually work.

---

## 11. AI Layer Design

### 11.1 Role of AI in the Product
The AI layer is a progressive extension designed to reduce repetitive work inside the accounting platform.

It is not the product’s foundation.

### 11.2 Agent-Based AI Layer
The AI layer can be structured through specialized agents:

**Document Intake Agent**  
Receives raw files and prepares them for processing and linking to dossiers.

**OCR & Extraction Agent**  
Transforms scans or images into structured fields.

**Classification Agent**  
Identifies document type and routes it to the correct accounting workflow.

**Accounting Engine Agent**  
Proposes journal entries based on Moroccan accounting rules and platform context.

**Validation Agent**  
Checks for balance issues, anomalies, duplicates, missing logic, and sequence inconsistencies.

**Reporting Agent**  
Supports generation of accounting outputs from validated structured data.

### 11.3 Dependency Rule
These agents should operate on top of:

- existing dossiers
- structured accounts
- journals
- reporting logic
- audit trails
- document relationships

That is why AI comes second.

### 11.4 Human-in-the-Loop
AI outputs should be:

- reviewable
- traceable
- correctable
- confidence-scored
- progressively improvable through feedback

---

## 12. Go-to-Market Strategy

### 12.1 Entry Strategy
The go-to-market strategy begins with accounting firms because they have:

- repetitive high-volume workflows
- multi-dossier needs
- immediate productivity pain
- strong value from integrated operations

### 12.2 Adoption Strategy
Adoption should follow a trust-driven path:

- deploy the accounting core first
- validate reliability in real workflows
- expand module by module
- introduce AI only where trust is already established

### 12.3 Sales Narrative
The strongest commercial message is not “we use AI”.

It is:

> we modernize and unify your accounting operations, then automate the repetitive layers.

That is a much stronger and more credible story.

---

## 13. Business Model

### 13.1 Core Revenue Logic
The product should be monetized first as a SaaS accounting platform.

Possible charging dimensions:

- firm subscription
- number of dossiers
- user seats
- premium reporting features
- advanced modules such as payroll or commercial

### 13.2 AI Monetization
The AI layer can later become a premium add-on based on:

- processed documents
- AI-assisted workflows
- automation volume
- premium validation/reporting services

### 13.3 Strategic Benefit
This creates a healthier business model than AI-first pricing because the platform has core recurring value even before automation upsell.

---

## 14. Financial Logic

### 14.1 Build Logic
The financial model should reflect a phased build:

- first investment for accounting MVP and core platform
- second layer for payroll and commercial expansion
- later layer for AI deployment and optimization

### 14.2 Why This Is More Credible
This approach is easier to defend because it aligns spending with product maturity.

You are not funding the full vision on day one.  
You are funding a platform that expands in controlled layers.

### 14.3 Investor Interpretation
This is not a simple software build. It is the creation of a long-term vertical SaaS asset with regulated domain depth and future automation leverage.

---

## 15. Incubator / Investor Positioning

### 15.1 Core Story
The strongest pitch is:

- large operational pain
- fragmented legacy tools
- accounting firms as a structurally important market
- Moroccan localization as a moat
- platform scalability through multi-dossier architecture
- AI as a second-stage multiplier

### 15.2 Better Than an AI-Only Story
An AI-only pitch can sound fragile.

A platform-first story is stronger because it says:

- we own the workflow
- we own the data model
- we own the user environment
- then we automate it

That creates a much more defensible business.

### 15.3 Expansion Logic
Regional expansion should only be discussed after local product-market fit and regulatory solidity in Morocco.

---

## 16. Legal, Privacy & Compliance

### 16.1 Core Requirements
The product must include:

- secure document storage
- access control
- audit trails
- backup and recovery
- controlled data processing
- privacy-safe handling of accounting and payroll data

### 16.2 AI-Specific Controls
As AI is added, additional care is required for:

- document handling
- extraction logs
- correction history
- model output traceability
- confidence-driven review workflows

### 16.3 Platform Principle
Compliance is easier to manage when AI is introduced on top of a controlled system rather than as a loose external process.

---

## 17. Risk Mitigation

### 17.1 Product Risk
Risk: trying to build too much too early.  
Mitigation: keep accounting core as the first milestone.

### 17.2 Trust Risk
Risk: users do not trust automation.  
Mitigation: establish trust through correct accounting workflows first, then add reviewable AI.

### 17.3 Technical Risk
Risk: AI complexity slows delivery.  
Mitigation: do not block core platform delivery on AI maturity.

### 17.4 Market Risk
Risk: firms resist change.  
Mitigation: start with real partners, strong migration logic, and visible operational gains.

### 17.5 Strategic Risk
Risk: the product becomes an OCR tool instead of a platform.  
Mitigation: keep the system of record at the center of every roadmap decision.

---

## 18. Immediate Action Items

### 18.1 Product
Define the accounting MVP precisely:

- dossiers
- journals
- entries
- VAT
- reporting
- documents
- audit logs
- access control

### 18.2 Technical
Lock the platform architecture for:

- multi-tenant SaaS
- transactional integrity
- document linkage
- modular expansion
- future AI service integration

### 18.3 Partner Work
Run structured sessions with the accounting partner focused on:

- accounting workflows
- dossier lifecycle
- review/correction logic
- reporting expectations
- future automation priorities

### 18.4 AI Preparation
Prepare AI only after the core is modeled correctly:

- define document types
- identify extraction targets
- map accounting suggestion opportunities
- define validation rules
- design reviewer workflows

### 18.5 Strategic Message
From now on, the official narrative should be:

> Accountech is a Moroccan accounting platform first.  
> AI is a progressive layer that automates repetitive accounting workflows once the platform foundation is in place.
