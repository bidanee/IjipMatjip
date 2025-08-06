import express from 'express';
import axios from 'axios';
import 'dotenv/config';

const reportRouter = express.Router();

const AI_SERVER_URL = process.env.FASTAPI_SERVER;

reportRouter.post('/generate', async (req, res) => {
  try {
    const response = await axios.post(`${AI_SERVER_URL}/report/generate`, req.body);
    res.json(response.data);
  } catch (error) {
    console.error('AI 서버 리포트 생성 API 통신 중 에러 발생:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ detail: 'AI 리포트 생성 중 서버 에러 발생' });
    }
  }
});

export default reportRouter;