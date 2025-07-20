// import {useState, useEffect} from 'react'
// import { useLocation, useNavigate, Link } from 'react-router-dom'
// import axios from 'axios'
// import NeighborhoodCard from '../components/NeighborhoodCard'

// function RecommendationView () {

//   const location = useLocation()
//   const navigate = useNavigate()
//   const searchConditions = location.state?.conditions;

//   const [recommendations, setRecommendations] = useState([])
//   const [properties, setProperties] = useState([])
//   const [loading, setLoading] = useState(true)

//   useEffect(()=>{
//     if(!searchConditions){
//       alert("검색 조건이 없습니다. 이전 페이지로 돌아갑니다.")
//       navigate('/')
//       return
//     }

//     const fetchRecommendations = async() => {
//       setLoading(true)
//       try{
//         // 1. 동네 추천 API 호출
//         // Node.js 서버에 사용자의 모든 조건을 보내는 대신,
//         // neighborhood 추천에 필요한 데이터만 골라서 보냅니다.
//         const response = await axios.post('/api/recommend/neighborhood', {
//           preferences: searchConditions.lifestyle,
//           budget: searchConditions.budget
//         });
//         // --- 여기까지 수정 ---
        
//         setRecommendations(response.data);

//         // 새로운 매물 추천 API 호출 로직 추가
//         const propertiesResponse = await axios.post('/api/recommend/properties', {
//           preferences: searchConditions.lifestyle,
//           budget: searchConditions.budget,
//           size_pyeong: searchConditions.size 
//         });
//         setProperties(propertiesResponse.data)
//       } catch(error){
//         console.error('추천 데이터를 불러오는 데 실패했습니다.', error)
//       } finally{
//         setLoading(false)
//       }
//     }
//     fetchRecommendations()
//   }, [searchConditions, navigate])

//   if(loading){
//     return <div>AI가 최적의 동네를 찾고 있습니다...</div>
//   }

//   return (
//     <div>
//       <h2> 2. AI 추천 결과입니다.</h2>
//       <h3 className='my-4'>이런 동네는 어떠세요?</h3>
//       <div className='flex gap-4 flex-wrap'>
//         {recommendations.map((dong, index)=> (
//           <NeighborhoodCard key={index} dongData={dong} onCardClick={onDongClick}/>
//         ))}
//       </div>
//       {/* --- 👇 맞춤 매물 리스트 UI 추가 --- */}
//       <h3 className='mt-8 text-xl font-bold'>맞춤 매물 리스트</h3>
//       <div className='flex flex-col gap-4 mt-4'>
//         {properties.map((prop, index) => (
//           <Link to={`/detail/${index}`} key={index} className='no-underline text-black'>
//             <div className='flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow'>
//               <div className='w-24 h-24 bg-gray-200 rounded flex items-center justify-center text-gray-500 font-bold text-lg'>?</div>
//               <div className='flex flex-col justify-center'>
//                 <p className='font-semibold text-lg'>{prop.dong} {prop.name}</p>
//                 <p className='text-md text-gray-600'>{Math.round(prop.size_m2 / 3.3)}평, {prop.floor}층</p>
//                 <p className='text-blue-600 font-bold text-xl mt-1'>
//                   AI 예측가: {(prop.predicted_price / 10000).toFixed(1)}억 원
//                 </p>
//               </div>
//             </div>
//           </Link>
//         ))}
//       </div>
//       {/* --- 여기까지 추가 --- */}
//     </div>
//   )
// }
// export default RecommendationView


import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import NeighborhoodCard from '../components/NeighborhoodCard';

