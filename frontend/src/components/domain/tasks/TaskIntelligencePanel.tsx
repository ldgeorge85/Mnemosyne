import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Badge,
  Button,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Divider,
  Tooltip,
  IconButton,
  useToast,
  Flex,
  Progress,
} from '@chakra-ui/react';
// import { 
//   BellIcon, 
//   CalendarIcon, 
//   StarIcon, 
//   RefreshCwIcon,
//   CheckCircleIcon,
//   ClockIcon,
//   AlertTriangleIcon,
//   AddIcon,
// } from 'lucide-react';
import { BellIcon, CalendarIcon, StarIcon, RepeatIcon as RefreshCwIcon, AddIcon } from '@chakra-ui/icons';
const CheckCircleIcon = () => <span>✅</span>;
const ClockIcon = () => <span>🕐</span>;
const AlertTriangleIcon = () => <span>⚠️</span>;
import {
  getUpcomingReminders,
  getDailySummary,
  getTaskSuggestions,
  createTask,
  type TaskReminder,
  type DailySummary,
  type TaskSuggestion,
  type TaskCreate,
  TaskStatus,
  TaskPriority,
} from '../../../api/tasks';

interface TaskIntelligencePanelProps {
  onTaskCreated?: () => void;
}

/**
 * Task Intelligence Panel
 * Displays AI-powered task insights, reminders, and suggestions
 */
