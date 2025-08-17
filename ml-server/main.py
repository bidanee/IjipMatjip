from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
import json # json 라이브러리를 임포트합니다.

from fastapi.middleware.cors import CORSMiddleware
from routes import predict, recommend, infrastructure, report, external_apis

load_dotenv()
app = FastAPI()

# --- CORS 설정 시작---
origins = [
   "http://13.55.21.100:4000",
   "http://13.55.21.100:4001",
   "http://13.55.21.100",
   "https://dev-bidanee.site"
]

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"]
)
# --- CORS 설정 끝---

# --- 👇 디버깅을 위한 특별 에러 핸들러 추가 ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("\n\n--- 🕵️ DETAILED VALIDATION ERROR! 🕵️ ---")
    print(json.dumps(exc.errors(), indent=2))
    print("-------------------------------------------\n\n")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
# --- 여기까지 디버깅 코드 ---

# --- 라우터 Prefix를 '/api'로 통일하여 관리 용이성 증대 ---
api_router = APIRouter(prefix="/api")

api_router.include_router(predict.router, prefix="/predict", tags=["Predictions"])
api_router.include_router(recommend.router, prefix="/recommend", tags=["Recommendations"])
api_router.include_router(infrastructure.router, prefix="/infrastructure", tags=["Infrastructure"])
api_router.include_router(report.router, prefix="/report", tags=["Reports"])

# --- 카카오 API 라우터 등록
api_router.include_router(external_apis.router, tags=["External APIs"])

app.include_router(api_router)

@app.get("/")
def read_root():
  return {"message" : "AI Server is running"}

