/**
 * Conversation Detail Page Component
 * 
 * This component displays a detailed view of a single conversation,
 * showing all messages and allowing users to send new messages.
 */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Flex,
  Heading,
  IconButton,
  Input,
  Text,
  useColorModeValue,
  useToast,
} from '@chakra-ui/react';
import {
  FiSend,
  FiEdit,
  FiTrash2,
  FiArrowLeft,
  FiMessageSquare,
} from 'react-icons/fi';
import { useConversationStore } from '../stores';
import { Message } from '../types';
import { MessageList, MessageSkeleton } from '../components/domain/conversation';

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
  
  // Toast for notifications
  const toast = useToast();
  
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
  
  // No need for manual scroll effect as MessageList handles this
  
  // Handle sending a new message
  const handleSendMessage = () => {
    if (id && messageContent.trim()) {
      sendMessage(id, messageContent.trim());
      setMessageContent('');
    }
  };
  
  // Handle copying a message to clipboard
  const handleCopyMessage = (message: Message) => {
    navigator.clipboard.writeText(message.content)
      .then(() => {
        toast({
          title: 'Message copied',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
      })
      .catch((error) => {
        console.error('Failed to copy message:', error);
        toast({
          title: 'Failed to copy message',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  };
  
  // Handle pressing Enter to send
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
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
    <Box p={5} maxWidth="1200px" margin="0 auto">
      {/* Header with back button and conversation title */}
      <Flex mb={5} align="center">
        <IconButton
          icon={<FiArrowLeft />}
          aria-label="Back to conversations"
          variant="ghost"
          mr={3}
          onClick={() => navigate('/conversations')}
        />
        
        {editTitleMode ? (
          <Flex flex={1}>
            <Input
              value={title}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)}
              onBlur={() => {
                if (id && title.trim()) {
                  updateConversation(id, { title: title.trim() });
                }
                setEditTitleMode(false);
              }}
              onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
                if (e.key === 'Enter') {
                  if (id && title.trim()) {
                    updateConversation(id, { title: title.trim() });
                  }
                  setEditTitleMode(false);
                } else if (e.key === 'Escape') {
                  setTitle(currentConversation?.title || '');
                  setEditTitleMode(false);
                }
              }}
              autoFocus
            />
          </Flex>
        ) : (
          <Flex flex={1} align="center">
            <Heading size="lg" flex={1}>
              {currentConversation?.title || 'New Conversation'}
            </Heading>
            <IconButton
              icon={<FiEdit />}
              aria-label="Edit title"
              variant="ghost"
              size="sm"
              onClick={() => setEditTitleMode(true)}
            />
          </Flex>
        )}
      </Flex>
      
      {/* Message display area */}
      <Box 
        flex={1} 
        overflowY="auto" 
        mb={5} 
        height="calc(100vh - 250px)"
        borderRadius="md"
        border="1px"
        borderColor={useColorModeValue('gray.200', 'gray.700')}
      >
        {isLoading && !currentConversation ? (
          <MessageSkeleton count={4} />
        ) : currentConversation ? (
          <MessageList
            messages={currentConversation.messages || []}
            isLoading={isLoading}
            error={error}
            onDeleteMessage={(messageId: string) => deleteMessage(id as string, messageId)}
            onCopyMessage={handleCopyMessage}
            autoScroll={true}
          />
        ) : (
          <Flex
            direction="column"
            align="center"
            justify="center"
            height="100%"
            p={10}
            color="gray.500"
          >
            <Box as={FiMessageSquare} size="48px" mb={4} />
            <Text>Start the conversation by sending a message below</Text>
          </Flex>
        )}
      </Box>
      
      {/* Message input area */}
      <Flex mt={4}>
        <Input
          flex={1}
          placeholder="Type your message..."
          value={messageContent}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMessageContent(e.target.value)}
          onKeyPress={handleKeyPress}
          mr={2}
        />
        <IconButton
          colorScheme="blue"
          aria-label="Send message"
          icon={<FiSend />}
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
