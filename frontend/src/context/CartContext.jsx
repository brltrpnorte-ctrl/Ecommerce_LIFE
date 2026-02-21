import { useEffect, useMemo, useState } from 'react'
import { CartContext } from './cartContext.js'

const STORAGE_KEY = 'ecommerce_life_cart'
const readInitialItems = () => {
  if (typeof window === 'undefined') {
    return []
  }

  const saved = localStorage.getItem(STORAGE_KEY)
  if (!saved) {
    return []
  }

  try {
    return JSON.parse(saved)
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return []
  }
}

export function CartProvider({ children }) {
  const [items, setItems] = useState(readInitialItems)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }, [items])

  const addItem = (product, selectedSize = null, selectedColor = null, quantity = 1) => {
    setItems((current) => {
      const existingIndex = current.findIndex(
        (item) =>
          item.id === product.id && item.selectedSize === selectedSize && item.selectedColor === selectedColor,
      )

      if (existingIndex >= 0) {
        const clone = [...current]
        clone[existingIndex].quantity += quantity
        return clone
      }

      return [
        ...current,
        {
          id: product.id,
          slug: product.slug,
          name: product.name,
          price: product.price,
          media: product.media,
          selectedSize,
          selectedColor,
          quantity,
        },
      ]
    })
  }

  const removeItem = (index) => {
    setItems((current) => current.filter((_, itemIndex) => itemIndex !== index))
  }

  const updateQuantity = (index, quantity) => {
    if (quantity <= 0) {
      removeItem(index)
      return
    }

    setItems((current) => {
      const clone = [...current]
      clone[index].quantity = quantity
      return clone
    })
  }

  const clearCart = () => setItems([])

  const totalItems = useMemo(() => items.reduce((sum, item) => sum + item.quantity, 0), [items])
  const subtotal = useMemo(() => items.reduce((sum, item) => sum + item.price * item.quantity, 0), [items])

  const value = {
    items,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    totalItems,
    subtotal,
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}
