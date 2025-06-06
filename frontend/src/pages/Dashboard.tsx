/**
 * Dashboard Page Component
 * 
 * This component renders the main dashboard for the application
 * with an overview of the user's conversations, memories, and tasks.
 */
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  StatGroup,
  Flex,
  Icon,
  useColorModeValue
} from '@chakra-ui/react';
import { FiMessageSquare, FiDatabase, FiCheckSquare, FiClock } from 'react-icons/fi';

/**
 * Dashboard page component that displays overview metrics and recent activity
 */
const Dashboard: React.FC = () => {
  // Background colors for cards
  const cardBg = useColorModeValue('white', 'gray.700');
  
  return (
    <Box>
      <Heading as="h1" size="lg" mb={6}>
        Dashboard
      </Heading>
      
      {/* Stats Overview */}
      <StatGroup 
        mb={8} 
        bg={cardBg} 
        p={4} 
        borderRadius="lg" 
        boxShadow="sm"
      >
        <Stat>
          <StatLabel>Conversations</StatLabel>
          <StatNumber>24</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            23% increase
          </StatHelpText>
        </Stat>
        
        <Stat>
          <StatLabel>Memories</StatLabel>
          <StatNumber>345</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            12% increase
          </StatHelpText>
        </Stat>
        
        <Stat>
          <StatLabel>Tasks</StatLabel>
          <StatNumber>18</StatNumber>
          <StatHelpText>
            <StatArrow type="decrease" />
            9% decrease
          </StatHelpText>
        </Stat>
        
        <Stat>
          <StatLabel>Completed</StatLabel>
          <StatNumber>42</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            28% increase
          </StatHelpText>
        </Stat>
      </StatGroup>
      
      {/* Activity Cards */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} mb={8}>
        <ActivityCard 
          title="Recent Conversations"
          icon={FiMessageSquare}
          color="blue.500"
          items={[
            { id: '1', title: 'Project Kickoff Discussion', date: '2 hours ago' },
            { id: '2', title: 'Weekly Team Sync', date: 'Yesterday' },
            { id: '3', title: 'Client Meeting Notes', date: '3 days ago' }
          ]}
          linkTo="/conversations"
          linkText="View All Conversations"
        />
        
        <ActivityCard 
          title="Important Memories"
          icon={FiDatabase}
          color="purple.500"
          items={[
            { id: '1', title: 'Client contact information', date: '1 day ago' },
            { id: '2', title: 'Project deadline extended', date: '1 week ago' },
            { id: '3', title: 'New team member joining', date: '2 weeks ago' }
          ]}
          linkTo="/memories"
          linkText="View All Memories"
        />
        
        <ActivityCard 
          title="Upcoming Tasks"
          icon={FiCheckSquare}
          color="green.500"
          items={[
            { id: '1', title: 'Submit quarterly report', date: 'Tomorrow' },
            { id: '2', title: 'Team retrospective meeting', date: 'In 2 days' },
            { id: '3', title: 'Review project proposal', date: 'Next week' }
          ]}
          linkTo="/tasks"
          linkText="View All Tasks"
        />
      </SimpleGrid>
      
      {/* Recent Activity Timeline */}
      <Card bg={cardBg}>
        <CardHeader>
          <Heading size="md">
            <Flex align="center">
              <Icon as={FiClock} mr={2} />
              Recent Activity
            </Flex>
          </Heading>
        </CardHeader>
        <CardBody>
          <TimelineItem 
            title="Created a new task"
            description="Submit quarterly report"
            time="2 hours ago"
          />
          <TimelineItem 
            title="Completed a task"
            description="Prepare presentation slides"
            time="Yesterday at 4:30 PM"
          />
          <TimelineItem 
            title="New conversation"
            description="Project Kickoff Discussion"
            time="Yesterday at 2:15 PM"
          />
          <TimelineItem 
            title="Added a memory"
            description="Client contact information"
            time="1 day ago"
            isLast
          />
        </CardBody>
        <CardFooter>
          <Button variant="outline" colorScheme="brand" size="sm">
            View Full Activity Log
          </Button>
        </CardFooter>
      </Card>
    </Box>
  );
};

/**
 * Activity card component for displaying recent items
 */
interface ActivityCardProps {
  title: string;
  icon: React.ComponentType;
  color: string;
  items: Array<{
    id: string;
    title: string;
    date: string;
  }>;
  linkTo: string;
  linkText: string;
}

const ActivityCard: React.FC<ActivityCardProps> = ({ 
  title, 
  icon, 
  color, 
  items, 
  linkTo, 
  linkText 
}) => {
  return (
    <Card>
      <CardHeader pb={0}>
        <Heading size="md">
          <Flex align="center">
            <Icon as={icon} mr={2} color={color} />
            {title}
          </Flex>
        </Heading>
      </CardHeader>
      <CardBody>
        {items.map((item) => (
          <Box key={item.id} mb={3} pb={3} borderBottom="1px solid" borderColor="gray.100">
            <Text fontWeight="medium">{item.title}</Text>
            <Text fontSize="sm" color="gray.500">{item.date}</Text>
          </Box>
        ))}
      </CardBody>
      <CardFooter pt={0}>
        <Button 
          as={RouterLink} 
          to={linkTo} 
          variant="link" 
          colorScheme="brand" 
          size="sm"
        >
          {linkText}
        </Button>
      </CardFooter>
    </Card>
  );
};

/**
 * Timeline item component for the activity feed
 */
interface TimelineItemProps {
  title: string;
  description: string;
  time: string;
  isLast?: boolean;
}

const TimelineItem: React.FC<TimelineItemProps> = ({ 
  title, 
  description, 
  time, 
  isLast = false 
}) => {
  return (
    <Flex mb={isLast ? 0 : 4}>
      <Box
        position="relative"
        mr={4}
      >
        {/* Timeline dot */}
        <Box
          w={3}
          h={3}
          borderRadius="full"
          bg="brand.500"
          mt={1}
        />
        
        {/* Timeline line */}
        {!isLast && (
          <Box
            position="absolute"
            top={3}
            left={1}
            bottom={-12}
            width="1px"
            bg="gray.200"
          />
        )}
      </Box>
      
      <Box flex={1}>
        <Text fontWeight="medium">{title}</Text>
        <Text color="gray.600" fontSize="sm">{description}</Text>
        <Text color="gray.400" fontSize="xs">{time}</Text>
      </Box>
    </Flex>
  );
};

export default Dashboard;
