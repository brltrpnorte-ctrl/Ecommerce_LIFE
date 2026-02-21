import { Link } from 'react-router-dom'

export function WishlistPage() {
  return (
    <section className="page container wishlist-page">
      <header className="section-head">
        <h1>Wishlist</h1>
        <p>Salve produtos favoritos para comprar depois.</p>
      </header>

      <article className="info-card">
        <p>Nenhum produto salvo no momento.</p>
        <Link className="btn-primary" to="/produtos">
          Ir para produtos
        </Link>
      </article>
    </section>
  )
}
