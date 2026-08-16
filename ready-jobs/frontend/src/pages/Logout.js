import React, { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

export default function Logout() {
  const { logout } = useContext(AuthContext)
  const navigate = useNavigate()

  const handleClick = () => {
    logout()            // clears user, token, axios header, localStorage
    navigate('/login')  // send them back to login page
  }

  return (
    <button onClick={handleClick} className="btn btn-link">
      Logout
    </button>
  )
}