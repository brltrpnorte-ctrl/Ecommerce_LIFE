import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import story1 from "@/assets/story-1.jpg";
import story2 from "@/assets/story-2.jpg";
import story3 from "@/assets/story-3.jpg";

gsap.registerPlugin(ScrollTrigger);

const stories = [
  {
    image: story1,
    caption: "Estilo de rua",
    description: "Onde a autenticidade encontra a moda",
    rotation: -3,
  },
  {
    image: story2,
    caption: "Sneaker culture",
    description: "Cada passo conta uma história",
    rotation: 2,
  },
  {
    image: story3,
    caption: "Lupas premium",
    description: "Visão de quem sabe o que quer",
    rotation: -1.5,
  },
];

const StoryGallery = () => {
  const sectionRef = useRef<HTMLElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      if (cardsRef.current) {
        gsap.fromTo(
          cardsRef.current.children,
          { opacity: 0, y: 80, rotation: 10 },
          {
            opacity: 1,
            y: 0,
            rotation: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "power3.out",
            scrollTrigger: {
              trigger: sectionRef.current,
              start: "top 60%",
              toggleActions: "play none none reverse",
            },
          }
        );
      }
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className="py-24 md:py-32 relative overflow-hidden">
      {/* Subtle bg gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card/30 to-background" />

      <div className="relative container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16 space-y-4">
          <span className="inline-block px-4 py-1.5 text-xs font-medium tracking-widest uppercase text-primary border border-primary/30 rounded-full">
            Nossa Essência
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-display font-black">
            Cada peça, uma <span className="text-gradient">história</span>
          </h2>
          <p className="text-muted-foreground max-w-lg mx-auto">
            Não vendemos roupas. Vendemos sentimentos, memórias e atitude.
            Conheça as histórias por trás de cada coleção.
          </p>
        </div>

        {/* Polaroid Gallery */}
        <div
          ref={cardsRef}
          className="flex flex-wrap justify-center gap-8 md:gap-12"
        >
          {stories.map((story, i) => (
            <div
              key={i}
              className="polaroid-card group cursor-pointer hover:scale-105 transition-transform duration-500"
              style={{ "--rotation": `${story.rotation}deg` } as React.CSSProperties}
            >
              <div className="w-56 h-72 md:w-64 md:h-80 overflow-hidden rounded-sm">
                <img
                  src={story.image}
                  alt={story.caption}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
              </div>
              <div className="absolute bottom-2 left-2 right-2 text-center">
                <p className="font-display font-bold text-background text-sm">
                  {story.caption}
                </p>
                <p className="text-[10px] text-background/60">
                  {story.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center mt-16">
          <button className="px-8 py-3.5 rounded-full font-display font-semibold border border-primary/40 text-primary hover:bg-primary hover:text-primary-foreground transition-all duration-300 glow-border">
            Ver Todas as Histórias
          </button>
        </div>
      </div>
    </section>
  );
};

export default StoryGallery;
