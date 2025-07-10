import express from 'express'
import signupRouter from './routes/signup.js'
import loginRouter from './routes/login.js'

const app = express();
const port = 3001;

app.use(express.json());

app.use('/api/signup', signupRouter);

app.use('/api/login', loginRouter)

app.listen(port, () => {
  console.log(`✅ Server is running on port ${port}`)
})