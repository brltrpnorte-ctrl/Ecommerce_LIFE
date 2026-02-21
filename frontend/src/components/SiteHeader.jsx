import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useCart } from '../context/useCart.js'
import lifeLogo from '../assets/life-logo.svg'

const links = [
  { label: 'Inicio', to: '/' },
  { label: 'Produtos', to: '/produtos' },
  { label: 'Checkout', to: '/checkout' },
  { label: 'Minha Conta', to: '/conta' },
  { label: 'Rastreamento', to: '/rastreamento' },
  { label: 'Admin', to: '/admin' },
]

export function SiteHeader() {
  const [open, setOpen] = useState(false)
  const { totalItems } = useCart()

  return (
    <header className="site-header">
      <div className="header-layout container">
        <div className="header-grid">
          <div className="header-column">
            <div className="header-inner">
              <div className="header-bottom">
                <NavLink to="/" className="brand-mark" onClick={() => setOpen(false)}>
                  LIFE <span>Style Store</span>
                </NavLink>

                <button
                  className="menu-toggle"
                  type="button"
                  onClick={() => setOpen((value) => !value)}
                  aria-label="Abrir menu"
                >
                  Menu
                </button>

                <nav className={`main-nav ${open ? 'open' : ''}`}>
                  {links.map((link) => (
                    <NavLink
                      key={link.to}
                      to={link.to}
                      className={({ isActive }) => (isActive ? 'active' : '')}
                      onClick={() => setOpen(false)}
                    >
                      {link.label}
                    </NavLink>
                  ))}
                  <NavLink to="/checkout" className="cart-pill" onClick={() => setOpen(false)}>
                    Carrinho ({totalItems})
                  </NavLink>
                  <NavLink to="/login" className="auth-pill" onClick={() => setOpen(false)}>
                    Entrar
                  </NavLink>
                </nav>
              </div>
            </div>
          </div>
          <div className="header-column header-column-right">
            <div className="logo-section">
              <NavLink to="/" className="header-logo-link" onClick={() => setOpen(false)} aria-label="Pagina inicial">
                <img className="header-logo mx-auto" src={lifeLogo} alt="LIFE Style" />
              </NavLink>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
