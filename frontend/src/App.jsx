import { useState } from "react"
import InfrastructureMap from "./components/InfrastructureMap.jsx"
import RecommendationComponent from "./components/RecommendationComponent.jsx"
import Signup from "./pages/Signup"

function App() {
  // 지도의 중심점을 state로 관리
  const [mapCenter, setMapCenter] = useState({
    lat: 37.4979,
    lng: 127.0276
  })

  // 동네를 클릭했을 때 지도의 중심을 변경하는 함수
  const handleDongClick = (newCenter) => {
    setMapCenter(newCenter)
  }

  return (
    <>
      <h1 className="text-3xl font-bold underline" > AI 부동산 추천 서비스</h1>
      <RecommendationComponent onDongCLick={handleDongClick}/>
      <hr className="my-8"/>
      <h2 className="text-2xl font-bold">주변 인프라 지도</h2>
      <InfrastructureMap lat={mapCenter.lat} lng={mapCenter.lng}/>
    </>
  )

}

export default App
