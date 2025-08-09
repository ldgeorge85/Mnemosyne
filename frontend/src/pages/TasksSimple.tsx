/**
 * Simple Tasks Page Component
 * Works without backend API for development
 */
import React, { useState } from 'react';
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
  Checkbox,
  Button,
  Input,
  Badge,
  Flex,
  IconButton,
  useColorMode,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Progress
} from '@chakra-ui/react';
import { FiPlus, FiMoon, FiSun, FiCalendar, FiClock, FiCheck, FiX } from 'react-icons/fi';

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
}

const TasksSimple: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Complete authentication system',
      description: 'Implement W3C DID and OAuth providers',
      status: 'in-progress',
      priority: 'high',
      dueDate: '2024-01-15'
    },
    {
      id: '2',
      title: 'Set up vector database',
      description: 'Configure Qdrant for memory embeddings',
      status: 'pending',
      priority: 'high',
      dueDate: '2024-01-16'
    },
    {
      id: '3',
      title: 'Create memory pipeline',
      description: 'Build async processing pipeline for memories',
      status: 'pending',
      priority: 'medium'
    },
    {
      id: '4',
      title: 'Deploy Docker containers',
      description: 'Set up Docker Compose for all services',
      status: 'completed',
      priority: 'high'
    }
  ]);

  const toggleTaskStatus = (taskId: string) => {
    setTasks(tasks.map(task => {
      if (task.id === taskId) {
        if (task.status === 'pending') return { ...task, status: 'in-progress' };
        if (task.status === 'in-progress') return { ...task, status: 'completed' };
        return { ...task, status: 'pending' };
      }
      return task;
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'in-progress': return 'blue';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'yellow';
      default: return 'green';
    }
  };

  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const inProgressTasks = tasks.filter(t => t.status === 'in-progress');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  const completionRate = Math.round((completedTasks.length / tasks.length) * 100);

  return (
    <Container maxW="container.xl" py={8}>
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Heading>Tasks</Heading>
        <HStack spacing={2}>
          <Button colorScheme="blue" leftIcon={<FiPlus />}>
            New Task
          </Button>
          <IconButton
            aria-label="Toggle dark mode"
            icon={colorMode === 'dark' ? <FiSun /> : <FiMoon />}
            onClick={toggleColorMode}
          />
        </HStack>
      </Flex>

      {/* Statistics */}
      <Card mb={6}>
        <CardBody>
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.500">Total Tasks</Text>
              <Text fontSize="2xl" fontWeight="bold">{tasks.length}</Text>
            </VStack>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.500">In Progress</Text>
              <Text fontSize="2xl" fontWeight="bold" color="blue.500">{inProgressTasks.length}</Text>
            </VStack>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.500">Completed</Text>
              <Text fontSize="2xl" fontWeight="bold" color="green.500">{completedTasks.length}</Text>
            </VStack>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" color="gray.500">Completion Rate</Text>
              <Text fontSize="2xl" fontWeight="bold">{completionRate}%</Text>
            </VStack>
          </HStack>
          <Progress value={completionRate} colorScheme="green" borderRadius="full" />
        </CardBody>
      </Card>

      {/* Tasks Tabs */}
      <Tabs variant="enclosed">
        <TabList>
          <Tab>All Tasks ({tasks.length})</Tab>
          <Tab>Pending ({pendingTasks.length})</Tab>
          <Tab>In Progress ({inProgressTasks.length})</Tab>
          <Tab>Completed ({completedTasks.length})</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <VStack spacing={4} align="stretch">
              {tasks.map(task => (
                <TaskCard key={task.id} task={task} onToggle={toggleTaskStatus} />
              ))}
            </VStack>
          </TabPanel>
          <TabPanel>
            <VStack spacing={4} align="stretch">
              {pendingTasks.map(task => (
                <TaskCard key={task.id} task={task} onToggle={toggleTaskStatus} />
              ))}
            </VStack>
          </TabPanel>
          <TabPanel>
            <VStack spacing={4} align="stretch">
              {inProgressTasks.map(task => (
                <TaskCard key={task.id} task={task} onToggle={toggleTaskStatus} />
              ))}
            </VStack>
          </TabPanel>
          <TabPanel>
            <VStack spacing={4} align="stretch">
              {completedTasks.map(task => (
                <TaskCard key={task.id} task={task} onToggle={toggleTaskStatus} />
              ))}
            </VStack>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  );
};

const TaskCard: React.FC<{ task: Task; onToggle: (id: string) => void }> = ({ task, onToggle }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'in-progress': return 'blue';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'yellow';
      default: return 'green';
    }
  };

  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" align="start">
          <HStack align="start" spacing={4}>
            <Checkbox
              isChecked={task.status === 'completed'}
              onChange={() => onToggle(task.id)}
              size="lg"
              colorScheme="green"
            />
            <VStack align="start" spacing={2}>
              <Text
                fontWeight="medium"
                textDecoration={task.status === 'completed' ? 'line-through' : 'none'}
                opacity={task.status === 'completed' ? 0.6 : 1}
              >
                {task.title}
              </Text>
              <Text fontSize="sm" color="gray.600">
                {task.description}
              </Text>
              <HStack spacing={2}>
                <Badge colorScheme={getStatusColor(task.status)}>
                  {task.status}
                </Badge>
                <Badge colorScheme={getPriorityColor(task.priority)}>
                  {task.priority} priority
                </Badge>
                {task.dueDate && (
                  <Badge colorScheme="purple" variant="outline">
                    <FiCalendar style={{ marginRight: '4px' }} />
                    {task.dueDate}
                  </Badge>
                )}
              </HStack>
            </VStack>
          </HStack>
          <HStack>
            <IconButton
              aria-label="Mark complete"
              icon={<FiCheck />}
              size="sm"
              variant="ghost"
              colorScheme="green"
              onClick={() => onToggle(task.id)}
            />
          </HStack>
        </HStack>
      </CardBody>
    </Card>
  );
};

export default TasksSimple;