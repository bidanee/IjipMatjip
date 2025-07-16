import React, { useState } from "react"
import axios from 'axios'

function RecommendationComponent(){
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleRecommendClick = async() => {
    setLoading(true);
    try{
      // 1. Node.js 서버의 API를 호출합니다.
      const response = await axios.post('/api/recommend/neighborhood',{
        preferences:['school','subway']
      })
      //  2. 서버로부터 받은 추천 동네 목록을 state에 저장
      setRecommendations(response.data)
    } catch(error){
      console.error("추천 데이터를 불러오는 데 실패했습니다.", error);
      alert(error.response.data.detail || '데이터를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1> 맞춤 동네 추천받기</h1>
      <button onClick={handleRecommendClick} disabled={loading}>
        {loading ? '추천 중...' : '학교와 교통이 좋은 동네 추천받기'}
      </button>

      <h2>추천 동네 목록</h2>
      <ul>
        {recommendations.map((dong, index) => (
          <li key={index}>
            <strong>{dong.dong}</strong> (총점: {dong.total_score.toFixed(2)})
            <br/>
            <span> - 학교 점수 : {dong.school_score}, 지하철 점수: {dong.subway_score}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default RecommendationComponent