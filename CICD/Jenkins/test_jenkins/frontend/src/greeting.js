export function greet(name) {
  const trimmed = name?.trim()
  if (!trimmed) {
    return 'Hello, world!'
  }
  return `Hello, ${trimmed}!`
}
