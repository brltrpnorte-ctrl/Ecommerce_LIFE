import { useEffect, useMemo, useState } from 'react'
import { ProductCard } from '../components/ProductCard.jsx'
import { api } from '../lib/api.js'
import { categoryLabels } from '../data/siteContent.js'

export function ProductsPage() {
  const [categories, setCategories] = useState([])
  const [brands, setBrands] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)

  const [filters, setFilters] = useState({
    category: '',
    brand: '',
    q: '',
    min_price: '',
    max_price: '',
  })

  useEffect(() => {
    let isMounted = true

    Promise.all([api.getCategories(), api.getBrands()])
      .then(([categoryResponse, brandResponse]) => {
        if (isMounted) {
          setCategories(categoryResponse.items)
          setBrands(brandResponse.items)
        }
      })
      .catch(() => {
        if (isMounted) {
          setCategories([])
          setBrands([])
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    let isMounted = true

    api
      .getProducts(filters)
      .then((response) => {
        if (isMounted) {
          setProducts(response.items)
        }
      })
      .catch(() => {
        if (isMounted) {
          setProducts([])
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [filters])

  const totalStock = useMemo(() => products.reduce((sum, item) => sum + item.stock, 0), [products])

  const updateFilter = (key, value) => {
    setLoading(true)
    setFilters((state) => ({ ...state, [key]: value }))
  }

  return (
    <section className="page container products-page">
      <header className="section-head">
        <div>
          <p className="eyebrow">Galeria de Produtos</p>
          <h1>Catalogo com filtros por marca e categoria</h1>
        </div>
        <p>{products.length} produtos encontrados - {totalStock} unidades em estoque</p>
      </header>

      <form className="filter-grid" onSubmit={(event) => event.preventDefault()}>
        <input
          placeholder="Buscar por nome"
          value={filters.q}
          onChange={(event) => updateFilter('q', event.target.value)}
        />

        <select
          value={filters.category}
          onChange={(event) => updateFilter('category', event.target.value)}
        >
          <option value="">Todas categorias</option>
          {categories.map((item) => (
            <option key={item} value={item}>
              {categoryLabels[item] || item}
            </option>
          ))}
        </select>

        <select value={filters.brand} onChange={(event) => updateFilter('brand', event.target.value)}>
          <option value="">Todas marcas</option>
          {brands.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <input
          type="number"
          min="0"
          placeholder="Preco minimo"
          value={filters.min_price}
          onChange={(event) => updateFilter('min_price', event.target.value)}
        />

        <input
          type="number"
          min="0"
          placeholder="Preco maximo"
          value={filters.max_price}
          onChange={(event) => updateFilter('max_price', event.target.value)}
        />
      </form>

      {loading ? <p>Carregando catalogo...</p> : null}

      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  )
}

