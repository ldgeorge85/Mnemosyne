/**
 * Chat Page
 * 
 * This page demonstrates the complete chat interface, including the message list,
 * typing indicators, and input area. It serves as a working demonstration of
 * the UI-01 task implementation.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  useToast,
  Flex,
} from '@chakra-ui/react';
import { ChatContainer } from '../components/domain/conversation';
import { Message } from '../types';
import { v4 as uuidv4 } from 'uuid';

/**
 * Demo chat page component
 */
const ChatPage: React.FC = () => {
  // State for messages
  const [messages, setMessages] = useState<Message[]>([]);
  // State for loading messages
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  // State for sending a message
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  // State for typing indicator
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  // Error state
  const [error, setError] = useState<string | null>(null);
  
  // Toast for notifications
  const toast = useToast();
  
  // Load initial conversation on mount
  useEffect(() => {
    loadConversation();
  }, []);
  
  /**
   * Load a conversation
   */
  const loadConversation = async () => {
    setIsLoadingMessages(true);
    setError(null);
    
    try {
      // In a real app, this would be an API call
      // For demo purposes, we'll use a timeout and mock data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Sample conversation
      const sampleMessages: Message[] = [
        {
          id: uuidv4(),
          conversationId: '1',
          content: 'Hello! How can I assist you today?',
          role: 'assistant',
          createdAt: new Date(Date.now() - 60000).toISOString(),
        },
        {
          id: uuidv4(),
          conversationId: '1',
          content: 'I need help organizing my tasks for the week.',
          role: 'user',
          createdAt: new Date(Date.now() - 45000).toISOString(),
        },
        {
          id: uuidv4(),
          conversationId: '1',
          content: 'I can help you organize your tasks. Would you like me to create a schedule or just help you prioritize your existing tasks?',
          role: 'assistant',
          createdAt: new Date(Date.now() - 30000).toISOString(),
        }
      ];
      
      setMessages(sampleMessages);
    } catch (err) {
      setError('Failed to load conversation. Please try again.');
      console.error('Error loading conversation:', err);
    } finally {
      setIsLoadingMessages(false);
    }
  };
  
  /**
   * Send a message
   */
  const handleSendMessage = async (content: string) => {
    // Create a new user message
    const userMessage: Message = {
      id: uuidv4(),
      conversationId: '1',
      content,
      role: 'user',
      createdAt: new Date().toISOString(),
    };
    
    // Add user message to the list
    setMessages([...messages, userMessage]);
    setIsSendingMessage(true);
    
    // Show typing indicator
    setIsAgentTyping(true);
    
    try {
      // In a real app, this would be an API call
      // For demo purposes, we'll use a timeout
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Create assistant response
      const assistantMessage: Message = {
        id: uuidv4(),
        conversationId: '1',
        content: generateResponse(content),
        role: 'assistant',
        createdAt: new Date().toISOString(),
      };
      
      // Hide typing indicator and add assistant message
      setIsAgentTyping(false);
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (err) {
      setIsAgentTyping(false);
      setError('Failed to send message. Please try again.');
      console.error('Error sending message:', err);
      
      toast({
        title: 'Error',
        description: 'Failed to send message',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSendingMessage(false);
    }
  };
  
  /**
   * Generate a simple response based on input
   * In a real app, this would be handled by the backend
   */
  const generateResponse = (input: string): string => {
    const lowercaseInput = input.toLowerCase();
    
    if (lowercaseInput.includes('hello') || lowercaseInput.includes('hi')) {
      return 'Hello! How can I assist you today?';
    } else if (lowercaseInput.includes('help')) {
      return 'I\'m here to help. What specifically do you need assistance with?';
    } else if (lowercaseInput.includes('task') || lowercaseInput.includes('schedule')) {
      return 'I can help you manage your tasks. Would you like me to create a new task, list your current tasks, or help you prioritize them?';
    } else if (lowercaseInput.includes('memory') || lowercaseInput.includes('remember')) {
      return 'I\'m equipped with a memory system that helps me recall our previous conversations and important information. What would you like me to remember?';
    } else {
      return 'I understand. Is there anything specific you\'d like me to help you with regarding that?';
    }
  };
  
  /**
   * Handle message deletion
   */
  const handleDeleteMessage = (messageId: string) => {
    setMessages(messages.filter(message => message.id !== messageId));
    
    toast({
      title: 'Message deleted',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };
  
  /**
   * Handle message copy
   */
  const handleCopyMessage = (message: Message) => {
    navigator.clipboard.writeText(message.content);
    
    toast({
      title: 'Copied to clipboard',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };
  
  /**
   * Handle file attachment
   */
  const handleAddAttachment = (file: File) => {
    toast({
      title: 'File attached',
      description: `${file.name} (${Math.round(file.size / 1024)}KB)`,
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
    
    // In a real app, this would upload the file to a server
    console.log('File attached:', file);
  };
  
  return (
    <Container maxW="container.lg" py={8}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="xl" mb={2}>
            Chat Demo
          </Heading>
          <Text color="gray.600">
            This page demonstrates the chat interface implementation (UI-01)
          </Text>
        </Box>
        
        <Box height="70vh">
          <ChatContainer
            title="Demo Conversation"
            description="This is a demonstration of the chat interface components, including message list, typing indicators, and input area."
            messages={messages}
            isLoadingMessages={isLoadingMessages}
            isSendingMessage={isSendingMessage}
            error={error}
            isAgentTyping={isAgentTyping}
            onSendMessage={handleSendMessage}
            onDeleteMessage={handleDeleteMessage}
            onCopyMessage={handleCopyMessage}
            allowAttachments={true}
            onAddAttachment={handleAddAttachment}
          />
        </Box>
      </VStack>
    </Container>
  );
};

export default ChatPage;
