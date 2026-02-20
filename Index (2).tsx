import Navbar from "@/components/Navbar";
import HeroCarousel from "@/components/HeroCarousel";
import HologramSection from "@/components/HologramSection";
import CategoriesSection from "@/components/CategoriesSection";
import StoryGallery from "@/components/StoryGallery";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroCarousel />
      <CategoriesSection />
      <HologramSection />
      <StoryGallery />
      <Footer />
    </div>
  );
};

export default Index;
