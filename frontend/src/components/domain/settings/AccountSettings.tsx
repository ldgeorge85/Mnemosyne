/**
 * Account Settings Component
 * 
 * This component allows users to manage their account details,
 * including personal information, password, and linked accounts.
 */
import React from 'react';
import {
  Box,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Button,
  Divider,
  Text,
  Avatar,
  HStack,
  FormHelperText,
  useColorModeValue,
  IconButton,
  Badge,
  SimpleGrid,
  InputGroup,
  InputRightElement,
  useToast,
} from '@chakra-ui/react';
import { 
  FiEdit2, 
  FiUpload, 
  FiEye, 
  FiEyeOff, 
  FiGithub, 
  FiTwitter, 
  FiMail,
  FiUser,
  FiLock,
  FiSave,
  FiTrash2,
} from 'react-icons/fi';

/**
 * Account settings component
 */
const AccountSettings: React.FC = () => {
  // Form state
  const [name, setName] = React.useState('Alex Johnson');
  const [email, setEmail] = React.useState('alex.johnson@example.com');
  const [currentPassword, setCurrentPassword] = React.useState('');
  const [newPassword, setNewPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  
  // UI state
  const [isEditingProfile, setIsEditingProfile] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);
  const [showNewPassword, setShowNewPassword] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  
  // Connected accounts
  const [connectedAccounts, setConnectedAccounts] = React.useState({
    github: true,
    google: false,
    twitter: true,
  });
  
  // Toast for notifications
  const toast = useToast();
  
  // Card styling
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.700');
  
  /**
   * Handle profile update
   */
  const handleProfileUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulating API call
    setTimeout(() => {
      setIsSubmitting(false);
      setIsEditingProfile(false);
      
      toast({
        title: 'Profile updated',
        description: 'Your profile information has been updated successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    }, 1000);
  };
  
  /**
   * Handle password change
   */
  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Password validation
    if (newPassword !== confirmPassword) {
      toast({
        title: 'Passwords do not match',
        description: 'New password and confirm password must be the same.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsSubmitting(false);
      return;
    }
    
    // Simulating API call
    setTimeout(() => {
      setIsSubmitting(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      
      toast({
        title: 'Password changed',
        description: 'Your password has been changed successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    }, 1000);
  };
  
  /**
   * Handle connected account toggle
   */
  const handleToggleConnection = (account: string) => {
    setConnectedAccounts({
      ...connectedAccounts,
      [account]: !connectedAccounts[account as keyof typeof connectedAccounts],
    });
    
    toast({
      title: connectedAccounts[account as keyof typeof connectedAccounts] 
        ? `Disconnected from ${account}` 
        : `Connected to ${account}`,
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md" mb={2}>Account Settings</Heading>
      
      {/* Profile Information */}
      <Box p={5} borderRadius="md" bg={cardBg} borderWidth="1px" borderColor={cardBorder}>
        <form onSubmit={handleProfileUpdate}>
          <VStack spacing={6} align="stretch">
            <HStack justify="space-between">
              <Heading size="sm">Profile Information</Heading>
              <Button
                size="sm"
                leftIcon={isEditingProfile ? <FiSave /> : <FiEdit2 />}
                onClick={() => !isSubmitting && setIsEditingProfile(!isEditingProfile)}
                colorScheme={isEditingProfile ? "brand" : "gray"}
                variant={isEditingProfile ? "solid" : "outline"}
                type={isEditingProfile ? "submit" : "button"}
                isLoading={isSubmitting}
              >
                {isEditingProfile ? "Save Changes" : "Edit Profile"}
              </Button>
            </HStack>
            
            <HStack spacing={4}>
              <Avatar 
                size="xl" 
                name={name} 
                src="https://bit.ly/broken-link" 
              />
              <VStack align="start" spacing={1}>
                <Text fontWeight="bold">{name}</Text>
                <Text color="gray.500">{email}</Text>
                <Badge colorScheme="green">Active Account</Badge>
                
                {isEditingProfile && (
                  <Button
                    size="sm"
                    leftIcon={<FiUpload />}
                    mt={2}
                  >
                    Upload New Photo
                  </Button>
                )}
              </VStack>
            </HStack>
            
            <Divider />
            
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              <FormControl>
                <FormLabel htmlFor="profile-name">
                  <HStack>
                    <FiUser />
                    <Text>Full Name</Text>
                  </HStack>
                </FormLabel>
                <Input
                  id="profile-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  isReadOnly={!isEditingProfile}
                />
              </FormControl>
              
              <FormControl>
                <FormLabel htmlFor="profile-email">
                  <HStack>
                    <FiMail />
                    <Text>Email Address</Text>
                  </HStack>
                </FormLabel>
                <Input
                  id="profile-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  isReadOnly={!isEditingProfile}
                />
                <FormHelperText>
                  This email is used for notifications and account recovery
                </FormHelperText>
              </FormControl>
            </SimpleGrid>
          </VStack>
        </form>
      </Box>
      
      {/* Password Management */}
      <Box p={5} borderRadius="md" bg={cardBg} borderWidth="1px" borderColor={cardBorder}>
        <form onSubmit={handlePasswordChange}>
          <VStack spacing={6} align="stretch">
            <Heading size="sm" mb={2}>
              <HStack>
                <FiLock />
                <Text>Password Management</Text>
              </HStack>
            </Heading>
            
            <FormControl mb={3}>
              <FormLabel htmlFor="current-password">Current Password</FormLabel>
              <InputGroup>
                <Input
                  id="current-password"
                  type={showPassword ? "text" : "password"}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                />
                <InputRightElement>
                  <IconButton
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    icon={showPassword ? <FiEyeOff /> : <FiEye />}
                    onClick={() => setShowPassword(!showPassword)}
                    variant="ghost"
                    size="sm"
                  />
                </InputRightElement>
              </InputGroup>
            </FormControl>
            
            <FormControl mb={3}>
              <FormLabel htmlFor="new-password">New Password</FormLabel>
              <InputGroup>
                <Input
                  id="new-password"
                  type={showNewPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
                <InputRightElement>
                  <IconButton
                    aria-label={showNewPassword ? "Hide password" : "Show password"}
                    icon={showNewPassword ? <FiEyeOff /> : <FiEye />}
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    variant="ghost"
                    size="sm"
                  />
                </InputRightElement>
              </InputGroup>
              <FormHelperText>
                Password must be at least 8 characters with a mix of letters, numbers, and symbols
              </FormHelperText>
            </FormControl>
            
            <FormControl mb={3}>
              <FormLabel htmlFor="confirm-password">Confirm New Password</FormLabel>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </FormControl>
            
            <Button
              colorScheme="brand"
              type="submit"
              isLoading={isSubmitting}
              isDisabled={!currentPassword || !newPassword || !confirmPassword}
            >
              Change Password
            </Button>
          </VStack>
        </form>
      </Box>
      
      {/* Connected Accounts */}
      <Box p={5} borderRadius="md" bg={cardBg} borderWidth="1px" borderColor={cardBorder}>
        <VStack spacing={6} align="stretch">
          <Heading size="sm" mb={2}>Connected Accounts</Heading>
          
          <VStack spacing={4} align="stretch">
            <HStack justify="space-between">
              <HStack>
                <FiGithub size={20} />
                <Text>GitHub</Text>
                {connectedAccounts.github && <Badge colorScheme="green">Connected</Badge>}
              </HStack>
              <Button
                size="sm"
                variant="outline"
                colorScheme={connectedAccounts.github ? "red" : "green"}
                onClick={() => handleToggleConnection('github')}
              >
                {connectedAccounts.github ? "Disconnect" : "Connect"}
              </Button>
            </HStack>
            
            <HStack justify="space-between">
              <HStack>
                <Box fontSize="xl">G</Box>
                <Text>Google</Text>
                {connectedAccounts.google && <Badge colorScheme="green">Connected</Badge>}
              </HStack>
              <Button
                size="sm"
                variant="outline"
                colorScheme={connectedAccounts.google ? "red" : "green"}
                onClick={() => handleToggleConnection('google')}
              >
                {connectedAccounts.google ? "Disconnect" : "Connect"}
              </Button>
            </HStack>
            
            <HStack justify="space-between">
              <HStack>
                <FiTwitter size={20} />
                <Text>Twitter</Text>
                {connectedAccounts.twitter && <Badge colorScheme="green">Connected</Badge>}
              </HStack>
              <Button
                size="sm"
                variant="outline"
                colorScheme={connectedAccounts.twitter ? "red" : "green"}
                onClick={() => handleToggleConnection('twitter')}
              >
                {connectedAccounts.twitter ? "Disconnect" : "Connect"}
              </Button>
            </HStack>
          </VStack>
        </VStack>
      </Box>
      
      {/* Danger Zone */}
      <Box p={5} borderRadius="md" borderWidth="1px" borderColor="red.300" bg={useColorModeValue('red.50', 'rgba(254, 178, 178, 0.12)')}>
        <VStack spacing={4} align="stretch">
          <Heading size="sm" color="red.500">Danger Zone</Heading>
          <Text>Permanently delete your account and all associated data.</Text>
          <Button
            leftIcon={<FiTrash2 />}
            colorScheme="red"
            variant="outline"
            size="sm"
          >
            Delete Account
          </Button>
        </VStack>
      </Box>
    </VStack>
  );
};

export default AccountSettings;
