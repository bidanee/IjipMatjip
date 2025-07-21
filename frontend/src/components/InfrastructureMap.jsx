import { useEffect, useState } from "react"
import { Map, MapMarker } from "react-kakao-maps-sdk"
import axios from 'axios'

//props로 지도의 중심 좌표 받음
const InfrastructureMap = ({lat, lng, isPropertyMarker = false}) => {
  const [schools, setSchools] = useState([])
  const [subways, setSubways] = useState([])

  //컴포넌트가 처음 렌더링될 때 주변 인프라 데이터를 불러옴
  useEffect(() => {
    const fetchInfrastructure = async() => {
      if (!lat || !lng) return;
      try{
        const response = await axios.post('/api/infrastructure',{
          latitude:lat,
          longitude:lng,
          radius_km:0.5
        })
        setSchools(response.data.schools)
        setSubways(response.data.subways)
      } catch(error){
        console.error("인프라 데이터를 불러오는 데 실패했습니다.", error)
      }
    }
    fetchInfrastructure()
  },[lat, lng])

  return (
    <Map center={{lat,lng}} style={{ width: '100%', height:'450px'}} level={4}>
      {/* 매물 위치 마커 추가 */}
      {isPropertyMarker && (<MapMarker position={{lat,lng}} image={{src:'/images/home_pin.png', size:{width:80, height:80}, options:{offset:{x:24, y:48}}}}></MapMarker>)}
      {/* 학교 마커 표시 */}
      {schools.map((school,index) => (
        <MapMarker key={`school-${index}`} position={{lat:school.latitude, lng:school.longitude}} image={{ src: '/images/school.png', size: { width: 80, height: 80 },}} title={school.name} />
      ))}
      {/* 지하철역 마커 표시 */}
      {subways.map((subway,index) => (
        <MapMarker key={`subway-${index}`} position={{lat:subway.latitude, lng:subway.longitude}} image={{src:'/images/subway.png', size: {width:80, height:80},}} title={subway.name} /> 
      ))}
    </Map>
  )
}

export default InfrastructureMap