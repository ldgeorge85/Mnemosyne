/**
 * Conversations Page Component
 * 
 * This component displays a list of conversations and allows users
 * to create new conversations or select existing ones.
 */
import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Flex,
  Grid,
  Heading,
  Input,
  InputGroup,
  InputLeftElement,
  Stack,
  Text,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  useColorModeValue,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { 
  FiPlus, 
  FiSearch, 
  FiMoreVertical, 
  FiMessageSquare, 
  FiEdit, 
  FiTrash2,
  FiMessageCircle,
} from 'react-icons/fi';
import { useConversationStore } from '../stores';
import { Conversation } from '../types';

/**
 * Conversations page component that displays all user conversations
 */
const Conversations: React.FC = () => {
  // Get conversations from store
  const { 
    conversations, 
    fetchConversations, 
    createConversation,
    deleteConversation, 
    isLoading,
  } = useConversationStore();
  
  // State for search query
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modal for creating new conversation
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [newTitle, setNewTitle] = useState('');
  
  // Background colors
  const cardBg = useColorModeValue('white', 'gray.700');
  
  // Fetch conversations on component mount
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);
  
  // Filter conversations based on search query
  const filteredConversations = conversations.filter(conversation => 
    conversation.title.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Handle creating a new conversation
  const handleCreateConversation = async () => {
    if (newTitle.trim()) {
      await createConversation(newTitle.trim());
      setNewTitle('');
      onClose();
    }
  };
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading as="h1" size="lg">Conversations</Heading>
        <Button 
          leftIcon={<FiPlus />} 
          colorScheme="brand" 
          onClick={onOpen}
        >
          New Conversation
        </Button>
      </Flex>
      
      {/* Search input */}
      <InputGroup mb={6}>
        <InputLeftElement pointerEvents="none">
          <FiSearch color="gray.300" />
        </InputLeftElement>
        <Input 
          placeholder="Search conversations" 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </InputGroup>
      
      {/* Conversations grid */}
      {isLoading ? (
        <Text>Loading conversations...</Text>
      ) : filteredConversations.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Box as={FiMessageCircle} size="48px" mx="auto" mb={4} />
          <Heading as="h3" size="md" mb={2}>No conversations found</Heading>
          <Text color="gray.500">
            {searchQuery 
              ? "No conversations match your search criteria" 
              : "Start a new conversation to begin"}
          </Text>
          <Button 
            mt={4} 
            colorScheme="brand" 
            leftIcon={<FiPlus />}
            onClick={onOpen}
          >
            New Conversation
          </Button>
        </Box>
      ) : (
        <Grid 
          templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} 
          gap={6}
        >
          {filteredConversations.map((conversation) => (
            <ConversationCard 
              key={conversation.id} 
              conversation={conversation} 
              onDelete={deleteConversation}
            />
          ))}
        </Grid>
      )}
      
      {/* New conversation modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>New Conversation</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl>
              <FormLabel>Conversation Title</FormLabel>
              <Input 
                placeholder="Enter a title for your conversation"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button 
              colorScheme="brand" 
              mr={3} 
              onClick={handleCreateConversation}
              isDisabled={!newTitle.trim()}
            >
              Create
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

/**
 * Conversation card component for displaying individual conversations
 */
interface ConversationCardProps {
  conversation: Conversation;
  onDelete: (id: string) => Promise<void>;
}

const ConversationCard: React.FC<ConversationCardProps> = ({ conversation, onDelete }) => {
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Calculate conversation summary
  const getLastMessage = () => {
    if (conversation.messages.length === 0) {
      return "No messages yet";
    }
    
    const lastMessage = conversation.messages[conversation.messages.length - 1];
    return lastMessage.content.length > 100
      ? `${lastMessage.content.substring(0, 100)}...`
      : lastMessage.content;
  };
  
  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  return (
    <Card 
      bg={cardBg} 
      borderWidth="1px" 
      borderColor={borderColor}
      borderRadius="lg" 
      overflow="hidden"
      _hover={{ 
        transform: 'translateY(-4px)', 
        boxShadow: 'md',
        borderColor: 'brand.300',
      }}
      transition="all 0.2s"
    >
      <CardHeader pb={2}>
        <Flex justify="space-between" align="center">
          <Flex align="center">
            <Box color="brand.500" mr={2}>
              <FiMessageSquare />
            </Box>
            <Heading size="md" noOfLines={1}>
              {conversation.title}
            </Heading>
          </Flex>
          <Menu>
            <MenuButton
              as={IconButton}
              icon={<FiMoreVertical />}
              variant="ghost"
              size="sm"
              aria-label="Options"
            />
            <MenuList>
              <MenuItem as={RouterLink} to={`/conversations/${conversation.id}`} icon={<FiEdit />}>
                Open
              </MenuItem>
              <MenuItem 
                icon={<FiTrash2 />} 
                color="red.500"
                onClick={() => onDelete(conversation.id)}
              >
                Delete
              </MenuItem>
            </MenuList>
          </Menu>
        </Flex>
      </CardHeader>
      <CardBody py={2}>
        <Text noOfLines={3} fontSize="sm" color="gray.500">
          {getLastMessage()}
        </Text>
      </CardBody>
      <CardFooter pt={2} justify="space-between" align="center">
        <Text fontSize="xs" color="gray.500">
          {conversation.messages.length} messages
        </Text>
        <Text fontSize="xs" color="gray.500">
          Updated: {formatDate(conversation.updatedAt)}
        </Text>
      </CardFooter>
    </Card>
  );
};

export default Conversations;
