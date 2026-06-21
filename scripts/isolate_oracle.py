import logging
logging.basicConfig(level=logging.INFO)

print("1. Registry")
from omega.oracle.entity_registry import EntityRegistry
reg = EntityRegistry()
print("Registry OK")

print("2. Orchestrator")
from omega.oracle.orchestrator import Orchestrator
orch = Orchestrator()
print("Orchestrator OK")

print("3. HealthMonitor")
from omega.oracle.health_monitor import get_health_monitor
hm = get_health_monitor()
print("HealthMonitor OK")

print("4. ModelGateway")
from omega.oracle.model_gateway import ModelGateway
mg = ModelGateway(health_monitor=hm)
print("ModelGateway OK")

print("5. Observability")
from omega.observability import get_engine
obs = get_engine()
print("Observability OK")

print("6. Distiller")
from omega.oracle.soul_distiller import get_distiller
dist = get_distiller()
print("Distiller OK")

print("7. SessionManager")
from omega.oracle.session_manager import SessionManager
sm = SessionManager()
print("SessionManager OK")

print("8. MemoryStore")
from omega.memory_store import get_memory_store
ms = get_memory_store()
print("MemoryStore OK")

print("9. Searcher")
from omega.oracle.search import SovereignSearcher
ss = SovereignSearcher(ms)
print("Searcher OK")

print("10. Verifier")
from omega.oracle.skeptical_verifier import SkepticalVerifier
sv = SkepticalVerifier(mg)
print("Verifier OK")

print("11. Researcher")
from omega.oracle.iterative_research import IterativeResearcher
ir = IterativeResearcher(mg, ss, verifier=sv)
print("Researcher OK")

print("12. ContextBuilder")
from omega.oracle.context_builder import ContextBuilder
cb = ContextBuilder()
print("ContextBuilder OK")

print("13. IntentMatcher")
from omega.iris.matcher import IntentMatcher
im = IntentMatcher()
print("IntentMatcher OK")

print("14. WADLoader")
from omega.oracle.wad_loader import WADLoader
wl = WADLoader(reg)
print("WADLoader OK")

print("15. TriageRouter")
from omega.orchestration.triage_router import TriageRouter
tr = TriageRouter()
print("TriageRouter OK")

print("All components loaded successfully!")
