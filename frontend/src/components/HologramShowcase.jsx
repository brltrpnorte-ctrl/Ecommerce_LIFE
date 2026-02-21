import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const defaultCopy = {
  eyebrow: 'Holograma Lifestyle Store',
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

      gsap.to('.projection-card', {
        y: (index) => -10 - index * 12,
        rotationY: (index) => index * 6 - 8,
        repeat: -1,
        yoyo: true,
        duration: 2.8,
        ease: 'sine.inOut',
        stagger: 0.16,
      })

      gsap.to('.hologram-core', {
        boxShadow: '0 0 80px rgba(108,255,160,0.55)',
        duration: 1.8,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
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

      <div className="hologram-stage" aria-label="Projecao holografica do emblema">
        <div className="hologram-floor" />
        <div className="hologram-core" />
        <div className="projection-card p1">Colecao Aurora</div>
        <div className="projection-card p2">Drop Sneaker Neon</div>
        <div className="projection-card p3">Lupa Signature</div>
      </div>
    </section>
  )
}
