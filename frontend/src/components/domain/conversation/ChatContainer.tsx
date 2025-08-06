/**
 * Chat Container Component
 * 
 * A comprehensive chat interface container that combines message list,
 * typing indicators, and input area into a complete chat experience.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Flex,
  VStack,
  Heading,
  Text,
  Divider,
  useColorModeValue,
  useDisclosure,
  Collapse,
  Icon,
  Badge,
} from '@chakra-ui/react';
import { FiInfo, FiAlertCircle } from 'react-icons/fi';
import { Message } from '../../../types';
import MessageList from './MessageList';
import MessageSkeleton from './MessageSkeleton';
import ChatInput from './ChatInput';

interface ChatContainerProps {
  /**
   * Title of the chat conversation
   */
  title?: string;
  
  /**
   * Optional description or context for the conversation
   */
  description?: string;
  
  /**
   * List of messages in the conversation
   */
  messages: Message[];
  
  /**
   * Whether messages are currently being fetched
   */
  isLoadingMessages?: boolean;
  
  /**
   * Whether a message is currently being sent
   */
  isSendingMessage?: boolean;
  
  /**
   * Error message if loading failed
   */
  error?: string | null;
  
  /**
   * Whether the agent is currently typing
   */
  isAgentTyping?: boolean;
  
  /**
   * Called when a new message is sent
   */
  onSendMessage: (content: string) => void;
  
  /**
   * Called when a message is deleted
   */
  onDeleteMessage?: (messageId: string) => void;
  
  /**
   * Called when a message is copied to clipboard
   */
  onCopyMessage?: (message: Message) => void;
  
  /**
   * Whether to allow file attachments
   */
  allowAttachments?: boolean;
  
  /**
   * Called when a file attachment is added
   */
  onAddAttachment?: (file: File) => void;
}

/**
 * Complete chat interface combining messages and input
 */
const ChatContainer: React.FC<ChatContainerProps> = ({
  title = 'Conversation',
  description,
  messages = [],
  isLoadingMessages = false,
  isSendingMessage = false,
  error = null,
  isAgentTyping = false,
  onSendMessage,
  onDeleteMessage,
  onCopyMessage,
  allowAttachments = false,
  onAddAttachment,
}) => {
  // State for info panel disclosure
  const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: !!description });
  
  // Background and border colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const headerBgColor = useColorModeValue('gray.50', 'gray.700');
  
  // Handle message submission
  const handleSendMessage = useCallback((content: string) => {
    onSendMessage(content);
  }, [onSendMessage]);
  
  // Render typing indicator
  const renderTypingIndicator = () => {
    if (isAgentTyping) {
      return <MessageSkeleton />;
    }
    return null;
  };
  
  return (
    <Box
      width="100%"
      height="100%"
      borderRadius="md"
      border="1px solid"
      borderColor={borderColor}
      bg={bgColor}
      overflow="hidden"
      display="flex"
      flexDirection="column"
    >
      {/* Header with title */}
      <Box
        p={4}
        bg={headerBgColor}
        borderBottom="1px solid"
        borderColor={borderColor}
      >
        <Flex justify="space-between" align="center">
          <Heading size="md">{title}</Heading>
          <Badge colorScheme="blue">{messages.length} messages</Badge>
        </Flex>
        
        {/* Collapsible description */}
        {description && (
          <>
            <Divider my={2} />
            <Box onClick={onToggle} cursor="pointer" _hover={{ opacity: 0.8 }}>
              <Flex align="center">
                <Icon as={FiInfo} mr={2} color="blue.500" />
                <Text fontSize="sm" fontWeight="medium">
                  Context & Information
                </Text>
              </Flex>
            </Box>
            <Collapse in={isOpen} animateOpacity>
              <Box mt={2} p={3} borderRadius="md" bg={useColorModeValue('blue.50', 'blue.900')}>
                <Text fontSize="sm">{description}</Text>
              </Box>
            </Collapse>
          </>
        )}
      </Box>
      
      {/* Error banner */}
      {error && (
        <Box bg="red.100" color="red.800" p={3} borderBottomWidth="1px">
          <Flex align="center">
            <Icon as={FiAlertCircle} mr={2} />
            <Text fontWeight="medium">{error}</Text>
          </Flex>
        </Box>
      )}
      
      {/* Main chat area with message list */}
      <VStack
        flex="1"
        width="100%"
        spacing={0}
        overflowY="auto"
        p={0}
        position="relative"
      >
        <Box width="100%" height="100%" overflowY="auto" p={2}>
          <MessageList
            messages={messages}
            isLoading={isLoadingMessages}
            error={error}
            onDeleteMessage={onDeleteMessage}
            onCopyMessage={onCopyMessage}
            autoScroll={true}
          />
          {renderTypingIndicator()}
        </Box>
      </VStack>
      
      {/* Chat input area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isSendingMessage}
        placeholder="Type your message..."
        maxHeight={150}
        allowAttachments={allowAttachments}
        onAddAttachment={onAddAttachment}
      />
    </Box>
  );
};

export default ChatContainer;
