import {useState, useEffect} from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'

function RecommendationView () {
  const location = useLocation()
  const navigate = useNavigate()
  const searchConditions = location.state?.conditions;

  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(()=>{
    if(!searchConditions){
      alert("검색 조건이 없습니다. 이전 페이지로 돌아갑니다.")
      navigate('/')
      return
    }

    const fetchRecommendations = async() => {
      setLoading(true)
      try{
        //Node.js에 넘겨
        const response = await axios.post('/api/recommend/neighborhood',{
          //lifestyle 조건만 preferences로 전달
          preferences: searchConditions.lifestyle
        })
        setRecommendations(response.data)
      } catch(error){
        console.error('추천 데이터를 불러오는 데 실패했습니다.', error)
      } finally{
        setLoading(false)
      }
    }
    fetchRecommendations()
  }, [searchConditions, navigate])

  if(loading){
    return <div>AI가 최적의 동네를 찾고 있습니다...</div>
  }

  return (
    <div>
      <h2> 2. AI 추천 결과입니다.</h2>
      <h3>이런 동네는 어떠세요?</h3>
      <div className='flex gap-4'>
        {recommendations.map((dong, index)=> (
          <div key={index} className='border border-solid border-[#eee] p-4'>
            <h4>{dong.dong}</h4>
            <p>총점: {dong.total_score.toFixed(2)}</p>
            <br/>
            {dong.avg_price > 0 && <span className='text-[#555]'>평균 가격 : {dong.avg_price.toLocaleString()}만원</span>}
            {/* todo: 출퇴근 시간 등 추가 정보 표시 */}
          </div>
        ))}
      </div>
    </div>
  )
}
export default RecommendationView