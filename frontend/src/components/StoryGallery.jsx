import { useState } from 'react'

const defaultCopy = {
  eyebrow: 'Nossa Historia',
  title: 'Galeria polaroid com sentimento e memoria',
}

export function StoryGallery({ items, copy = defaultCopy }) {
  const [selected, setSelected] = useState(null)

  const renderMedia = (item, { expanded = false } = {}) => {
    if (item.type === 'video') {
      return (
        <video
          src={item.src}
          className={expanded ? 'story-media-expanded' : 'story-media'}
          playsInline
          muted={!expanded}
          loop={!expanded}
          controls={expanded}
          preload="metadata"
        />
      )
    }
    return <img src={item.src} alt={item.title} loading="lazy" />
  }

  return (
    <section className="story-section">
      <div className="story-header">
        <p className="eyebrow">{copy.eyebrow || defaultCopy.eyebrow}</p>
        <h2>{copy.title || defaultCopy.title}</h2>
      </div>

      <div className="story-grid">
        {items.map((item) => (
          <button key={item.id} className="polaroid-card" type="button" onClick={() => setSelected(item)}>
            {renderMedia(item)}
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
            {renderMedia(selected, { expanded: true })}
            <h3>{selected.title}</h3>
            <p>{selected.text}</p>
          </div>
        </div>
      ) : null}
    </section>
  )
}
