/**
 * Real Chat Implementation - No Mocking
 * Connects to actual backend LLM endpoints
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Input,
  Button,
  Text,
  Flex,
  Avatar,
  IconButton,
  useColorMode,
  Card,
  CardBody,
  useToast,
  Spinner
} from '@chakra-ui/react';
import { FiSend, FiMoon, FiSun, FiTrash2, FiRefreshCw } from 'react-icons/fi';
import { apiClient } from '../api/client';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

const ChatReal: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;
    if (isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Call the real backend endpoint
      const response = await apiClient.post('/llm/chat/completions', {
        messages: [
          ...messages.map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
          })),
          { role: 'user', content: inputText }
        ],
        model: 'gpt-3.5-turbo', // Use a default model
        temperature: 0.7,
        max_tokens: 500
      });

      if (response.data && response.data.choices && response.data.choices[0]) {
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          text: response.data.choices[0].message.content,
          sender: 'assistant',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      
      // Show error to user
      toast({
        title: 'Chat Error',
        description: error.response?.data?.detail || 'Failed to get response. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });

      // Add error message to chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        text: 'Sorry, I encountered an error. Please try again or check your connection.',
        sender: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <Container maxW="container.lg" py={8}>
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Heading>Chat</Heading>
        <HStack spacing={2}>
          <Button
            leftIcon={<FiRefreshCw />}
            variant="outline"
            size="sm"
            onClick={handleClearChat}
          >
            New Chat
          </Button>
          <IconButton
            aria-label="Toggle dark mode"
            icon={colorMode === 'dark' ? <FiSun /> : <FiMoon />}
            onClick={toggleColorMode}
          />
        </HStack>
      </Flex>

      <Card h="600px">
        <CardBody>
          <VStack h="full" spacing={4}>
            {/* Messages Area */}
            <Box
              flex={1}
              w="full"
              overflowY="auto"
              border="1px"
              borderColor="gray.200"
              borderRadius="md"
              p={4}
            >
              <VStack spacing={4} align="stretch">
                {messages.length === 0 ? (
                  <Text color="gray.500" textAlign="center" mt={8}>
                    Start a conversation by typing a message below
                  </Text>
                ) : (
                  messages.map((message) => (
                    <HStack
                      key={message.id}
                      align="start"
                      spacing={3}
                      alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                      maxW="70%"
                    >
                      {message.sender === 'assistant' && (
                        <Avatar size="sm" name="AI" bg="blue.500" />
                      )}
                      <Box
                        bg={message.sender === 'user' ? 'blue.500' : 'gray.100'}
                        color={message.sender === 'user' ? 'white' : 'black'}
                        px={4}
                        py={2}
                        borderRadius="lg"
                      >
                        <Text>{message.text}</Text>
                        <Text fontSize="xs" opacity={0.8} mt={1}>
                          {message.timestamp.toLocaleTimeString()}
                        </Text>
                      </Box>
                      {message.sender === 'user' && (
                        <Avatar size="sm" name="You" bg="green.500" />
                      )}
                    </HStack>
                  ))
                )}
                {isLoading && (
                  <HStack alignSelf="flex-start" spacing={3}>
                    <Avatar size="sm" name="AI" bg="blue.500" />
                    <Box bg="gray.100" px={4} py={2} borderRadius="lg">
                      <Spinner size="sm" />
                    </Box>
                  </HStack>
                )}
                <div ref={messagesEndRef} />
              </VStack>
            </Box>

            {/* Input Area */}
            <HStack w="full">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                isDisabled={isLoading}
                size="lg"
              />
              <IconButton
                aria-label="Send message"
                icon={<FiSend />}
                onClick={handleSendMessage}
                isLoading={isLoading}
                colorScheme="blue"
                size="lg"
              />
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    </Container>
  );
};

export default ChatReal;