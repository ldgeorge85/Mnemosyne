/**
 * Privacy Settings Component
 * 
 * This component allows users to configure privacy-related settings,
 * including data sharing, analytics, and access controls.
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
  Divider,
  Text,
  Button,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useColorModeValue,
  HStack,
  Icon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  Select,
} from '@chakra-ui/react';
import { 
  FiShield, 
  FiEye, 
  FiEyeOff, 
  FiActivity, 
  FiDownload,
  FiTrash2,
  FiAlertTriangle,
  FiLock,
} from 'react-icons/fi';

/**
 * Privacy settings component
 */
const PrivacySettings: React.FC = () => {
  // State for privacy settings
  const [dataCollection, setDataCollection] = React.useState(true);
  const [thirdPartySharing, setThirdPartySharing] = React.useState(false);
  const [showActivity, setShowActivity] = React.useState(true);
  const [memoryRetention, setMemoryRetention] = React.useState('90');
  
  // Modal state for data deletion
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [confirmText, setConfirmText] = React.useState('');
  
  // Card styling
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.700');
  const alertBg = useColorModeValue('red.50', 'rgba(254, 178, 178, 0.16)');
  
  return (
    <>
      <VStack spacing={6} align="stretch">
        <Heading size="md" mb={2}>Privacy Settings</Heading>
        
        <Box p={5} borderRadius="md" bg={cardBg} borderWidth="1px" borderColor={cardBorder}>
          <VStack spacing={6} align="stretch">
            {/* Data Collection */}
            <Box>
              <Heading size="sm" mb={4}>Data Collection & Usage</Heading>
              
              <FormControl display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <HStack>
                  <Icon as={FiActivity} />
                  <FormLabel htmlFor="data-collection" mb="0">
                    Usage Analytics
                  </FormLabel>
                </HStack>
                <Switch
                  id="data-collection"
                  isChecked={dataCollection}
                  onChange={() => setDataCollection(!dataCollection)}
                  colorScheme="brand"
                />
              </FormControl>
              <FormHelperText mb={4}>
                Allow collection of anonymous usage data to help improve the application
              </FormHelperText>
              
              <FormControl display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <HStack>
                  <Icon as={FiEye} />
                  <FormLabel htmlFor="third-party-sharing" mb="0">
                    Third-party Data Sharing
                  </FormLabel>
                </HStack>
                <Switch
                  id="third-party-sharing"
                  isChecked={thirdPartySharing}
                  onChange={() => setThirdPartySharing(!thirdPartySharing)}
                  colorScheme="brand"
                />
              </FormControl>
              <FormHelperText mb={4}>
                Allow sharing of anonymized data with trusted third parties
              </FormHelperText>
            </Box>
            
            <Divider />
            
            {/* Privacy Controls */}
            <Box>
              <Heading size="sm" mb={4}>Privacy Controls</Heading>
              
              <FormControl display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <HStack>
                  <Icon as={FiEyeOff} />
                  <FormLabel htmlFor="activity-visibility" mb="0">
                    Show Activity Status
                  </FormLabel>
                </HStack>
                <Switch
                  id="activity-visibility"
                  isChecked={showActivity}
                  onChange={() => setShowActivity(!showActivity)}
                  colorScheme="brand"
                />
              </FormControl>
              <FormHelperText mb={4}>
                Allow others to see when you're online or recently active
              </FormHelperText>
              
              <FormControl mb={4}>
                <FormLabel htmlFor="memory-retention">
                  <HStack>
                    <Icon as={FiShield} />
                    <Text>Memory Retention Period</Text>
                  </HStack>
                </FormLabel>
                <Select
                  id="memory-retention"
                  value={memoryRetention}
                  onChange={(e) => setMemoryRetention(e.target.value)}
                >
                  <option value="30">30 days</option>
                  <option value="90">90 days</option>
                  <option value="180">180 days</option>
                  <option value="365">1 year</option>
                  <option value="forever">Forever</option>
                </Select>
                <FormHelperText>
                  How long the system should retain your conversation history and memories
                </FormHelperText>
              </FormControl>
            </Box>
            
            <Divider />
            
            {/* Data Management */}
            <Box>
              <Heading size="sm" mb={4}>Data Management</Heading>
              
              <VStack spacing={4} align="stretch">
                <Button 
                  leftIcon={<FiDownload />} 
                  variant="outline"
                  size="sm"
                >
                  Download All My Data
                </Button>
                
                <Button
                  leftIcon={<FiTrash2 />}
                  colorScheme="red"
                  variant="outline"
                  size="sm"
                  onClick={onOpen}
                >
                  Delete All My Data
                </Button>
              </VStack>
            </Box>
          </VStack>
        </Box>
        
        {/* Privacy Information */}
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Your privacy matters</AlertTitle>
            <AlertDescription>
              We're committed to protecting your data privacy and security.
              Review our <Text as="span" fontWeight="bold" textDecor="underline">Privacy Policy</Text> for more details.
            </AlertDescription>
          </Box>
        </Alert>
      </VStack>
      
      {/* Data Deletion Confirmation Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Delete All Data?</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Alert status="error" mb={4} bg={alertBg}>
              <AlertIcon />
              <Box>
                <AlertTitle>Warning: This action cannot be undone</AlertTitle>
                <AlertDescription>
                  All your conversations, memories, and personal data will be permanently deleted.
                </AlertDescription>
              </Box>
            </Alert>
            
            <Text mb={4}>
              To confirm deletion, please type "DELETE MY DATA" below:
            </Text>
            
            <Input 
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              placeholder="Type DELETE MY DATA"
            />
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="red" 
              leftIcon={<FiTrash2 />}
              isDisabled={confirmText !== 'DELETE MY DATA'}
            >
              Permanently Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default PrivacySettings;
