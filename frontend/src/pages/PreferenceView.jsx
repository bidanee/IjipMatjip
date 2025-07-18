import { useState } from 'react'
import {useNavigate} from 'react-router-dom'

function PreferenceView () {
  const navigate = useNavigate()
  // 사용자의 입력을 저장하기 위한 state 변수
  const [region, setRegion] = useState('')
  const [desiredSize, setDesiredSize] = useState('')
  const [minBudget, setMinBudget] = useState('')
  const [maxBudget, setMaxBudget] = useState('')
  const [roomCount, setRoomCount] = useState('1')
  const [lifestyle, setLifestyle] = useState({
    quite:true,
    lively:false,
    school:true,
    pet:false
  })
  const [workAddress, setWorkAddress] = useState('')
  const [transportation, setTransportation] = useState('public') //기본값 대중 교통

  const handleLifestyleChange = (e) => {
    const {name, checked} = e.target
    setLifestyle(prev => ({...prev, [name]: checked})) 
  }
  
  const handleSearch = () => {
    const searchConditions = {
      region,
      size: desiredSize,
      min: minBudget ? parseInt(minBudget, 10) * 10000 : null,
      max: maxBudget ? parseInt(maxBudget, 10) * 10000 : null,
      rooms: roomCount,
      lifestyle:Object.keys(lifestyle).filter(key => lifestyle[key]),
      commute:{
        address: workAddress,
        transport: transportation,
      }
    } 
    console.log('최종 검색 조건: ', searchConditions)
    navigate('/recommend', {state:{conditions: searchConditions}})
  }
  return (
    <div>
      <h2 className='text-xl font-bold mb-4'>1. 원하는 조건을 알려주세요</h2>
      <div className='grid grid-cols-2 gap-8'>
        {/* 좌측 입력칸*/}
        <div className='space-y-4'>
          <div>
            <label className='block text-sm font-medium text-gray-700'>희망 지역</label>
            <input type='text' value={region} onChange={(e)=> setRegion(e.target.value)} placeholder='예: 서울시 강남구' className='mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm'/>
          </div>
          <div>
            <label className='block text-sm font-medium text-gray-700'>희망 평수</label>
            <input type='text' value={desiredSize} onChange={(e) => setDesiredSize(e.target.value)} placeholder='예: 최소 8평 ~ 최대 42평' className='mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm'/>
          </div>
          <div>
            <label className='block text-sm font-medium text-gray-700'>예산 범위 (만원 단위)</label>
            <div className='flex justify-center items-center'>
              <input type='number' value={minBudget} onChange={(e) => setMinBudget(e.target.value)} placeholder='최소 예산 (예:5000 -> 5000만원)' className='mt-1 mr-4 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm'/>
              <span> ~ </span>
              <input type='number' value={maxBudget} onChange={(e) => setMaxBudget(e.target.value)} placeholder='최대 예산 (예:60000 -> 60000만원 : 6억)' className='mt-1 ml-4 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm'/>
            </div>
          </div>
          <div>
            <label className='block text-sm font-medium text-gray-700'>방 개수</label>
            <select type='text' value={roomCount} onChange={(e) => setRoomCount(e.target.value)} className='mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm'>
              <option value="1">1개</option>
              <option value="2">2개</option>
              <option value="3">3개 이상</option>
            </select>
          </div>
        </div>
        {/* 우측 입력란 */}
        <div className='space-y-4'>
          <div>
            <label className='block text-sm font-medium text-gray-700'>라이프 스타일</label>
            <div className='mt-2 space-x-4'>
              <label><input type='checkbox' name='quite' checked={lifestyle.quite} onChange={handleLifestyleChange}/>조용한 주거 환경</label>
              <label><input type='checkbox' name='lively' checked={lifestyle.lively} onChange={handleLifestyleChange}/>번화가 선호</label>
              <label><input type='checkbox' name='school' checked={lifestyle.school} onChange={handleLifestyleChange}/>학군 중요</label>
              <label><input type='checkbox' name='pet' checked={lifestyle.pet} onChange={handleLifestyleChange}/>반려동물</label>
            </div>
          </div>
          <div>
            <label className='block text-sm font-medium text-gray-700'>출퇴근 정보</label>
            <input type='text' value={workAddress} onChange={(e) => setWorkAddress(e.target.value)} placeholder='회사 주소 (예: 서울 강남구 테헤란로)' className='mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm'/>
            <select value={transportation} onChange={(e)=>setTransportation(e.target.value)} className='mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm'>
              <option value='public'>대중교통</option>
              <option value='car'>자가용</option>
            </select>
          </div>
        </div>
      </div>
      <button onClick={handleSearch} className='mt-6 px-4 py-2 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-700'>
        AI 추천받기
      </button>
    </div>
  )
}

export default PreferenceView
