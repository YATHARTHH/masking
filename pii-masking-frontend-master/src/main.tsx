import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@/index.css'
import App from '@/App.tsx'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css';
import { UserProvider } from '@/context/userContext'
import { UsersDataProvider } from '@/context/usersDataContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
      <UserProvider>
        <UsersDataProvider>
          <ToastContainer
            position='top-right'
            closeOnClick={true}
            autoClose={3000}
          />
          <App />
        </UsersDataProvider>
      </UserProvider>
  </StrictMode>,
)
