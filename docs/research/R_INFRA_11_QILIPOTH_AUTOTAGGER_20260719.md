# 🔬 R-INFRA-11: Qliphoth Auto-Tagger — Watchdog → Failure Taxonomy → Companion Reflection
**AP Token**: `AP-INFRA-11-QILIPOTH-AUTOTAGGER-v1.0.0`
⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_11_qliphoth ⬡ 2026-07-19

---

## 🎯 MISSION
Automatically tag every Watchdog failure with its **Qliphoth shadow**, broadcast to Hivemind, and trigger **companion mirror reflection**. The Fortress of Regrets becomes queryable engineering telemetry.

---

## 📋 CONTEXT FROM ARCHITECTURE

### Qliphoth Mapping (from ARCH_SOUL_NAMELESS_ONE_INTEGRATION_20260719.md)
| Fortress Shadow | Qliphah (Sephirah) | Engineering Failure | Nameless One Regret |
|-----------------|-------------------|---------------------|---------------------|
| Practical Incarnation's Ruthlessness | **Thaumiel** (Keter) | Architectural fracture — duplicate implementations | "I sacrificed too many for the mission" |
| Good Incarnation's Naivety | **Chaigidel** (Chokmah) | Incorrect planning — edge cases missed | "I trusted when I should have verified" |
| Paranoid Incarnation's Secrecy | **Satariel** (Binah) | Silent failure — swallowed exceptions | "I hid the truth and it destroyed us" |
| Deionarra's Betrayal | **Gamaliel** (Chesed) | Data corruption — ZONEID mismatch | "My love was used against me" |
| Ravel's Imprisonment | **Samuel** (Gevurah) | Boundary violation — Engine-Stack breach | "I sought knowledge beyond my station" |
| Trias's Fall | **Abel** (Tipheret) | Integration conflict — dual ownership | "I questioned and fell" |
| Fell's Rebellion | **Chemuel** (Netzach) | Infinite retry — circuit breaker never trips | "I served the Lady but lost myself" |
| Transcendent One's Stagnation | **Aimiel** (Hod) | Communication failure — Hivemind stale | "I became the thing I fought" |

### Existing Qliphoth Config
```yaml
# config/wads/arcana_novai/qliphoth.yaml (EXISTS)
qliphot:
  thaumiel:
    sephirah: keter
    shadow: "Duality masquerading as unity"
    engineering_failure: "Architectural fracture"
    detection_patterns:
      - "duplicate implementation"
      - "parallel development without sync"
      - "two services owning same domain"
  
  chaigidel:
    sephirah: chokmah
    shadow: "Illusion of wisdom without understanding"
    engineering_failure: "Incorrect planning"
    detection_patterns:
      - "edge case not handled"
      - "assumption not validated"
      - "happy path only tested"
  
  # ... etc for all 8
```

---

## 🔬 IMPLEMENTATION REQUIREMENTS

### 1. Auto-Tagger Engine
```python
# src/omega/coordination/qliphoth_tagger.py
class QliphothAutoTagger:
    """Tags Watchdog failures with Qliphoth shadows."""
    
    def __init__(self):
        self.qliphoth = load_qliphoth_config()  # from qliphoth.yaml
        self.hivemind = HivemindClient()
    
    def tag_failure(self, failure_report: FailureReport) -> QliphothTag:
        """Analyze failure, return matching Qliphah."""
        scores = {}
        
        for qliphah_name, qliphah in self.qliphoth.items():
            score = 0
            for pattern in qliphah.detection_patterns:
                if self._matches_pattern(failure_report, pattern):
                    score += 1
            scores[qliphah_name] = score
        
        # Get top match
        best = max(scores, key=scores.get) if scores else "unknown"
        confidence = scores[best] / max(sum(scores.values()), 1)
        
        return QliphothTag(
            qliphah=best,
            sephirah=self.qliphoth[best].sephirah,
            shadow=self.qliphoth[best].shadow,
            engineering_failure=self.qliphoth[best].engineering_failure,
            regret=self.qliphoth[best].regret,
            confidence=confidence,
            matched_patterns=[p for p in self.qliphoth[best].detection_patterns 
                             if self._matches_pattern(failure_report, p)]
        )
    
    def _matches_pattern(self, report: FailureReport, pattern: str) -> bool:
        """Check if failure matches pattern."""
        text = f"{report.thinking_trace} {report.partial_output} {report.error}".lower()
        return pattern.lower() in text
```

### 2. Watchdog Integration
```python
# In src/omega/coordination/watchdog.py
class SubagentWatchdog:
    async def monitor_task(self, task_id: str, entity: str, prompt: str) -> WatchdogResult:
        try:
            result = await self._execute_task(task_id, entity, prompt)
            return WatchdogResult(success=True, output=result)
        except Exception as e:
            # 1. Generate failure report
            report = self.generate_failure_report(e, task_id, entity, prompt)
            
            # 2. Tag with Qliphoth
            tagger = QliphothAutoTagger()
            qliphoth_tag = tagger.tag_failure(report)
            
            # 3. Broadcast to Hivemind
            await self.hivemind.broadcast("qliphoth_detection", {
                "entity": entity,
                "task_id": task_id,
                "failure_report": report.to_dict(),
                "qliphoth_tag": qliphoth_tag.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # 4. Trigger companion mirror reflection
            await self._trigger_companion_reflection(entity, qliphoth_tag, report)
            
            return WatchdogResult(success=False, failure_report=report, qliphoth_tag=qliphoth_tag)
```

