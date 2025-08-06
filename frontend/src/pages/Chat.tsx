/**
 * Chat Page
 * 
 * This page provides a complete chat interface connected to the backend API,
 * including conversation management, message handling, and real-time responses.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  useToast,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  Button,
  IconButton,
  Tooltip,
} from '@chakra-ui/react';
import { AddIcon, RepeatIcon } from '@chakra-ui/icons';
import { ChatContainer } from '../components/domain/conversation';
import { Message, Conversation } from '../types';
import { 
  getConversations, 
  getConversation, 
  createConversation, 
  sendMessage,
  sendMessageStream
} from '../api/conversations';

/**
 * Chat page component with real API integration
 */
const ChatPage: React.FC = () => {
  // State for current conversation
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  // State for messages
  const [messages, setMessages] = useState<Message[]>([]);
  // State for loading messages
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  // State for sending a message
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  // State for creating conversation
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);
  // State for typing indicator
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  // Error state
  const [error, setError] = useState<string | null>(null);
  
  // Toast for notifications
  const toast = useToast();
  
  // Load conversations on mount
  useEffect(() => {
    loadInitialConversation();
  }, []);
  
  /**
   * Load the most recent conversation or create a new one
   */
  const loadInitialConversation = async () => {
    setIsLoadingMessages(true);
    setError(null);
    
    try {
      // Try to get existing conversations
      const conversationsResponse = await getConversations(1, 0);
      
      if (conversationsResponse.success && conversationsResponse.data.items.length > 0) {
        // Load the most recent conversation
        const conversation = conversationsResponse.data.items[0];
        await loadConversation(conversation.id);
      } else {
        // No conversations exist, create a new one
        await createNewConversation();
      }
    } catch (err) {
      setError('Failed to load conversation. Please try again.');
    } finally {
      setIsLoadingMessages(false);
    }
  };
  
  /**
   * Load a specific conversation and its messages
   */
  const loadConversation = async (conversationId: string) => {
    setIsLoadingMessages(true);
    setError(null);
    
    try {
      const response = await getConversation(conversationId);
      
      if (response.success && response.data) {
        setCurrentConversation(response.data);
        // Handle messages as paginated response
        const messages = response.data.messages?.items || response.data.messages || [];
        setMessages(Array.isArray(messages) ? messages : []);
      } else {
        throw new Error(response.message || 'Failed to load conversation');
      }
    } catch (err) {
      setError('Failed to load conversation. Please try again.');
      toast({
        title: 'Error',
        description: 'Failed to load conversation',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoadingMessages(false);
    }
  };
  
  /**
   * Create a new conversation
   */
  const createNewConversation = async () => {
    setIsCreatingConversation(true);
    setError(null);
    
    try {
      const response = await createConversation('New Chat');
      
      if (response.success && response.data) {
        setCurrentConversation(response.data);
        setMessages([]);
        
        toast({
          title: 'Success',
          description: 'New conversation created',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        throw new Error(response.message || 'Failed to create conversation');
      }
    } catch (err) {
      setError('Failed to create new conversation. Please try again.');
      toast({
        title: 'Error',
        description: 'Failed to create new conversation',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsCreatingConversation(false);
    }
  };
  
  /**
   * Send a message to the current conversation with streaming response
   */
  const handleSendMessage = async (content: string) => {
    if (!currentConversation) {
      toast({
        title: 'Error',
        description: 'No active conversation',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    // Create a temporary user message for immediate UI feedback
    const tempUserMessage: Message = {
      id: `temp-user-${Date.now()}`,
      conversation_id: currentConversation.id,
      content,
      role: 'user',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    // Add user message immediately
    setMessages(prev => [...prev, tempUserMessage]);
    setIsSendingMessage(true);
    setIsAgentTyping(true);
    
    try {
      // TEMPORARY: Use non-streaming API to debug
      const response = await sendMessage(currentConversation.id, content);
      
      if (response.success && response.data) {
        // Update the user message with the real ID
        setMessages(prev => 
          prev.map(msg => 
            msg.id === tempUserMessage.id 
              ? { ...msg, id: response.data.id }
              : msg
          )
        );
        
        // Add the assistant response if available
        if (response.data.assistant_response) {
          setMessages(prev => [...prev, response.data.assistant_response]);
        }
      } else {
        throw new Error(response.message || 'Failed to send message');
      }
      
      setIsAgentTyping(false);
      setIsSendingMessage(false);
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Remove temporary message on error
      setMessages(prev => prev.filter(msg => msg.id !== tempUserMessage.id));
      
      setError('Failed to send message. Please try again.');
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to send message',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsSendingMessage(false);
      setIsAgentTyping(false);
    }
  };
  
  /**
   * Refresh the current conversation
   */
  const handleRefresh = () => {
    if (currentConversation) {
      loadConversation(currentConversation.id);
    } else {
      loadInitialConversation();
    }
  };
  
  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Chat</Heading>
            <Text color="gray.600">
              {currentConversation 
                ? `Conversation: ${currentConversation.title}`
                : 'AI-powered conversations'
              }
            </Text>
          </VStack>
          
          <HStack spacing={2}>
            <Tooltip label="Refresh conversation">
              <IconButton
                aria-label="Refresh conversation"
                icon={<RepeatIcon />}
                onClick={handleRefresh}
                isLoading={isLoadingMessages}
                variant="outline"
              />
            </Tooltip>
            
            <Tooltip label="New conversation">
              <IconButton
                aria-label="New conversation"
                icon={<AddIcon />}
                onClick={createNewConversation}
                isLoading={isCreatingConversation}
                colorScheme="blue"
              />
            </Tooltip>
          </HStack>
        </Flex>
        
        {/* Error Alert */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {/* Loading State */}
        {isLoadingMessages && !currentConversation && (
          <Flex justify="center" py={8}>
            <VStack spacing={4}>
              <Spinner size="lg" />
              <Text>Loading conversation...</Text>
            </VStack>
          </Flex>
        )}
        
        {/* Chat Interface */}
        {currentConversation && (
          <Box flex={1}>
            <ChatContainer
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoadingMessages={isLoadingMessages}
              isSendingMessage={isSendingMessage}
              isAgentTyping={isAgentTyping}
            />
          </Box>
        )}
        
        {/* Empty State */}
        {!currentConversation && !isLoadingMessages && (
          <Flex justify="center" py={12}>
            <VStack spacing={4} textAlign="center">
              <Text fontSize="lg" color="gray.600">
                No conversation loaded
              </Text>
              <Button
                leftIcon={<AddIcon />}
                colorScheme="blue"
                onClick={createNewConversation}
                isLoading={isCreatingConversation}
              >
                Start New Conversation
              </Button>
            </VStack>
          </Flex>
        )}
      </VStack>
    </Container>
  );
};

export default ChatPage;
