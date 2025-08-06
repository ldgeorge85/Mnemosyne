/**
 * Message List Component
 * 
 * This component displays a list of messages in a conversation,
 * with proper formatting and loading states.
 */
import React, { useEffect, useRef } from 'react';
import {
  VStack,
  Spinner,
  Text,
  Box,
  useColorModeValue,
  Flex,
} from '@chakra-ui/react';
import { Message } from '../../../types';
import MessageItem from './MessageItem';

interface MessageListProps {
  /**
   * List of messages to display
   */
  messages: Message[];
  
  /**
   * Whether messages are currently loading
   */
  isLoading: boolean;
  
  /**
   * Error message if loading failed
   */
  error?: string | null;
  
  /**
   * Called when a message is deleted
   */
  onDeleteMessage?: (messageId: string) => void;
  
  /**
   * Called when a message is copied
   */
  onCopyMessage?: (message: Message) => void;
  
  /**
   * Whether to auto-scroll to the bottom when new messages arrive
   */
  autoScroll?: boolean;
}

/**
 * Displays a list of messages with loading states and error handling
 */
const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  error,
  onDeleteMessage,
  onCopyMessage,
  autoScroll = true,
}) => {
  // Reference to the end of the message list for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Background colors
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const errorBgColor = useColorModeValue('red.50', 'red.900');
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (autoScroll && messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);
  
  // If there are no messages, show a message
  if (messages.length === 0 && !isLoading) {
    return (
      <Box
        p={6}
        borderRadius="md"
        bg={bgColor}
        textAlign="center"
        width="100%"
      >
        <Text color="gray.500">No messages yet. Start a conversation!</Text>
      </Box>
    );
  }
  
  // If there's an error, show it
  if (error) {
    return (
      <Box
        p={6}
        borderRadius="md"
        bg={errorBgColor}
        textAlign="center"
        width="100%"
      >
        <Text color="red.500">Error: {error}</Text>
      </Box>
    );
  }
  
  return (
    <VStack
      spacing={4}
      align="stretch"
      width="100%"
      minHeight="400px"
      maxHeight="calc(100vh - 300px)"
      overflowY="auto"
      p={4}
      bg={bgColor}
      borderRadius="md"
    >
      {/* Messages */}
      {Array.isArray(messages) && messages.map((message) => (
        <MessageItem
          key={message.id}
          message={message}
          onDelete={onDeleteMessage ? () => onDeleteMessage(message.id) : undefined}
          onCopy={onCopyMessage ? () => onCopyMessage(message) : undefined}
        />
      ))}
      
      {/* Loading spinner */}
      {isLoading && (
        <Flex justify="center" p={4}>
          <Spinner size="md" color="blue.500" />
        </Flex>
      )}
      
      {/* Reference for auto-scrolling */}
      <div ref={messagesEndRef} />
    </VStack>
  );
};

export default MessageList;
