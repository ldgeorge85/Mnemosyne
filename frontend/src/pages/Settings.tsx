/**
 * Settings Page Component
 * 
 * This component provides the application settings interface
 * for controlling user preferences and account settings.
 */
import React from 'react';
import {
  Box,
  Button,
  Divider,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Select,
  Stack,
  Switch,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  useColorMode,
  useToast,
} from '@chakra-ui/react';
import { useUIStore } from '../stores';

/**
 * Settings page component for user preferences and account settings
 */
const Settings: React.FC = () => {
  const toast = useToast();
  const { colorMode, toggleColorMode } = useColorMode();
  const { colorMode: storeColorMode, toggleColorMode: toggleStoreColorMode } = useUIStore();
  
  // Toggle color mode in both Chakra UI and our store
  const handleToggleColorMode = () => {
    toggleColorMode();
    toggleStoreColorMode();
  };
  
  // Handle form submission
  const handleSaveSettings = () => {
    toast({
      title: 'Settings saved',
      description: 'Your settings have been saved successfully.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };
  
  return (
    <Box>
      <Heading as="h1" size="lg" mb={6}>
        Settings
      </Heading>
      
      <Tabs colorScheme="brand" variant="enclosed">
        <TabList>
          <Tab>General</Tab>
          <Tab>Account</Tab>
          <Tab>Notifications</Tab>
          <Tab>API Keys</Tab>
        </TabList>
        
        <TabPanels>
          {/* General Settings */}
          <TabPanel>
            <Stack spacing={6}>
              <Heading as="h2" size="md" mb={4}>
                General Settings
              </Heading>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="dark-mode" mb="0">
                  Dark Mode
                </FormLabel>
                <Switch
                  id="dark-mode"
                  isChecked={colorMode === 'dark'}
                  onChange={handleToggleColorMode}
                  colorScheme="brand"
                />
              </FormControl>
              
              <FormControl>
                <FormLabel>Language</FormLabel>
                <Select defaultValue="en">
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </Select>
              </FormControl>
              
              <FormControl>
                <FormLabel>Time Zone</FormLabel>
                <Select defaultValue="utc">
                  <option value="utc">UTC</option>
                  <option value="est">Eastern Time (US & Canada)</option>
                  <option value="pst">Pacific Time (US & Canada)</option>
                  <option value="cet">Central European Time</option>
                </Select>
              </FormControl>
            </Stack>
          </TabPanel>
          
          {/* Account Settings */}
          <TabPanel>
            <Stack spacing={6}>
              <Heading as="h2" size="md" mb={4}>
                Account Settings
              </Heading>
              
              <FormControl>
                <FormLabel>Full Name</FormLabel>
                <Input defaultValue="John Doe" />
              </FormControl>
              
              <FormControl>
                <FormLabel>Email Address</FormLabel>
                <Input defaultValue="john.doe@example.com" type="email" />
              </FormControl>
              
              <Divider />
              
              <Heading as="h3" size="sm" mt={2}>
                Change Password
              </Heading>
              
              <FormControl>
                <FormLabel>Current Password</FormLabel>
                <Input type="password" />
              </FormControl>
              
              <FormControl>
                <FormLabel>New Password</FormLabel>
                <Input type="password" />
              </FormControl>
              
              <FormControl>
                <FormLabel>Confirm New Password</FormLabel>
                <Input type="password" />
              </FormControl>
            </Stack>
          </TabPanel>
          
          {/* Notification Settings */}
          <TabPanel>
            <Stack spacing={6}>
              <Heading as="h2" size="md" mb={4}>
                Notification Settings
              </Heading>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="email-notifications" mb="0">
                  Email Notifications
                </FormLabel>
                <Switch id="email-notifications" defaultChecked colorScheme="brand" />
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="task-reminders" mb="0">
                  Task Reminders
                </FormLabel>
                <Switch id="task-reminders" defaultChecked colorScheme="brand" />
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="system-updates" mb="0">
                  System Updates
                </FormLabel>
                <Switch id="system-updates" defaultChecked colorScheme="brand" />
              </FormControl>
              
              <FormControl>
                <FormLabel>Notification Frequency</FormLabel>
                <Select defaultValue="realtime">
                  <option value="realtime">Real-time</option>
                  <option value="daily">Daily Digest</option>
                  <option value="weekly">Weekly Summary</option>
                </Select>
              </FormControl>
            </Stack>
          </TabPanel>
          
          {/* API Keys Settings */}
          <TabPanel>
            <Stack spacing={6}>
              <Heading as="h2" size="md" mb={4}>
                API Integration
              </Heading>
              
              <Box p={4} borderWidth="1px" borderRadius="md">
                <Heading as="h3" size="sm">
                  OpenAI API Key
                </Heading>
                <Text fontSize="sm" color="gray.500" mb={2}>
                  Required for AI-powered features
                </Text>
                <FormControl>
                  <Input
                    type="password"
                    placeholder="Enter your OpenAI API key"
                    defaultValue="sk-•••••••••••••••••••••••••••••••"
                  />
                </FormControl>
              </Box>
              
              <Box p={4} borderWidth="1px" borderRadius="md">
                <Heading as="h3" size="sm">
                  Google Calendar API
                </Heading>
                <Text fontSize="sm" color="gray.500" mb={2}>
                  Required for calendar integration
                </Text>
                <FormControl>
                  <Input
                    placeholder="Enter your Google Calendar API key"
                  />
                </FormControl>
                <Button size="sm" colorScheme="blue" mt={2}>
                  Connect Account
                </Button>
              </Box>
            </Stack>
          </TabPanel>
        </TabPanels>
      </Tabs>
      
      <Flex justify="flex-end" mt={8}>
        <Button colorScheme="gray" mr={3}>
          Cancel
        </Button>
        <Button colorScheme="brand" onClick={handleSaveSettings}>
          Save Settings
        </Button>
      </Flex>
    </Box>
  );
};

export default Settings;
