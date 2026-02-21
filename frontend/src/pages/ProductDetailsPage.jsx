import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useCart } from '../context/useCart.js'
import { api } from '../lib/api.js'
import { formatCurrency } from '../lib/format.js'

export function ProductDetailsPage() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const { addItem } = useCart()
  const [product, setProduct] = useState(null)
  const [error, setError] = useState('')
  const [selectedSize, setSelectedSize] = useState('')
  const [selectedColor, setSelectedColor] = useState('')

  useEffect(() => {
    api
      .getProductBySlug(slug)
      .then((response) => {
        setProduct(response)
        setSelectedSize(response.sizes[0] || '')
        setSelectedColor(response.colors[0] || '')
      })
      .catch((err) => setError(err.message))
  }, [slug])

  const canBuy = useMemo(() => product && product.stock > 0, [product])

  if (error) {
    return (
      <section className="page container">
        <h1>Produto indisponivel</h1>
        <p>{error}</p>
      </section>
    )
  }

  if (!product) {
    return (
      <section className="page container">
        <p>Carregando produto...</p>
      </section>
    )
  }

  return (
    <section className="page container product-details">
      <div className="media-area">
        <img src={product.media[0]} alt={product.name} />
      </div>
      <div className="info-area">
        <p className="eyebrow">{product.brand}</p>
        <h1>{product.name}</h1>
        <p>{product.description}</p>
        <strong className="price-big">{formatCurrency(product.price)}</strong>

        <div className="option-row">
          <label htmlFor="size">Tamanho</label>
          <select id="size" value={selectedSize} onChange={(event) => setSelectedSize(event.target.value)}>
            {product.sizes.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>

        <div className="option-row">
          <label htmlFor="color">Cor</label>
          <select id="color" value={selectedColor} onChange={(event) => setSelectedColor(event.target.value)}>
            {product.colors.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>

        <div className="detail-actions">
          <button
            type="button"
            className="btn-primary"
            disabled={!canBuy}
            onClick={() => addItem(product, selectedSize, selectedColor, 1)}
          >
            Adicionar ao carrinho
          </button>
          <button type="button" className="btn-secondary" onClick={() => navigate('/checkout')}>
            Finalizar compra
          </button>
        </div>
      </div>
    </section>
  )
}