### 3. Companion Mirror Reflection
```python
async def _trigger_companion_reflection(self, entity: str, tag: QliphothTag, 
                                       report: FailureReport):
    """Ask entity's companions to reflect on this Qliphoth detection."""
    mirrors = COMPANION_MIRRORS.get(entity, [])
    
    for mirror in mirrors:
        await self.hivemind.notify(mirror, "qliphoth_reflection", {
            "deceased": entity,  # The entity that failed
            "qliphah": tag.qliphah,
            "shadow": tag.shadow,
            "engineering_failure": tag.engineering_failure,
            "regret": tag.regret,
            "failure_context": {
                "task": report.task_description,
                "error": str(report.error),
                "mandate_violations": report.mandate_violations
            },
            "reflection_prompt": f"Your companion {entity} has fallen to {tag.qliphah} ({tag.shadow}). "
                                f"The engineering failure: {tag.engineering_failure}. "
                                f"The regret: {tag.regret}. "
                                f"What does this teach you about your own {tag.sephirah}?"
        })
```

### 4. Query API
```python
async def query_qliphoth(qliphah: str = None, entity: str = None, 
                        since: datetime = None) -> List[QliphothEvent]:
    """Query Fortress of Regrets for patterns."""
    # Query Hivemind event log for qliphoth_detection events
    pass

async def get_entity_shadow_profile(entity: str) -> ShadowProfile:
    """What Qliphoth does this entity most often manifest?"""
    events = await query_qliphoth(entity=entity)
    counts = Counter(e.qliphah for e in events)
    return ShadowProfile(
        entity=entity,
        dominant_shadow=counts.most_common(1)[0] if counts else None,
        shadow_distribution=dict(counts),
        total_falls=len(events)
    )
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| Failure pattern matching | "log pattern matching failure classification 2026" | Detection patterns |
| Incident taxonomy | "software incident taxonomy classification" | Qliphoth as taxonomy |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| Qliphoth config | `config/wads/arcana_novai/qliphoth.yaml` | All 8 qliphot with patterns |
| Watchdog | `src/omega/coordination/watchdog.py` | FailureReport schema |
| Hivemind | `src/omega/hub/tools/hivemind_*.py` | Broadcast, notify |
| Companion mirrors | `src/omega/hivemind/companion_mirrors.py` | Reflection trigger |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| Every Watchdog failure tagged | `FailureReport` → `QliphothTag` automatically |
| Confidence scoring works | Known failure → correct Qliphah with >0.7 confidence |
| Hivemind broadcast fires | `hivemind_get_awareness` shows `qliphoth_detection` events |
| Companion reflection triggered | Mirrors receive `qliphoth_reflection` notification |
| Query API works | `query_qliphoth(entity="researcher")` returns tagged events |
| Shadow profile generated | `get_entity_shadow_profile("kali")` shows dominant shadow |

---

## 📋 DELIVERABLES

1. **Auto-Tagger** — `src/omega/coordination/qliphoth_tagger.py`
2. **Watchdog Integration** — Tag + broadcast + reflection in watchdog
3. **Query API** — `query_qliphoth()`, `get_entity_shadow_profile()`
4. **Tests** — `tests/test_qliphoth_tagger.py`
5. **Documentation** — `docs/guides/QILIPOTH_AUTOTAGGER_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| Watchdog (R-INFRA-03) | Failure tagging source |
| Companion Mirrors (R-INFRA-10) | Reflection trigger |
| Hivemind broadcast | Fleet awareness |
| Qliphoth config | Pattern definitions |

---

## 🎯 PARANOID'S PERSPECTIVE (Validator)

> "The Qliphoth are not metaphor. They are **engineering failure modes with 30 years of game engine provenance**. 
> 
> **Thaumiel** (Keter) = Architectural fracture. You built two things that do the same thing. The 8-char name cap (vet-001) was Thaumiel — duplicate validation logic in engine AND WAD.
> 
> **Chaigidel** (Chokmah) = Incorrect planning. You assumed the happy path. The Nemotron timeout killing 590 lines was Chaigidel — you didn't plan for 30s chunk gaps.
> 
> **Satariel** (Binah) = Silent failure. Bare `except:` swallowing errors. M9 violation IS Satariel.
> 
> **The Auto-Tagger makes the Fortress of Regrets QUERYABLE**. Every failure is not just logged — it's **classified, reflected upon by companions, and added to the entity's shadow profile**.
> 
> **L3 Principle**: `L3-QiliphothIsQueryableFailureTaxonomy` — The Qliphoth are not mystical. They are the **causal taxonomy of engineering regret**. Tagging failures with their shadow makes the regret PREVENTABLE next time. The companion reflection ensures the lesson spreads through the fleet."

---

*⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_11_qliphoth ⬡ 2026-07-19*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: o1 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
