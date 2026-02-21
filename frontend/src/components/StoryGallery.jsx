import { useState } from 'react'

export function StoryGallery({ items }) {
  const [selected, setSelected] = useState(null)

  return (
    <section className="story-section">
      <div className="story-header">
        <p className="eyebrow">Nossa Historia</p>
        <h2>Galeria polaroid com sentimento e memoria</h2>
      </div>

      <div className="story-grid">
        {items.map((item) => (
          <button key={item.id} className="polaroid-card" type="button" onClick={() => setSelected(item)}>
            <img src={item.src} alt={item.title} loading="lazy" />
            <h3>{item.title}</h3>
            <p>{item.text}</p>
          </button>
        ))}
      </div>

      {selected ? (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-card">
            <button type="button" onClick={() => setSelected(null)} className="modal-close">
              Fechar
            </button>
            <img src={selected.src} alt={selected.title} />
            <h3>{selected.title}</h3>
            <p>{selected.text}</p>
          </div>
        </div>
      ) : null}
    </section>
  )
}
