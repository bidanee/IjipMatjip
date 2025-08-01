from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.infrastructure_analyzer import InfrastructureAnalyzer


router = APIRouter()
infra_analyzer = InfrastructureAnalyzer()

class InfraQuery(BaseModel):
  latitude: float
  longitude: float
  radius_km: float
  
@router.post("/")
def get_nearby_infrastructure(query: InfraQuery):
  if not infra_analyzer:
    raise HTTPException(status_code=503, detail="인프라 분석기가 준비되지 않았습니다.")
  return {
      "schools": infra_analyzer.find_nearby(query.latitude, query.longitude, query.radius_km, 'school'),
      "subways": infra_analyzer.find_nearby(query.latitude, query.longitude, query.radius_km, 'subway'),
      "hospitals": infra_analyzer.find_nearby(query.latitude, query.longitude, query.radius_km, 'hospital'),
      "marts": infra_analyzer.find_nearby(query.latitude, query.longitude, query.radius_km, 'mart'),
      "parks": infra_analyzer.find_nearby(query.latitude, query.longitude, query.radius_km, 'park')
  }