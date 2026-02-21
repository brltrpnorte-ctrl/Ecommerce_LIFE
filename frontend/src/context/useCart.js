import { useContext } from 'react'
import { CartContext } from './cartContext.js'

export function useCart() {
  const context = useContext(CartContext)
  if (!context) {
    throw new Error('useCart precisa ser usado dentro de CartProvider')
  }
  return context
}
