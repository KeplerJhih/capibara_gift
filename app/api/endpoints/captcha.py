from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from loguru import logger
from typing import Optional
from app.services.captcha_service import CaptchaService
import httpx
import os

router = APIRouter()
captcha_service = CaptchaService()

@router.get("/test")
async def test_apis():
    """測試外部 API 的可用性"""
    results = {}
    
    # 測試驗證碼生成 API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{os.getenv('CAPTCHA_BASE_URL')}/generate",
                headers={'Content-Type': 'application/json'}
            )
            results['captcha_generate'] = {
                'status': response.status_code,
                'accessible': response.status_code == 200,
                'response': response.text[:200] if response.status_code != 200 else 'OK'
            }
    except Exception as e:
        results['captcha_generate'] = {
            'status': 'error',
            'accessible': False,
            'response': str(e)
        }
    
    # 測試兌換 API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                os.getenv('CLAIM_API_URL'),
                headers={'Content-Type': 'application/json'},
                json={"test": "connection"}
            )
            results['claim_api'] = {
                'status': response.status_code,
                'accessible': True,  # 任何響應都表示可訪問
                'response': response.text[:200]
            }
    except Exception as e:
        results['claim_api'] = {
            'status': 'error',
            'accessible': False,
            'response': str(e)
        }
    
    return {
        'env_vars': {
            'CAPTCHA_BASE_URL': os.getenv('CAPTCHA_BASE_URL'),
            'CLAIM_API_URL': os.getenv('CLAIM_API_URL')
        },
        'test_results': results
    }

@router.post("/captcha/generate")
async def generate_captcha():
    """代理驗證碼生成請求"""
    try:
        captcha_url = f"{os.getenv('CAPTCHA_BASE_URL')}/generate"
        logger.info(f"正在請求驗證碼: {captcha_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                captcha_url,
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f"驗證碼 API 響應: status={response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"驗證碼 API 錯誤: {response.text}")
                raise HTTPException(status_code=400, detail=f"無法生成驗證碼: {response.text}")
            
            result = response.json()
            logger.info(f"驗證碼生成成功: {result}")
            return result
            
    except httpx.TimeoutException:
        logger.error("驗證碼 API 請求超時")
        raise HTTPException(status_code=500, detail="請求超時")
    except Exception as e:
        logger.error(f"生成驗證碼失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/captcha/image/{captcha_id}")
async def get_captcha_image(captcha_id: str):
    """代理驗證碼圖片請求"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{os.getenv('CAPTCHA_BASE_URL')}/image/{captcha_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="無法獲取驗證碼圖片")
            
            from fastapi.responses import Response
            return Response(content=response.content, media_type="image/png")
    except Exception as e:
        logger.error(f"獲取驗證碼圖片失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/captcha", status_code=200)
async def recognize_captcha(
    game_id: str = Form(...),
    serial_number: str = Form(...),
    captcha_id: str = Form(...)
):
    try:
        logger.info(f"接收到辨識請求: game_id={game_id}, serial_number={serial_number}, captcha_id={captcha_id}")
        
        # 從遠程服務器獲取驗證碼圖片
        base_url = os.getenv('CAPTCHA_BASE_URL')
        image_url = f"{base_url}/image/{captcha_id}"
            
        logger.info(f"獲取驗證碼圖片: {image_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code != 200:
                logger.error(f"獲取驗證碼圖片失敗: status={response.status_code}, response={response.text}")
                raise HTTPException(status_code=400, detail=f"無法獲取驗證碼圖片: {response.text}")
            
            image_content = response.content
            logger.info("成功獲取驗證碼圖片")

        # 調用驗證碼辨識服務
        try:
            result = await captcha_service.recognize(image_content)
            logger.info(f"驗證碼辨識結果: {result}")
            
            response_data = {
                "success": True,
                "result": result,
                "message": "辨識成功"
            }
            logger.info(f"返回結果: {response_data}")
            return response_data

        except ValueError as ve:
            logger.warning(f"驗證碼辨識值錯誤: {str(ve)}")
            return {
                "success": False,
                "result": None,
                "message": str(ve)
            }
        except Exception as e:
            logger.error(f"驗證碼辨識失敗: {str(e)}")
            return {
                "success": False,
                "result": None,
                "message": f"辨識失敗: {str(e)}"
            }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"處理請求失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 