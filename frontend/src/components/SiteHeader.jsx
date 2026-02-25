import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useCart } from '../context/useCart.js'
import lifeLogo from '../assets/life-logo.png'

const ADMIN_ACCESS_KEY = 'ecommerce_life_admin_access'

const primaryLinks = [
  { label: 'Inicio', to: '/' },
  { label: 'Produtos', to: '/produtos' },
  { label: 'Promocoes', to: '/promocoes' },
]

const menuLinks = [
  { label: 'Checkout', to: '/checkout' },
  { label: 'Minha Conta', to: '/conta' },
  { label: 'Rastreamento', to: '/rastreamento' },
  { label: 'Wishlist', to: '/wishlist' },
]

export function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [hasAdminAccess, setHasAdminAccess] = useState(false)
  const { totalItems } = useCart()

  useEffect(() => {
    const syncAccess = () => {
      if (typeof window === 'undefined') {
        setHasAdminAccess(false)
        return
      }
      setHasAdminAccess(localStorage.getItem(ADMIN_ACCESS_KEY) === 'true')
    }

    syncAccess()
    window.addEventListener('storage', syncAccess)
    window.addEventListener('admin-access-changed', syncAccess)
    return () => {
      window.removeEventListener('storage', syncAccess)
      window.removeEventListener('admin-access-changed', syncAccess)
    }
  }, [])

  return (
    <header className="site-header">
      <div className="container header-inner">
        <div className="header-top">
          <NavLink to="/" className="header-logo-link" onClick={() => setMenuOpen(false)} aria-label="Pagina inicial">
            <img className="header-logo logo-spin-slow" src={lifeLogo} alt="Logo da LIFE STYLE" />
          </NavLink>
        </div>

        <div className="header-bottom">
          <div className="header-controls">
            <nav className="primary-nav" aria-label="Navegacao principal">
              {primaryLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) => (isActive ? 'active' : '')}
                  onClick={() => setMenuOpen(false)}
                >
                  {link.label}
                </NavLink>
              ))}
            </nav>

            <div className="header-actions">
              <NavLink to="/login" className="auth-pill" onClick={() => setMenuOpen(false)}>
                Entrar
              </NavLink>

              <div className="header-menu-wrap">
                <button
                  className="icon-menu-toggle"
                  type="button"
                  onClick={() => setMenuOpen((value) => !value)}
                  aria-label={menuOpen ? 'Fechar menu de opcoes' : 'Abrir menu de opcoes'}
                  aria-controls="header-action-menu"
                  aria-expanded={menuOpen}
                >
                  <span className="menu-icon" aria-hidden="true">
                    <span />
                    <span />
                    <span />
                  </span>
                </button>

                <nav id="header-action-menu" className={`action-menu ${menuOpen ? 'open' : ''}`} aria-label="Menu secundario">
                  {menuLinks.map((link) => (
                    <NavLink
                      key={link.to}
                      to={link.to}
                      className={({ isActive }) => (isActive ? 'active' : '')}
                      onClick={() => setMenuOpen(false)}
                    >
                      {link.label}
                    </NavLink>
                  ))}
                  {hasAdminAccess ? (
                    <NavLink to="/admin" onClick={() => setMenuOpen(false)}>
                      Admin
                    </NavLink>
                  ) : null}
                  <NavLink to="/checkout" className="menu-cart-pill" onClick={() => setMenuOpen(false)}>
                    Carrinho ({totalItems})
                  </NavLink>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