function RecommendationView() {
  const location = useLocation();
  const navigate = useNavigate();
  const searchConditions = location.state?.conditions;

  const [recommendations, setRecommendations] = useState([]);
  const [properties, setProperties] = useState([]); // 전체 매물 목록
  const [loading, setLoading] = useState(true);
  const [selectedDong, setSelectedDong] = useState(null); // 필터링할 동네 이름

  useEffect(() => {
    if (!searchConditions) {
      alert("검색 조건이 없습니다. 이전 페이지로 돌아갑니다.");
      navigate('/');
      return;
    }

    const fetchAllRecommendations = async () => {
      setLoading(true);
      try {
        const payload = {
          preferences: searchConditions.lifestyle,
          region: searchConditions.region,
          budget: searchConditions.budget,
          size_pyeong: searchConditions.size,
        };
        // --- 👇 이 부분을 수정합니다 ---
        // 1. 이제 API를 한번만 호출합니다.
        const response = await axios.post('/api/recommend/neighborhood', payload);

        // 2. 하나의 응답에서 neighborhoods와 properties를 각각 꺼내서 state에 저장합니다.
        setRecommendations(response.data.neighborhoods || []);
        setProperties(response.data.properties || []);
        // --- 여기까지 수정 ---

      } catch (error) {
        console.error('추천 데이터를 불러오는 데 실패했습니다.', error);
        alert(error.response?.data?.detail || '데이터를 불러올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAllRecommendations();
  }, [searchConditions, navigate]);
  
  // 동네 카드를 클릭하면, 선택된 동네 이름을 state에 저장 (토글 방식)
  const handleNeighborhoodClick = (dongName) => {
    if (selectedDong === dongName) {
      setSelectedDong(null); // 같은 카드를 다시 누르면 필터 해제
    } else {
      setSelectedDong(dongName);
    }
  };

  // 선택된 동네(selectedDong)가 있으면 전체 매물(properties)을 필터링
  const filteredProperties = selectedDong
    ? properties.filter(prop => prop.dong === selectedDong)
    : properties;

  if (loading) {
    return <div className="text-center p-8">AI가 최적의 동네와 매물을 찾고 있습니다...</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold">2. AI 추천 결과입니다.</h2>
      <h3 className='my-4 text-xl font-semibold'>이런 동네는 어떠세요? (클릭하여 매물 필터링)</h3>
      <div className='flex gap-4 flex-wrap'>
        {recommendations.map((dong, index) => (
          <NeighborhoodCard
            key={index}
            dongData={dong}
            // 카드 클릭 시 handleNeighborhoodClick 함수 호출
            onCardClick={() => handleNeighborhoodClick(dong.dong)}
            // 현재 선택된 카드인지 여부를 전달하여 시각적 효과 부여
            isSelected={selectedDong === dong.dong}
          />
        ))}
      </div>

      <h3 className='mt-8 text-xl font-bold'>
        맞춤 매물 리스트 {selectedDong && `(${selectedDong})`}
      </h3>
      <div className='flex flex-col gap-4 mt-4'>
        {/* 이제 필터링된 매물 목록(filteredProperties)을 화면에 표시 */}
        {filteredProperties.map((prop, index) => (
          <Link to={`/detail/${index}`} state={{ propertyData: prop, conditions: searchConditions }} key={index} className='no-underline text-black'>
            <div className='flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow'>
              <div className='w-24 h-24 bg-gray-200 rounded flex items-center justify-center text-gray-500 font-bold text-lg'>?</div>
              <div className='flex flex-col justify-center'>
                <p className='font-semibold text-lg'>{prop.dong} {prop.name}</p>
                <p className='text-md text-gray-600'>{prop.size_m2 ? `${Math.round(prop.size_m2 / 3.3)}평` : ''}, {prop.floor}층</p>
                <p className='text-blue-600 font-bold text-xl mt-1'>
                  AI 예측가: {prop.predicted_price ? `${(prop.predicted_price / 10000).toFixed(1)}억 원` : '정보 없음'}
                </p>
              </div>
            </div>
          </Link>
        ))}
        {filteredProperties.length === 0 && <p>해당 조건에 맞는 매물이 없습니다.</p>}
      </div>
    </div>
  );
}

export default RecommendationView;