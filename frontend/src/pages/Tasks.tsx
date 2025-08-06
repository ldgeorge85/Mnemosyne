import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Card,
  CardHeader,
  CardBody,
  Text,
  Badge,
  Button,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  SimpleGrid,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  useToast,
  IconButton,
  Tooltip,
  Input,
  Textarea,
  Select,
  FormControl,
  FormLabel,
  ModalFooter,
  Flex,
  Tag,
  TagLabel,
  TagCloseButton,
  Wrap,
  WrapItem,
  Divider,
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, CheckIcon, InfoIcon } from '@chakra-ui/icons';
import TaskIntelligencePanel from '../components/domain/tasks/TaskIntelligencePanel';
import { 
  listTasks, 
  createTask, 
  updateTask, 
  deleteTask, 
  type Task, 
  type TaskCreate, 
  type TaskUpdate, 
  TaskStatus, 
  TaskPriority 
} from '../api/tasks';

/**
 * Tasks page component
 * 
 * Displays user's tasks with CRUD operations and filtering
 */
const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<number>(0);
  
  // Form state
  const [formData, setFormData] = useState<TaskCreate & { id?: string }>({
    title: '',
    description: '',
    status: TaskStatus.PENDING,
    priority: TaskPriority.MEDIUM,
    tags: [],
  });
  const [newTag, setNewTag] = useState<string>('');

  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    fetchTasks();
  }, []);

  /**
   * Fetch tasks from the API
   */
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await listTasks({ limit: 100 });
      
      if (response.success && response.data) {
        setTasks(response.data.tasks || []);
      } else {
        throw new Error(response.message || 'Failed to fetch tasks');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch tasks. The API may not be available.');
      toast({
        title: 'Error',
        description: 'Failed to fetch tasks. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Filter tasks by status
   */
  const getFilteredTasks = (status?: TaskStatus) => {
    if (!status) return tasks;
    return tasks.filter(task => task.status === status);
  };

  /**
   * Get task count by status
   */
  const getTaskCount = (status: TaskStatus) => {
    return tasks.filter(task => task.status === status).length;
  };

  /**
   * Open modal for creating new task
   */
  const handleCreateTask = () => {
    setFormData({
      title: '',
      description: '',
      status: TaskStatus.PENDING,
      priority: TaskPriority.MEDIUM,
      tags: [],
    });
    setSelectedTask(null);
    setIsEditing(false);
    onOpen();
  };

  /**
   * Open modal for editing existing task
   */
  const handleEditTask = (task: Task) => {
    setFormData({
      id: task.id,
      title: task.title,
      description: task.description || '',
      status: task.status,
      priority: task.priority,
      due_date: task.due_date,
      tags: task.tags || [],
    });
    setSelectedTask(task);
    setIsEditing(true);
    onOpen();
  };

  /**
   * Save task (create or update)
   */
  const handleSaveTask = async () => {
    if (!formData.title.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Title is required.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      if (isEditing && selectedTask) {
        const updateData: TaskUpdate = {
          title: formData.title,
          description: formData.description,
          status: formData.status,
          priority: formData.priority,
          due_date: formData.due_date,
          tags: formData.tags,
        };
        await updateTask(selectedTask.id, updateData);
        toast({
          title: 'Success',
          description: 'Task updated successfully.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        await createTask(formData);
        toast({
          title: 'Success',
          description: 'Task created successfully.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
      
      onClose();
      fetchTasks();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: `Failed to ${isEditing ? 'update' : 'create'} task. Please try again.`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  /**
   * Delete task
   */
  const handleDeleteTask = async (taskId: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await deleteTask(taskId);
      toast({
        title: 'Success',
        description: 'Task deleted successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      fetchTasks();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to delete task. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  /**
   * Quick status update
   */
  const handleStatusUpdate = async (taskId: string, newStatus: TaskStatus) => {
    try {
      await updateTask(taskId, { status: newStatus });
      toast({
        title: 'Success',
        description: 'Task status updated.',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      fetchTasks();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to update task status.',
        status: 'error',
        duration: 3000,
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

  /**
   * Get priority color
   */
  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT: return 'red';
      case TaskPriority.HIGH: return 'orange';
      case TaskPriority.MEDIUM: return 'yellow';
      case TaskPriority.LOW: return 'green';
      default: return 'gray';
    }
  };

  /**
   * Get status color
   */
  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED: return 'green';
      case TaskStatus.IN_PROGRESS: return 'blue';
      case TaskStatus.ON_HOLD: return 'orange';
      case TaskStatus.CANCELLED: return 'red';
      case TaskStatus.PENDING: return 'gray';
      default: return 'gray';
    }
  };

  /**
   * Component to display task source badge
   */
  const TaskSourceBadge: React.FC<{ source?: string; confidence?: number }> = ({ source, confidence }) => {
    if (!source) return null;
    
    const colorScheme = source === 'conversation' ? 'green' : 
                        source === 'manual' ? 'blue' : 
                        source === 'suggestion' ? 'purple' : 'gray';
    
    return (
      <Tooltip label={confidence ? `${Math.round(confidence * 100)}% confidence` : undefined}>
        <Badge colorScheme={colorScheme} fontSize="xs">
          {source === 'conversation' ? '🤖 AI Extracted' : source}
        </Badge>
      </Tooltip>
    );
  };

  /**
   * Render task card
   */
  const renderTaskCard = (task: Task) => (
    <Card key={task.id} size="sm">
      <CardHeader pb={2}>
        <Flex justify="space-between" align="flex-start">
          <VStack align="stretch" spacing={1} flex={1}>
            <HStack justify="space-between">
              <Heading size="sm">{task.title}</Heading>
              <TaskSourceBadge 
                source={task.metadata?.source} 
                confidence={task.metadata?.extraction_confidence}
              />
            </HStack>
            <HStack spacing={2}>
              <Badge colorScheme={getStatusColor(task.status)} variant="subtle">
                {task.status.replace('_', ' ').toUpperCase()}
              </Badge>
              <Badge colorScheme={getPriorityColor(task.priority)} variant="outline">
                {task.priority.toUpperCase()}
              </Badge>
              {task.metadata?.is_recurring && (
                <Badge colorScheme="purple" variant="outline" fontSize="xs">
                  🔄 {task.metadata.recurrence_pattern}
                </Badge>
              )}
            </HStack>
          </VStack>
          <HStack spacing={1}>
            {task.status !== TaskStatus.COMPLETED && (
              <Tooltip label="Mark as completed">
                <IconButton
                  aria-label="Complete task"
                  icon={<CheckIcon />}
                  size="xs"
                  variant="outline"
                  colorScheme="green"
                  onClick={() => handleStatusUpdate(task.id, TaskStatus.COMPLETED)}
                />
              </Tooltip>
            )}
            <Tooltip label="Edit task">
              <IconButton
                aria-label="Edit task"
                icon={<EditIcon />}
                size="xs"
                variant="outline"
                onClick={() => handleEditTask(task)}
              />
            </Tooltip>
            <Tooltip label="Delete task">
              <IconButton
                aria-label="Delete task"
                icon={<DeleteIcon />}
                size="xs"
                variant="outline"
                colorScheme="red"
                onClick={() => handleDeleteTask(task.id)}
              />
            </Tooltip>
          </HStack>
        </Flex>
      </CardHeader>
      <CardBody pt={0}>
        {task.description && (
          <Text fontSize="sm" color="gray.600" noOfLines={2} mb={2}>
            {task.description}
          </Text>
        )}
        {task.tags && task.tags.length > 0 && (
          <Wrap mb={2}>
            {task.tags.map((tag) => (
              <WrapItem key={tag}>
                <Badge size="sm" colorScheme="blue" variant="subtle">
                  {tag}
                </Badge>
              </WrapItem>
            ))}
          </Wrap>
        )}
        
        {/* Display linked memories */}
        {task.metadata?.linked_memories && task.metadata.linked_memories.length > 0 && (
          <Box mb={2}>
            <HStack spacing={1} mb={1}>
              <InfoIcon boxSize={3} color="gray.500" />
              <Text fontSize="xs" color="gray.500">Linked memories:</Text>
            </HStack>
            <VStack align="stretch" spacing={1} pl={4}>
              {task.metadata.linked_memories.slice(0, 2).map((memory, idx) => (
                <Text key={idx} fontSize="xs" color="gray.600" noOfLines={1}>
                  • {memory.title} ({Math.round(memory.relevance * 100)}% relevant)
                </Text>
              ))}
              {task.metadata.linked_memories.length > 2 && (
                <Text fontSize="xs" color="gray.500">
                  +{task.metadata.linked_memories.length - 2} more
                </Text>
              )}
            </VStack>
          </Box>
        )}
        
        <Text fontSize="xs" color="gray.500">
          Created: {new Date(task.created_at).toLocaleDateString()}
          {task.due_date && (
            <> • Due: {new Date(task.due_date).toLocaleDateString()}</>
          )}
        </Text>
      </CardBody>
    </Card>
  );

  if (loading && tasks.length === 0) {
    return (
      <Container maxW="container.xl" py={6}>
        <Flex justify="center" align="center" minH="200px">
          <VStack spacing={4}>
            <Spinner size="xl" />
            <Text>Loading tasks...</Text>
          </VStack>
        </Flex>
      </Container>
    );
  }

  if (error && tasks.length === 0) {
    return (
      <Container maxW="container.xl" py={6}>
        <Alert status="error">
          <AlertIcon />
          <Box>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
        <Button mt={4} onClick={fetchTasks}>
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <Heading size="lg">Tasks</Heading>
          <Button leftIcon={<AddIcon />} colorScheme="blue" onClick={handleCreateTask}>
            New Task
          </Button>
        </Flex>

        {/* AI Intelligence Panel */}
        <TaskIntelligencePanel onTaskCreated={fetchTasks} />

        {/* Task Statistics */}
        <SimpleGrid columns={{ base: 2, md: 5 }} spacing={4}>
          <Card size="sm">
            <CardBody textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="gray.600">
                {getTaskCount(TaskStatus.PENDING)}
              </Text>
              <Text fontSize="sm" color="gray.500">Pending</Text>
            </CardBody>
          </Card>
          <Card size="sm">
            <CardBody textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                {getTaskCount(TaskStatus.IN_PROGRESS)}
              </Text>
              <Text fontSize="sm" color="gray.500">In Progress</Text>
            </CardBody>
          </Card>
          <Card size="sm">
            <CardBody textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="green.500">
                {getTaskCount(TaskStatus.COMPLETED)}
              </Text>
              <Text fontSize="sm" color="gray.500">Completed</Text>
            </CardBody>
          </Card>
          <Card size="sm">
            <CardBody textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                {getTaskCount(TaskStatus.ON_HOLD)}
              </Text>
              <Text fontSize="sm" color="gray.500">On Hold</Text>
            </CardBody>
          </Card>
          <Card size="sm">
            <CardBody textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="red.500">
                {getTaskCount(TaskStatus.CANCELLED)}
              </Text>
              <Text fontSize="sm" color="gray.500">Cancelled</Text>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Task Tabs */}
        <Tabs index={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>All Tasks ({tasks.length})</Tab>
            <Tab>Pending ({getTaskCount(TaskStatus.PENDING)})</Tab>
            <Tab>In Progress ({getTaskCount(TaskStatus.IN_PROGRESS)})</Tab>
            <Tab>Completed ({getTaskCount(TaskStatus.COMPLETED)})</Tab>
          </TabList>

          <TabPanels>
            {/* All Tasks */}
            <TabPanel px={0}>
              {tasks.length === 0 ? (
                <Alert status="info">
                  <AlertIcon />
                  <AlertDescription>
                    No tasks found. Click "New Task" to create your first task.
                  </AlertDescription>
                </Alert>
              ) : (
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {tasks.map(renderTaskCard)}
                </SimpleGrid>
              )}
            </TabPanel>

            {/* Pending Tasks */}
            <TabPanel px={0}>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                {getFilteredTasks(TaskStatus.PENDING).map(renderTaskCard)}
              </SimpleGrid>
            </TabPanel>

            {/* In Progress Tasks */}
            <TabPanel px={0}>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                {getFilteredTasks(TaskStatus.IN_PROGRESS).map(renderTaskCard)}
              </SimpleGrid>
            </TabPanel>

            {/* Completed Tasks */}
            <TabPanel px={0}>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                {getFilteredTasks(TaskStatus.COMPLETED).map(renderTaskCard)}
              </SimpleGrid>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>

      {/* Create/Edit Task Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isEditing ? 'Edit Task' : 'Create New Task'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Title</FormLabel>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter task title..."
                />
              </FormControl>
              
              <FormControl>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Enter task description..."
                  rows={4}
                />
              </FormControl>

              <HStack spacing={4} width="100%">
                <FormControl>
                  <FormLabel>Status</FormLabel>
                  <Select
                    value={formData.status}
                    onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as TaskStatus }))}
                  >
                    {Object.values(TaskStatus).map(status => (
                      <option key={status} value={status}>
                        {status.replace('_', ' ').toUpperCase()}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Priority</FormLabel>
                  <Select
                    value={formData.priority}
                    onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as TaskPriority }))}
                  >
                    {Object.values(TaskPriority).map(priority => (
                      <option key={priority} value={priority}>
                        {priority.toUpperCase()}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </HStack>

              <FormControl>
                <FormLabel>Due Date</FormLabel>
                <Input
                  type="datetime-local"
                  value={formData.due_date}
                  onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
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
            <Button colorScheme="blue" onClick={handleSaveTask}>
              {isEditing ? 'Update' : 'Create'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default Tasks;
