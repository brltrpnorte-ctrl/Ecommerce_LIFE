import { Navigate, Route, Routes } from 'react-router-dom'
import { SiteHeader } from './components/SiteHeader.jsx'
import { SiteFooter } from './components/SiteFooter.jsx'
import { HomePage } from './pages/HomePage.jsx'
import { ProductsPage } from './pages/ProductsPage.jsx'
import { ProductDetailsPage } from './pages/ProductDetailsPage.jsx'
import { CheckoutPage } from './pages/CheckoutPage.jsx'
import { AccountPage } from './pages/AccountPage.jsx'
import { LoginPage } from './pages/LoginPage.jsx'
import { TrackingPage } from './pages/TrackingPage.jsx'
import { AdminPage } from './pages/AdminPage.jsx'
import { WishlistPage } from './pages/WishlistPage.jsx'
import { NotFoundPage } from './pages/NotFoundPage.jsx'

function App() {
  return (
    <div className="app-shell">
      <SiteHeader />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/produtos" element={<ProductsPage />} />
          <Route path="/produto/:slug" element={<ProductDetailsPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/conta" element={<AccountPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/rastreamento" element={<TrackingPage />} />
          <Route path="/wishlist" element={<WishlistPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/home" element={<Navigate to="/" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <SiteFooter />
    </div>
  )
}

export default App
