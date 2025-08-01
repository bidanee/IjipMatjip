from fastapi import FastAPI
from dotenv import load_dotenv
from routes import predict, recommend, infrastructure

load_dotenv()
app = FastAPI()

# 각 라우터 파일들을 메인 앱에 포함
app.include_router(predict.router, prefix="/predict", tags=["Predictions"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendations"])
app.include_router(infrastructure.router, prefix="/infrastructure", tags=["Infrastructure"])

@app.get("/")
def read_root():
  return {"message" : "AI Server is running"}