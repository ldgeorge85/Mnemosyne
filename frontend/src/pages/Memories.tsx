import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Card,
  CardBody,
  Badge,
  Button,
  Input,
  InputGroup,
  InputLeftElement,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Flex,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Textarea,
  FormControl,
  FormLabel,
  Tag,
  TagLabel,
  TagCloseButton,
  Wrap,
  WrapItem,
  Progress,
  Tooltip,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
} from '@chakra-ui/react';
import { SearchIcon, AddIcon, EditIcon, DeleteIcon, InfoIcon, StarIcon } from '@chakra-ui/icons';
import { 
  listMemories, 
  createMemory, 
  updateMemory, 
  deleteMemory, 
  searchMemories, 
  getMemoryStatistics,
  type Memory, 
  type MemoryCreate, 
  type MemoryUpdate,
  type MemoryStatistics 
} from '../api/memories';
import { useAuth } from '../contexts/AuthContext';

/**
 * Component to display importance score as stars
 */
const ImportanceScore: React.FC<{ score: number }> = ({ score }) => {
  const normalizedScore = Math.max(0, Math.min(10, score)); // Ensure 0-10 range
  const stars = Math.round(normalizedScore / 2); // Convert to 0-5 stars
  
  return (
    <HStack spacing={1}>
      {[...Array(5)].map((_, i) => (
        <StarIcon
          key={i}
          color={i < stars ? 'yellow.400' : 'gray.300'}
          boxSize={3}
        />
      ))}
      <Text fontSize="xs" color="gray.600" ml={1}>
        {score.toFixed(1)}
      </Text>
    </HStack>
  );
};

/**
 * Component to display memory source badge
 */
const MemorySourceBadge: React.FC<{ source?: string }> = ({ source }) => {
  const colorScheme = source === 'conversation' ? 'green' : 
                      source === 'manual' ? 'blue' : 'gray';
  return (
    <Badge colorScheme={colorScheme} fontSize="xs">
      {source || 'unknown'}
    </Badge>
  );
};

/**
 * Memories page component
 * 
 * Displays user's memories with CRUD operations and search functionality
 */
