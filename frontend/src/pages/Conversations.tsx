/**
 * Conversations Page Component
 * 
 * This component displays a list of conversations and allows users
 * to create new conversations or select existing ones.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  Button,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Text,
  IconButton,
  useColorModeValue,
  useToast,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  FormControl,
  FormLabel,
  InputGroup,
  InputLeftElement,
  Flex,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
} from '@chakra-ui/react';
import { 
  FiMessageSquare, 
  FiTrash2, 
  FiPlus,
  FiSearch,
  FiMoreVertical,
  FiEdit,
} from 'react-icons/fi';
import { Conversation } from '../types';
import { getConversations, createConversation, deleteConversation } from '../api/conversations';

/**
 * Conversations page component that displays all user conversations
 */
const Conversations: React.FC = () => {
  // State management
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [newTitle, setNewTitle] = useState('');
  
  // Navigation and UI
  const navigate = useNavigate();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // Theme colors
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Fetch conversations on component mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Fetch conversations from API
  const fetchConversations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getConversations(50, 0); // Get up to 50 conversations
      setConversations(data.items || []);
    } catch (err) {
      setError('Failed to load conversations. Please try again.');
      toast({
        title: 'Error',
        description: 'Failed to load conversations',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Filter conversations based on search query
  const filteredConversations = conversations.filter(conversation => 
    conversation.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle creating a new conversation
  const handleCreateConversation = async () => {
    if (!newTitle.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a conversation title',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      const response = await createConversation(newTitle.trim());
      setConversations(prev => [response.data, ...prev]);
      setNewTitle('');
      onClose();
      toast({
        title: 'Success',
        description: 'Conversation created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Navigate to the new conversation
      navigate(`/chat/${response.data.id}`);
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to create conversation',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  // Handle deleting a conversation
  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(conv => conv.id !== id));
      toast({
        title: 'Success',
        description: 'Conversation deleted successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to delete conversation',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  // Helper function to get last message preview
  const getLastMessage = (conversation: Conversation): string => {
    if (!conversation.messages || conversation.messages.length === 0) {
      return 'No messages yet';
    }
    const lastMessage = conversation.messages[conversation.messages.length - 1];
    return lastMessage.content.length > 100 
      ? lastMessage.content.substring(0, 100) + '...'
      : lastMessage.content;
  };

  // Helper function to format date
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Center minH="50vh">
          <Spinner size="xl" color="blue.500" />
        </Center>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          <AlertTitle>Error!</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button mt={4} onClick={fetchConversations}>
          Try Again
        </Button>
      </Container>
    );
  }

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
      {filteredConversations.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Box as={FiMessageSquare} size="48px" mx="auto" mb={4} />
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
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
          {filteredConversations.map((conversation) => (
            <Card 
              key={conversation.id} 
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
                        onClick={() => handleDeleteConversation(conversation.id)}
                      >
                        Delete
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </Flex>
              </CardHeader>
              <CardBody py={2}>
                <Text noOfLines={3} fontSize="sm" color="gray.500">
                  {getLastMessage(conversation)}
                </Text>
              </CardBody>
              <CardFooter pt={2} justify="space-between" align="center">
                <Text fontSize="xs" color="gray.500">
                  {(conversation.messages ? conversation.messages.length : 0)} messages
                </Text>
                <Text fontSize="xs" color="gray.500">
                  Updated: {formatDate((conversation as any).updatedAt || (conversation as any).updated_at)}
                </Text>
              </CardFooter>
            </Card>
          ))}
        </SimpleGrid>
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

export default Conversations;
