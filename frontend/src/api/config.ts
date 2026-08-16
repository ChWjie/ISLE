const configuredBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim()

/** API root. An empty value uses same-origin requests. */
export const API_BASE_URL = configuredBaseUrl.replace(/\/+$/, '')

export const apiUrl = (path: string): string => {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    return `${API_BASE_URL}${normalizedPath}`
}
