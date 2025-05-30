/**
 * Date and time utility functions for the application
 */

/**
 * Formats a timestamp in a human-readable format
 * Shows time for today, date for earlier timestamps
 * 
 * @param timestamp ISO string or Date object to format
 * @returns Formatted timestamp string
 */
export function formatTimestamp(timestamp: string | Date): string {
  if (!timestamp) return '';
  
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  
  // For messages from today, show only the time (e.g., "2:45 PM")
  if (isToday) {
    return date.toLocaleTimeString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  }
  
  // For messages from the past 7 days, show the day of week and time
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  if (date > weekAgo) {
    return date.toLocaleDateString(undefined, {
      weekday: 'short',
    }) + ' ' + date.toLocaleTimeString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  }
  
  // For older messages, show the full date (e.g., "May 12, 2025")
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Returns a relative time string (e.g., "2 minutes ago")
 * 
 * @param timestamp ISO string or Date object to format
 * @returns Relative time string
 */
export function getRelativeTime(timestamp: string | Date): string {
  if (!timestamp) return '';
  
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  
  if (diffSec < 60) {
    return 'just now';
  } else if (diffMin < 60) {
    return `${diffMin} ${diffMin === 1 ? 'minute' : 'minutes'} ago`;
  } else if (diffHour < 24) {
    return `${diffHour} ${diffHour === 1 ? 'hour' : 'hours'} ago`;
  } else if (diffDay < 30) {
    return `${diffDay} ${diffDay === 1 ? 'day' : 'days'} ago`;
  } else {
    // For older timestamps, return the formatted date
    return formatTimestamp(date);
  }
}
