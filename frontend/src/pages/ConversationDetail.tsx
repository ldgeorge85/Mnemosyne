/**
 * Conversation Detail Page Component
 * 
 * This component displays a detailed view of a single conversation,
 * showing all messages and allowing users to send new messages.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Flex,
  Heading,
  IconButton,
  Input,
  Text,
  VStack,
  HStack,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Divider,
  useColorModeValue,
  Tooltip,
} from '@chakra-ui/react';
import {
  FiSend,
  FiEdit,
  FiTrash2,
  FiMoreVertical,
  FiCopy,
  FiArrowLeft,
  FiMessageSquare,
} from 'react-icons/fi';
import { useConversationStore } from '../stores';
import { Message } from '../types';

/**
 * Conversation detail page component that displays a conversation thread
 */
const ConversationDetail: React.FC = () => {
  // Get conversation ID from URL params
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // Get conversation data and actions from store
  const { 
    currentConversation, 
    getConversation, 
    sendMessage, 
    deleteMessage,
    updateConversation,
    isLoading, 
    error 
  } = useConversationStore();
  
  // State for message input
  const [messageContent, setMessageContent] = useState('');
  const [editTitleMode, setEditTitleMode] = useState(false);
  const [title, setTitle] = useState('');
  
  // Ref for scrolling to bottom of conversation
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Fetch conversation on component mount
  useEffect(() => {
    if (id) {
      getConversation(id);
    }
  }, [id, getConversation]);
  
  // Update title state when conversation changes
  useEffect(() => {
    if (currentConversation) {
      setTitle(currentConversation.title);
    }
  }, [currentConversation]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages]);
  
  // Handle sending a new message
  const handleSendMessage = () => {
    if (id && messageContent.trim()) {
      sendMessage(id, messageContent.trim());
      setMessageContent('');
    }
  };
  
  // Handle pressing Enter to send
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  // Handle title update
  const handleUpdateTitle = () => {
    if (id && title.trim() && currentConversation) {
      updateConversation(id, { title: title.trim() });
      setEditTitleMode(false);
    }
  };
  
  // Handle title edit cancel
  const handleTitleEditCancel = () => {
    if (currentConversation) {
      setTitle(currentConversation.title);
    }
    setEditTitleMode(false);
  };
  
  // Copy text to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };
  
  // Background colors
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const userMessageBg = useColorModeValue('brand.100', 'brand.800');
  const assistantMessageBg = useColorModeValue('gray.100', 'gray.600');
  
  if (isLoading) {
    return <Text>Loading conversation...</Text>;
  }
  
  if (error) {
    return <Text color="red.500">Error: {error}</Text>;
  }
  
  if (!currentConversation) {
    return <Text>Conversation not found</Text>;
  }
  
  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Flex align="center">
          <IconButton
            aria-label="Back to conversations"
            icon={<FiArrowLeft />}
            variant="ghost"
            mr={2}
            onClick={() => navigate('/conversations')}
          />
          
          {editTitleMode ? (
            <HStack>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                size="md"
                width="auto"
                onKeyPress={(e) => e.key === 'Enter' && handleUpdateTitle()}
                autoFocus
              />
              <Button size="sm" onClick={handleUpdateTitle}>Save</Button>
              <Button size="sm" variant="ghost" onClick={handleTitleEditCancel}>Cancel</Button>
            </HStack>
          ) : (
            <Heading as="h1" size="lg" display="flex" alignItems="center">
              <Box as={FiMessageSquare} mr={2} />
              {currentConversation.title}
              <IconButton
                aria-label="Edit title"
                icon={<FiEdit />}
                variant="ghost"
                size="sm"
                ml={2}
                onClick={() => setEditTitleMode(true)}
              />
            </Heading>
          )}
        </Flex>
      </Flex>
      
      {/* Messages */}
      <Box
        bg={bgColor}
        borderRadius="md"
        p={4}
        mb={4}
        height="calc(70vh - 100px)"
        overflowY="auto"
      >
        {currentConversation.messages.length === 0 ? (
          <Flex
            direction="column"
            align="center"
            justify="center"
            height="100%"
            color="gray.500"
          >
            <Box as={FiMessageSquare} size="48px" mb={4} />
            <Text>Start the conversation by sending a message below</Text>
          </Flex>
        ) : (
          <VStack spacing={4} align="stretch">
            {currentConversation.messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onDelete={() => id && deleteMessage(id, message.id)}
                onCopy={() => copyToClipboard(message.content)}
              />
            ))}
            <div ref={messagesEndRef} />
          </VStack>
        )}
      </Box>
      
      {/* Message input */}
      <Flex>
        <Input
          placeholder="Type your message here..."
          value={messageContent}
          onChange={(e) => setMessageContent(e.target.value)}
          onKeyPress={handleKeyPress}
          mr={2}
          bg={useColorModeValue('white', 'gray.700')}
        />
        <IconButton
          aria-label="Send message"
          icon={<FiSend />}
          colorScheme="brand"
          onClick={handleSendMessage}
          isDisabled={!messageContent.trim()}
        />
      </Flex>
    </Box>
  );
};

/**
 * Message bubble component for displaying individual messages
 */
interface MessageBubbleProps {
  message: Message;
  onDelete: () => void;
  onCopy: () => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onDelete, onCopy }) => {
  const isUser = message.role === 'user';
  const userMessageBg = useColorModeValue('brand.100', 'brand.800');
  const assistantMessageBg = useColorModeValue('gray.100', 'gray.600');
  
  // Format date
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  return (
    <Flex
      direction="column"
      alignSelf={isUser ? 'flex-end' : 'flex-start'}
      maxWidth="80%"
    >
      <Flex align="center" mb={1}>
        <Avatar
          size="xs"
          name={isUser ? 'You' : 'Assistant'}
          bg={isUser ? 'brand.500' : 'gray.500'}
          color="white"
          mr={2}
        />
        <Text fontWeight="bold" fontSize="sm">
          {isUser ? 'You' : 'Assistant'}
        </Text>
        <Text fontSize="xs" color="gray.500" ml={2}>
          {formatTime(message.createdAt)}
        </Text>
        
        <Menu>
          <MenuButton
            as={IconButton}
            icon={<FiMoreVertical />}
            variant="ghost"
            size="xs"
            ml={1}
            aria-label="Options"
          />
          <MenuList>
            <MenuItem icon={<FiCopy />} onClick={onCopy}>
              Copy message
            </MenuItem>
            {isUser && (
              <MenuItem icon={<FiTrash2 />} color="red.500" onClick={onDelete}>
                Delete message
              </MenuItem>
            )}
          </MenuList>
        </Menu>
      </Flex>
      
      <Box
        bg={isUser ? userMessageBg : assistantMessageBg}
        p={3}
        borderRadius="lg"
        boxShadow="sm"
      >
        <Text whiteSpace="pre-wrap">{message.content}</Text>
      </Box>
    </Flex>
  );
};

export default ConversationDetail;
