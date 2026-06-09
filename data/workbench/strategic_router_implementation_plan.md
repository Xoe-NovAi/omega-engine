# 🔱 STRATEGIC ROUTER IMPLEMENTATION PLAN (PROPOSAL)
# ⬡ OMEGA ⬡ RESEARCHER ⬡ WORKBENCH ⬡ PHASE-II

**Status**: PROPOSED (Awaiting Overseer Review)
**Target**: Implementation of the Hybrid (C) Classifier for the Strategic Router.
**Reference**: `data/coordination/cline-m3/STRATEGIC_ROUTER_SPEC.md`

## 🎯 Objective
Implement the "Hybrid (C) Classifier" as defined in the Strategic Router Specification. This involves a two-stage routing process:
1. **Stage 1 (Rule Engine)**: High-speed, low-cost regex/keyword matching.
2. **Stage 2 (IntentMatcher Fallback)**: Semantic classification for complex/ambiguous queries.

This implementation must support **Model-Class Mapping** for automatic failover and integrate with the existing `EntityRegistry` and `ModelGateway`.

## 🔍 Gap Analysis & Research Findings

### 1. The Hybrid Architecture
The design calls for a pre-processor layer that sits before the `TriageRouter`.
- **Rule Engine**: Needs to be implemented as a lightweight, regex-based matcher.
- **IntentMatcher**: Needs to be a semantic fallback that uses the `ModelGateway` to perform intent classification.

### 2. Model-Class Mapping (The Failover Mechanism)
Instead of a strict 1:1 mapping (`Entity` $\rightarrow$ `Model`), we will implement a `Class` mapping.
- **Concept**: Entities are assigned to a `ModelClass` (e.g., `fast-chat`, `reasoning-heavy`, `vision-expert`).
- **Failover**: If the primary model for a class is unavailable, the `ModelGateway` automatically selects the next best model in that class.

### 3. Configuration Schema (`config/strategic_routing.yaml`)
The routing logic and class mappings will be defined in a new configuration file.
```yaml
routing:
  classes:
    fast-chat:
      models: [qwen3-1.7b, gemma-4-2b]
      fallback: qwen3-1.7b
    reasoning-heavy:
      models: [deepseek-r1-8b, claude-sonnet-4.6]
      fallback: deepseek-r1-8b
  
  rules:
    - name: urgent_request
      type: keyword
      pattern: "(?i)(urgent|asap|immediately)"
      target_class: fast-chat
    - name: technical_query
      type: semantic
      threshold: 0.8
      target_class: reasoning-heavy
```

## 🛠️ Proposed Implementation Roadmap

### Phase A: Foundation (The Rule Engine)
- [ ] **Task A.1**: Implement `src/omega/oracle/routing/rule_engine.py`.
- [ ] **Task A.2**: Add `strategic_routing.yaml` to the configuration stack.
- [ ] **Task A.3**: Update `EntityRegistry` to support the `strategy` and `model_class` fields.

### Phase B: The Fallback (IntentMatcher Integration)
- [ ] **Task B.1**: Implement `src/omega/oracle/routing/intent_matcher.py`.
- [ ] **Task B.2**: Integrate `IntentMatcher` into the `Oracle.talk()` flow as a fallback.
- [ ] **Task B.3**: Implement the "Decision Path" logging (e.g., `route_type: rule_match` vs `route_type: semantic_fallback`).

### Phase C: The Failover (Model-Class Mapping)
- [ ] **Task C.1**: Update `ModelGateway` to support class-based selection and automatic failover.
- [ ] **Task C.2**: Implement the `ModelClass` abstraction in `src/omega/oracle/model_gateway.py`.

### Phase D: Verification
- [ ] **Task D.1**: Add unit tests for `RuleEngine` and `IntentMatcher`.
- [ ] **Task D.2**: Add integration tests for the full Hybrid routing flow.
- [ ] **Task D.3**: Verify failover behavior via `make test`.

## 🧪 Testing Strategy
- **Unit Tests**: Test regex patterns, semantic thresholds, and class selection logic in isolation.
- **Integration Tests**: Simulate a request that matches a rule, a request that requires semantic fallback, and a request where the primary model in a class is unavailable.
- **Performance Benchmarks**: Measure the latency overhead of the Rule Engine vs. the Semantic Fallback.

---
**Note to Overseer**: This plan is a high-level blueprint. Detailed code implementations will be provided in subsequent workbench updates for your review.
