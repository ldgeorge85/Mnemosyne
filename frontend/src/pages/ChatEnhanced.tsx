import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Button,
  useToast,
  Alert,
  AlertIcon,
  AlertDescription,
  Spinner,
  Text,
  Card,
  CardBody,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
} from '@chakra-ui/react';
// import { PlusIcon, BrainIcon, RefreshCwIcon } from 'lucide-react';
import { AddIcon as PlusIcon, RepeatIcon as RefreshCwIcon } from '@chakra-ui/icons';
const BrainIcon = () => <span>🧠</span>;
import { useNavigate } from 'react-router-dom';
import EnhancedChat from '../components/domain/conversation/EnhancedChat';
import { Message, Conversation } from '../types';
import { useAuth } from '../contexts/AuthContext';

// Import the enhanced chat API (we'll need to create this)
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ChatRequest {
  messages: ChatMessage[];
  conversation_id?: string;
  create_conversation?: boolean;
  extract_memories?: boolean;
  extract_tasks?: boolean;
  stream?: boolean;
}

interface ChatResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  role: string;
  created_at: string;
  memories_extracted: boolean;
  tasks_extracted: boolean;
}

// Mock enhanced chat API for now
const createChatCompletion = async (request: ChatRequest): Promise<ChatResponse> => {
  // In real implementation, this would call the enhanced chat API
  const response = await fetch('/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
};

/**
 * Enhanced Chat Page with AI Intelligence Features
 */
const ChatEnhanced: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();

  // State
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStats, setConversationStats] = useState({
    totalMemories: 0,
    totalTasks: 0,
    messagesInContext: 0,
  });

  // Mock data for demonstration
  const [memoriesUsed, setMemoriesUsed] = useState(0);
  const [tasksExtracted, setTasksExtracted] = useState(0);

  useEffect(() => {
    // Initialize with a new conversation
    createNewConversation();
  }, []);

  const createNewConversation = async () => {
    const newConversation: Conversation = {
      id: `conv-${Date.now()}`,
      title: 'New Conversation',
      user_id: user?.id || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true,
      message_count: 0,
      metadata: {},
    };
    setCurrentConversation(newConversation);
    setMessages([]);
    setMemoriesUsed(0);
    setTasksExtracted(0);
  };

  const handleSendMessage = async (content: string) => {
    if (!currentConversation || !user) return;

    // Add user message to UI immediately
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      conversation_id: currentConversation.id,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true,
      metadata: {},
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);

    try {
      // Prepare chat request
      const chatMessages = messages.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }));
      chatMessages.push({ role: 'user', content });

      // Send to enhanced API
      const response = await createChatCompletion({
        messages: chatMessages,
        conversation_id: currentConversation.id,
        create_conversation: messages.length === 0,
        extract_memories: true,
        extract_tasks: true,
        stream: false,
      });

      // Add assistant response
      const assistantMessage: Message = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.content,
        created_at: response.created_at,
        updated_at: response.created_at,
        is_active: true,
        metadata: {
          memories_extracted: response.memories_extracted,
          tasks_extracted: response.tasks_extracted,
        },
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Update stats (mock data for demonstration)
      if (response.memories_extracted) {
        setMemoriesUsed(prev => prev + Math.floor(Math.random() * 3) + 1);
      }
      if (response.tasks_extracted) {
        setTasksExtracted(prev => prev + Math.floor(Math.random() * 2));
      }

      // Update conversation stats
      setConversationStats(prev => ({
        totalMemories: prev.totalMemories + (response.memories_extracted ? 1 : 0),
        totalTasks: prev.totalTasks + (response.tasks_extracted ? 1 : 0),
        messagesInContext: messages.length + 2,
      }));

      toast({
        title: 'AI Processing Complete',
        description: `${response.memories_extracted ? 'Memories extracted. ' : ''}${response.tasks_extracted ? 'Tasks identified.' : ''}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: 'top-right',
      });

    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: 'Error',
        description: 'Failed to send message. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      // Remove the user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleMemoryClick = (memoryId: string) => {
    // Navigate to memory detail view
    navigate(`/memories/${memoryId}`);
  };

  return (
    <Container maxW="container.xl" py={6}>
      <VStack spacing={6} align="stretch" h="calc(100vh - 120px)">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Enhanced Chat</Heading>
            <Text fontSize="sm" color="gray.600">
              AI-powered conversation with memory and task extraction
            </Text>
          </VStack>
          <HStack spacing={2}>
            <Button
              leftIcon={<RefreshCwIcon size={16} />}
              variant="outline"
              size="sm"
              onClick={createNewConversation}
            >
              New Chat
            </Button>
            <Button
              leftIcon={<BrainIcon size={16} />}
              variant="outline"
              size="sm"
              onClick={onOpen}
            >
              View Stats
            </Button>
          </HStack>
        </HStack>

        {/* Statistics Cards */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          <Card size="sm">
            <CardBody>
              <Stat>
                <StatLabel>Memories Active</StatLabel>
                <StatNumber>{memoriesUsed}</StatNumber>
                <StatHelpText>Enhancing responses</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          <Card size="sm">
            <CardBody>
              <Stat>
                <StatLabel>Tasks Found</StatLabel>
                <StatNumber>{tasksExtracted}</StatNumber>
                <StatHelpText>Ready to manage</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          <Card size="sm">
            <CardBody>
              <Stat>
                <StatLabel>Context Size</StatLabel>
                <StatNumber>{messages.length}</StatNumber>
                <StatHelpText>Messages in memory</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Chat Interface */}
        <Box flex={1} minH={0}>
          <EnhancedChat
            conversationId={currentConversation?.id}
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            memoriesUsed={memoriesUsed}
            tasksExtracted={tasksExtracted}
            onMemoryClick={handleMemoryClick}
          />
        </Box>
      </VStack>

      {/* Stats Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Conversation Intelligence</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4} align="stretch">
              <Alert status="info">
                <AlertIcon />
                <AlertDescription>
                  This conversation has enhanced {conversationStats.totalMemories} memories
                  and identified {conversationStats.totalTasks} tasks.
                </AlertDescription>
              </Alert>
              
              <SimpleGrid columns={2} spacing={4}>
                <Stat>
                  <StatLabel>Total Memories</StatLabel>
                  <StatNumber>{conversationStats.totalMemories}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Total Tasks</StatLabel>
                  <StatNumber>{conversationStats.totalTasks}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Messages</StatLabel>
                  <StatNumber>{conversationStats.messagesInContext}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>AI Learning</StatLabel>
                  <StatNumber color="green.500">Active</StatNumber>
                </Stat>
              </SimpleGrid>

              <Text fontSize="sm" color="gray.600">
                The AI is continuously learning from this conversation to provide
                better responses and extract actionable insights.
              </Text>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default ChatEnhanced;