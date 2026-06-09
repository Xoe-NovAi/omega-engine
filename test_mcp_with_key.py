import subprocess
import json
import os

def test_mcp():
    env = os.environ.copy()
    env['FIRECRAWL_API_KEY'] = os.environ.get('FIRECRAWL_API_KEY', 'your-api-key-here')

    process = subprocess.Popen(
        ['npx', '-y', 'firecrawl-mcp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    process.stdin.write(json.dumps(init_request) + '\n')
    process.stdin.flush()

    try:
        response = process.stdout.readline()
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()

if __name__ == '__main__':
    test_mcp()
