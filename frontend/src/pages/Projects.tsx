import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Button,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Progress,
  IconButton,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Menu,
  MenuButton,
  MenuList,
  MenuItem
} from '@chakra-ui/react';
import { AddIcon, SettingsIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';
import { listProjects, deleteProject } from '../api/projects';

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'on-hold' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  progress: number;
  start_date: string;
  due_date?: string;
  team_members: string[];
  tasks_count: number;
  completed_tasks: number;
  created_at: string;
}

/**
 * Projects page component
 * 
 * Displays user's projects with status tracking and management
 */
const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  

// Fetch from API
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const response = await listProjects();
        if (response.success) {
          setProjects(response.data);
          return;
        }
        throw new Error('Failed to fetch projects');
        /* Legacy mock data kept for docs
        const mockProjects: Project[] = [
          {
            id: '1',
            name: 'Mnemosyne AI Assistant',
            description: 'AI-powered task management and memory system with agent orchestration',
            status: 'active',
            priority: 'high',
            progress: 97,
            start_date: '2025-06-01',
            due_date: '2025-06-30',
            team_members: ['Alice', 'Bob', 'Charlie'],
            tasks_count: 25,
            completed_tasks: 24,
            created_at: '2025-06-01T10:00:00Z'
          },
          {
            id: '2',
            name: 'Mobile App Development',
            description: 'React Native mobile application for iOS and Android',
            status: 'planning',
            priority: 'medium',
            progress: 15,
            start_date: '2025-07-01',
            due_date: '2025-09-30',
            team_members: ['David', 'Eve'],
            tasks_count: 12,
            completed_tasks: 2,
            created_at: '2025-06-10T14:30:00Z'
          },
          {
            id: '3',
            name: 'API Documentation',
            description: 'Comprehensive API documentation and developer guides',
            status: 'completed',
            priority: 'low',
            progress: 100,
            start_date: '2025-05-15',
            due_date: '2025-06-15',
            team_members: ['Frank'],
            tasks_count: 8,
            completed_tasks: 8,
            created_at: '2025-05-15T09:00:00Z'
          },
          {
            id: '4',
            name: 'Performance Optimization',
            description: 'Backend performance improvements and database optimization',
            status: 'on-hold',
            priority: 'medium',
            progress: 45,
            start_date: '2025-06-05',
            team_members: ['Grace', 'Henry'],
            tasks_count: 15,
            completed_tasks: 7,
            created_at: '2025-06-05T11:15:00Z'
          }
        ];
        
        */
      } catch (err) {
        setError('Failed to load projects');
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green';
      case 'completed': return 'blue';
      case 'on-hold': return 'yellow';
      case 'cancelled': return 'red';
      case 'planning': return 'purple';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      case 'low': return 'green';
      default: return 'gray';
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      const response = await deleteProject(projectId);
      if (response.success && response.data.success) {
        setProjects(prev => prev.filter((project: Project) => project.id !== projectId));
      } else {
        throw new Error('Failed to delete');
      }
      toast({
        title: 'Project deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Failed to delete project',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading projects...</Text>
        </VStack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="6xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between" align="center">
          <Heading size="lg">Projects</Heading>
          <Button leftIcon={<AddIcon />} colorScheme="blue" size="sm">
            New Project
          </Button>
        </HStack>

        {projects.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text fontSize="lg" color="gray.500" mb={4}>
              No projects found.
            </Text>
            <Button leftIcon={<AddIcon />} colorScheme="blue">
              Create Your First Project
            </Button>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {projects.map((project) => (
              <Card key={project.id} variant="outline">
                <CardHeader pb={2}>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex={1}>
                      <Heading size="sm" noOfLines={2}>
                        {project.name}
                      </Heading>
                      <HStack>
                        <Badge colorScheme={getStatusColor(project.status)} variant="subtle">
                          {project.status}
                        </Badge>
                        <Badge colorScheme={getPriorityColor(project.priority)} variant="outline">
                          {project.priority}
                        </Badge>
                      </HStack>
                    </VStack>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        aria-label="Project options"
                        icon={<SettingsIcon />}
                        variant="ghost"
                        size="sm"
                      />
                      <MenuList>
                        <MenuItem icon={<EditIcon />}>Edit Project</MenuItem>
                        <MenuItem 
                          icon={<DeleteIcon />} 
                          color="red.500"
                          onClick={() => handleDeleteProject(project.id)}
                        >
                          Delete Project
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack align="stretch" spacing={4}>
                    <Text fontSize="sm" color="gray.600" noOfLines={3}>
                      {project.description}
                    </Text>
                    
                    <Box>
                      <HStack justify="space-between" mb={2}>
                        <Text fontSize="sm" fontWeight="medium">Progress</Text>
                        <Text fontSize="sm" color="gray.600">
                          {project.progress}%
                        </Text>
                      </HStack>
                      <Progress 
                        value={project.progress} 
                        colorScheme={project.progress === 100 ? 'green' : 'blue'}
                        size="sm"
                        borderRadius="md"
                      />
                    </Box>

                    <HStack justify="space-between" fontSize="sm">
                      <VStack align="start" spacing={0}>
                        <Text color="gray.500">Tasks</Text>
                        <Text fontWeight="medium">
                          {project.completed_tasks}/{project.tasks_count}
                        </Text>
                      </VStack>
                      <VStack align="end" spacing={0}>
                        <Text color="gray.500">Team</Text>
                        <Text fontWeight="medium">
                          {project.team_members.length} members
                        </Text>
                      </VStack>
                    </HStack>

                    {project.due_date && (
                      <Box>
                        <Text fontSize="xs" color="gray.500">
                          Due: {new Date(project.due_date).toLocaleDateString()}
                        </Text>
                      </Box>
                    )}
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Container>
  );
};

export default Projects;
