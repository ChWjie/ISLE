import requests

# Test backend API
try:
    # 1. Test root endpoint
    resp = requests.get("http://localhost:8000/")
    print(f"✓ Root endpoint: {resp.status_code}")
    print(f"   Response: {resp.json()}")

    # 2. Test agents endpoint
    resp = requests.get("http://localhost:8000/api/v1/agents")
    print(f"\n✓ Agents endpoint: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Data structure: {data}")
        if 'data' in data and isinstance(data['data'], list):
            print(f"   Total agents: {len(data['data'])}")
            if data['data']:
                print(f"   First agent: {data['data'][0]['name']}")
        else:
            print(f"   Unexpected data format")
    else:
        print(f"   Error: {resp.text}")

except Exception as e:
    print(f"✗ Error: {e}")
