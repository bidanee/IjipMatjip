import React, {useState} from 'react'
import axios from 'axios'

// onDongClick 함수를 props로 받음
const RecommendationComponent = ({onDongCLick}) => {
  const [preferences, setPreferences] = useState({
    school: true,
    subway:true,
    price: false
  })
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  const handleCheckboxChange = (e) => {
    const {name, checked} = e.target;
    setPreferences(prev => ({...prev, [name]: checked}))
  }

  const handleRecommendClick = async() => {
    setLoading(true)
    // 체크된 항목들만 배열로 만듦
    const selectedPreferences = Object.keys(preferences).filter(key => preferences[key])

    try {
      const response = await axios.post('/api/recommend/neighborhood', {
        preferences: selectedPreferences
      })
      setRecommendations(response.data)
    }catch (error) {
      console.error("추천 데이터를 불러오는 데 실패했습니다", error)
      alert(error.response?.data?.detail || "데이터를 불러올 수 없습니다.")
    }finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>맞춤 동네 추천받기</h1>
      <div>
        <label><input type="checkbox" name="school" checked={preferences.school} onChange={handleCheckboxChange} />학군</label>
        <label className='ml-4'><input type='checkbox' name='subway' checked={preferences.subway} onChange={handleCheckboxChange} />교통</label>
        <label className='ml-4'><input type='checkbox' name='price' checked={preferences.price} onChange={handleCheckboxChange} />가격</label>
      </div>
      <button onClick={handleRecommendClick} disabled={loading} className='mt-4' >
        {loading ? '추천 중...' : '추천받기'}
      </button>

      <h2>추천 동네 목록</h2>
      <ul>
        {recommendations.map((dong,index) => (
          <li key={index} onClick={() => onDongCLick({ lat:dong.latitude, lng:dong.longitude})} className='cursor-pointer' >
            <strong>{dong.dong}</strong> (총점 : {dong.total_score.toFixed(2)})
          </li>
        ))}
      </ul>
    </div>
  )
}

export default RecommendationComponent