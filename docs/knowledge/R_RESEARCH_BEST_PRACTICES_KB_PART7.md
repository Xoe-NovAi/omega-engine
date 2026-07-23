# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-KB-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22

---

## §8 Living Document Maintenance and Evolution

### 8.1 The Living Document Principle

This guide itself follows the **living document principle** from Golchian 2026: "The spec is versioned like code because it is code's source of truth. When an incident teaches you something, the fix goes in the spec, not just the implementation, so the next generation inherits the lesson."

#### 8.1.1 Versioning Strategy
- **Format**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Incompatible changes, breaking changes to the framework
- **MINOR**: Backward-compatible feature additions, significant improvements
- **PATCH**: Backward-compatible bug fixes, minor clarifications, typo fixes
- **Current Version**: v1.0.0 (Initial release)

#### 8.1.2 Change Log Format
All versions of this document must maintain a change log at the end:

```yaml
## 📜 Change Log

| Version | Date       | Description                                                                 |
|---------|------------|-----------------------------------------------------------------------------|
| v1.0.0  | 2026-07-22 | Initial release - Integrated 8 authoritative sources (2024-2026)            |
|         |            | - Created research job specification template                               |
|         |            | - Defined context engineering rules and techniques                          |
|         |            | - Established tool design principles                                        |
|         |            | - Outlined execution patterns and decision rules                            |
|         |            | - Detailed quality gates and evaluation framework                           |
|         |            | - Mapped integration with Omega Engine processes                            |
|         |            | - Established living document maintenance procedures                        |
| v1.1.0  | [FUTURE]   | [Example: Added insights from Q3 2026 research jobs]                        |
| v1.2.0  | [FUTURE]   | [Example: Integrated new LLM agent frameworks]                              |
```

#### 8.1.3 Update Triggers
Update this guide when:

| Trigger | Example | Update Type |
|---------|---------|-------------|
| **Process Incident** | Research job failed due to missing context engineering | PATCH: Add specific context rule |
| **New Best Practice** | Discovered superior tool design pattern | MINOR: Add new tool design principle |
| **Framework Change** | Adopted new research methodology standard | MAJOR: Overhaul execution patterns |
| **Regulatory Change** | New mandate interpretation affects research | MINOR: Update mandate alignment guidance |
| **Tool Evolution** | New version of research tool with breaking changes | PATCH: Update tool descriptions |
| **Lesson Learned** | Multiple research jobs showed same improvement opportunity | MINOR: Add new guideline based on pattern |
| **Stakeholder Feedback** | Verity/Kali/MaKaLi suggest improvement | PATCH/MINOR: Based on feedback severity |

#### 8.1.4 Update Process
1. **Identify Need**: Incident, observation, feedback, or new learning
2. **Draft Update**: Write proposed changes using same format as this guide
3. **Human Review**: 
   - Technical updates: @maat (P3) review
   - Compliance updates: @verity review
   - Architecture updates: @kali review
   - Soul-related updates: @john_carmack review
4. **Version Bump**: Determine appropriate version increase (PATCH/MINOR/MAJOR)
5. **Update Change Log**: Add entry with version, date, description
6. **Update Document**: Apply changes to guide
7. **Verify**: Run `make doc-llm-validate` to ensure Doc Standards compliance
8. **Commit**: Git commit with descriptive message
9. **Notify**: Inform relevant stakeholders of update

### 8.2 Contribution Model

This guide follows an **open contribution model** within the Omega Engine team:

#### 8.2.1 Who Can Contribute
- **Primary Contributors**: @researcher (maintainer), @maat (P3), @verity, @kali, @john_carmack
- **Secondary Contributors**: Any Omega Engine team member with relevant expertise
- **Contribution Types**: 
  - Corrections (typos, inaccuracies, outdated info)
  - Improvements (clarifications, examples, better explanations)
  - Additions (new sections, techniques, principles)
  - Removals (obsolete, redundant, or incorrect content)

