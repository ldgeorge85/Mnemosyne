/**
 * Login Page Component
 * 
 * This component renders the login form for user authentication.
 */
import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Checkbox,
  Container,
  Divider,
  FormControl,
  FormLabel,
  Heading,
  HStack,
  Input,
  Link,
  Stack,
  Text,
  useColorModeValue,
  FormErrorMessage,
  useToast,
} from '@chakra-ui/react';
import { FiLock, FiMail } from 'react-icons/fi';

/**
 * Login page component that handles user authentication
 */
const Login: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Reset error state
    setError('');
    
    // Validate form
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }
    
    // Show loading state
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, you would call your authentication API here
      // const response = await authService.login(email, password);
      
      // Store token in localStorage
      localStorage.setItem('token', 'demo-token');
      
      // Show success message
      toast({
        title: 'Login successful',
        description: 'You have been logged in successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      // Handle error
      setError('Invalid email or password. Please try again.');
    } finally {
      // Reset loading state
      setIsLoading(false);
    }
  };
  
  return (
    <Container maxW="md" py={{ base: '12', md: '24' }}>
      <Stack spacing="8">
        <Stack spacing="6" textAlign="center">
          <Heading size="xl" fontWeight="bold">
            Sign in to your account
          </Heading>
          <Text color={useColorModeValue('gray.600', 'gray.400')}>
            Enter your email and password to access your account
          </Text>
        </Stack>
        
        <Box
          py={{ base: '0', sm: '8' }}
          px={{ base: '4', sm: '10' }}
          bg={useColorModeValue('white', 'gray.700')}
          boxShadow={{ base: 'none', sm: 'md' }}
          borderRadius={{ base: 'none', sm: 'xl' }}
        >
          <form onSubmit={handleSubmit}>
            <Stack spacing="6">
              <Stack spacing="5">
                {/* Email field */}
                <FormControl isRequired isInvalid={!!error}>
                  <FormLabel htmlFor="email">Email</FormLabel>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    leftElement={<Box ml={3}><FiMail /></Box>}
                  />
                </FormControl>
                
                {/* Password field */}
                <FormControl isRequired isInvalid={!!error}>
                  <FormLabel htmlFor="password">Password</FormLabel>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    leftElement={<Box ml={3}><FiLock /></Box>}
                  />
                  
                  {/* Error message */}
                  {error && <FormErrorMessage>{error}</FormErrorMessage>}
                </FormControl>
              </Stack>
              
              {/* Remember me and forgot password */}
              <HStack justify="space-between">
                <Checkbox defaultChecked>Remember me</Checkbox>
                <Link as={RouterLink} to="/forgot-password" fontSize="sm" color="brand.500">
                  Forgot password?
                </Link>
              </HStack>
              
              {/* Submit button */}
              <Button
                type="submit"
                colorScheme="brand"
                size="lg"
                fontSize="md"
                isLoading={isLoading}
              >
                Sign in
              </Button>
              
              {/* Divider */}
              <HStack>
                <Divider />
                <Text fontSize="sm" color="gray.500">
                  OR
                </Text>
                <Divider />
              </HStack>
              
              {/* OAuth providers (placeholders) */}
              <Button
                variant="outline"
                colorScheme="gray"
                isFullWidth
                onClick={() => toast({
                  title: "Feature not available",
                  description: "OAuth login is not implemented in the demo.",
                  status: "info",
                  duration: 3000,
                  isClosable: true,
                })}
              >
                Continue with Google
              </Button>
            </Stack>
          </form>
        </Box>
        
        {/* Sign up link */}
        <HStack spacing="1" justify="center">
          <Text color="gray.500">Don't have an account?</Text>
          <Link as={RouterLink} to="/register" color="brand.500">
            Sign up
          </Link>
        </HStack>
      </Stack>
    </Container>
  );
};

export default Login;