export const TaskIntelligencePanel: React.FC<TaskIntelligencePanelProps> = ({ onTaskCreated }) => {
  const [loading, setLoading] = useState(false);
  const [reminders, setReminders] = useState<TaskReminder[]>([]);
  const [dailySummary, setDailySummary] = useState<DailySummary | null>(null);
  const [suggestions, setSuggestions] = useState<TaskSuggestion[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const toast = useToast();

  useEffect(() => {
    fetchIntelligenceData();
  }, []);

  const fetchIntelligenceData = async () => {
    setLoading(true);
    try {
      // Fetch all data in parallel
      const [remindersRes, summaryRes, suggestionsRes] = await Promise.all([
        getUpcomingReminders(24),
        getDailySummary(true),
        getTaskSuggestions(true),
      ]);

      if (remindersRes.success && remindersRes.data) {
        setReminders(remindersRes.data);
      }
      if (summaryRes.success && summaryRes.data) {
        setDailySummary(summaryRes.data);
      }
      if (suggestionsRes.success && suggestionsRes.data) {
        setSuggestions(suggestionsRes.data);
      }
    } catch (error) {
      console.error('Failed to fetch task intelligence:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSuggestedTask = async (suggestion: TaskSuggestion) => {
    try {
      const taskData: TaskCreate = {
        title: suggestion.title,
        description: suggestion.description,
        priority: suggestion.priority,
        due_date: suggestion.suggested_due_date,
        metadata: {
          source: 'suggestion',
          suggestion_type: suggestion.type,
          confidence: suggestion.confidence,
        },
      };

      const response = await createTask(taskData);
      if (response.success) {
        toast({
          title: 'Task created',
          description: `"${suggestion.title}" has been added to your tasks.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        // Refresh data and notify parent
        fetchIntelligenceData();
        onTaskCreated?.();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create task from suggestion.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const getReminderIcon = (type: string) => {
    switch (type) {
      case 'urgent':
        return <AlertTriangleIcon size={16} />;
      case 'soon':
        return <ClockIcon size={16} />;
      case 'today':
        return <CalendarIcon size={16} />;
      default:
        return <BellIcon size={16} />;
    }
  };

  const getReminderColor = (type: string) => {
    switch (type) {
      case 'urgent':
        return 'red';
      case 'soon':
        return 'orange';
      case 'today':
        return 'blue';
      default:
        return 'gray';
    }
  };

  if (loading && !dailySummary) {
    return (
      <Card>
        <CardBody>
          <Flex justify="center" align="center" minH="200px">
            <Spinner />
          </Flex>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">Task Intelligence</Heading>
          <IconButton
            aria-label="Refresh"
            icon={<RefreshCwIcon size={16} />}
            size="sm"
            variant="ghost"
            onClick={fetchIntelligenceData}
            isLoading={loading}
          />
        </HStack>
      </CardHeader>
      <CardBody>
        <Tabs index={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>Daily Summary</Tab>
            <Tab>
              Reminders
              {reminders.length > 0 && (
                <Badge ml={2} colorScheme="red" variant="solid">
                  {reminders.length}
                </Badge>
              )}
            </Tab>
            <Tab>Suggestions</Tab>
          </TabList>

          <TabPanels>
            {/* Daily Summary Tab */}
            <TabPanel>
              {dailySummary ? (
                <VStack spacing={4} align="stretch">
                  {/* Statistics */}
                  <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                    <Stat>
                      <StatLabel>Today's Tasks</StatLabel>
                      <StatNumber>{dailySummary.tasks_today}</StatNumber>
                      <StatHelpText>
                        {dailySummary.today_breakdown.high_priority} high priority
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Completed (24h)</StatLabel>
                      <StatNumber>{dailySummary.tasks_completed_24h}</StatNumber>
                      <StatHelpText>
                        <CheckCircleIcon size={12} /> Keep it up!
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Overdue</StatLabel>
                      <StatNumber color={dailySummary.tasks_overdue > 0 ? 'red.500' : 'green.500'}>
                        {dailySummary.tasks_overdue}
                      </StatNumber>
                      <StatHelpText>
                        {dailySummary.tasks_overdue > 0 ? 'Need attention' : 'All on track'}
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Progress</StatLabel>
                      <StatNumber>
                        {dailySummary.tasks_today > 0 
                          ? Math.round((dailySummary.tasks_completed_24h / (dailySummary.tasks_today + dailySummary.tasks_completed_24h)) * 100)
                          : 0}%
                      </StatNumber>
                      <Progress 
                        value={dailySummary.tasks_today > 0 
                          ? (dailySummary.tasks_completed_24h / (dailySummary.tasks_today + dailySummary.tasks_completed_24h)) * 100
                          : 0} 
                        size="xs" 
                        colorScheme="green"
                        mt={2}
                      />
                    </Stat>
                  </SimpleGrid>

                  <Divider />

                  {/* Today's Tasks */}
                  {dailySummary.tasks.today.length > 0 && (
                    <Box>
                      <Heading size="sm" mb={2}>Today's Tasks</Heading>
                      <VStack spacing={2} align="stretch">
                        {dailySummary.tasks.today.map((task) => (
                          <HStack key={task.id} justify="space-between" p={2} bg="gray.50" borderRadius="md">
                            <Text fontSize="sm">{task.title}</Text>
                            <HStack spacing={2}>
                              {task.due_time && (
                                <Badge size="sm" colorScheme="blue">
                                  {task.due_time}
                                </Badge>
                              )}
                              <Badge size="sm" colorScheme={getPriorityColor(task.priority)}>
                                {task.priority}
                              </Badge>
                            </HStack>
                          </HStack>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  {/* Overdue Tasks */}
                  {dailySummary.tasks.overdue.length > 0 && (
                    <Box>
                      <Heading size="sm" mb={2} color="red.500">Overdue Tasks</Heading>
                      <VStack spacing={2} align="stretch">
                        {dailySummary.tasks.overdue.map((task) => (
                          <HStack key={task.id} justify="space-between" p={2} bg="red.50" borderRadius="md">
                            <Text fontSize="sm">{task.title}</Text>
                            <Badge size="sm" colorScheme="red">
                              {task.days_overdue} day{task.days_overdue !== 1 ? 's' : ''} overdue
                            </Badge>
                          </HStack>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  {/* Insights */}
                  {dailySummary.insights && (
                    <>
                      <Divider />
                      <Box>
                        <Heading size="sm" mb={2}>AI Insights</Heading>
                        {dailySummary.insights.patterns.length > 0 && (
                          <VStack spacing={1} align="stretch" mb={2}>
                            {dailySummary.insights.patterns.map((pattern, idx) => (
                              <Text key={idx} fontSize="sm" color="gray.600">
                                • {pattern}
                              </Text>
                            ))}
                          </VStack>
                        )}
                        {dailySummary.insights.suggestions.length > 0 && (
                          <VStack spacing={1} align="stretch">
                            {dailySummary.insights.suggestions.map((suggestion, idx) => (
                              <Text key={idx} fontSize="sm" color="blue.600">
                                💡 {suggestion}
                              </Text>
                            ))}
                          </VStack>
                        )}
                      </Box>
                    </>
                  )}
                </VStack>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  <AlertDescription>No summary data available.</AlertDescription>
                </Alert>
              )}
            </TabPanel>

            {/* Reminders Tab */}
            <TabPanel>
              {reminders.length > 0 ? (
                <VStack spacing={3} align="stretch">
                  {reminders.map((reminder) => (
                    <Card key={reminder.task_id} size="sm" borderColor={getReminderColor(reminder.reminder_type)} borderWidth={1}>
                      <CardBody>
                        <HStack spacing={3} align="flex-start">
                          <Box color={`${getReminderColor(reminder.reminder_type)}.500`}>
                            {getReminderIcon(reminder.reminder_type)}
                          </Box>
                          <VStack align="stretch" spacing={1} flex={1}>
                            <Text fontWeight="medium">{reminder.title}</Text>
                            {reminder.description && (
                              <Text fontSize="sm" color="gray.600">{reminder.description}</Text>
                            )}
                            <HStack spacing={2}>
                              <Badge colorScheme={getReminderColor(reminder.reminder_type)} size="sm">
                                {reminder.hours_until_due < 1 
                                  ? `${Math.round(reminder.hours_until_due * 60)} minutes`
                                  : `${Math.round(reminder.hours_until_due)} hours`
                                } until due
                              </Badge>
                              <Badge colorScheme={getPriorityColor(reminder.priority)} size="sm">
                                {reminder.priority}
                              </Badge>
                            </HStack>
                            {reminder.context && reminder.context.length > 0 && (
                              <Box mt={2}>
                                <Text fontSize="xs" color="gray.500" mb={1}>Related memories:</Text>
                                <VStack spacing={1} align="stretch">
                                  {reminder.context.map((memory) => (
                                    <Text key={memory.memory_id} fontSize="xs" color="gray.600">
                                      • {memory.title}
                                    </Text>
                                  ))}
                                </VStack>
                              </Box>
                            )}
                          </VStack>
                        </HStack>
                      </CardBody>
                    </Card>
                  ))}
                </VStack>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  <AlertDescription>No upcoming reminders in the next 24 hours.</AlertDescription>
                </Alert>
              )}
            </TabPanel>

            {/* Suggestions Tab */}
            <TabPanel>
              {suggestions.length > 0 ? (
                <VStack spacing={3} align="stretch">
                  {suggestions.map((suggestion, idx) => (
                    <Card key={idx} size="sm">
                      <CardBody>
                        <VStack align="stretch" spacing={2}>
                          <HStack justify="space-between" align="flex-start">
                            <VStack align="stretch" spacing={1} flex={1}>
                              <Text fontWeight="medium">{suggestion.title}</Text>
                              <Text fontSize="sm" color="gray.600">{suggestion.description}</Text>
                              <HStack spacing={2}>
                                <Badge colorScheme={getTypeColor(suggestion.type)} size="sm">
                                  {suggestion.type.replace('_', ' ')}
                                </Badge>
                                <Badge colorScheme="purple" size="sm">
                                  {Math.round(suggestion.confidence * 100)}% confident
                                </Badge>
                              </HStack>
                              <Text fontSize="xs" color="gray.500">{suggestion.reason}</Text>
                            </VStack>
                            <Tooltip label="Create this task">
                              <IconButton
                                aria-label="Create task"
                                icon={<AddIcon />}
                                size="sm"
                                colorScheme="blue"
                                onClick={() => handleCreateSuggestedTask(suggestion)}
                              />
                            </Tooltip>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </VStack>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  <AlertDescription>No task suggestions available. Keep using the system to get personalized suggestions!</AlertDescription>
                </Alert>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>
      </CardBody>
    </Card>
  );
};

// Helper functions
const getPriorityColor = (priority: TaskPriority) => {
  switch (priority) {
    case TaskPriority.URGENT: return 'red';
    case TaskPriority.HIGH: return 'orange';
    case TaskPriority.MEDIUM: return 'yellow';
    case TaskPriority.LOW: return 'green';
    default: return 'gray';
  }
};

const getTypeColor = (type: string) => {
  switch (type) {
    case 'recurring': return 'blue';
    case 'follow_up': return 'purple';
    case 'memory_based': return 'teal';
    case 'time_based': return 'orange';
    default: return 'gray';
  }
};

export default TaskIntelligencePanel;