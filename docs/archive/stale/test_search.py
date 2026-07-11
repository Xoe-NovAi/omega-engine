import asyncio
from omega.oracle.sovereign_search_service import SovereignSearchService
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.health_monitor import get_health_monitor

async def main():
    service = SovereignSearchService(
        model_gateway=ModelGateway(health_monitor=get_health_monitor())
    )
    print("Testing T1 (SearXNG)...")
    try:
        res = await service._tier_1_searxng("test", 5)
        print(f"T1 Result: {res}")
    except Exception as e:
        print(f"T1 Failed: {e}")

    print("\nTesting T2 (Exa)...")
    try:
        res = await service._tier_2_exa("test", 5)
        print(f"T2 Result: {res}")
    except Exception as e:
        print(f"T2 Failed: {e}")

    print("\nTesting T3 (Firecrawl)...")
    try:
        res = await service._tier_3_firecrawl("test", 5)
        print(f"T3 Result: {res}")
    except Exception as e:
        print(f"T3 Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
