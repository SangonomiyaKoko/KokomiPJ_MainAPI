from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

'''
referer:
https://profile.worldofwarships.asia/
user-agent:
Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36
'''

@app.get("/proxy", summary='proxy', tags=['Default'])
async def proxy(
    url: str
):
    '''
    接口请求代理
    '''
    if 'api' in url:
        data = None
        status_code = None
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36'
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=30,
                headers=headers
            )
            data=response.json()
            status_code=response.status_code
        return JSONResponse(
            content=data, 
            status_code=status_code
        )
    else:
        return JSONResponse(
            content={}, 
            status_code=404
        )