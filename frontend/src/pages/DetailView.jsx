import { useEffect, useState } from 'react'
import {useLocation, Link} from 'react-router-dom';
import axios from 'axios';
import InfrastructureMap from '../components/InfrastructureMap';

function DetailView() {
  const location = useLocation();
  // RecommendationView에서 Link state로 전달한 정보 받기
  const propertyData = location.state?.propertyData;
  const searchConditions = location.state?.conditions;

  const [commuteTime, setCommuteTime] = useState(null);
  const [isCommuteLoading, setIsCommuteLoading] = useState(true);
  const [nearbyInfrastructure, setNearbyInfrastructure] = useState(null);

  useEffect(() => {
    // 주변 인프라 정보는 항상 불러오기
    const fetchInfrastructure = async () => {
      if (!propertyData?.latitude) return;
      try{
        const infraResponse = await axios.post('/api/infrastructure',{
          latitude:propertyData.latitude,
          longitude:propertyData.longitude,
          radius_km:0.5
        })
        setNearbyInfrastructure(infraResponse.data)
      }catch(error){
        console.error("인프라 정보 로딩 실패:", error)
      }
    };

    // 출퇴근 시간은 회사 주소가 있을 때만 계산
    const fetchCommuteTime = async () => {
      if (!propertyData?.latitude || !searchConditions?.commute?.address) {
        setIsCommuteLoading(false);
        return;
      }
      setIsCommuteLoading(true);
      try {
        // 1. 회사 주소 좌표 변한
        const geocodeResponse = await axios.post('/api/geocode', {address: searchConditions.commute.address});
        const workCoords = geocodeResponse.data;

        // 2. 출퇴근 시간 계산
        const directionsResponse = await axios.post('/api/directions', {origin:{lat:propertyData.latitude, lng:propertyData.longitude}, destination: workCoords})
        setCommuteTime(directionsResponse.data.duration_minutes);
      } catch (error){
        console.error("출퇴근 시간 계산 실패:", error);
      } finally{
        setIsCommuteLoading(false)
      }
    }
    fetchInfrastructure();
    fetchCommuteTime();
  },[propertyData,searchConditions]);

  if (!propertyData){
    return (
      <div>
        <p>매물 정보가 없습니다.</p>
        <Link to="/">처음으로 돌아가기</Link>
      </div>
    )
  }

  return (
    <div>
      <Link to="/recommend" state={{conditions: searchConditions}} className='text-blue-500 hover:underline'> &larr; 목록으로 돌아가기</Link>
      <div className='mt-4 grid md:grid-cols-2 gap-8'>
        {/* 지도분석 */}
        <div>
          <h3 className='text-xl font-bold mb-2'>지도 분석</h3>
          <div className='border rounded-lg overflow-hidden'>
            <InfrastructureMap lat={propertyData.latitude} lng={propertyData.longitude} isPropertyMarker={true}/>
          </div>
        </div>
        {/* 상세 정보 */}
        <div className='space-y-6'>
          <div>
            <h3 className='text-2xl font-bold'>{propertyData.name}</h3>
            <p className='text-gray-600'>{Math.round(propertyData.size_m2 / 3.3)}평, {propertyData.floor}층</p>
          </div>

          <div className='p-4 border rounded-lg'>
            <p className='text-sm text-gray-500'>매매가</p>
            <p className='text-3xl font-bold text-blue-600'>
              {propertyData.predicted_price ? `${(propertyData.predicted_price / 10000).toFixed(1)}억 원` : '정보 없음'}
            </p>
          </div>

          <div className='p-4 border rounded-lg'>
            <h4 className='font-bold mb-2'>주변 인프라 (반경 500m)</h4>
            {nearbyInfrastructure ? (
              <ul className='space-y-1 text-sm'>
                <li>🏫 학교: {nearbyInfrastructure.schools.length}개</li>
                <li>🚇 지하철: {nearbyInfrastructure.subways.length}개</li>
              </ul>
            ):<p>정보를 불러오는 중...</p>}
          </div>

          <div className='p-4 border rounded-lg'>
            <h4 className='font-bold mb-2'>출퇴근 분석</h4>
            {isCommuteLoading?(<p className='text-sm'>계산 중...</p>): commuteTime ? (<p className='text-sm'>🚇 대중교통: 약 {commuteTime}분</p>):(<p className='text-sm' >회사 주소가 입력되지 않았습니다.</p>)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DetailView