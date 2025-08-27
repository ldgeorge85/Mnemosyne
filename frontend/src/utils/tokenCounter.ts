/**
 * Token counting utility for managing context limits
 * Uses simple approximation: ~4 characters per token for English text
 * This is a rough estimate - actual tokenization varies by model
 */

export interface TokenCountResult {
  tokens: number;
  characters: number;
  withinLimit: boolean;
}

/**
 * Count approximate tokens in text
 * @param text - The text to count tokens for
 * @returns Approximate token count
 */
export function countTokens(text: string): number {
  // Better approximation based on OpenAI's guidance:
  // - ~4 characters per token for English text
  // - But we use 3.5 to be more conservative (avoid underestimating)
  // For exact counts, we'd need tiktoken or similar library
  return Math.ceil(text.length / 3.5);
}

/**
 * Count tokens in a message array
 * @param messages - Array of chat messages
 * @returns Total approximate token count
 */
export function countMessageTokens(messages: Array<{ role: string; content: string }>): number {
  let total = 0;
  
  for (const message of messages) {
    // Add tokens for role (system/user/assistant) + formatting
    total += countTokens(message.role) + 4; // ~4 tokens for message formatting
    total += countTokens(message.content);
  }
  
  return total;
}

/**
 * Truncate messages to fit within token limit
 * @param messages - Array of chat messages
 * @param maxTokens - Maximum allowed tokens
 * @param preserveLatest - Number of latest messages to always preserve
 * @returns Truncated message array
 */
export function truncateMessages(
  messages: Array<{ role: string; content: string }>,
  maxTokens: number,
  preserveLatest: number = 2
): Array<{ role: string; content: string }> {
  if (messages.length <= preserveLatest) {
    return messages;
  }
  
  // Always keep the latest messages
  const latestMessages = messages.slice(-preserveLatest);
  const latestTokens = countMessageTokens(latestMessages);
  
  if (latestTokens >= maxTokens) {
    // Even the latest messages exceed limit, truncate the content
    const lastMessage = latestMessages[latestMessages.length - 1];
    const maxContentTokens = maxTokens - 20; // Reserve tokens for formatting
    const maxChars = maxContentTokens * 4;
    
    if (lastMessage.content.length > maxChars) {
      lastMessage.content = lastMessage.content.slice(0, maxChars) + '... [truncated]';
    }
    
    return latestMessages;
  }
  
  // Add older messages until we hit the limit
  const remainingTokens = maxTokens - latestTokens;
  const olderMessages = messages.slice(0, -preserveLatest);
  const result: Array<{ role: string; content: string }> = [];
  let currentTokens = 0;
  
  // Try to add older messages from most recent to oldest
  for (let i = olderMessages.length - 1; i >= 0; i--) {
    const messageTokens = countTokens(olderMessages[i].content) + countTokens(olderMessages[i].role) + 4;
    
    if (currentTokens + messageTokens <= remainingTokens) {
      result.unshift(olderMessages[i]);
      currentTokens += messageTokens;
    } else {
      break;
    }
  }
  
  // Add system message if truncated
  if (result.length < olderMessages.length && result.length > 0) {
    result.unshift({
      role: 'system',
      content: '[Earlier conversation history truncated due to length]'
    });
  }
  
  return [...result, ...latestMessages];
}

/**
 * Check if messages are within token limit
 * @param messages - Array of chat messages
 * @param maxTokens - Maximum allowed tokens
 * @returns Result with token count and limit status
 */
export function checkTokenLimit(
  messages: Array<{ role: string; content: string }>,
  maxTokens: number
): TokenCountResult {
  const tokens = countMessageTokens(messages);
  const characters = messages.reduce((sum, msg) => sum + msg.content.length + msg.role.length, 0);
  
  return {
    tokens,
    characters,
    withinLimit: tokens <= maxTokens
  };
}