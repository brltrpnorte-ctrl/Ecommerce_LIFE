import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import cloverImg from "@/assets/clover-hologram.png";
import hero1 from "@/assets/hero-1.jpg";
import hero2 from "@/assets/hero-2.jpg";

gsap.registerPlugin(ScrollTrigger);

const hologramImages = [hero1, hero2];

const HologramSection = () => {
  const sectionRef = useRef<HTMLElement>(null);
  const cloverRef = useRef<HTMLDivElement>(null);
  const hologramRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Clover entrance
      gsap.fromTo(
        cloverRef.current,
        { scale: 0.6, opacity: 0, rotateY: -30 },
        {
          scale: 1,
          opacity: 1,
          rotateY: 0,
          duration: 1.5,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 70%",
            end: "top 20%",
            scrub: 1,
          },
        }
      );

      // Hologram projection entrance
      gsap.fromTo(
        hologramRef.current,
        { y: 60, opacity: 0, scale: 0.8 },
        {
          y: -30,
          opacity: 1,
          scale: 1,
          duration: 1.5,
          ease: "power2.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 50%",
            end: "top 10%",
            scrub: 1,
          },
        }
      );

      // Title
      gsap.fromTo(
        titleRef.current,
        { opacity: 0, x: -50 },
        {
          opacity: 1,
          x: 0,
          duration: 1,
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 60%",
            toggleActions: "play none none reverse",
          },
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden py-20"
      style={{ background: "radial-gradient(ellipse at center, hsl(142 72% 10% / 0.15), hsl(0 0% 3%))" }}
    >
      {/* Ambient particles */}
      <div className="absolute inset-0 overflow-hidden">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 rounded-full bg-primary/30 animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              animationDuration: `${3 + Math.random() * 4}s`,
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Text */}
          <div className="space-y-6">
            <h2
              ref={titleRef}
              className="text-4xl md:text-5xl lg:text-6xl font-display font-black leading-tight"
            >
              Onde a <span className="text-gradient">sorte</span> encontra<br />
              o <span className="text-gradient">estilo</span>
            </h2>
            <p className="text-lg text-muted-foreground max-w-md">
              Cada peça é selecionada para trazer não só estilo, mas também a energia positiva
              do nosso trevo de 4 folhas. Vista sorte.
            </p>
            <button className="gradient-primary px-8 py-3.5 rounded-full font-display font-semibold text-primary-foreground hover:scale-105 transition-transform duration-300 glow-box">
              Conhecer Produtos
            </button>
          </div>

          {/* Hologram Scene */}
          <div className="relative flex flex-col items-center perspective-1000">
            {/* Hologram projection */}
            <div
              ref={hologramRef}
              className="relative z-10 w-64 h-80 md:w-80 md:h-96 preserve-3d animate-hologram-flicker"
            >
              {/* Scan line effect */}
              <div className="absolute inset-0 overflow-hidden rounded-lg pointer-events-none z-20">
                <div className="w-full h-8 bg-gradient-to-b from-primary/10 via-primary/5 to-transparent animate-scan-line" />
              </div>

              {/* Hologram image */}
              <div className="relative w-full h-full rounded-lg overflow-hidden border border-primary/20"
                style={{
                  boxShadow: "0 0 40px hsl(142 72% 45% / 0.3), 0 0 80px hsl(142 72% 45% / 0.15), inset 0 0 30px hsl(142 72% 45% / 0.1)",
                }}
              >
                <img
                  src={hologramImages[0]}
                  alt="Hologram projection"
                  className="w-full h-full object-cover"
                  style={{
                    mixBlendMode: "screen",
                    filter: "brightness(1.2) contrast(1.1) saturate(0.8)",
                  }}
                />
                {/* Hologram overlay tint */}
                <div className="absolute inset-0 bg-primary/10 mix-blend-overlay" />
                {/* Scanline texture */}
                <div
                  className="absolute inset-0 pointer-events-none opacity-20"
                  style={{
                    backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, hsl(142 72% 45% / 0.05) 2px, hsl(142 72% 45% / 0.05) 4px)",
                  }}
                />
              </div>
            </div>

            {/* Clover "carpet" / base */}
            <div
              ref={cloverRef}
              className="relative -mt-16 z-0"
            >
              <img
                src={cloverImg}
                alt="Trevo de 4 folhas"
                className="w-48 h-48 md:w-64 md:h-64 object-contain hologram-glow animate-glow-pulse"
              />
              {/* Reflection/glow pool */}
              <div
                className="absolute inset-x-0 bottom-0 h-1/2 rounded-full blur-3xl opacity-40"
                style={{ background: "radial-gradient(ellipse, hsl(142 72% 45% / 0.4), transparent)" }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HologramSection;
