/**
 * Settings Page Component
 * 
 * This component provides a comprehensive application settings interface
 * for controlling user preferences, account settings, notifications, and privacy.
 */
import React from 'react';
import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  useToast,
  VStack,
  useColorModeValue,
  Text,
  FormControl,
  Input
} from '@chakra-ui/react';
import { FiSettings, FiBell, FiUser, FiShield, FiMonitor } from 'react-icons/fi';

// Import our specialized settings components
import ThemeSettings from '../components/domain/settings/ThemeSettings';
import NotificationSettings from '../components/domain/settings/NotificationSettings';
import PrivacySettings from '../components/domain/settings/PrivacySettings';
import AccountSettings from '../components/domain/settings/AccountSettings';

/**
 * Settings page component for user preferences and account settings
 */
const Settings: React.FC = () => {
  const toast = useToast();
  
  // Background colors for different tab states
  const tabBg = useColorModeValue('gray.100', 'gray.700');
  const activeBg = useColorModeValue('white', 'gray.800');
  
  // Handle form submission
  const handleSaveSettings = () => {
    toast({
      title: 'Settings saved',
      description: 'Your settings have been updated successfully.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };
  
  return (
    <Container maxW="container.lg" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading as="h1" size="lg" mb={6}>
          Settings
        </Heading>
        
        <Box 
          borderRadius="lg" 
          overflow="hidden" 
          boxShadow="sm"
        >
          <Tabs colorScheme="brand" variant="soft-rounded" size="md">
            <TabList
              bg={tabBg}
              p={2}
              borderTopRadius="lg"
              borderBottomWidth="1px"
              borderBottomColor={useColorModeValue("gray.200", "gray.600")}
            >
              <Tab 
                _selected={{ bg: activeBg, fontWeight: "semibold" }} 
                borderRadius="md"
                display="flex"
                alignItems="center"
                gap={2}
              >
                <FiMonitor />
                <Text display={{ base: "none", md: "block" }}>Appearance</Text>
              </Tab>
              <Tab 
                _selected={{ bg: activeBg, fontWeight: "semibold" }} 
                borderRadius="md"
                display="flex"
                alignItems="center"
                gap={2}
              >
                <FiUser />
                <Text display={{ base: "none", md: "block" }}>Account</Text>
              </Tab>
              <Tab 
                _selected={{ bg: activeBg, fontWeight: "semibold" }} 
                borderRadius="md"
                display="flex"
                alignItems="center"
                gap={2}
              >
                <FiBell />
                <Text display={{ base: "none", md: "block" }}>Notifications</Text>
              </Tab>
              <Tab 
                _selected={{ bg: activeBg, fontWeight: "semibold" }} 
                borderRadius="md"
                display="flex"
                alignItems="center"
                gap={2}
              >
                <FiShield />
                <Text display={{ base: "none", md: "block" }}>Privacy</Text>
              </Tab>
              <Tab 
                _selected={{ bg: activeBg, fontWeight: "semibold" }} 
                borderRadius="md"
                display="flex"
                alignItems="center"
                gap={2}
              >
                <FiSettings />
                <Text display={{ base: "none", md: "block" }}>API Keys</Text>
              </Tab>
            </TabList>
            
            <TabPanels bg={activeBg} p={6}>
              {/* Appearance Settings Tab */}
              <TabPanel>
                <ThemeSettings />
              </TabPanel>
              
              {/* Account Settings Tab */}
              <TabPanel>
                <AccountSettings />
              </TabPanel>
              
              {/* Notification Settings Tab */}
              <TabPanel>
                <NotificationSettings />
              </TabPanel>
              
              {/* Privacy Settings Tab */}
              <TabPanel>
                <PrivacySettings />
              </TabPanel>
              
              {/* API Keys Settings Tab */}
              <TabPanel>
                <Box p={0}>
                  <VStack spacing={6} align="stretch">
                    <Heading size="md" mb={2}>API Integration</Heading>
                    
                    <Box p={5} borderRadius="md" borderWidth="1px" borderColor={useColorModeValue("gray.200", "gray.700")}>
                      <Heading as="h3" size="sm">
                        OpenAI API Key
                      </Heading>
                      <Text fontSize="sm" color="gray.500" mb={2}>
                        Required for AI functionality. Get your API key from OpenAI.
                      </Text>
                      <FormControl>
                        <Input 
                          type="password" 
                          placeholder="sk-..." 
                        />
                      </FormControl>
                      
                      <Heading as="h3" size="sm">
                        Pinecone API Key (Optional)
                      </Heading>
                      <Text fontSize="sm" color="gray.500" mb={2}>
                        For enhanced vector search capabilities.
                      </Text>
                      <FormControl>
                        <Input 
                          type="password" 
                          placeholder="Enter your Pinecone API key" 
                        />
                      </FormControl>
                    </Box>
                  </VStack>
                </Box>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Box>
        
        <Flex justify="flex-end" mt={6}>
          <Button variant="outline" mr={3}>
            Cancel
          </Button>
          <Button colorScheme="brand" onClick={handleSaveSettings}>
            Save Settings
          </Button>
        </Flex>
      </VStack>
    </Container>
  );
};

export default Settings;
