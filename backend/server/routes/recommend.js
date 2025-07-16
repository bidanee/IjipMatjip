import express from 'express'
import axios from 'axios'
import 'dotenv/config'

const recommendRouter = express.Router()

const AI_SERVER_URL = process.env.FASTAPI_SERVER

recommendRouter.post('/neighborhood', async (req, res) => {
  try {
    const preferences = req.body.preferences;

    const response = await axios.post(`${AI_SERVER_URL}/recommend/neighborhood`, {
      preferences: preferences
    });

    res.json(response.data);

  } catch (error) {
    console.error('AI 서버 통신 중 에러 발생:', error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ detail: 'AI 서버와 통신할 수 없습니다.' });
    }
  }
});

export default recommendRouter;