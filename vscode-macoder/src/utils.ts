/**
 * Debounce a function
 * 
 * @param func The function to debounce
 * @param wait The wait time in milliseconds
 * @returns The debounced function
 */
export function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout | null = null;
    
    return function(this: any, ...args: Parameters<T>): void {
        const later = () => {
            timeout = null;
            func.apply(this, args);
        };
        
        if (timeout !== null) {
            clearTimeout(timeout);
        }
        
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle a function
 * 
 * @param func The function to throttle
 * @param limit The limit in milliseconds
 * @returns The throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
): (...args: Parameters<T>) => void {
    let inThrottle = false;
    let lastFunc: NodeJS.Timeout;
    let lastRan: number;
    
    return function(this: any, ...args: Parameters<T>): void {
        if (!inThrottle) {
            func.apply(this, args);
            lastRan = Date.now();
            inThrottle = true;
            
            setTimeout(() => {
                inThrottle = false;
            }, limit);
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(() => {
                if (Date.now() - lastRan >= limit) {
                    func.apply(this, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
}

/**
 * Format a date as a string
 * 
 * @param date The date to format
 * @returns The formatted date
 */
export function formatDate(date: Date): string {
    return date.toLocaleString();
}

/**
 * Format a size in bytes to a human-readable string
 * 
 * @param bytes The size in bytes
 * @returns The formatted size
 */
export function formatSize(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    
    return `${size.toFixed(2)} ${units[unitIndex]}`;
}

/**
 * Truncate a string to a maximum length
 * 
 * @param str The string to truncate
 * @param maxLength The maximum length
 * @returns The truncated string
 */
export function truncate(str: string, maxLength: number): string {
    if (str.length <= maxLength) {
        return str;
    }
    
    return str.substring(0, maxLength) + '...';
}

/**
 * Escape HTML special characters
 * 
 * @param html The HTML string to escape
 * @returns The escaped HTML
 */
export function escapeHtml(html: string): string {
    return html
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Generate a random ID
 * 
 * @param length The length of the ID
 * @returns The random ID
 */
export function generateId(length: number = 8): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    return result;
}
