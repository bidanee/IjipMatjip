from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from routes import predict, recommend, infrastructure, report
import json # json 라이브러리를 임포트합니다.

load_dotenv()
app = FastAPI()

# --- 👇 디버깅을 위한 특별 에러 핸들러 추가 ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic 모델 유효성 검사(422) 오류가 발생했을 때,
    그 상세 내용을 터미널에 명확하게 출력하기 위한 핸들러입니다.
    """
    print("\n\n--- 🕵️ DETAILED VALIDATION ERROR! 🕵️ ---")
    # exc.errors()는 오류에 대한 상세 정보를 담고 있는 리스트입니다.
    # json.dumps를 사용해 사람이 보기 좋게 출력합니다.
    print(json.dumps(exc.errors(), indent=2))
    print("-------------------------------------------\n\n")
    
    # 원래 FastAPI가 하던 대로 클라이언트에게 422 응답을 보냅니다.
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
# --- 여기까지 디버깅 코드 ---

# 각 라우터 파일들을 메인 앱에 포함
app.include_router(predict.router, prefix="/predict", tags=["Predictions"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendations"])
app.include_router(infrastructure.router, prefix="/infrastructure", tags=["Infrastructure"])
app.include_router(report.router, prefix="/report", tags=["Reports"])
@app.get("/")
def read_root():
  return {"message" : "AI Server is running"}

