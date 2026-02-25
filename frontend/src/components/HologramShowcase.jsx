import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const defaultCopy = {
  eyebrow: 'Holograma LIFE STYLE',
  title: 'Emblema de 4 folhas como tapete de projecao 3D',
  body: 'A vitrine central projeta fotos e videos em camadas, simulando elevacao holografica do catalogo.',
}

export function HologramShowcase({ copy = defaultCopy }) {
  const sectionRef = useRef(null)

  useEffect(() => {
    const context = gsap.context(() => {
      gsap.from('.hologram-label', {
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.hologram-block',
          start: 'top 75%',
        },
      })
    }, sectionRef)

    return () => context.revert()
  }, [])

  return (
    <section className="hologram-block" ref={sectionRef}>
      <div className="hologram-label">
        <p className="eyebrow">{copy.eyebrow || defaultCopy.eyebrow}</p>
        <h2>{copy.title || defaultCopy.title}</h2>
        <p>{copy.body || defaultCopy.body}</p>
      </div>

      <div className="hologram-stage" aria-label="Banner trevo em destaque">
        <video
          className="hologram-banner"
          src="/trevo.mp4"
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          aria-hidden="true"
        />
      </div>
    </section>
  )
}
