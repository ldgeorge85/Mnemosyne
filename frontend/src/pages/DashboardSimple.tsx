/**
 * Simple Dashboard Page Component
 * Works without backend API for development
 */
import React from 'react';
import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
  VStack,
  Button,
  useColorMode,
  IconButton,
  Flex,
  Stat,
  StatLabel,
  StatNumber,
  Badge
} from '@chakra-ui/react';
import { FiMoon, FiSun, FiMessageCircle, FiDatabase, FiCheckSquare, FiUsers } from 'react-icons/fi';
import { Link } from 'react-router-dom';

const DashboardSimple: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Container maxW="container.xl" py={8}>
      <Flex justifyContent="space-between" alignItems="center" mb={8}>
        <Heading>Mnemosyne Dashboard</Heading>
        <IconButton
          aria-label="Toggle dark mode"
          icon={colorMode === 'dark' ? <FiSun /> : <FiMoon />}
          onClick={toggleColorMode}
        />
      </Flex>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Memories</StatLabel>
              <StatNumber>0</StatNumber>
              <Text fontSize="sm" color="gray.500">Total stored</Text>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Conversations</StatLabel>
              <StatNumber>0</StatNumber>
              <Text fontSize="sm" color="gray.500">Active chats</Text>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Tasks</StatLabel>
              <StatNumber>0</StatNumber>
              <Text fontSize="sm" color="gray.500">Pending</Text>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Agents</StatLabel>
              <StatNumber>3</StatNumber>
              <Text fontSize="sm" color="gray.500">Available</Text>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Quick Actions</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Button as={Link} to="/chat" colorScheme="blue" leftIcon={<FiMessageCircle />}>
                Start New Chat
              </Button>
              <Button as={Link} to="/memories" variant="outline" leftIcon={<FiDatabase />}>
                Browse Memories
              </Button>
              <Button as={Link} to="/tasks" variant="outline" leftIcon={<FiCheckSquare />}>
                Manage Tasks
              </Button>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">System Status</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              <Flex justify="space-between">
                <Text>Backend API</Text>
                <Badge colorScheme="green">Connected</Badge>
              </Flex>
              <Flex justify="space-between">
                <Text>Vector Store</Text>
                <Badge colorScheme="yellow">Ready</Badge>
              </Flex>
              <Flex justify="space-between">
                <Text>Auth Mode</Text>
                <Badge colorScheme="orange">Development</Badge>
              </Flex>
              <Flex justify="space-between">
                <Text>Dark Mode</Text>
                <Badge>{colorMode === 'dark' ? 'Enabled' : 'Disabled'}</Badge>
              </Flex>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Card mt={6}>
        <CardHeader>
          <Heading size="md">Welcome to Mnemosyne Protocol</Heading>
        </CardHeader>
        <CardBody>
          <Text mb={4}>
            A cognitive-symbolic operating system for preserving human agency. This is your personal
            instance running in development mode.
          </Text>
          <Text fontSize="sm" color="gray.500">
            Sprint 1C: Frontend UI is now accessible! Start exploring the interface or create your
            first memory.
          </Text>
        </CardBody>
      </Card>
    </Container>
  );
};

export default DashboardSimple;