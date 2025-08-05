import React from 'react';

const NeighborhoodCard = ({ dongData, onCardClick, isSelected }) => {
  const tags = [];
  const { school_count, subway_count, hospital_count, mart_count, park_count } = dongData;

  // --- 데이터 기반으로 동적 태그 생성 ---
  // 교육
  if (school_count >= 10) {
    tags.push({ text: '#우수학군', color: 'blue' });
  }

  // 생활 편의
  if (subway_count >= 3) {
    tags.push({ text: '#교통의 중심', color: 'purple' });
  }
  if (mart_count >= 3 && hospital_count >= 5) {
    tags.push({ text: '#슬세권', color: 'gray' });
  }
  
  // 분위기 / 환경
  if (park_count >= 5) {
    tags.push({ text: '#숲세권', color: 'green' });
  } else if (park_count >= 3 && subway_count <= 2) {
    tags.push({ text: '#조용한 주거지', color: 'gray' });
  }
  
  if ((subway_count + mart_count + hospital_count) >= 15) {
    tags.push({ text: '#활기찬 번화가', color: 'yellow' });
  }
  // --- 여기까지 ---

  // Tailwind CSS 색상 맵
  const tagColors = {
    blue: "bg-blue-100 text-blue-800",
    purple: "bg-purple-100 text-purple-800",
    green: "bg-green-100 text-green-800",
    yellow: "bg-yellow-100 text-yellow-800",
    gray: "bg-gray-100 text-gray-800",
  };

  const cardStyle = isSelected
    ? "border-pink-400 ring-2 ring-[#FF7E97]"
    : "border-gray-200 hover:shadow-lg";

  return (
    <div 
      onClick={() => onCardClick(dongData.dong)}
      className={`bg-white/80 backdrop-blur-lg p-5 rounded-xl shadow-lg border-2 transition-all duration-300 cursor-pointer ${cardStyle}`}
    >
      <h3 className='font-bold text-slate-900'>{dongData.dong}</h3>
      <p className='text-sm text-gray-500 mt-1'>{dongData.sigungu_name}</p>
      
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
