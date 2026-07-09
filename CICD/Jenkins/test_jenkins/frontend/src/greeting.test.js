import { describe, expect, it } from 'vitest'
import { greet } from './greeting'

describe('greet', () => {
  it('greets by name', () => {
    expect(greet('Jenkins')).toBe('Hello, Jenkins!')
  })

  it('trims whitespace', () => {
    expect(greet('  Jenkins  ')).toBe('Hello, Jenkins!')
  })

  it('falls back to world when name is missing', () => {
    expect(greet()).toBe('Hello, world!')
    expect(greet('   ')).toBe('Hello, world!')
  })
})
