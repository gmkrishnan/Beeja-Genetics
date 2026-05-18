import httpx
import json

async def check_ollama():
    url = "http://localhost:11434/api/tags"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            print(f"Models: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error connecting to Ollama: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_ollama())
