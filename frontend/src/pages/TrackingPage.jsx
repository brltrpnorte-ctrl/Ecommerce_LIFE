import { useState } from 'react'

const demoSteps = ['Pedido confirmado', 'Pagamento aprovado', 'Em separacao', 'Enviado', 'Saiu para entrega', 'Entregue']

export function TrackingPage() {
  const [code, setCode] = useState('')
  const [stage, setStage] = useState(null)

  function handleTrack(event) {
    event.preventDefault()
    const normalized = code.trim().length
    setStage(Math.min(demoSteps.length - 1, Math.max(0, normalized % demoSteps.length)))
  }

  return (
    <section className="page container tracking-page">
      <header className="section-head">
        <h1>Rastreamento de Pedido</h1>
        <p>Consulte status por codigo dos Correios/transportadora.</p>
      </header>

      <form className="tracking-form" onSubmit={handleTrack}>
        <input
          value={code}
          onChange={(event) => setCode(event.target.value)}
          placeholder="Ex: NL123456789BR"
          required
        />
        <button type="submit" className="btn-primary">
          Consultar
        </button>
      </form>

      {stage !== null ? (
        <ol className="timeline">
          {demoSteps.map((step, index) => (
            <li key={step} className={index <= stage ? 'done' : ''}>
              {step}
            </li>
          ))}
        </ol>
      ) : null}
    </section>
  )
}
