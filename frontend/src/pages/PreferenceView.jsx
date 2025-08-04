import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import regionData from '../data/regions.json';

// --- 아이콘 컴포넌트 ---
const HomeIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);
const ZapIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2z" />
  </svg>
);

const lifestyleOptions = ['조용한 곳', '학군 중요', '교통 편리', '번화가', '생활편의시설','가성비'];

const PreferenceView = () => {
  const navigate = useNavigate();

  // --- 모든 입력 값을 저장하기 위한 State 선언 ---
  const [tradeType, setTradeType] = useState('전세');
  const [selectedSido, setSelectedSido] = useState('');
  const [selectedSigungu, setSelectedSigungu] = useState('');
  
  const [jeonseMin, setJeonseMin] = useState('');
  const [jeonseMax, setJeonseMax] = useState('');

  const [wolseDepositMax, setWolseDepositMax] = useState('');
  const [wolseMin, setWolseMin] = useState('');
  const [wolseMax, setWolseMax] = useState('');

  const [roomType, setRoomType] = useState('전체');
  const [areaPyeong, setAreaPyeong] = useState('');

  const [selectedLifestyles, setSelectedLifestyles] = useState(['교통 편리']);
  
  const [sidoList, setSidoList] = useState([]);
  const [sigunguList, setSigunguList] = useState([]);

  useEffect(() => {
    setSidoList(Object.keys(regionData));
    if (Object.keys(regionData).length > 0) {
      setSelectedSido(Object.keys(regionData)[0]);
    }
  }, []);

  useEffect(() => {
    if (selectedSido) {
      setSigunguList(regionData[selectedSido] || []);
      setSelectedSigungu('');
    } else {
      setSigunguList([]);
    }
  }, [selectedSido]);

  const handleLifestyleClick = (lifestyle) => {
    setSelectedLifestyles((prev) =>
      prev.includes(lifestyle)
        ? prev.filter((item) => item !== lifestyle)
        : [...prev, lifestyle]
    );
  };

  const handleSearch = () => {
    const searchConditions = {
      region: selectedSigungu,
      deal_type: tradeType,
      budget: tradeType === '전세' ? {
        min: jeonseMin ? parseInt(jeonseMin) : null,
        max: jeonseMax ? parseInt(jeonseMax) : null,
      } : {
        deposit_max: wolseDepositMax ? parseInt(wolseDepositMax) : null,
        rent_min: wolseMin ? parseInt(wolseMin) : null,
        rent_max: wolseMax ? parseInt(wolseMax) : null,
      },
      room_type: roomType === '전체' ? null : roomType,
      size_pyeong: {
        min: areaPyeong ? parseInt(areaPyeong) : null,
      },
      preferences: selectedLifestyles,
    };
    
    
    navigate('/recommend', { state: { conditions: searchConditions } });
  };

  return (
    <div className="w-full min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-100 to-orange-50 p-4">
      <div className="w-full max-w-2xl flex flex-col gap-8 bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 border border-gray-200">
        <div className="text-center flex flex-col gap-2">
          <div className="flex justify-center items-center">
            <HomeIcon className="w-12 h-12 mb-2 text-[#FF7E97]" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900">AI 부동산 추천</h1>
          <p className="text-gray-600 mt-2">
            원하는 조건을 입력하고, 나에게 맞는 동네와 집을 찾아보세요.
          </p>
        </div>

        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 희망지역 */}
            <div className='md:col-span-2'>
              <label className="font-semibold text-gray-700">희망지역</label>
              <div className="flex space-x-2 mt-2 gap-2">
                <select value={selectedSido} onChange={(e) => setSelectedSido(e.target.value)} className="w-1/2 p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]">
                  <option value="">시/도 선택</option>
                  {sidoList.map((sido) => <option key={sido} value={sido}>{sido}</option>)}
                </select>
                <select value={selectedSigungu} onChange={(e) => setSelectedSigungu(e.target.value)} className="w-1/2 p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]" disabled={!selectedSido}>
                  <option value="">시/군/구 선택</option>
                  {sigunguList.map((sigungu) => <option key={sigungu} value={sigungu}>{sigungu}</option>)}
                </select>
              </div>
            </div>
            {/* 거래유형 */}
            <div className='md:col-span-2'>
              <label className='block text-sm font-semibold text-gray-700'>거래유형</label>
              <div className='flex space-x-4 gap-4'>
                <div className='flex items-center gap-2'>
                    <input type='radio' id="tradeTypeJeonse" name="tradeType" value="전세" checked={tradeType === '전세'} onChange={(e) => setTradeType(e.target.value)} className='h-4 w-4 text-pink-600 border-gray-300 focus:ring-pink-500' />
                    <label htmlFor='tradeTypeJeonse' className='ml-2 block text-sm text-gray-900'>전세</label>
                </div>
                <div className='flex items-center gap-2'>
                    <input type='radio' id="tradeTypeWolse" name="tradeType" value="월세" checked={tradeType === '월세'} onChange={(e) => setTradeType(e.target.value)} className='h-4 w-4 text-pink-600 border-gray-300 focus:ring-pink-500' />
                    <label htmlFor='tradeTypeWolse' className='ml-2 block text-sm text-gray-900'>월세</label>
                </div>
              </div>
            </div>
            {/* 전세 */}
            {tradeType === '전세' && (
              <div className='md:col-span-2 grid grid-cols-2 gap-x-6' >
                <div>
                  <label className='block text-sm font-semibold text-gray-700 mb-1'>전세금 (최소)</label>
                  <div className='flex items-center gap-2'>
                    <input type='number' value={jeonseMin} onChange={(e) => setJeonseMin(e.target.value)} placeholder='10000' className='w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]'/>
                    <span className='ml-2 text-gray-600'>만원</span>
                  </div>
                </div>
                <div>
                  <label className='block text-sm font-semibold text-gray-700 mb-1'>전세금 (최대)</label>
                  <div className='flex items-center gap-2'>
                    <input type='number' value={jeonseMax} onChange={(e) => setJeonseMax(e.target.value)} placeholder='30000' className='w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]'/>
                    <span className='ml-2 text-gray-600'>만원</span>
                  </div>
                </div>
              </div>
            )}
            {/* 월세 */}
            {tradeType === '월세' && (
              <div className='md:col-span-2'>
                <div>
                  <label className='block text-sm font-semibold text-gray-700 mb-1'>보증금 (최대)</label>
                  <div className='flex items-center mb-4 gap-3'>
                    <input type='number' value={wolseDepositMax} onChange={(e) => setWolseDepositMax(e.target.value)} placeholder='5000' className='flex-1 p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]'/>
                    <span className='ml-2 text-gray-600'>만원</span>
                  </div>
                </div>
                <div className='grid grid-cols-2 gap-x-4'>
                  <div>
                    <label className='block text-sm font-semibold text-gray-700 mb-1'>월세 (최소)</label>
                    <div className='flex items-center gap-2'>
                      <input type='number' value={wolseMin} onChange={(e) => setWolseMin(e.target.value)} placeholder='50' className='w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]'/>
                      <span className='ml-2 text-gray-600'>만원</span>
                    </div>
                  </div>
                  <div>
                    <label className='block text-sm font-semibold text-gray-700 mb-1'>월세 (최대)</label>
                    <div className='flex items-center gap-2'>
                      <input type='number' value={wolseMax} onChange={(e) => setWolseMax(e.target.value)} placeholder='100' className='w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]'/>
                      <span className='ml-2 text-gray-600'>만원</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {/* 방 구조 및 평수 */}
            <div className='md:col-span-1'>
              <label className='block text-sm font-semibold text-gray-700 mb-1'>방 구조</label>
              <select value={roomType} onChange={(e) => setRoomType(e.target.value)} className='w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]'>
                <option>전체</option>
                <option>원룸</option>
                <option>투룸</option>
              </select>
            </div>
            <div className='md:col-span-1'>
              <label className='block text-sm font-semibold text-gray-700 mb-1'>평수</label>
              <input type='number' value={areaPyeong} onChange={(e) => setAreaPyeong(e.target.value)} placeholder='10' className='w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7E97]' />
            </div>
            {/* 라이프스타일 */}
            <div className="md:col-span-2">
              <label className="font-semibold text-gray-700">라이프스타일 (선택)</label>
              <div className="mt-2 grid grid-cols-2 sm:grid-cols-3 gap-3">
                {lifestyleOptions.map((style) => (
                  <button key={style} type='button' onClick={() => handleLifestyleClick(style)} className={`p-3 text-sm border rounded-lg transition-all focus:outline-none focus:ring-2 ${selectedLifestyles.includes(style) ? 'border-[#FF7E97] bg-pink-50 text-[#FF7E97] ring-[#FF7E97]' : 'border-gray-300 text-gray-700 hover:border-[#FF7E97] hover:bg-pink-50 hover:text-[#FF7E97]'}`}>
                    {style}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <button onClick={handleSearch} className="w-full mt-4 bg-gradient-to-r from-[#FF7E97] to-[#F89BAF] text-white font-bold py-4 rounded-lg text-lg flex items-center justify-center gap-2 shadow-lg shadow-[#FF7E97]/40 hover:scale-105 transition-transform">
            <ZapIcon className="w-6 h-6" />
            <span>AI 추천받기</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PreferenceView;