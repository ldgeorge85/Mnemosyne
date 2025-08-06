/**
 * Notification Settings Component
 * 
 * This component allows users to configure notification preferences,
 * including email notifications, push notifications, and alerts.
 */
import React from 'react';
import {
  Box,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Switch,
  FormHelperText,
  Select,
  Divider,
  Text,
  Badge,
  Checkbox,
  SimpleGrid,
  useColorModeValue,
  HStack,
  Icon,
} from '@chakra-ui/react';
import { 
  FiBell, 
  FiMail, 
  FiCalendar, 
  FiMessageSquare,
  FiAlertCircle,
  FiBriefcase,
  FiUsers,
} from 'react-icons/fi';

/**
 * Notification settings component
 */
const NotificationSettings: React.FC = () => {
  // State for notification settings
  const [emailEnabled, setEmailEnabled] = React.useState(true);
  const [pushEnabled, setPushEnabled] = React.useState(true);
  const [soundEnabled, setSoundEnabled] = React.useState(true);
  const [frequency, setFrequency] = React.useState('immediate');
  const [doNotDisturb, setDoNotDisturb] = React.useState(false);
  const [notificationTypes, setNotificationTypes] = React.useState({
    messages: true,
    tasks: true,
    calendar: true,
    system: true,
    mentions: true,
    contacts: false,
  });

  // Card styling
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.700');
  
  /**
   * Handle notification type toggle
   */
  const handleNotificationTypeToggle = (type: string) => {
    setNotificationTypes((prev) => ({
      ...prev,
      [type]: !prev[type as keyof typeof prev],
    }));
  };

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md" mb={2}>Notification Settings</Heading>
      
      <Box p={5} borderRadius="md" bg={cardBg} borderWidth="1px" borderColor={cardBorder}>
        <VStack spacing={6} align="stretch">
          {/* General Notification Settings */}
          <Box>
            <Heading size="sm" mb={4}>General Settings</Heading>
            
            <FormControl display="flex" alignItems="center" justifyContent="space-between" mb={3}>
              <HStack>
                <Icon as={FiMail} />
                <FormLabel htmlFor="email-notifications" mb="0">
                  Email Notifications
                </FormLabel>
              </HStack>
              <Switch
                id="email-notifications"
                isChecked={emailEnabled}
                onChange={() => setEmailEnabled(!emailEnabled)}
                colorScheme="brand"
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center" justifyContent="space-between" mb={3}>
              <HStack>
                <Icon as={FiBell} />
                <FormLabel htmlFor="push-notifications" mb="0">
                  Push Notifications
                </FormLabel>
              </HStack>
              <Switch
                id="push-notifications"
                isChecked={pushEnabled}
                onChange={() => setPushEnabled(!pushEnabled)}
                colorScheme="brand"
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center" justifyContent="space-between" mb={3}>
              <FormLabel htmlFor="notification-sounds" mb="0">
                Notification Sounds
              </FormLabel>
              <Switch
                id="notification-sounds"
                isChecked={soundEnabled}
                onChange={() => setSoundEnabled(!soundEnabled)}
                colorScheme="brand"
              />
            </FormControl>
            
            <FormControl mb={3}>
              <FormLabel htmlFor="notification-frequency">
                Notification Frequency
              </FormLabel>
              <Select
                id="notification-frequency"
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
              >
                <option value="immediate">Immediate</option>
                <option value="hourly">Hourly Digest</option>
                <option value="daily">Daily Digest</option>
                <option value="weekly">Weekly Digest</option>
              </Select>
              <FormHelperText>
                How often you want to receive notification summaries
              </FormHelperText>
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="do-not-disturb" mb="0">
                Do Not Disturb
              </FormLabel>
              <Switch
                id="do-not-disturb"
                isChecked={doNotDisturb}
                onChange={() => setDoNotDisturb(!doNotDisturb)}
                colorScheme="brand"
              />
            </FormControl>
          </Box>
          
          <Divider />
          
          {/* Notification Types */}
          <Box>
            <Heading size="sm" mb={4}>Notification Types</Heading>
            <Text fontSize="sm" mb={4}>
              Select which types of notifications you want to receive
            </Text>
            
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
              <FormControl display="flex" alignItems="center">
                <Checkbox 
                  isChecked={notificationTypes.messages}
                  onChange={() => handleNotificationTypeToggle('messages')}
                  colorScheme="brand"
                >
                  <HStack>
                    <Text>Messages</Text>
                    <Icon as={FiMessageSquare} />
                  </HStack>
                </Checkbox>
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <Checkbox 
                  isChecked={notificationTypes.tasks}
                  onChange={() => handleNotificationTypeToggle('tasks')}
                  colorScheme="brand"
                >
                  <HStack>
                    <Text>Tasks</Text>
                    <Icon as={FiBriefcase} />
                  </HStack>
                </Checkbox>
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <Checkbox 
                  isChecked={notificationTypes.calendar}
                  onChange={() => handleNotificationTypeToggle('calendar')}
                  colorScheme="brand"
                >
                  <HStack>
                    <Text>Calendar Events</Text>
                    <Icon as={FiCalendar} />
                  </HStack>
                </Checkbox>
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <Checkbox 
                  isChecked={notificationTypes.system}
                  onChange={() => handleNotificationTypeToggle('system')}
                  colorScheme="brand"
                >
                  <HStack>
                    <Text>System Alerts</Text>
                    <Icon as={FiAlertCircle} />
                  </HStack>
                </Checkbox>
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <Checkbox 
                  isChecked={notificationTypes.mentions}
                  onChange={() => handleNotificationTypeToggle('mentions')}
                  colorScheme="brand"
                >
                  <HStack>
                    <Text>Mentions</Text>
                    <Badge colorScheme="blue" ml={1}>@</Badge>
                  </HStack>
                </Checkbox>
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <Checkbox 
                  isChecked={notificationTypes.contacts}
                  onChange={() => handleNotificationTypeToggle('contacts')}
                  colorScheme="brand"
                >
                  <HStack>
                    <Text>Contact Updates</Text>
                    <Icon as={FiUsers} />
                  </HStack>
                </Checkbox>
              </FormControl>
            </SimpleGrid>
          </Box>
        </VStack>
      </Box>
      
      <Text fontSize="sm" color="gray.500" mt={2}>
        Notification preferences are synchronized across all your devices.
      </Text>
    </VStack>
  );
};

export default NotificationSettings;
