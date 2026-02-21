export function AccountPage() {
  return (
    <section className="page container account-page">
      <header className="section-head">
        <h1>Minha Conta</h1>
        <p>Dados pessoais, enderecos e historico de pedidos.</p>
      </header>

      <div className="cards-grid">
        <article className="info-card">
          <h3>Dados pessoais</h3>
          <p>Nome, e-mail e telefone do cliente.</p>
        </article>
        <article className="info-card">
          <h3>Enderecos salvos</h3>
          <p>Gestao de endereco principal e secundarios.</p>
        </article>
        <article className="info-card">
          <h3>Historico de pedidos</h3>
          <p>Status, pagamentos e reenvio de comprovantes.</p>
        </article>
        <article className="info-card">
          <h3>Avaliacoes</h3>
          <p>Area para avaliar produtos apos entrega.</p>
        </article>
      </div>
    </section>
  )
}
