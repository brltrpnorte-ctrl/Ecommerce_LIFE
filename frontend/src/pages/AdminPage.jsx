import { useState } from 'react'
import { api } from '../lib/api.js'

const ADMIN_ACCESS_KEY = 'ecommerce_life_admin_access'

function formatPayload(payload) {
  return JSON.stringify(payload, null, 2)
}

function parsePayload(raw) {
  let parsed
  try {
    parsed = JSON.parse(raw)
  } catch {
    throw new Error('JSON invalido no editor')
  }

  if (!parsed || typeof parsed !== 'object') {
    throw new Error('Payload invalido')
  }

  if (!parsed.site_content || !parsed.catalog) {
    throw new Error('Payload deve conter site_content e catalog')
  }

  return {
    site_content: parsed.site_content,
    catalog: parsed.catalog,
  }
}

export function AdminPage() {
  const [token, setToken] = useState('')
  const [overview, setOverview] = useState(null)
  const [editorValue, setEditorValue] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('success')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const setAdminAccess = (enabled) => {
    if (typeof window === 'undefined') {
      return
    }
    if (enabled) {
      localStorage.setItem(ADMIN_ACCESS_KEY, 'true')
    } else {
      localStorage.removeItem(ADMIN_ACCESS_KEY)
    }
    window.dispatchEvent(new Event('admin-access-changed'))
  }

  async function handleLoadDashboard() {
    if (!token.trim()) {
      setError('Informe o token admin para carregar o painel')
      return
    }

    setError('')
    setMessage('')
    setLoading(true)

    try {
      const [overviewResponse, contentResponse] = await Promise.all([api.getAdminOverview(token), api.getAdminContent(token)])
      setOverview(overviewResponse)
      setEditorValue(formatPayload(contentResponse))
      setMessage('Conteudo carregado com sucesso.')
      setMessageType('success')
      setAdminAccess(true)
    } catch (err) {
      setError(err.message)
      setOverview(null)
      setEditorValue('')
      setAdminAccess(false)
    } finally {
      setLoading(false)
    }
  }

  function handleValidateEditor() {
    setError('')
    try {
      parsePayload(editorValue)
      setMessage('JSON valido. Pronto para salvar.')
      setMessageType('success')
    } catch (err) {
      setMessage(err.message)
      setMessageType('error')
    }
  }

  async function handleSaveEditor() {
    if (!token.trim()) {
      setError('Informe o token admin para salvar alteracoes')
      return
    }

    setError('')
    setSaving(true)

    try {
      const payload = parsePayload(editorValue)
      const updated = await api.updateAdminContent(token, payload)
      const refreshedOverview = await api.getAdminOverview(token)
      setOverview(refreshedOverview)
      setEditorValue(formatPayload(updated))
      setMessage(`Conteudo salvo com sucesso em ${new Date(updated.updated_at).toLocaleString('pt-BR')}.`)
      setMessageType('success')
      setAdminAccess(true)
    } catch (err) {
      setMessage(err.message)
      setMessageType('error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="page container admin-page">
      <header className="section-head">
        <h1>Painel Administrador</h1>
        <p>Edite banners, fotos/videos, textos, promocoes, categorias, marcas e produtos em um unico painel.</p>
      </header>

      <div className="admin-auth">
        <input
          placeholder="Token admin"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          type="password"
        />
        <button type="button" className="btn-primary" onClick={handleLoadDashboard} disabled={loading}>
          {loading ? 'Carregando...' : 'Carregar painel'}
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

      {editorValue ? (
        <article className="info-card admin-editor-card">
          <h3>Editor CMS (JSON)</h3>
          <p>
            Altere qualquer conteudo do site neste JSON: hero/carrossel, banners com imagem/video, biblioteca de midia,
            textos, polaroids, ordem de secoes, categorias, marcas, produtos e promocoes.
          </p>

          <textarea
            className="admin-json-editor"
            value={editorValue}
            onChange={(event) => setEditorValue(event.target.value)}
            spellCheck={false}
            aria-label="Editor de conteudo do site"
          />

          <div className="admin-editor-actions">
            <button type="button" onClick={handleValidateEditor}>
              Validar JSON
            </button>
            <button type="button" className="btn-primary" onClick={handleSaveEditor} disabled={saving}>
              {saving ? 'Salvando...' : 'Salvar alteracoes'}
            </button>
          </div>

          {message ? <p className={messageType === 'error' ? 'error-text' : 'success-text'}>{message}</p> : null}
        </article>
      ) : null}
    </section>
  )
}
