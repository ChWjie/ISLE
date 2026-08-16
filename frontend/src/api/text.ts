const suspiciousPattern = /[ÃÂÆÇÐÑØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]/i

export const repairMojibake = (value: string): string => {
    if (!value || !suspiciousPattern.test(value)) return value

    try {
        const bytes = Uint8Array.from([...value].map(char => char.charCodeAt(0) & 0xff))
        const decoded = new TextDecoder('utf-8', { fatal: false }).decode(bytes)
        return decoded.includes('�') ? value : decoded
    } catch {
        return value
    }
}

export const repairMojibakeDeep = <T>(input: T): T => {
    if (typeof input === 'string') {
        return repairMojibake(input) as T
    }

    if (Array.isArray(input)) {
        return input.map(item => repairMojibakeDeep(item)) as T
    }

    if (input && typeof input === 'object') {
        const repaired = Object.entries(input as Record<string, unknown>).reduce<Record<string, unknown>>((acc, [key, value]) => {
            acc[key] = repairMojibakeDeep(value)
            return acc
        }, {})
        return repaired as T
    }

    return input
}