#### 8.2.2 Contribution Workflow
```mermaid
flowchart TD
    A[Identify Improvement Opportunity] --> B[Fork/Clone Repository]
    B --> C[Create Feature Branch: research/bp-update-[description]]
    C --> D[Make Changes to Guide]
    D --> E[Run make doc-llm-validate]
    E -->|Fail| F[Fix Doc Standards Issues]
    E -->|Pass| G[Run Tests if Applicable]
    G -->|Pass| H[Create Pull Request]
    H --> I[Required Reviews: ]
    I --> I1[@maat (P3) for technical]
    I --> I2[@verity for compliance]
    I --> I3[@kali for architecture]
    I --> I4[@john_carmack for soul-related]
    I --> I5[@researcher as maintainer]
    I --> I6[Optional: Subject matter experts]
    I --> J[Address Review Feedback]
    J --> K[Update Change Log with new version]
    K --> L[Update Document]
    L --> M[Run Final Validation]
    M -->|Pass| N[Merge to Main Branch]
    M -->|Fail| N[Fix Issues and Repeat]
    N --> O[Notify Stakeholders of Update]
```

#### 8.2.3 Contribution Guidelines
- **Small Changes** (PATCH): Typos, clarifications, minor additions → Direct contribution after self-review
- **Medium Changes** (MINOR): New sections, significant improvements → Requires at least one relevant reviewer
- **Large Changes** (MAJOR): Framework overhauls, major restructuring → Requires all relevant reviewers + @researcher approval
- **All Changes**: Must pass `make doc-llm-validate`
- **All Changes**: Must update Change Log with appropriate version bump
- **All Changes**: Must include rationale in PR description explaining why change is needed

### 8.3 Knowledge Preservation and Transfer

#### 8.3.1 Onboarding New Researchers
New team members should:
1. Read this guide in its entirety
2. Complete a shadow research job under supervision
3. Conduct their first research job with mentorship
4. Participate in after-action review to provide feedback on the guide
5. Suggest improvements based on their fresh perspective

#### 8.3.2 Knowledge Transfer Sessions
Schedule regular knowledge transfer:
- **Monthly**: 30-minute "Research Job Tip of the Month" session
- **Quarterly**: 1-hour deep dive on a specific section (e.g., "Context Engineering Deep Dive")
- **Annually**: 4-hour workshop on research job best practices (part of onboarding)
- **Ad-hoc**: When new techniques or tools are discovered

#### 8.3.3 Research Job Apprenticeship Model
For complex research jobs:
1. **Observer Phase**: New researcher shadows experienced researcher
2. **Assistant Phase**: New researcher handles sub-tasks under supervision
3. **Lead Phase**: New researcher leads research job with mentorship
4. **Independent Phase**: New researcher conducts research jobs independently
5. **Mentor Phase**: Experienced researcher mentors others (paying it forward)

### 8.4 Measuring Guide Effectiveness

Track these metrics to assess the guide's effectiveness:

#### 8.4.1 Adoption Metrics
- **Spec Usage Rate**: Percentage of research jobs that begin with a proper spec
- **Template Compliance**: Percentage of specs that follow the template
- **Acceptance Check Usage**: Percentage of jobs that define acceptance checks first
- **Context Engineering Usage**: Percentage of jobs that apply context engineering rules

#### 8.4.2 Quality Metrics
- **First-Pass Quality Gate Rate**: Percentage of research jobs that pass all quality gates on first attempt
- **Rework Rate**: Percentage of research jobs requiring significant rework
- **Spec Update Frequency**: How often specs are updated during execution (lower is better after initial learning)
- **Stakeholder Satisfaction**: Satisfaction scores from consumers of research outputs

#### 8.4.3 Efficiency Metrics
- **Average Time to Completion**: Average time from spec approval to research completion
- **Estimate Accuracy**: How close actual time/effort is to estimates
- **Token Efficiency**: Average token cost per unit of research value delivered
- **Knowledge Reuse Rate**: How often research outputs are referenced in subsequent work

#### 8.4.4 Impact Metrics
- **Mandate Compliance Improvement**: Improvement in M5, M11, M14, M17, M21 compliance rates
- **Capability Enablement**: Number of new capabilities enabled by research
- **Technical Debt Reduction**: Reduction in research-related technical debt
- **Innovation Rate**: Number of novel approaches or techniques discovered

