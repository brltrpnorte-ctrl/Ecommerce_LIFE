import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { HologramShowcase } from '../components/HologramShowcase.jsx'
import { StoryGallery } from '../components/StoryGallery.jsx'
import { ProductCard } from '../components/ProductCard.jsx'
import { api } from '../lib/api.js'
import { heroSlides, storyGallery } from '../data/siteContent.js'

gsap.registerPlugin(ScrollTrigger)

export function HomePage() {
  const [current, setCurrent] = useState(0)
  const [featured, setFeatured] = useState([])

  useEffect(() => {
    const id = window.setInterval(() => {
      setCurrent((value) => (value + 1) % heroSlides.length)
    }, 5200)
    return () => window.clearInterval(id)
  }, [])

  useEffect(() => {
    const context = gsap.context(() => {
      gsap.from('.hero-content > *', {
        y: 25,
        opacity: 0,
        stagger: 0.12,
        duration: 0.8,
      })

      gsap.from('.featured-products .product-card', {
        y: 40,
        opacity: 0,
        duration: 0.8,
        stagger: 0.1,
        scrollTrigger: {
          trigger: '.featured-products',
          start: 'top 75%',
        },
      })
    })

    return () => context.revert()
  }, [featured])

  useEffect(() => {
    api.getProducts({ featured: true, page_size: 6 }).then((response) => setFeatured(response.items)).catch(() => setFeatured([]))
  }, [])

  const activeSlide = heroSlides[current]

  return (
    <div className="page home-page">
      <section className="hero" style={{ backgroundImage: `url(${activeSlide.image})` }}>
        <div className="hero-overlay" />
        <div className="container hero-content">
          <p className="eyebrow">Loja oficial LIFE Style</p>
          <p>{activeSlide.subtitle}</p>
          <div className="hero-actions">
            <Link to="/produtos" className="btn-primary">
              {activeSlide.cta}
            </Link>
            <Link to="/checkout" className="btn-secondary">
              Ir para Checkout
            </Link>
          </div>
          <div className="slide-dots">
            {heroSlides.map((slide, index) => (
              <button
                key={slide.id}
                type="button"
                onClick={() => setCurrent(index)}
                className={index === current ? 'active' : ''}
                aria-label={`Slide ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="presentation container">
        <h2>Uma loja de roupas que comunica historia em cada sessao</h2>
        <p>
          A home foi desenhada como apresentacao de marca, com carrossel, storytelling visual e entrada direta para
          galerias de produto.
        </p>
      </section>

      <div className="container">
        <HologramShowcase />
      </div>

      <div className="container">
        <StoryGallery items={storyGallery} />
      </div>

      <section className="featured-products container">
        <div className="section-head">
          <h2>Destaques para conversao</h2>
          <Link to="/produtos">Ver todos</Link>
        </div>
        <div className="product-grid">
          {featured.map((item) => (
            <ProductCard key={item.id} product={item} />
          ))}
        </div>
      </section>
    </div>
  )
}
