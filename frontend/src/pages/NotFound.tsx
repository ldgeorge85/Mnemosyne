/**
 * NotFound Page Component
 * 
 * This component renders a 404 page when a route is not found
 * and provides a way to navigate back to the home page.
 */
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  Button,
  VStack,
  Container,
  useColorModeValue
} from '@chakra-ui/react';

/**
 * NotFound page component displayed when a route doesn't exist
 * Provides helpful information and navigation back to valid parts of the app
 */
const NotFound: React.FC = () => {
  return (
    <Container maxW="container.md" py={12}>
      <VStack spacing={6} textAlign="center">
        <Heading
          display="inline-block"
          as="h1"
          size="4xl"
          color={useColorModeValue('brand.500', 'brand.300')}
          fontSize="9xl"
        >
          404
        </Heading>
        <Heading as="h2" size="xl" mt={6} mb={2}>
          Page Not Found
        </Heading>
        <Text color={useColorModeValue('gray.600', 'gray.400')} fontSize="lg">
          The page you're looking for doesn't seem to exist.
          It might have been moved or deleted.
        </Text>
        <Box mt={6}>
          <Button
            colorScheme="brand"
            as={RouterLink}
            to="/"
            variant="solid"
            size="lg"
            mt={8}
          >
            Return Home
          </Button>
        </Box>
      </VStack>
    </Container>
  );
};

export default NotFound;
