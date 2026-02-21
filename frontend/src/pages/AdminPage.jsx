import { useState } from 'react'
import { api } from '../lib/api.js'

export function AdminPage() {
  const [token, setToken] = useState('')
  const [overview, setOverview] = useState(null)
  const [error, setError] = useState('')

  async function handleLoadDashboard() {
    setError('')
    setOverview(null)

    try {
      const response = await api.getAdminOverview(token)
      setOverview(response)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <section className="page container admin-page">
      <header className="section-head">
        <h1>Painel Administrador</h1>
        <p>Estoque, produtos, banners, promocoes e visao financeira.</p>
      </header>

      <div className="admin-auth">
        <input
          placeholder="Token admin"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          type="password"
        />
        <button type="button" className="btn-primary" onClick={handleLoadDashboard}>
          Carregar painel
        </button>
      </div>

      {error ? <p className="error-text">{error}</p> : null}

      {overview ? (
        <div className="cards-grid">
          <article className="info-card">
            <h3>Produtos cadastrados</h3>
            <p>{overview.total_products}</p>
          </article>
          <article className="info-card">
            <h3>Alertas de estoque</h3>
            <p>{overview.low_stock_alerts}</p>
          </article>
          <article className="info-card">
            <h3>Pedidos abertos</h3>
            <p>{overview.open_orders}</p>
          </article>
          <article className="info-card">
            <h3>Receita estimada</h3>
            <p>R$ {overview.estimated_month_revenue.toLocaleString('pt-BR')}</p>
          </article>
        </div>
      ) : null}
    </section>
  )
}
