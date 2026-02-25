import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ProductCard } from '../components/ProductCard.jsx'
import { api } from '../lib/api.js'

const PROMOTIONS_PAGE_SIZE = 48

async function fetchAllPromotions() {
  const items = []
  let page = 1
  let total = null

  while (page <= 50) {
    const response = await api.getProducts({
      promo_only: true,
      page,
      page_size: PROMOTIONS_PAGE_SIZE,
    })

    const pageItems = Array.isArray(response.items) ? response.items : []
    items.push(...pageItems)

    if (typeof response.total === 'number') {
      total = response.total
    }

    if (!pageItems.length || (total !== null && items.length >= total)) {
      break
    }

    page += 1
  }

  return items
}

export function PromotionsPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let isMounted = true

    fetchAllPromotions()
      .then((items) => {
        if (!isMounted) return
        const sorted = [...items].sort((a, b) => {
          if (Boolean(a.featured) !== Boolean(b.featured)) {
            return Number(Boolean(b.featured)) - Number(Boolean(a.featured))
          }
          return Number(b.rating || 0) - Number(a.rating || 0)
        })
        setProducts(sorted)
      })
      .catch((err) => {
        if (!isMounted) return
        setProducts([])
        setError(err.message || 'Nao foi possivel carregar promocoes')
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  const totalStock = useMemo(() => products.reduce((sum, item) => sum + Number(item.stock || 0), 0), [products])
  const brandCount = useMemo(() => new Set(products.map((item) => item.brand)).size, [products])

  return (
    <section className="page container promotions-page">
      <header className="section-head">
        <div>
          <p className="eyebrow">Promocoes do Dia</p>
          <h1>Produtos em promocao publicados pelo painel admin</h1>
        </div>
        <p>{products.length} ofertas ativas - {totalStock} unidades em estoque</p>
      </header>

      <article className="info-card promotions-note">
        <div>
          <h3>Como um produto aparece aqui</h3>
          <p>
            No painel admin, edite o produto no JSON do catalogo e preencha o campo <code>promo_tag</code>. Ao salvar,
            ele entra automaticamente nesta pagina.
          </p>
        </div>
        <div className="promotions-note-actions">
          <p>{brandCount} marcas com ofertas ativas</p>
          <Link className="btn-secondary" to="/produtos">
            Ver catalogo completo
          </Link>
        </div>
      </article>

      {loading ? <p>Carregando promocoes do dia...</p> : null}
      {error ? <p className="error-text">{error}</p> : null}

      {!loading && !error && products.length === 0 ? (
        <article className="info-card promotions-empty">
          <h3>Nenhuma promocao publicada no momento</h3>
          <p>Adicione um valor em <code>promo_tag</code> no produto via painel admin para exibir ofertas nesta pagina.</p>
        </article>
      ) : null}

      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  )
}
