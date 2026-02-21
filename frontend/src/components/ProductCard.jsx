import { Link } from 'react-router-dom'
import { formatCurrency } from '../lib/format.js'

export function ProductCard({ product }) {
  return (
    <article className="product-card">
      <img src={product.media[0]} alt={product.name} loading="lazy" />
      <div className="product-content">
        <p className="product-brand">{product.brand}</p>
        <h3>{product.name}</h3>
        <p className="product-meta">
          {product.category} - estoque {product.stock}
        </p>
        {product.promo_tag ? <p className="product-promo">{product.promo_tag}</p> : null}
        <div className="product-footer">
          <strong>{formatCurrency(product.price)}</strong>
          <Link to={`/produto/${product.slug}`}>Ver produto</Link>
        </div>
      </div>
    </article>
  )
}