#### 8.4.5 Collection Methods
- **Automatic**: Git history, CI/CD pipelines, metrics collection
- **Semi-Automatic**: Surveys, questionnaires, usage tracking
- **Manual**: Periodic audits, stakeholder interviews, quality gate audits

### 8.5 Future Evolution

This guide will evolve as the Omega Engine ecosystem evolves. Anticipated future directions include:

#### 8.5.1 Integration with Emerging LLM Techniques
- **Context Length Increases**: Adapting to 1M+ token context windows
- **New Architectures**: Mixture of Experts (MoE), State Space Models (SSMs)
- **New Paradigms**: Agentic workflows, tool use, reasoning traces
- **New Tools**: Advanced retrieval, reasoning engines, verification systems

#### 8.5.2 Enhanced Automation
- **Spec Generation**: AI-assisted spec writing from high-level intent
- **Context Engineering Automation**: Automatic context management and compression
- **Tool Selection**: AI-recommended tool selection based on task characteristics
- **Quality Gate Automation**: More sophisticated automated quality checking

#### 8.5.3 Deeper Omega Integration
- **Soul-Guided Research**: Using soul.yaml principles to guide research priorities
- **Mandate-Driven Research**: Automatic research job generation from mandate gaps
- **Research-to-Action Pipeline**: Fully automated promotion of research outputs to soul.yaml/enhancements
- **Predictive Research**: Using past research to predict future needs

#### 8.5.4 Community and Open Source Contributions
- **External Contributions**: Incorporating best practices from external research communities
- **Standards Alignment**: Aligning with emerging AI agent standards (when they emerge)
- **Open Source Sharing**: Sharing non-proprietary sections with broader community
- **Feedback Loops**: Incorporating lessons from external users and contributors

#### 8.5.5 Advanced Evaluation Techniques
- **Longitudinal Studies**: Tracking research job effectiveness over months/years
- **A/B Testing**: Comparing different research approaches on same problems
- **Predictive Validity**: Measuring how well research predicts future outcomes
- **ROI Measurement**: Quantifying return on research investment in tangible terms

### 8.6 Final Reminders

#### 8.6.1 The Core Message
> **Spec-driven, context-engineered, quality-gated research is not optional—it's how we build sovereign agents.**

#### 8.6.2 The Three Non-Negotiables
1. **Start with a spec** (written backward from acceptance checks)
2. **Engineer the context** (write conclusions, don't dump raw text)
3. **Pass all quality gates** (Temple-Grade, Doc Standards, Mandate alignment, etc.)

#### 8.6.2 The Living Mindset
- Treat this guide as a living document—update it when you learn
- Treat research specs as living documents—update them when you learn
- Treat research as a continuous learning process—not a one-time task
- Remember: The goal is not just to produce research outputs, but to continuously improve our research capability

#### 8.6.3 Your Role in the Ecosystem
Every research job you design and execute:
- Contributes to the collective wisdom of the Omega Engine
- Improves the capability of our agent fleet
- Reduces technical debt and increases sovereignty
- Makes the next research job easier for someone else
- Helps us fulfill our mission: *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

## 📜 Change Log

| Version | Date       | Description                                                                 |
|---------|------------|-----------------------------------------------------------------------------|
| v1.0.0  | 2026-07-22 | Initial release - Integrated 8 authoritative sources (2024-2026)            |
|         |            | - Created research job specification template                               |
|         |            | - Defined context engineering rules and techniques                          |
|         |            | - Established tool design principles                                        |
|         |            | - Outlined execution patterns and decision rules                            |
|         |            | - Detailed quality gates and evaluation framework                           |
|         |            | - Mapped integration with Omega Engine processes                            |
|         |            | - Established living document maintenance procedures                        |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22*
*This guide is the single source of truth for autonomous agent research job design best practices in the Omega Engine ecosystem.*
*All research outputs must be written to `docs/research/` or `docs/strategy/` per Doc Standards.*
*This is a living document. Updates must be made via PR with spec-driven changes.*