// const NeighborhoodCard = ({dongData, onCardClick, isSelected}) => {
//   const tags = [];

//   if (dongData.school_score > 70) tags.push({text:'#학군우수',color:'blue'})
//   if(dongData.subway_score > 70) tags.push({text: '#교통편리', color:'purple'})
//   if((dongData.park_count || 0) >=3) tags.push({text:'#자연친화',color:'yellow'})
//   if(dongData.subway_count >=5) {
//     tags.push({text:"#번화가",color:'yellow'})
//   }else if (dongData.subway_count <=1) {
//     tags.push({text:'#조용한', color:'gray'})
//   }
  
//   const tagColors = {
//     blue: 'bg-blue-100 text-blue-800',
//     purple: 'bg-purple-100 text-purplee-800',
//     green: 'bg-green-100 text-green-800',
//     yellow: 'bg-yellow-100 text-yellow-800',
//     gray: 'bg-gray-100 text-gray-800',
//   }

//   const cardStyle = isSelected ? 'border-blue-500 ring-2 ring-blue-300' : 'border-gray-200 hover:shadow-lg'

//   return(
//     <div onClick={() => onCardClick(dongData)} className={`border rounded-lg p-4 w-72 cursor-pointer shadow-md transition-shadow ${cardStyle}`}>
//       <h4 className="font-bold text-lg text-gray-800">
//         {dongData.dong}
//       </h4>
//       <p className="text-sm text-gray-600 my-2 truncate">
//         {dongData.sigungu_name}
//       </p>
//       {dongData.commute_minutes !=null && (
//         <p className="text-sm font-medium text-gray-700">
//           출퇴근: 🚇 약 {dongData.commute_minutes}분
//         </p>
//       )}
      
//       <div className="mt-3 flex gap-2 flex-wrap">
//         {tags.map(tag => (
//           <span key={tag.text} className={`${tagColors[tag.color]} text-xs font-medium px-2.5 py-0.5 rounded-full`}>
//             {tag.text}
//           </span>
//         ) )}
//       </div>
//     </div>
//   )

// }

// export default NeighborhoodCard


import React from 'react';

const NeighborhoodCard = ({ dongData, onCardClick, isSelected }) => {
  const tags = [];
  
  // --- 👇 데이터 기반으로 동적 태그 생성 ---
  // school_score가 70점 이상이면 '학군우수' 태그 추가
  if (dongData.school_score > 80) {
    tags.push({ text: '#학군우수', color: 'blue' });
  }
  // subway_score가 70점 이상이면 '교통편리' 태그 추가
  if (dongData.subway_score > 70) {
    tags.push({ text: '#교통편리', color: 'purple' });
  }
  // price_score가 70점 이상이면 '가성비' 태그 추가
  if (dongData.price_score > 80) {
    tags.push({ text: '#가성비', color: 'green' });
  }
  // --- 여기까지 ---

  // Tailwind CSS 색상 맵
  const tagColors = {
    blue: "bg-blue-100 text-blue-800",
    purple: "bg-purple-100 text-purple-800",
    green: "bg-green-100 text-green-800",
  };

  // 선택되었을 때의 스타일
  const cardStyle = isSelected
    ? "border-pink-400 ring-2 ring-[#FF7E97]"
    : "border-gray-200";

  return (
    <div 
      onClick={() => onCardClick(dongData.dong)}
      className={`bg-white/80 backdrop-blur-lg p-5 rounded-xl shadow-lg border-2 transition-all duration-300 cursor-pointer ${cardStyle}`}
    >
      <h3 className='font-bold text-slate-900'>{dongData.dong}</h3>
      <p className='text-sm text-gray-500 mt-1'>{dongData.sigungu_name}</p>
      
      {/* 출퇴근 시간이 있을 경우 표시 */}
      {dongData.commute_minutes != null && (
        <p className="text-sm font-medium text-gray-700 mt-2">
          🚇 약 {dongData.commute_minutes}분
        </p>
      )}

      <div className="mt-3 flex gap-2 flex-wrap">
        {tags.map(tag => (
          <span 
            key={tag.text} 
            className={`${tagColors[tag.color]} text-xs font-medium px-2.5 py-0.5 rounded-full`}
          >
            {tag.text}
          </span>
        ))}
      </div>
    </div>
  );
};

export default NeighborhoodCard;