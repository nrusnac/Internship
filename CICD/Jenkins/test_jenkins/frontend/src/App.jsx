import { useEffect, useState } from 'react'
import { greet } from './greeting'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8081'

function App() {
  const [message, setMessage] = useState(greet('browser'))
  const [backendUp, setBackendUp] = useState(false)

  useEffect(() => {
    fetch(`${API_URL}/api/hello?name=Jenkins`)
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.message)
        setBackendUp(true)
      })
      .catch(() => setBackendUp(false))
  }, [])

  return (
    <main style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '4rem' }}>
      <h1>{message}</h1>
      <p>
        {backendUp
          ? 'Message served by the Gradle backend.'
          : 'Backend offline — showing local greeting.'}
      </p>
    </main>
  )
}

export default App
