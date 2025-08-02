import React from 'react'
import ReactDOM from 'react-dom/client'
import {createBrowserRouter, RouterProvider} from 'react-router-dom'
import './index.css'

import App from './App.jsx'
import Home from './pages/Home.jsx'
import PreferenceView from './pages/PreferenceView.jsx'
import RecommendationView from './pages/RecommendationView.jsx'
import DetailView from './pages/DetailView.jsx'
import Ui from './pages/Ui.jsx'

const router = createBrowserRouter([
  {
    path:'/',
    element:<App/>,
    children:[
      // {path:'/', element:<Home/>},
      // {path:'/', element:<Ui/>},
      // {path:'/preference', element:<PreferenceView/>},// 조건 입력
      {path:'/', element:<PreferenceView/>},// 조건 입력
      {path:'/recommend',element:<RecommendationView/>}, // 추천 결과
      {path:'/detail/:propertyId',element:<DetailView/>} // 상세분석
    ]
  }
])

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router}/>
  </React.StrictMode>
)
