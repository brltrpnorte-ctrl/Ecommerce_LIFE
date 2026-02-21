export function LoginPage() {
  return (
    <section className="page container login-page">
      <header className="section-head">
        <h1>Login do Cliente</h1>
        <p>Acesso com e-mail/senha ou login social.</p>
      </header>

      <div className="login-grid">
        <form className="info-card">
          <label htmlFor="email">E-mail</label>
          <input id="email" type="email" placeholder="cliente@email.com" />
          <label htmlFor="password">Senha</label>
          <input id="password" type="password" placeholder="********" />
          <button type="button" className="btn-primary">
            Entrar
          </button>
          <button type="button" className="btn-secondary">
            Recuperar senha
          </button>
        </form>

        <div className="info-card">
          <h3>Login social</h3>
          <p>Preparado para Google Identity Services e Sign in with Apple.</p>
          <button type="button" className="btn-primary">
            Continuar com Google
          </button>
          <button type="button" className="btn-secondary">
            Continuar com Apple (iCloud)
          </button>
        </div>
      </div>
    </section>
  )
}
