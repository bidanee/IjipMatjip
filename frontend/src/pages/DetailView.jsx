import React, { useState, useEffect } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import client from '../api/client';
import InfrastructureMap from '../components/InfrastructureMap';
import { getPhotoUrl } from '../function/getPhotoUrl'

// --- 아이콘 컴포넌트 ---
const ArrowLeftIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
);
const Share2Icon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
);
const HeartIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
);
const ZapIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
);
const CheckCircleIcon = (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
);
const XCircleIcon = (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...props}><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
);
const MapPinIcon = (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
);

// 가격 포맷팅 함수
const formatPrice = (prop) => {
  if (!prop) return '정보 없음';
  if (prop.deal_type === '월세') {
    const deposit = prop.price_deposit >= 10000 ? `${(prop.price_deposit / 10000).toFixed(0)}억` : `${prop.price_deposit}만`;
    return `${deposit} / ${prop.price_rent}`;
  }
  if (prop.deal_type === '전세') {
    return prop.price_deposit >= 10000 ? `${(prop.price_deposit / 10000).toFixed(1)}억` : `${prop.price_deposit}만`;
  }
  return '정보 없음';
};

const DetailView = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const estateData = location.state?.estateData;
  const photo_urls = getPhotoUrl(estateData.photo_url)
  const searchConditions = location.state?.conditions

  // AI 리포트, 인프라, 출퇴근 시간 등 추가 데이터를 위한 State
  const [aiReport, setAiReport] = useState(null);
  const [infrastructure, setInfrastructure] = useState({ schools: [], subways: [], hospitals: [], marts: [], parks: [] });
  const [commuteTime, setCommuteTime] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [selectedImage, setSelectedImage] = useState(photo_urls[0] || 'https://placehold.co/800x500/e2e8f0/4a5568?text=Image');

  useEffect(() => {
    if (!estateData) {
      setLoading(false);
      return;
    }

    const fetchDetails = async () => {
      setLoading(true);
      try {
        // TODO: 실제 AI 리포트 생성 API 호출 , 현재 더미 데이터
        const reportPromise = client.post('/api/report/generate',{
          property_data : estateData,
          user_preferences: searchConditions
        })
        const infraPromise = client.post('/api/infrastructure',{
          latitude: estateData.latitude,
          longitude: estateData.longitude,
          radius_km:1.0
        })

        const promises = [reportPromise]

        if(searchConditions?.commute?.address){
          promises.push(client.post('/api/geocode', {address: searchConditions.commute.address}))
        }

        promises.push(infraPromise)
        
        // 모든 API 호출을 병렬로 처리
        const results = await Promise.all(promises);
        let resultIndex = 0;
        
        setAiReport(results[resultIndex].data);
        resultIndex++;

        if(searchConditions?.commute?.address){
          const workCoords = results[resultIndex].data;
          const directionsRes = await client.post('/api/directions', {
            origin:{lat: estateData.latitude, lng: estateData.longitude},
            destination: workCoords,
          })
          setCommuteTime(directionsRes .data.duration_minutes)
          resultIndex++;
        }

        setInfrastructure(results[resultIndex].data)
      } catch (error) {
        console.error("상세 정보 로딩 실패:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [estateData, searchConditions]);

  if (!estateData) {
    return (
      <div className="text-center p-10">
        <p>매물 정보가 없습니다.</p>
        <Link to="/" className="text-blue-500 hover:underline">처음으로 돌아가기</Link>
      </div>
    );
  }
  

  return (
    <div className="bg-gray-50 min-h-screen font-sans">
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-20">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-600 hover:text-slate-900">
            <ArrowLeftIcon className="w-5 h-5" />
            <span className="font-semibold">목록으로</span>
          </button>
          <div className="flex items-center gap-2">
            <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"><Share2Icon className="w-5 h-5 text-gray-600"/></button>
            <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"><HeartIcon className="w-5 h-5 text-gray-600"/></button>
          </div>
        </div>
      </header>
      
      <main className="container p-2">
        <div className="w-full grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column */}
            <div className="flex flex-col gap-2">
                <div className="flex flex-col gap-2">
                    <img src={selectedImage} alt="Main view" className="w-full h-auto max-h-[530px] object-cover rounded-2xl shadow-lg mb-4" />
                    <div className="grid grid-cols-5 gap-4">
                        {photo_urls.map((img, index) => (
                            <img 
                                key={index} 
                                src={img} 
                                alt={`Thumb ${index + 1}`} 
                                onClick={() => setSelectedImage(img)} 
                                className={`w-full h-auto max-h-[105px] object-cover rounded-lg cursor-pointer transition-all duration-200 ${selectedImage === img ? 'ring-4 ring-[#FF7E97] shadow-md' : 'opacity-70 hover:opacity-100'}`} 
                            />
                        ))}
                    </div>
                </div>
                <div className= "w-full flex flex-col gap-2 bg-white p-6 rounded-2xl shadow-md border border-gray-100">
                  <div className='flex gap-4'>
                    <h1 className="text-2xl font-bold text-slate-900">{estateData.room_type}</h1>
                    <p className="text-gray-500  flex items-center gap-1"><MapPinIcon /> {estateData.address}</p>
                  </div>
                    <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                        <div><p className="text-sm text-gray-500">거래 종류</p><p className="font-bold text-lg text-slate-800">{estateData.deal_type}</p></div>
                        <div><p className="text-sm text-gray-500">가격</p><p className="font-bold text-lg text-slate-800">{formatPrice(estateData)}</p></div>
                        <div><p className="text-sm text-gray-500">면적</p><p className="font-bold text-lg text-slate-800">{`${Math.round(estateData.area_m2 / 3.3)}평`}</p></div>
                        <div><p className="text-sm text-gray-500">층</p><p className="font-bold text-lg text-slate-800">{estateData.floor}</p></div>
                    </div>
                </div>

            </div>
            
            {/* Right Column */}
            <div className="flex flex-col gap-12">
                <div className=" flex flex-col gap-2 bg-white p-6 rounded-2xl shadow-md border border-gray-100">
                    <h2 className="text-2xl font-bold text-slate-900 mb-4">위치 및 주변 정보</h2>
                    <div className="h-80 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                      <InfrastructureMap 
                        lat={estateData.latitude} 
                        lng={estateData.longitude} 
                        isEstateMarker={true}
                        markers={[]} // TODO: 필터링 기능 연동
                      />
                    </div>
                </div>
                {loading || !aiReport ? (
                  <div className="bg-gradient-to-br from-pink-50 to-orange-50 p-6 rounded-2xl shadow-md text-center">
                    <p>AI 리포트를 생성 중입니다...</p>
                  </div>
                ) : (
                  <div className="flex flex-col gap-2 bg-gradient-to-br from-pink-50 to-orange-50 p-6 rounded-2xl shadow-md">
                      <div className="flex items-center gap-2 mb-4">
                          <ZapIcon className="w-8 h-8 text-[#FF7E97]" />
                          <h2 className="text-2xl font-bold text-slate-900">AI 분석 리포트</h2>
                          <span className="px-3 py-1 text-sm font-bold text-white bg-gradient-to-r from-[#FF7E97] to-[#f89baf] rounded-full">
                              SCORE {aiReport.score}
                          </span>
                      </div>
                      <p className="text-gray-700 mb-6">{aiReport.summary}</p>
                      <div className="grid md:grid-cols-2 gap-6">
                          <div className=' flex flex-col gap-2'>
                              <h4 className="font-bold text-green-600 mb-2">👍 추천하는 이유</h4>
                              <ul className="space-y-2 text-sm text-gray-600 flex flex-col gap-2">
                                  {aiReport.pros.map((pro, i) => <li key={i} className="flex gap-2"><CheckCircleIcon className="text-green-500 flex-shrink-0 mt-0.5"/>{pro}</li>)}
                              </ul>
                          </div>
                          <div className=' flex flex-col gap-2'>
                              <h4 className="font-bold text-red-600 ">🤔 고려할 점</h4>
                              <ul className="space-y-2 text-sm text-gray-600 flex flex-col gap-2">
                                  {aiReport.cons.map((con, i) => <li key={i} className="flex gap-2"><XCircleIcon className="text-red-500 flex-shrink-0 mt-0.5"/>{con}</li>)}
                              </ul>
                          </div>
                      </div>
                  </div>
                )}
            </div>
        </div>
      </main>
    </div>
  );
};

export default DetailView;