/**
 * Dashboard Page Component
 * 
 * Displays an overview of user activity including statistics, recent conversations,
 * memories, tasks, and a timeline of recent activity.
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Card,
  CardHeader,
  CardBody,
  Text,
  VStack,
  Flex,
  Icon,
  Badge,
  Button,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Divider,
  Avatar
} from '@chakra-ui/react';
import { FiMessageCircle, FiDatabase, FiCheckSquare, FiClock } from 'react-icons/fi';
import { 
  getDashboardStats, 
  getRecentConversations, 
  getImportantMemories, 
  getUpcomingTasks, 
  getRecentActivity,
  type DashboardStats,
  type ActivityItem
} from '../api/dashboard';

interface DashboardState {
  stats: DashboardStats | null;
  recentConversations: any[];
  importantMemories: any[];
  upcomingTasks: any[];
  recentActivity: ActivityItem[];
  loading: boolean;
  error: string | null;
}

interface ActivityCardProps {
  title: string;
  icon: React.ElementType;
  color: string;
  items: any[];
  linkTo: string;
  linkText: string;
}

interface TimelineItemProps {
  title: string;
  description: string;
  time: string;
}

const Dashboard: React.FC = () => {
  const [state, setState] = useState<DashboardState>({
    stats: null,
    recentConversations: [],
    importantMemories: [],
    upcomingTasks: [],
    recentActivity: [],
    loading: true,
    error: null
  });

  const toast = useToast();

  const fetchDashboardData = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      // Fetch all dashboard data in parallel
      const [stats, conversations, memories, tasks, activity] = await Promise.all([
        getDashboardStats(),
        getRecentConversations(),
        getImportantMemories(),
        getUpcomingTasks(),
        getRecentActivity()
      ]);

      setState({
        stats,
        recentConversations: conversations,
        importantMemories: memories,
        upcomingTasks: tasks,
        recentActivity: activity,
        loading: false,
        error: null
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load dashboard data';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      
      toast({
        title: 'Error loading dashboard',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRetry = () => {
    fetchDashboardData();
  };

  if (state.loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Flex justify="center" align="center" minH="400px">
          <VStack spacing={4}>
            <Spinner size="xl" color="blue.500" />
            <Text>Loading dashboard...</Text>
          </VStack>
        </Flex>
      </Container>
    );
  }

  if (state.error) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Error loading dashboard!</AlertTitle>
            <AlertDescription>
              {state.error}
              <Button ml={4} size="sm" onClick={handleRetry}>
                Retry
              </Button>
            </AlertDescription>
          </Box>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Dashboard</Heading>
          <Text color="gray.600">Welcome back! Here's what's happening with your AI assistant.</Text>
        </Box>

        {/* Statistics Overview */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Total Conversations</StatLabel>
                <StatNumber>{state.stats?.conversations.total || 0}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  {state.stats?.conversations.percentChange || 0}% recent activity
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Memories Stored</StatLabel>
                <StatNumber>{state.stats?.memories.total || 0}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  {state.stats?.memories.percentChange || 0}% recent activity
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Tasks Completed</StatLabel>
                <StatNumber>{state.stats?.tasks.completed || 0}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  {state.stats?.tasks.percentChange || 0}% completion rate
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Pending Tasks</StatLabel>
                <StatNumber>{state.stats?.tasks.pending || 0}</StatNumber>
                <StatHelpText>
                  <Icon as={FiClock} />
                  Active items
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Activity Cards */}
        <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6}>
          <ActivityCard
            title="Recent Conversations"
            icon={FiMessageCircle}
            color="blue"
            items={state.recentConversations}
            linkTo="/conversations"
            linkText="View all conversations"
          />

          <ActivityCard
            title="Important Memories"
            icon={FiDatabase}
            color="purple"
            items={state.importantMemories}
            linkTo="/memories"
            linkText="View all memories"
          />

          <ActivityCard
            title="Upcoming Tasks"
            icon={FiCheckSquare}
            color="green"
            items={state.upcomingTasks}
            linkTo="/tasks"
            linkText="View all tasks"
          />
        </SimpleGrid>

        {/* Recent Activity Timeline */}
        <Card>
          <CardHeader>
            <Heading size="md">Recent Activity</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {state.recentActivity.length > 0 ? (
                state.recentActivity.map((activity: ActivityItem, index: number) => (
                  <Box key={activity.id}>
                    <TimelineItem
                      title={activity.title}
                      description={activity.description}
                      time={activity.date}
                    />
                    {index < state.recentActivity.length - 1 && <Divider my={2} />}
                  </Box>
                ))
              ) : (
                <Text color="gray.500" textAlign="center" py={4}>
                  No recent activity to display
                </Text>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardBody>
            <Flex justify="center">
              <Button as={Link} to="/chat" colorScheme="blue" size="lg">
                Start New Conversation
              </Button>
            </Flex>
          </CardBody>
        </Card>
      </VStack>
    </Container>
  );
};

const ActivityCard: React.FC<ActivityCardProps> = ({
  title,
  icon,
  color,
  items,
  linkTo,
  linkText
}) => (
  <Card>
    <CardHeader>
      <Flex align="center" gap={2}>
        <Icon as={icon} color={`${color}.500`} />
        <Heading size="sm">{title}</Heading>
      </Flex>
    </CardHeader>
    <CardBody pt={0}>
      <VStack spacing={3} align="stretch">
        {items.length > 0 ? (
          items.map((item: any) => (
            <Box key={item.id} p={2} bg="gray.50" borderRadius="md">
              <Text fontSize="sm" fontWeight="medium" noOfLines={1}>
                {item.title}
              </Text>
              <Text fontSize="xs" color="gray.600">
                {item.date}
              </Text>
            </Box>
          ))
        ) : (
          <Text fontSize="sm" color="gray.500">
            No items to display
          </Text>
        )}
        <Button as={Link} to={linkTo} variant="ghost" size="sm" colorScheme={color}>
          {linkText}
        </Button>
      </VStack>
    </CardBody>
  </Card>
);

const TimelineItem: React.FC<TimelineItemProps> = ({ title, description, time }) => (
  <Flex align="start" gap={3}>
    <Avatar size="sm" bg="blue.500" />
    <Box flex={1}>
      <Text fontWeight="medium" fontSize="sm">
        {title}
      </Text>
      <Text fontSize="sm" color="gray.600" mb={1}>
        {description}
      </Text>
      <Badge colorScheme="gray" fontSize="xs">
        {time}
      </Badge>
    </Box>
  </Flex>
);

export default Dashboard;