const Memories: React.FC = () => {
  const { user } = useAuth();
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [statistics, setStatistics] = useState<MemoryStatistics | null>(null);
  
  // Form state
  const [formData, setFormData] = useState<Omit<MemoryCreate, 'user_id'> & { id?: string }>({
    title: '',
    content: '',
    tags: [],
  });
  const [newTag, setNewTag] = useState<string>('');

  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    fetchMemories();
    fetchStatistics();
  }, []);

  /**
   * Fetch memory statistics
   */
  const fetchStatistics = async () => {
    try {
      const response = await getMemoryStatistics();
      if (response.success && response.data) {
        setStatistics(response.data);
      }
    } catch (err) {
      // Statistics are optional, don't show error
      console.error('Failed to fetch statistics:', err);
    }
  };

  /**
   * Fetch memories from the API
   */
  const fetchMemories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await listMemories({ limit: 50 });
      
      if (response.success && response.data) {
        setMemories(response.data);
      } else {
        throw new Error(response.message || 'Failed to fetch memories');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch memories. The API may not be available.');
      toast({
        title: 'Error',
        description: 'Failed to fetch memories. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle search functionality
   */
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchMemories();
      return;
    }

    try {
      setLoading(true);
      const response = await searchMemories({
        query: searchQuery,
        limit: 50,
      });

      if (response.success && response.data) {
        setMemories(response.data);
      }
    } catch (err: any) {
      toast({
        title: 'Search Error',
        description: 'Failed to search memories. Please try again.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Open modal for creating new memory
   */
  const handleCreateMemory = () => {
    setFormData({ title: '', content: '', tags: [] });
    setSelectedMemory(null);
    setIsEditing(false);
    onOpen();
  };

  /**
   * Open modal for editing existing memory
   */
  const handleEditMemory = (memory: Memory) => {
    setFormData({
      id: memory.id,
      title: memory.title,
      content: memory.content,
      tags: memory.tags || [],
    });
    setSelectedMemory(memory);
    setIsEditing(true);
    onOpen();
  };

  /**
   * Save memory (create or update)
   */
  const handleSaveMemory = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Title and content are required.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      if (isEditing && selectedMemory) {
        const updateData: MemoryUpdate = {
          title: formData.title,
          content: formData.content,
          tags: formData.tags,
        };
        await updateMemory(selectedMemory.id, updateData);
        toast({
          title: 'Success',
          description: 'Memory updated successfully.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        if (!user?.id) {
          toast({
            title: 'Authentication required',
            description: 'Unable to determine current user. Please log in again.',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          return;
        }
        await createMemory({ 
          ...formData, 
          user_id: user.id,
          metadata: { source: 'manual' }
        });
        toast({
          title: 'Success',
          description: 'Memory created successfully.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
      
      onClose();
      fetchMemories();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: `Failed to ${isEditing ? 'update' : 'create'} memory. Please try again.`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  /**
   * Delete memory
   */
  const handleDeleteMemory = async (memoryId: string) => {
    if (!window.confirm('Are you sure you want to delete this memory?')) {
      return;
    }

    try {
      await deleteMemory(memoryId);
      toast({
        title: 'Success',
        description: 'Memory deleted successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      fetchMemories();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to delete memory. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  /**
   * Add tag to form data
   */
  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()]
      }));
      setNewTag('');
    }
  };

  /**
   * Remove tag from form data
   */
  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove) || []
    }));
  };

  if (loading && memories.length === 0) {
    return (
      <Box p={6}>
        <Flex justify="center" align="center" minH="200px">
          <VStack spacing={4}>
            <Spinner size="xl" />
            <Text>Loading memories...</Text>
          </VStack>
        </Flex>
      </Box>
    );
  }

  if (error && memories.length === 0) {
    return (
      <Box p={6}>
        <Alert status="error">
          <AlertIcon />
          <Box>
            <AlertTitle>Error loading memories</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
        <Button mt={4} onClick={fetchMemories}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <Heading size="lg">Memories</Heading>
          <Button leftIcon={<AddIcon />} colorScheme="blue" onClick={handleCreateMemory}>
            New Memory
          </Button>
        </Flex>

        {/* Statistics */}
        {statistics && (
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            <Stat>
              <StatLabel>Total Memories</StatLabel>
              <StatNumber>{statistics.total_memories}</StatNumber>
              <StatHelpText>{statistics.active_memories} active</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Memory Chunks</StatLabel>
              <StatNumber>{statistics.total_chunks}</StatNumber>
              <StatHelpText>Searchable pieces</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Avg Importance</StatLabel>
              <StatNumber>{statistics.average_importance_score.toFixed(1)}</StatNumber>
              <StatHelpText>Out of 10</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Extraction Rate</StatLabel>
              <StatNumber>
                {statistics.total_memories > 0 
                  ? Math.round((statistics.total_chunks / statistics.total_memories) * 100) 
                  : 0}%
              </StatNumber>
              <StatHelpText>AI enrichment</StatHelpText>
            </Stat>
          </SimpleGrid>
        )}

        {/* Search */}
        <HStack>
          <InputGroup flex={1}>
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search memories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </InputGroup>
          <Button onClick={handleSearch} isLoading={loading}>
            Search
          </Button>
          {searchQuery && (
            <Button variant="outline" onClick={() => { setSearchQuery(''); fetchMemories(); }}>
              Clear
            </Button>
          )}
        </HStack>

        {/* Memories List */}
        {memories.length === 0 ? (
          <Alert status="info">
            <AlertIcon />
            <Box>
              <AlertTitle>No memories found</AlertTitle>
              <AlertDescription>
                {searchQuery ? 'No memories match your search criteria.' : 'You haven\'t created any memories yet. Click "New Memory" to get started.'}
              </AlertDescription>
            </Box>
          </Alert>
        ) : (
          <VStack spacing={4} align="stretch">
            {memories.map((memory) => (
              <Card key={memory.id}>
                <CardBody>
                  <VStack align="stretch" spacing={3}>
                    <Flex justify="space-between" align="flex-start">
                      <VStack align="stretch" spacing={2} flex={1}>
                        <HStack justify="space-between" align="flex-start">
                          <Heading size="md">{memory.title}</Heading>
                          <HStack spacing={2}>
                            {memory.metadata?.source && (
                              <MemorySourceBadge source={memory.metadata.source} />
                            )}
                            {memory.similarity && (
                              <Badge colorScheme="purple" fontSize="xs">
                                {Math.round(memory.similarity * 100)}% match
                              </Badge>
                            )}
                          </HStack>
                        </HStack>
                        
                        <Text color="gray.600" noOfLines={3}>
                          {memory.content}
                        </Text>
                        
                        {/* Display extracted entities */}
                        {memory.metadata?.entities && memory.metadata.entities.length > 0 && (
                          <Wrap spacing={1}>
                            {memory.metadata.entities.slice(0, 5).map((entity, idx) => (
                              <WrapItem key={idx}>
                                <Tooltip label={`${entity.type} (${Math.round(entity.confidence * 100)}% confident)`}>
                                  <Badge 
                                    colorScheme={
                                      entity.type === 'PERSON' ? 'teal' :
                                      entity.type === 'LOCATION' ? 'orange' :
                                      entity.type === 'DATE' ? 'purple' : 'gray'
                                    }
                                    variant="outline"
                                    fontSize="xs"
                                  >
                                    {entity.text}
                                  </Badge>
                                </Tooltip>
                              </WrapItem>
                            ))}
                            {memory.metadata.entities.length > 5 && (
                              <WrapItem>
                                <Badge variant="outline" fontSize="xs">
                                  +{memory.metadata.entities.length - 5} more
                                </Badge>
                              </WrapItem>
                            )}
                          </Wrap>
                        )}
                        
                        {/* Tags */}
                        {memory.tags && memory.tags.length > 0 && (
                          <Wrap>
                            {memory.tags.map((tag) => (
                              <WrapItem key={tag}>
                                <Badge colorScheme="blue" variant="subtle">
                                  {tag}
                                </Badge>
                              </WrapItem>
                            ))}
                          </Wrap>
                        )}
                        
                        {/* Footer with metadata */}
                        <HStack fontSize="sm" color="gray.500" spacing={3}>
                          <Text>{new Date(memory.created_at).toLocaleDateString()}</Text>
                          {memory.importance_score !== undefined && (
                            <ImportanceScore score={memory.importance_score} />
                          )}
                          {memory.metadata?.domain && (
                            <Badge variant="subtle" colorScheme="gray" fontSize="xs">
                              {memory.metadata.domain}
                            </Badge>
                          )}
                        </HStack>
                      </VStack>
                      <HStack spacing={2}>
                        <IconButton
                          aria-label="Edit memory"
                          icon={<EditIcon />}
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditMemory(memory)}
                        />
                        <IconButton
                          aria-label="Delete memory"
                          icon={<DeleteIcon />}
                          size="sm"
                          variant="outline"
                          colorScheme="red"
                          onClick={() => handleDeleteMemory(memory.id)}
                        />
                      </HStack>
                    </Flex>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </VStack>
        )}
      </VStack>

      {/* Create/Edit Memory Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isEditing ? 'Edit Memory' : 'Create New Memory'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Title</FormLabel>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter memory title..."
                />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>Content</FormLabel>
                <Textarea
                  value={formData.content}
                  onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Enter memory content..."
                  rows={6}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Tags</FormLabel>
                <HStack>
                  <Input
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    placeholder="Add a tag..."
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  />
                  <Button onClick={handleAddTag} size="sm">
                    Add
                  </Button>
                </HStack>
                {formData.tags && formData.tags.length > 0 && (
                  <Wrap mt={2}>
                    {formData.tags.map((tag) => (
                      <WrapItem key={tag}>
                        <Tag size="md" colorScheme="blue" variant="solid">
                          <TagLabel>{tag}</TagLabel>
                          <TagCloseButton onClick={() => handleRemoveTag(tag)} />
                        </Tag>
                      </WrapItem>
                    ))}
                  </Wrap>
                )}
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handleSaveMemory}>
              {isEditing ? 'Update' : 'Create'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default Memories;
