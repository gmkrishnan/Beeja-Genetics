import requests

def debug_api():
    try:
        res = requests.get("http://localhost:8000/categories/tree")
        data = res.json()
        
        for major in data['masters']:
            major_name = str(major['name']).encode('ascii', 'ignore').decode()
            print(f"--- Major: {major_name} ---")
            for master in major['data']:
                master_name = str(master['name']).encode('ascii', 'ignore').decode()
                print(f"  Master: {master_name}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_api()
