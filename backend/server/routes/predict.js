import express from 'express'
import axios from 'axios'
import 'dotenv/config'

const predictRouter = express.Router()
const AI_SERVER_URL = process.env.FASTAPI_SERVER

predictRouter.post('/rental', async (req, res) => {
  try{
    // React로 받은 매물 정보를 그대로 AI 서버의 /predict/rental로 전달
    const response = await axios.post(`${AI_SERVER_URL}/predict/rental`, req.body)
    res.json(response.data)
  } catch(error) {
    console.error('AI 서버 전월세 예측 API 통신 중 에러 발생:', error.message)
    if(error.response){
      res.status(error.response.status).json(error.response.data)
    } else{
      res.status(500).json({detail: '전월세 예측 중 서버 에러 발생'})
    }
  }
})

export default predictRouter