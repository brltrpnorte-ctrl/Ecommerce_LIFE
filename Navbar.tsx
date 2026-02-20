import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X, ShoppingBag, Search, User } from "lucide-react";

const categories = [
  { name: "Camisas", href: "/produtos?cat=camisas" },
  { name: "Sneakers", href: "/produtos?cat=sneakers" },
  { name: "Lupas", href: "/produtos?cat=lupas" },
  { name: "Shorts & Bermudas", href: "/produtos?cat=shorts" },
  { name: "Blusas de Frio", href: "/produtos?cat=blusas" },
  { name: "Moletom", href: "/produtos?cat=moletom" },
  { name: "Conjuntos", href: "/produtos?cat=conjuntos" },
  { name: "Meias", href: "/produtos?cat=meias" },
  { name: "Cuecas", href: "/produtos?cat=cuecas" },
];

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 nav-glass">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl md:text-3xl font-display font-bold text-gradient">☘ TREVO</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden lg:flex items-center gap-8">
            <Link to="/" className="text-sm font-medium text-foreground/70 hover:text-primary transition-colors">
              Início
            </Link>
            <div className="group relative">
              <button className="text-sm font-medium text-foreground/70 hover:text-primary transition-colors">
                Categorias
              </button>
              <div className="absolute top-full left-1/2 -translate-x-1/2 pt-4 opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all duration-300">
                <div className="bg-card border border-border rounded-lg p-4 min-w-[200px] glow-border">
                  {categories.map((cat) => (
                    <Link
                      key={cat.name}
                      to={cat.href}
                      className="block px-3 py-2 text-sm text-foreground/70 hover:text-primary hover:bg-muted rounded-md transition-colors"
                    >
                      {cat.name}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
            <Link to="/produtos" className="text-sm font-medium text-foreground/70 hover:text-primary transition-colors">
              Produtos
            </Link>
            <Link to="/historia" className="text-sm font-medium text-foreground/70 hover:text-primary transition-colors">
              Nossa História
            </Link>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button className="p-2 text-foreground/70 hover:text-primary transition-colors">
              <Search className="w-5 h-5" />
            </button>
            <button className="p-2 text-foreground/70 hover:text-primary transition-colors">
              <User className="w-5 h-5" />
            </button>
            <button className="p-2 text-foreground/70 hover:text-primary transition-colors relative">
              <ShoppingBag className="w-5 h-5" />
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-primary text-primary-foreground text-[10px] font-bold rounded-full flex items-center justify-center">
                0
              </span>
            </button>
            <button
              className="lg:hidden p-2 text-foreground/70 hover:text-primary transition-colors"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="lg:hidden bg-card border-t border-border animate-fade-in">
          <div className="container mx-auto px-4 py-6 space-y-3">
            <Link to="/" className="block py-2 text-foreground/80 hover:text-primary transition-colors" onClick={() => setIsOpen(false)}>
              Início
            </Link>
            <div className="border-t border-border pt-3">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Categorias</p>
              {categories.map((cat) => (
                <Link
                  key={cat.name}
                  to={cat.href}
                  className="block py-1.5 pl-2 text-sm text-foreground/70 hover:text-primary transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  {cat.name}
                </Link>
              ))}
            </div>
            <Link to="/produtos" className="block py-2 text-foreground/80 hover:text-primary transition-colors" onClick={() => setIsOpen(false)}>
              Produtos
            </Link>
            <Link to="/historia" className="block py-2 text-foreground/80 hover:text-primary transition-colors" onClick={() => setIsOpen(false)}>
              Nossa História
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
