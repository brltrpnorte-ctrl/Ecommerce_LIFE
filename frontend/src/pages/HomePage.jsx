import { Fragment, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { HologramShowcase } from '../components/HologramShowcase.jsx'
import { StoryGallery } from '../components/StoryGallery.jsx'
import { ProductCard } from '../components/ProductCard.jsx'
import { api } from '../lib/api.js'
import { defaultSiteContent } from '../data/siteContent.js'

gsap.registerPlugin(ScrollTrigger)

function buildMediaIndex(siteContent) {
  const library = siteContent?.media_library || []
  const index = new Map()
  library.forEach((item) => index.set(item.id, item))
  return index
}

function resolveBanners(siteContent, fallback) {
  const banners = siteContent?.banners || []
  if (!banners.length) return fallback

  const mediaIndex = buildMediaIndex(siteContent)
  const now = new Date()

  const filtered = banners
    .filter((b) => (b.status || 'published') === 'published')
    .filter((b) => {
      const start = b.start_at ? new Date(b.start_at) : null
      const end = b.end_at ? new Date(b.end_at) : null
      if (start && now < start) return false
      if (end && now > end) return false
      return true
    })
    .sort((a, b) => Number(a.order || 0) - Number(b.order || 0))

  if (!filtered.length) return fallback

  const mapped = filtered
    .map((b) => {
      const media = mediaIndex.get(b.media_id)
      if (!media) return null
      return {
        id: b.id,
        title: b.title,
        subtitle: b.subtitle,
        cta: b.cta_text || 'Ver mais',
        media_type: b.type,
        media_url: media.url,
      }
    })
    .filter(Boolean)

  return mapped.length ? mapped : fallback
}

function resolveStoryItems(siteContent, fallback) {
  const polaroids = siteContent?.polaroids || []
  if (!polaroids.length) return fallback

  const mediaIndex = buildMediaIndex(siteContent)
  const sorted = [...polaroids].sort((a, b) => Number(a.order || 0) - Number(b.order || 0))

  const mapped = sorted
    .map((p) => {
      const media = mediaIndex.get(p.media_id)
      if (!media) return null
      return {
        id: p.id,
        title: p.caption,
        type: media.type,
        src: media.url,
        text: p.story,
      }
    })
    .filter(Boolean)

  return mapped.length ? mapped : fallback
}

export function HomePage() {
  const [current, setCurrent] = useState(0)
  const [featured, setFeatured] = useState([])
  const [siteContent, setSiteContent] = useState(defaultSiteContent)

  const slides = useMemo(() => {
    // prefer v2 banners; fallback v1 hero_slides
    if (siteContent?.banners?.length) {
      return resolveBanners(siteContent, defaultSiteContent.hero_slides)
    }
    return siteContent.hero_slides?.length ? siteContent.hero_slides : defaultSiteContent.hero_slides
  }, [siteContent])

  const storyItems = useMemo(() => {
    // prefer v2 polaroids; fallback v1 story_gallery
    if (siteContent?.polaroids?.length) {
      return resolveStoryItems(siteContent, defaultSiteContent.story_gallery)
    }
    return siteContent.story_gallery?.length ? siteContent.story_gallery : defaultSiteContent.story_gallery
  }, [siteContent])

  const texts = siteContent.texts || defaultSiteContent.texts
  const orderedSections = useMemo(() => {
    const defaults = ['presentation', 'hologram', 'story', 'featured']
    const raw = siteContent?.home_sections || []
    if (!raw.length) {
      return defaults
    }

    const validTypes = new Set(defaults)
    const seen = new Set()
    const fromCms = raw
      .filter((item) => item && validTypes.has(item.type) && item.enabled !== false)
      .sort((a, b) => Number(a.order || 0) - Number(b.order || 0))
      .map((item) => item.type)
      .filter((type) => {
        if (seen.has(type)) return false
        seen.add(type)
        return true
      })

    const missing = defaults.filter((type) => !seen.has(type))
    return [...fromCms, ...missing]
  }, [siteContent])

  useEffect(() => {
    if (slides.length <= 1) {
      return () => {}
    }
    const id = window.setInterval(() => {
      setCurrent((value) => (value + 1) % slides.length)
    }, 5200)
    return () => window.clearInterval(id)
  }, [slides.length])

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
    let isMounted = true
    api
      .getSiteContent()
      .then((response) => {
        if (isMounted) {
          setSiteContent(response)
        }
      })
      .catch(() => {
        if (isMounted) {
          setSiteContent(defaultSiteContent)
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    api
      .getProducts({ featured: true, page_size: 6 })
      .then((response) => setFeatured(response.items))
      .catch(() => setFeatured([]))
  }, [])

  const safeCurrent = slides.length > 0 ? current % slides.length : 0
  const activeSlide = slides[safeCurrent] || slides[0]
  const heroMediaType = activeSlide?.media_type || 'image'
  const heroMediaUrl = activeSlide?.media_url || ''
  const heroSubtitle = activeSlide?.subtitle || defaultSiteContent.hero_slides[0].subtitle
  const heroCta = activeSlide?.cta || defaultSiteContent.hero_slides[0].cta

  return (
    <div className="page home-page">
      <section className="hero">
        {heroMediaType === 'video' ? (
          <video
            key={heroMediaUrl}
            className="hero-media"
            src={heroMediaUrl}
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
          />
        ) : (
          <div className="hero-media hero-media-image" style={{ backgroundImage: `url(${heroMediaUrl})` }} />
        )}
        <div className="hero-overlay" />
        <div className="container hero-content">
          <p className="eyebrow">{texts.hero_eyebrow || defaultSiteContent.texts.hero_eyebrow}</p>
          <p>{heroSubtitle}</p>
          <div className="hero-actions">
            <Link to="/produtos" className="btn-primary">
              {heroCta}
            </Link>
          </div>
          <div className="slide-dots">
            {slides.map((slide, index) => (
              <button
                key={slide.id}
                type="button"
                onClick={() => setCurrent(index)}
                className={index === safeCurrent ? 'active' : ''}
                aria-label={`Slide ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </section>

      {orderedSections.map((sectionType) => {
        if (sectionType === 'presentation') {
          return (
            <section key={sectionType} className="presentation container">
              <h2>{texts.presentation_title || defaultSiteContent.texts.presentation_title}</h2>
              <p>{texts.presentation_body || defaultSiteContent.texts.presentation_body}</p>
            </section>
          )
        }

        if (sectionType === 'hologram') {
          return (
            <div key={sectionType} className="container">
              <HologramShowcase
                copy={{
                  eyebrow: texts.hologram_eyebrow,
                  title: texts.hologram_title,
                  body: texts.hologram_body,
                }}
              />
            </div>
          )
        }

        if (sectionType === 'story') {
          return (
            <div key={sectionType} className="container">
              <StoryGallery
                items={storyItems}
                copy={{
                  eyebrow: texts.story_eyebrow,
                  title: texts.story_title,
                }}
              />
            </div>
          )
        }

        if (sectionType === 'featured') {
          return (
            <section key={sectionType} className="featured-products container">
              <div className="section-head">
                <h2>{texts.featured_title || defaultSiteContent.texts.featured_title}</h2>
                <Link to="/produtos">{texts.featured_link_label || defaultSiteContent.texts.featured_link_label}</Link>
              </div>
              <div className="product-grid">
                {featured.map((item) => (
                  <ProductCard key={item.id} product={item} />
                ))}
              </div>
            </section>
          )
        }

        return <Fragment key={`${sectionType}-noop`} />
      })}
    </div>
  )
}
