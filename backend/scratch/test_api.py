import requests

def test_api():
    try:
        res = requests.get("http://localhost:8000/categories/tree")
        data = res.json()
        print(f"API Response Majors: {len(data['masters'])} found")
        
        found = False
        for major in data['masters']:
            major_name = str(major['name']).encode('ascii', 'ignore').decode()
            for master in major['data']:
                master_name = str(master['name']).encode('ascii', 'ignore').decode()
                if "Unknown" in master_name:
                    print(f"!!! FOUND UNKNOWN MASTER: Major={major_name}, Master={master_name}")
                    found = True
        
        if not found:
            print("The API is NOT sending any 'Unknown Master' for the specialist majors.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
