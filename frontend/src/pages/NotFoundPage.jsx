import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <section className="page container not-found-page">
      <h1>Pagina nao encontrada</h1>
      <p>O conteudo solicitado nao existe ou foi movido.</p>
      <Link to="/" className="btn-primary">
        Voltar ao inicio
      </Link>
    </section>
  )
}
