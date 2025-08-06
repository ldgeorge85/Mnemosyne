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
  Badge,
  IconButton,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { ChevronLeftIcon, ChevronRightIcon, AddIcon } from '@chakra-ui/icons';
import { listTasks, Task } from '../api/tasks';

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  type: 'task' | 'meeting' | 'reminder' | 'event';
  status: 'pending' | 'completed' | 'cancelled';
}

/**
 * Calendar page component
 * 
 * Displays calendar view with tasks and events
 */
const Calendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const cardBg = useColorModeValue('white', 'gray.700');
  const todayBg = useColorModeValue('blue.50', 'blue.900');
  const selectedBg = useColorModeValue('blue.100', 'blue.800');

  

// Fetch from API
  useEffect(() => {
    const loadEvents = async () => {
      try {
        const response = await listTasks({ limit: 100 });
        if (response.success) {
          const tasks = response.data.tasks ?? response.data; // adapt if response is array
          const apiEvents: CalendarEvent[] = tasks.map((task: Task) => ({
            id: task.id,
            title: task.title,
            date: (task.due_date || task.created_at).split('T')[0],
            time: task.due_date ? task.due_date.split('T')[1]?.slice(0,5) : undefined,
            type: 'task',
            status: task.status as any
          }));
          setEvents(apiEvents);
        } else {
          throw new Error('Failed to fetch tasks');
        }
        /* legacy mock
        const mockEvents: CalendarEvent[] = [
          {
            id: '1',
            title: 'Team Meeting',
            date: '2025-06-17',
            time: '10:00',
            type: 'meeting',
            status: 'pending'
          },
          {
            id: '2',
            title: 'Complete Project Report',
            date: '2025-06-18',
            time: '14:00',
            type: 'task',
            status: 'pending'
          },
          {
            id: '3',
            title: 'Doctor Appointment',
            date: '2025-06-19',
            time: '09:30',
            type: 'event',
            status: 'pending'
          },
          {
            id: '4',
            title: 'Review Code',
            date: '2025-06-17',
            time: '16:00',
            type: 'task',
            status: 'completed'
          }
        ];
        
        */
      } catch (err) {
        setError('Failed to load calendar events');
      } finally {
        setLoading(false);
      }
    };

    loadEvents();
  }, []);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };

  const getEventsForDate = (date: Date) => {
    const dateString = date.toISOString().split('T')[0];
    return events.filter(event => event.date === dateString);
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isSelected = (date: Date) => {
    return selectedDate && date.toDateString() === selectedDate.toDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'cancelled': return 'red';
      default: return 'blue';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'meeting': return 'purple';
      case 'task': return 'blue';
      case 'reminder': return 'orange';
      case 'event': return 'teal';
      default: return 'gray';
    }
  };

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading calendar...</Text>
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

  const days = getDaysInMonth(currentDate);
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between" align="center">
          <Heading size="lg">Calendar</Heading>
          <Button leftIcon={<AddIcon />} colorScheme="blue" size="sm">
            Add Event
          </Button>
        </HStack>

        {/* Calendar Header */}
        <HStack justify="space-between" align="center">
          <IconButton
            aria-label="Previous month"
            icon={<ChevronLeftIcon />}
            onClick={() => navigateMonth('prev')}
            variant="ghost"
          />
          <Heading size="md">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </Heading>
          <IconButton
            aria-label="Next month"
            icon={<ChevronRightIcon />}
            onClick={() => navigateMonth('next')}
            variant="ghost"
          />
        </HStack>

        {/* Calendar Grid */}
        <Box>
          {/* Day headers */}
          <SimpleGrid columns={7} spacing={1} mb={2}>
            {dayNames.map(day => (
              <Box key={day} textAlign="center" fontWeight="bold" py={2}>
                {day}
              </Box>
            ))}
          </SimpleGrid>

          {/* Calendar days */}
          <SimpleGrid columns={7} spacing={1}>
            {days.map((day, index) => (
              <Box
                key={index}
                minH="100px"
                p={2}
                bg={day ? (isToday(day) ? todayBg : isSelected(day) ? selectedBg : cardBg) : 'transparent'}
                borderWidth={day ? 1 : 0}
                borderRadius="md"
                cursor={day ? 'pointer' : 'default'}
                onClick={() => day && setSelectedDate(day)}
                position="relative"
              >
                {day && (
                  <>
                    <Text fontWeight={isToday(day) ? 'bold' : 'normal'} mb={1}>
                      {day.getDate()}
                    </Text>
                    <VStack spacing={1} align="stretch">
                      {getEventsForDate(day).slice(0, 2).map(event => (
                        <Badge
                          key={event.id}
                          colorScheme={getTypeColor(event.type)}
                          variant="subtle"
                          fontSize="xs"
                          noOfLines={1}
                        >
                          {event.time} {event.title}
                        </Badge>
                      ))}
                      {getEventsForDate(day).length > 2 && (
                        <Text fontSize="xs" color="gray.500">
                          +{getEventsForDate(day).length - 2} more
                        </Text>
                      )}
                    </VStack>
                  </>
                )}
              </Box>
            ))}
          </SimpleGrid>
        </Box>

        {/* Selected Date Events */}
        {selectedDate && (
          <Card>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <Heading size="md">
                  Events for {selectedDate.toLocaleDateString()}
                </Heading>
                {getEventsForDate(selectedDate).length === 0 ? (
                  <Text color="gray.500">No events scheduled for this date.</Text>
                ) : (
                  <VStack align="stretch" spacing={2}>
                    {getEventsForDate(selectedDate).map(event => (
                      <HStack key={event.id} justify="space-between" p={3} borderWidth={1} borderRadius="md">
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="bold">{event.title}</Text>
                          <HStack>
                            <Badge colorScheme={getTypeColor(event.type)} variant="subtle">
                              {event.type}
                            </Badge>
                            <Badge colorScheme={getStatusColor(event.status)} variant="outline">
                              {event.status}
                            </Badge>
                          </HStack>
                        </VStack>
                        {event.time && (
                          <Text fontWeight="bold" color="blue.500">
                            {event.time}
                          </Text>
                        )}
                      </HStack>
                    ))}
                  </VStack>
                )}
              </VStack>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Container>
  );
};

export default Calendar;
