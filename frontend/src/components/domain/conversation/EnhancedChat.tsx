import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Input,
  Button,
  Card,
  CardBody,
  Text,
  Badge,
  Tooltip,
  IconButton,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Progress,
  Collapse,
  useDisclosure,
  Divider,
  Flex,
} from '@chakra-ui/react';
// import { 
//   SendIcon, 
//   BrainIcon, 
//   TasksIcon,
//   SparklesIcon,
//   ChevronDownIcon,
//   ChevronUpIcon,
//   InfoIcon,
// } from 'lucide-react';
import { ChevronDownIcon, ChevronUpIcon, InfoIcon } from '@chakra-ui/icons';
const SendIcon = () => <span>📤</span>;
const BrainIcon = () => <span>🧠</span>;
const TasksIcon = () => <span>📋</span>;
const SparklesIcon = () => <span>✨</span>;
import { Message } from '../../../types';

interface EnhancedChatProps {
  conversationId?: string;
  onSendMessage: (message: string) => Promise<void>;
  messages: Message[];
  isLoading?: boolean;
  memoriesUsed?: number;
  tasksExtracted?: number;
  onMemoryClick?: (memoryId: string) => void;
}

interface MessageWithIntelligence extends Message {
  memoriesUsed?: Array<{ id: string; title: string; relevance: number }>;
  tasksExtracted?: Array<{ title: string; priority: string }>;
}

/**
 * Enhanced Chat Component with AI Intelligence Indicators
 */
