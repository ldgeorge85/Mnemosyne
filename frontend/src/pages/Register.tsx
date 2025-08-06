import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  Alert,
  AlertIcon,
  Link,
  Heading,
  useToast
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  full_name: string;
}

/**
 * User registration page component
 */
const Register: React.FC = () => {
  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      const response = await apiClient.post('/auth/register', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name
      });

      if (response.status === 200 || response.status === 201) {
        toast({
          title: 'Registration successful!',
          description: 'Please sign in with your new account.',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        navigate('/login');
      }
    } catch (err: any) {
      console.error('Registration error:', err);
      
      let errorMessage = 'Registration failed. Please try again.';
      
      if (err.response?.status === 400) {
        // Handle specific 400 errors
        const detail = err.response.data?.detail;
        if (typeof detail === 'string') {
          if (detail.includes('Username already registered')) {
            errorMessage = 'This username is already taken. Please choose a different username.';
          } else if (detail.includes('Email already registered')) {
            errorMessage = 'This email is already registered. Please use a different email or try logging in.';
          } else {
            errorMessage = detail;
          }
        } else {
          errorMessage = 'Username or email already exists. Please try different values.';
        }
      } else if (err.response?.status === 422) {
        // Handle validation errors
        const detail = err.response.data?.detail;
        if (Array.isArray(detail)) {
          const messages = detail.map((e: any) => {
            if (e.loc && e.loc.includes('password')) {
              return `Password: ${e.msg}`;
            } else if (e.loc && e.loc.includes('email')) {
              return `Email: ${e.msg}`;
            } else if (e.loc && e.loc.includes('username')) {
              return `Username: ${e.msg}`;
            }
            return e.msg;
          });
          errorMessage = messages.join('. ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = 'Please check your input and try again.';
        }
      } else if (err.message?.includes('Network Error')) {
        errorMessage = 'Unable to connect to server. Please check your connection and try again.';
      }
      
      setError(errorMessage);
      
      // Show toast notification as well
      toast({
        title: 'Registration failed',
        description: errorMessage,
        status: 'error',
        duration: 7000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxW="md" py={12}>
      <VStack spacing={8}>
        <Heading size="lg" textAlign="center">
          Create Your Account
        </Heading>
        
        <Box w="100%" p={8} borderWidth={1} borderRadius="lg" boxShadow="lg">
          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              {error && (
                <Alert status="error">
                  <AlertIcon />
                  {error}
                </Alert>
              )}

              <FormControl isRequired>
                <FormLabel>Full Name</FormLabel>
                <Input
                  name="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  placeholder="Enter your full name"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Username</FormLabel>
                <Input
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="Choose a username"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="Enter your email"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Password</FormLabel>
                <Input
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Create a strong password"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Confirm Password</FormLabel>
                <Input
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  placeholder="Confirm your password"
                />
              </FormControl>

              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                width="100%"
                isLoading={loading}
                loadingText="Creating Account..."
              >
                Sign Up
              </Button>
            </VStack>
          </form>
        </Box>

        <Text>
          Already have an account?{' '}
          <Link as={RouterLink} to="/login" color="blue.500">
            Sign in here
          </Link>
        </Text>
      </VStack>
    </Container>
  );
};

export default Register;
