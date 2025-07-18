import {Outlet} from 'react-router-dom'

function App() {
  return(
    <div className='p-8'>
      <header className='mb-8'>
        <h1 className='text-3xl font-bold'>AI 맞춤형 집 찾기</h1>
      </header>
      <main>
        {/* 각 페이지 내용 렌더링 */}
        <Outlet/>
      </main>
    </div>
  )
}

export default App