export const EnhancedChat: React.FC<EnhancedChatProps> = ({
  conversationId,
  onSendMessage,
  messages,
  isLoading = false,
  memoriesUsed = 0,
  tasksExtracted = 0,
  onMemoryClick,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const { isOpen: showIntelligence, onToggle: toggleIntelligence } = useDisclosure({ defaultIsOpen: true });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const message = inputValue.trim();
    setInputValue('');
    setIsTyping(true);

    try {
      await onSendMessage(message);
    } catch (error) {
      toast({
        title: 'Error sending message',
        description: 'Please try again.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <VStack spacing={4} align="stretch" h="full">
      {/* Intelligence Indicators */}
      <Card size="sm" bg="blue.50" borderColor="blue.200" borderWidth={1}>
        <CardBody>
          <HStack justify="space-between" align="center">
            <HStack spacing={4}>
              <Tooltip label="Memories being used to enhance responses">
                <HStack spacing={2}>
                  <BrainIcon size={16} color="#3182CE" />
                  <Text fontSize="sm" fontWeight="medium">
                    {memoriesUsed} memories active
                  </Text>
                </HStack>
              </Tooltip>
              
              <Divider orientation="vertical" h="20px" />
              
              <Tooltip label="Tasks will be extracted from this conversation">
                <HStack spacing={2}>
                  <TasksIcon size={16} color="#38A169" />
                  <Text fontSize="sm" fontWeight="medium">
                    {tasksExtracted} tasks found
                  </Text>
                </HStack>
              </Tooltip>
              
              <Divider orientation="vertical" h="20px" />
              
              <Tooltip label="AI is learning from this conversation">
                <HStack spacing={2}>
                  <SparklesIcon size={16} color="#D69E2E" />
                  <Text fontSize="sm" fontWeight="medium">
                    Learning enabled
                  </Text>
                </HStack>
              </Tooltip>
            </HStack>
            
            <Tooltip label={showIntelligence ? "Hide AI details" : "Show AI details"}>
              <IconButton
                aria-label="Toggle intelligence"
                icon={showIntelligence ? <ChevronUpIcon size={16} /> : <ChevronDownIcon size={16} />}
                size="xs"
                variant="ghost"
                onClick={toggleIntelligence}
              />
            </Tooltip>
          </HStack>
        </CardBody>
      </Card>

      {/* Messages Container */}
      <Box flex={1} overflowY="auto" p={4} bg="gray.50" borderRadius="md">
        <VStack spacing={4} align="stretch">
          {messages.map((message) => (
            <MessageBubble 
              key={message.id} 
              message={message as MessageWithIntelligence}
              showIntelligence={showIntelligence}
              onMemoryClick={onMemoryClick}
            />
          ))}
          
          {isTyping && (
            <HStack spacing={2} p={3}>
              <Spinner size="sm" />
              <Text fontSize="sm" color="gray.600">AI is thinking...</Text>
            </HStack>
          )}
          
          <div ref={messagesEndRef} />
        </VStack>
      </Box>

      {/* Input Area */}
      <HStack spacing={2}>
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
          size="lg"
        />
        <Tooltip label="Send message">
          <IconButton
            aria-label="Send"
            icon={<SendIcon size={20} />}
            onClick={handleSend}
            isLoading={isLoading}
            colorScheme="blue"
            size="lg"
          />
        </Tooltip>
      </HStack>
    </VStack>
  );
};

/**
 * Individual Message Bubble Component
 */
const MessageBubble: React.FC<{
  message: MessageWithIntelligence;
  showIntelligence: boolean;
  onMemoryClick?: (memoryId: string) => void;
}> = ({ message, showIntelligence, onMemoryClick }) => {
  const isUser = message.role === 'user';

  return (
    <Box>
      <HStack align="flex-start" justify={isUser ? 'flex-end' : 'flex-start'}>
        <VStack 
          align={isUser ? 'flex-end' : 'flex-start'} 
          spacing={1}
          maxW="70%"
        >
          <Card
            bg={isUser ? 'blue.500' : 'white'}
            color={isUser ? 'white' : 'black'}
            borderRadius="lg"
            boxShadow="sm"
          >
            <CardBody py={2} px={3}>
              <Text fontSize="sm">{message.content}</Text>
            </CardBody>
          </Card>
          
          {/* AI Intelligence Details */}
          <Collapse in={showIntelligence && !isUser && (message.memoriesUsed || message.tasksExtracted)}>
            <VStack align="flex-start" spacing={1} mt={1}>
              {message.memoriesUsed && message.memoriesUsed.length > 0 && (
                <Box>
                  <HStack spacing={1} mb={1}>
                    <BrainIcon size={12} color="#718096" />
                    <Text fontSize="xs" color="gray.600">Used memories:</Text>
                  </HStack>
                  <VStack align="flex-start" spacing={0.5} pl={4}>
                    {message.memoriesUsed.map((memory) => (
                      <Text
                        key={memory.id}
                        fontSize="xs"
                        color="blue.600"
                        cursor="pointer"
                        _hover={{ textDecoration: 'underline' }}
                        onClick={() => onMemoryClick?.(memory.id)}
                      >
                        • {memory.title} ({Math.round(memory.relevance * 100)}%)
                      </Text>
                    ))}
                  </VStack>
                </Box>
              )}
              
              {message.tasksExtracted && message.tasksExtracted.length > 0 && (
                <Box>
                  <HStack spacing={1} mb={1}>
                    <TasksIcon size={12} color="#718096" />
                    <Text fontSize="xs" color="gray.600">Extracted tasks:</Text>
                  </HStack>
                  <VStack align="flex-start" spacing={0.5} pl={4}>
                    {message.tasksExtracted.map((task, idx) => (
                      <HStack key={idx} spacing={1}>
                        <Text fontSize="xs" color="green.600">
                          • {task.title}
                        </Text>
                        <Badge size="xs" colorScheme={getPriorityColor(task.priority)}>
                          {task.priority}
                        </Badge>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}
            </VStack>
          </Collapse>
          
          <Text fontSize="xs" color="gray.500">
            {new Date(message.created_at).toLocaleTimeString()}
          </Text>
        </VStack>
      </HStack>
    </Box>
  );
};

// Helper function for priority colors
const getPriorityColor = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'urgent':
    case 'high':
      return 'red';
    case 'medium':
      return 'yellow';
    case 'low':
      return 'green';
    default:
      return 'gray';
  }
};

export default EnhancedChat;