/**
 * Simple Chat Page Component
 * Works without backend API for development
 */
import React, { useState } from 'react';
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
  Divider
} from '@chakra-ui/react';
import { FiSend, FiMoon, FiSun, FiTrash2, FiRefreshCw } from 'react-icons/fi';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

const ChatSimple: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your Mnemosyne assistant. How can I help you today?',
      sender: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    const assistantMessage: Message = {
      id: `assistant-${Date.now()}`,
      text: 'This is a demo response. The backend API is not connected yet, but once it is, I\'ll be able to help you manage your memories, tasks, and more!',
      sender: 'assistant',
      timestamp: new Date()
    };

    setMessages([...messages, userMessage, assistantMessage]);
    setInputText('');
  };

  const handleClearChat = () => {
    setMessages([{
      id: '1',
      text: 'Hello! I\'m your Mnemosyne assistant. How can I help you today?',
      sender: 'assistant',
      timestamp: new Date()
    }]);
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
            aria-label="Clear chat"
            icon={<FiTrash2 />}
            variant="outline"
            size="sm"
            onClick={handleClearChat}
          />
          <IconButton
            aria-label="Toggle dark mode"
            icon={colorMode === 'dark' ? <FiSun /> : <FiMoon />}
            onClick={toggleColorMode}
          />
        </HStack>
      </Flex>

      <Card height="60vh">
        <CardBody>
          <VStack
            spacing={4}
            align="stretch"
            height="100%"
            overflowY="auto"
            px={4}
            pb={4}
          >
            {messages.map((message, index) => (
              <Box key={message.id}>
                <Flex
                  justify={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                  mb={2}
                >
                  <HStack
                    maxW="70%"
                    bg={message.sender === 'user' ? 'blue.500' : 'gray.100'}
                    color={message.sender === 'user' ? 'white' : 'black'}
                    p={3}
                    borderRadius="lg"
                    spacing={3}
                  >
                    {message.sender === 'assistant' && (
                      <Avatar size="sm" name="AI" bg="purple.500" />
                    )}
                    <VStack align="start" spacing={1}>
                      <Text fontSize="sm">{message.text}</Text>
                      <Text fontSize="xs" opacity={0.7}>
                        {message.timestamp.toLocaleTimeString()}
                      </Text>
                    </VStack>
                    {message.sender === 'user' && (
                      <Avatar size="sm" name="You" bg="blue.600" />
                    )}
                  </HStack>
                </Flex>
                {index < messages.length - 1 && <Divider my={2} />}
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>

      <HStack mt={4}>
        <Input
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <Button
          colorScheme="blue"
          leftIcon={<FiSend />}
          onClick={handleSendMessage}
        >
          Send
        </Button>
      </HStack>

      <Box mt={4} p={4} bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'} borderRadius="md">
        <Text fontSize="sm" color="gray.500">
          <strong>Development Mode:</strong> Chat interface is working in demo mode. 
          Messages are not being processed by the backend yet.
        </Text>
      </Box>
    </Container>
  );
};

export default ChatSimple;