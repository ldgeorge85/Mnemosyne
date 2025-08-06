/**
 * Activity Page Component
 * 
 * Displays comprehensive activity timeline and analytics for the user.
 * Shows recent actions across all features: conversations, memories, tasks, projects, etc.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  Badge,
  Icon,
  Divider,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  useColorModeValue,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useToast
} from '@chakra-ui/react';
import {
  FiActivity,
  FiMessageSquare,
  FiCpu,
  FiCheckSquare,
  FiFolder,
  FiUsers,
  FiBookmark,
  FiRefreshCw
} from 'react-icons/fi';
import { getRecentActivity, type ActivityItem } from '../api/dashboard';

/**
 * Activity statistics interface
 */
interface ActivityStats {
  totalActions: number;
  todayActions: number;
  weekActions: number;
  mostActiveFeature: string;
}

/**
 * Activity page component
 */
const ActivityPage: React.FC = () => {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [stats, setStats] = useState<ActivityStats>({
    totalActions: 0,
    todayActions: 0,
    weekActions: 0,
    mostActiveFeature: 'Chat'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  /**
   * Load activity data from API
   */
  const loadActivityData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Get recent activity (expanded limit for activity page)
      const recentActivity = await getRecentActivity(50);
      setActivities(recentActivity);
      
      // Calculate statistics
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      
      const todayCount = recentActivity.filter(activity => 
        new Date(activity.createdAt) >= today
      ).length;
      
      const weekCount = recentActivity.filter(activity => 
        new Date(activity.createdAt) >= weekAgo
      ).length;
      
      // Count by feature type
      const featureCounts = recentActivity.reduce((acc, activity) => {
        acc[activity.type] = (acc[activity.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      
      const mostActive = Object.entries(featureCounts)
        .sort(([,a], [,b]) => b - a)[0]?.[0] || 'Chat';
      
      setStats({
        totalActions: recentActivity.length,
        todayActions: todayCount,
        weekActions: weekCount,
        mostActiveFeature: mostActive
      });
      
    } catch (err) {
      setError('Failed to load activity data. Please try again.');
      toast({
        title: 'Error loading activity',
        description: 'Failed to load activity data. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Get icon for activity type
   */
  const getActivityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'conversation':
      case 'chat':
        return FiMessageSquare;
      case 'memory':
        return FiCpu;
      case 'task':
        return FiCheckSquare;
      case 'project':
        return FiFolder;
      case 'contact':
        return FiUsers;
      case 'bookmark':
        return FiBookmark;
      default:
        return FiActivity;
    }
  };

  /**
   * Get color scheme for activity type
   */
  const getActivityColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'conversation':
      case 'chat':
        return 'blue';
      case 'memory':
        return 'purple';
      case 'task':
        return 'green';
      case 'project':
        return 'orange';
      case 'contact':
        return 'teal';
      case 'bookmark':
        return 'pink';
      default:
        return 'gray';
    }
  };

  /**
   * Format timestamp for display
   */
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) {
      return 'Just now';
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadActivityData();
  }, []);

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <HStack spacing={4} mb={2}>
            <Icon as={FiActivity} boxSize={8} color="blue.500" />
            <Heading size="lg">Activity Timeline</Heading>
          </HStack>
          <Text color="gray.600">
            Track your interactions and progress across all features
          </Text>
        </Box>

        {/* Statistics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card bg={bgColor} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>Total Actions</StatLabel>
                <StatNumber>{stats.totalActions}</StatNumber>
                <StatHelpText>All time</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card bg={bgColor} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>Today</StatLabel>
                <StatNumber>{stats.todayActions}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  Actions today
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card bg={bgColor} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>This Week</StatLabel>
                <StatNumber>{stats.weekActions}</StatNumber>
                <StatHelpText>Last 7 days</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card bg={bgColor} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>Most Active</StatLabel>
                <StatNumber fontSize="lg">{stats.mostActiveFeature}</StatNumber>
                <StatHelpText>Feature used most</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Activity Timeline */}
        <Card bg={bgColor} borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" mb={6}>
              <Heading size="md">Recent Activity</Heading>
              <Button
                leftIcon={<FiRefreshCw />}
                onClick={loadActivityData}
                isLoading={isLoading}
                size="sm"
                variant="outline"
              >
                Refresh
              </Button>
            </HStack>

            {error && (
              <Alert status="error" mb={4}>
                <AlertIcon />
                {error}
              </Alert>
            )}

            {isLoading ? (
              <Box textAlign="center" py={8}>
                <Spinner size="lg" />
                <Text mt={4} color="gray.600">Loading activity...</Text>
              </Box>
            ) : activities.length === 0 ? (
              <Box textAlign="center" py={8}>
                <Icon as={FiActivity} boxSize={12} color="gray.400" mb={4} />
                <Text color="gray.600">No recent activity found</Text>
                <Text fontSize="sm" color="gray.500" mt={2}>
                  Start using the app to see your activity timeline here
                </Text>
              </Box>
            ) : (
              <VStack spacing={4} align="stretch">
                {activities.map((activity: ActivityItem, index: number) => (
                  <Box key={index}>
                    <HStack spacing={4} align="start">
                      <Box
                        p={2}
                        borderRadius="full"
                        bg={`${getActivityColor(activity.type)}.100`}
                        color={`${getActivityColor(activity.type)}.600`}
                      >
                        <Icon as={getActivityIcon(activity.type)} boxSize={4} />
                      </Box>
                      
                      <Box flex={1}>
                        <HStack justify="space-between" align="start">
                          <VStack align="start" spacing={1}>
                            <Text fontWeight="medium">{activity.title}</Text>
                            <Text fontSize="sm" color="gray.600">
                              {activity.description}
                            </Text>
                            <HStack spacing={2}>
                              <Badge colorScheme={getActivityColor(activity.type)}>
                                {activity.type}
                              </Badge>
                              <Text fontSize="xs" color="gray.500">
                                {formatTimestamp(activity.createdAt)}
                              </Text>
                            </HStack>
                          </VStack>
                        </HStack>
                      </Box>
                    </HStack>
                    
                    {index < activities.length - 1 && <Divider mt={4} />}
                  </Box>
                ))}
              </VStack>
            )}
          </CardBody>
        </Card>
      </VStack>
    </Container>
  );
};

export default ActivityPage;
