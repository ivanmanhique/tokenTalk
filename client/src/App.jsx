import { BrowserRouter as Router , Route , Routes  } from 'react-router-dom'
import Dashboard from './Dashboard/Dashboard'
import LandingPage  from './LandingPage/LandingPage'
import './App.css'

function App() {

  return (
    <>
        <Router>
            <Routes>
                <Route path='/'  element={<LandingPage/>}/>
                 <Route path='/Dashboard'  element={<Dashboard/>}/>
            </Routes>
      </Router>
    </>
  )
}

export default App
