export const safeArray = (value) => {
  if (Array.isArray(value)) return value
  if (value === null || value === undefined) return []
  if (typeof value === 'object' && value.data) return safeArray(value.data)
  return []
}

export const safeNumber = (value, decimals = 2) => {
  const num = parseFloat(value)
  if (isNaN(num)) return '0.' + '0'.repeat(decimals)
  return num.toFixed(decimals)
}

export const isValidJSON = (data) => {
  if (typeof data === 'string') {
    return !data.trim().startsWith('<')
  }
  return true
}
