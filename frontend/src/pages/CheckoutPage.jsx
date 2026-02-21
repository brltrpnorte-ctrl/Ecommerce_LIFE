import { useMemo, useState } from 'react'
import { useCart } from '../context/useCart.js'
import { api } from '../lib/api.js'
import { formatCurrency } from '../lib/format.js'

export function CheckoutPage() {
  const { items, subtotal, removeItem, updateQuantity, clearCart } = useCart()
  const [zipCode, setZipCode] = useState('')
  const [shippingOptions, setShippingOptions] = useState([])
  const [selectedShipping, setSelectedShipping] = useState(null)
  const [email, setEmail] = useState('')
  const [method, setMethod] = useState('pix')
  const [installments, setInstallments] = useState(1)
  const [checkoutStatus, setCheckoutStatus] = useState(null)

  const totalWeight = useMemo(() => items.reduce((sum, item) => sum + item.quantity * 0.35, 0), [items])
  const shippingPrice = selectedShipping?.price || 0
  const finalTotal = subtotal + shippingPrice

  async function handleShipping(event) {
    event.preventDefault()

    try {
      const response = await api.getShippingQuote({
        zip_code: zipCode,
        subtotal,
        weight_kg: totalWeight || 0.3,
      })
      setShippingOptions(response.options)
      setSelectedShipping(response.options[0])
    } catch {
      setShippingOptions([])
      setSelectedShipping(null)
    }
  }

  async function handleValidateCheckout() {
    try {
      const response = await api.validateCheckout({
        cart_total: finalTotal,
        method,
        installments,
        customer_email: email,
      })
      setCheckoutStatus(response)
      if (response.approved) {
        clearCart()
      }
    } catch {
      setCheckoutStatus({ approved: false, risk_score: 100, recommended_action: 'Falha na validacao' })
    }
  }

  return (
    <section className="page container checkout-page">
      <header className="section-head">
        <h1>Carrinho e Checkout</h1>
        <p>Processo simples, rapido e seguro para conversao.</p>
      </header>

      <div className="checkout-grid">
        <div className="checkout-panel">
          <h2>Itens no carrinho</h2>
          {items.length === 0 ? <p>Seu carrinho esta vazio.</p> : null}

          {items.map((item, index) => (
            <article key={`${item.slug}-${index}`} className="cart-item">
              <img src={item.media[0]} alt={item.name} />
              <div>
                <h3>{item.name}</h3>
                <p>
                  {item.selectedSize || '-'} · {item.selectedColor || '-'}
                </p>
                <strong>{formatCurrency(item.price)}</strong>
              </div>

              <div className="quantity-box">
                <button type="button" onClick={() => updateQuantity(index, item.quantity - 1)}>
                  -
                </button>
                <span>{item.quantity}</span>
                <button type="button" onClick={() => updateQuantity(index, item.quantity + 1)}>
                  +
                </button>
                <button type="button" onClick={() => removeItem(index)}>
                  Remover
                </button>
              </div>
            </article>
          ))}
        </div>

        <aside className="checkout-panel">
          <h2>Resumo</h2>
          <p>Subtotal: {formatCurrency(subtotal)}</p>
          <p>Frete: {formatCurrency(shippingPrice)}</p>
          <strong>Total: {formatCurrency(finalTotal)}</strong>

          <form onSubmit={handleShipping} className="checkout-form">
            <label htmlFor="zip">CEP</label>
            <input id="zip" placeholder="00000-000" value={zipCode} onChange={(event) => setZipCode(event.target.value)} />
            <button type="submit">Calcular frete</button>
          </form>

          {shippingOptions.length > 0 ? (
            <div className="shipping-options">
              {shippingOptions.map((option) => (
                <button
                  key={option.name}
                  className={selectedShipping?.name === option.name ? 'selected' : ''}
                  type="button"
                  onClick={() => setSelectedShipping(option)}
                >
                  {option.name} · {option.days} dias · {formatCurrency(option.price)}
                </button>
              ))}
            </div>
          ) : null}

          <div className="checkout-form">
            <label htmlFor="email">E-mail</label>
            <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} />

            <label htmlFor="payment">Pagamento</label>
            <select id="payment" value={method} onChange={(event) => setMethod(event.target.value)}>
              <option value="pix">Pix</option>
              <option value="card">Cartao</option>
              <option value="boleto">Boleto</option>
            </select>

            <label htmlFor="installments">Parcelas</label>
            <input
              id="installments"
              type="number"
              min="1"
              max="12"
              value={installments}
              onChange={(event) => setInstallments(Number(event.target.value))}
            />

            <button type="button" className="btn-primary" onClick={handleValidateCheckout}>
              Confirmar pedido
            </button>
          </div>

          {checkoutStatus ? (
            <div className={`checkout-status ${checkoutStatus.approved ? 'approved' : 'warning'}`}>
              <p>Score de risco: {checkoutStatus.risk_score}</p>
              <p>{checkoutStatus.recommended_action}</p>
            </div>
          ) : null}
        </aside>
      </div>
    </section>
  )
}

