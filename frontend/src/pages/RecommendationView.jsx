import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import NeighborhoodCard from '../components/NeighborhoodCard';
import { getPhotoUrl } from '../../../ml-server/function/getPhotoUrl'

const formatPrice = (priceInManwon) => {
  if (!priceInManwon) return '정보 없음';
  if (priceInManwon >= 10000) {
    const eok = Math.floor(priceInManwon / 10000);
    const man = priceInManwon % 10000;
    return man > 0 ? `${eok}억 ${man.toLocaleString()}만` : `${eok}억`;
  }
  return `${priceInManwon.toLocaleString()}만`;
};

const RecommendationView = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchConditions = location.state?.conditions;
  const [recommendations, setRecommendations] = useState([]);
  const [estates, setEstates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDong, setSelectedDong] = useState(null);

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
            preferences: searchConditions.preferences,
            region: searchConditions.region,
            deal_type: searchConditions.deal_type,
            budget: searchConditions.budget,
            size_pyeong: searchConditions.size_pyeong,
            room_type: searchConditions.room_type,
        };
        const response = await axios.post('/api/recommend/neighborhood', payload);
        const { neighborhoods, estates } = response.data;
        
        setRecommendations(neighborhoods || []);
        setEstates(estates || []);

      } catch (error) {
        console.error('추천 데이터를 불러오는 데 실패했습니다.',  error.response?.data || error);
        alert(error.response?.data?.detail?.[0]?.msg || '데이터를 불러올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAllRecommendations();
  }, [searchConditions, navigate]);
  
  const handleNeighborhoodClick = (dongName) => {
    setSelectedDong(prev => prev === dongName ? null : dongName);
  };

  const filteredEstates = selectedDong
    ? estates.filter(prop => prop.address.includes(selectedDong))
    : estates;

  if (loading) {
    return <div className="text-center p-10">AI가 최적의 동네와 매물을 찾고 있습니다...</div>;
  }


  return (
    <div className="w-full flex justify-center min-h-screen bg-gradient-to-br from-pink-100 to-orange-50 p-4 py-10">
      <div className="w-full max-w-4xl mx-auto flex flex-col gap-6">
        <div className="w-full">
          <button onClick={() => navigate('/')} className='bg-white text-gray-700 font-semibold px-6 py-2 rounded-lg shadow-md hover:bg-gray-50 transition flex items-center gap-2'>
            ← 조건 다시 설정하기
          </button>
        </div>
        <div className='text-center'>
          <h1 className='text-3xl font-bold text-slate-900'>AI 추천 결과입니다.</h1>
          <p className='text-gray-600 mt-2'>사용자님의 조건을 분석하여 최적의 동네와 매물을 찾았어요.</p>
        </div>
        <section className='flex flex-col gap-2'>
          <div className='flex gap-2 items-center'>
          <h2 className='text-xl font-bold text-slate-800 mb-4'>이런 동네는 어떠세요?</h2>
          <button onClick={() => setSelectedDong(null)} className={`bg-white/80 rounded-xl border-2 ${!selectedDong ? 'border-pink-200 ring-2 ring-[#FF7E97]' :'border-gray-200'} px-1  cursor-pointer`}> 전체보기 </button>
          </div>
          <div className='grid grid-cols-2 md:grid-cols-5 gap-4'>
            {recommendations.map((dong,index) => (
              <NeighborhoodCard key={index} dongData={dong} onCardClick={handleNeighborhoodClick} isSelected={selectedDong === dong.dong}/>
              // <div key={dong.dong} onClick={() => handleNeighborhoodClick(dong.dong)}
              //   className={`bg-white/80 backdrop-blur-lg p-5 rounded-xl shadow-lg border-2 transition-all duration-300 cursor-pointer ${selectedDong === dong.dong ? 'border-pink-400 ring-2 ring-[#FF7E97]' : 'border-gray-200'}`}
              // >
              //   <h3 className='font-bold text-slate-900'>{dong.dong}</h3>
              //   <p className='text-sm text-gray-500 mt-1'>여기는 태그</p>
              // </div>
            ))}
            {/* <div onClick={() => setSelectedDong(null)} 
              className={`bg-white/80 backdrop-blur-lg p-5 rounded-xl shadow-lg border-2 transition-all duration-300 cursor-pointer flex flex-col justify-center items-center ${!selectedDong ? 'border-pink-400 ring-2 ring-[#FF7E97]' : 'border-gray-200'}`}
            >
              <h3 className='font-bold text-slate-900'>전체 보기</h3>
              <p className='text-sm text-gray-500 mt-1'>모든 추천 매물</p>
            </div> */}
            
          </div>
        </section>
        <section>
          <h2 className='text-xl font-bold text-slate-800 mb-4 flex items-center'>
            맞춤 매물 리스트
            {selectedDong && <span className='text-sm font-semibold text-pink-600 bg-pink-100 px-3 py-1 rounded-full ml-3'>{selectedDong}</span>}
          </h2>
          <div className='space-y-4 flex flex-col gap-2'>
            {filteredEstates.length > 0 ? (
              filteredEstates.map(prop => (
                <Link to={`/detail/${prop.id}`} state={{ estateData: prop, conditions: searchConditions }} key={prop.id} className='no-underline text-black'>
                  <div className='bg-white/80 backdrop-blur-lg p-4 rounded-xl shadow-lg border border-gray-200 flex items-center gap-6 hover:shadow-2xl hover:border-pink-300 transition-all duration-300 cursor-pointer'>
                    <img src={getPhotoUrl(prop.photo_url)[0]} alt={prop.address} className='w-32 h-32 object-cover rounded-lg' onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/200x130/fbcfe8/4a044e?text=No+Image'; }}/>
                    <div className='flex-grow'>
                      <p className='text-sm font-semibold text-gray-500'>{prop.address}</p>
                      <h3 className='text-lg font-bold text-slate-900 my-1'>{`${prop.room_type}, ${Math.round(prop.area_m2 / 3.3)}평, ${prop.floor}`}</h3>
                      <p className='text-sm text-gray-600'>관리비 {prop.maintenance_fee.toLocaleString()}원</p>
                    </div>
                    <div className='text-right'>
                      <p className='text-sm text-gray-500'>{prop.deal_type}</p>
                      <p className='font-bold text-lg text-[#FF7E97]'>
                        {prop.deal_type === '월세' 
                          ?`${formatPrice(prop.price_deposit)} / ${prop.price_rent}` : formatPrice(prop.price_deposit)
                        }
                      </p>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className='text-center py-10 bg-white/50 rounded-lg'>
                <p className='text-gray-500'>이 조건에 맞는 매물이 없습니다.</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default RecommendationView;