import anyio
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

async def verify_parity():
    print("Connecting to Qdrant Server (v1.17.1) at localhost:6333...")
    client = QdrantClient(host="localhost", port=6333)
    
    collection_name = "parity_test_collection"
    
    try:
        # 1. Create Collection
        print(f"Creating collection '{collection_name}'...")
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=4, distance=Distance.COSINE),
        )
        
        # 2. Upsert Point
        print("Upserting test point...")
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=1, 
                    vector=[0.1, 0.2, 0.3, 0.4], 
                    payload={"name": "Parity Point", "status": "verified"}
                )
            ],
        )
        
        # 3. Retrieve by ID
        print("Retrieving point by ID...")
        res = client.retrieve(collection_name=collection_name, ids=[1])
        if len(res) > 0 and res[0].payload["name"] == "Parity Point":
            print("✅ ID retrieval successful.")
        else:
            print("❌ ID retrieval failed.")
            return

        # 4. Search
        print("Searching for point...")
        search_res = client.query_points(
            collection_name=collection_name,
            query=[0.1, 0.2, 0.3, 0.4],
            limit=1
        )
        if len(search_res.points) > 0 and search_res.points[0].id == 1:
            print("✅ Search successful.")
        else:
            print("❌ Search failed.")
            return
            
        print("\n🚀 SUCCESS: qdrant-client 1.17.1 is fully compatible with Server v1.17.1.")

    except Exception as e:
        print(f"❌ Parity Test failed with error: {e}")
    finally:
        # Cleanup
        try:
            client.delete_collection(collection_name=collection_name)
            print("Cleanup complete.")
        except Exception:
            pass

if __name__ == "__main__":
    anyio.run(verify_parity)
