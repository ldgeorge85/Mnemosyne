/**
 * Simple Memories Page Component
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
  Badge,
  Flex,
  Input,
  InputGroup,
  InputLeftElement,
  IconButton,
  useColorMode
} from '@chakra-ui/react';
import { FiSearch, FiPlus, FiMoon, FiSun, FiBookmark, FiClock } from 'react-icons/fi';

const MemoriesSimple: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const [searchQuery, setSearchQuery] = React.useState('');

  // Sample memories for display
  const sampleMemories = [
    {
      id: '1',
      title: 'Project Initialization',
      content: 'Started working on the Mnemosyne Protocol. Set up Docker containers and basic authentication.',
      timestamp: '2 hours ago',
      tags: ['development', 'setup'],
      importance: 'high'
    },
    {
      id: '2',
      title: 'Research on W3C Standards',
      content: 'Reviewed W3C DID specifications and Verifiable Credentials for identity management.',
      timestamp: '5 hours ago',
      tags: ['research', 'standards'],
      importance: 'medium'
    },
    {
      id: '3',
      title: 'Frontend UI Development',
      content: 'Created React components with ChakraUI. Implemented dark mode and responsive design.',
      timestamp: '1 day ago',
      tags: ['frontend', 'UI'],
      importance: 'medium'
    }
  ];

  const filteredMemories = sampleMemories.filter(memory =>
    memory.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    memory.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Container maxW="container.xl" py={8}>
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Heading>Memories</Heading>
        <Flex gap={2}>
          <Button colorScheme="blue" leftIcon={<FiPlus />}>
            New Memory
          </Button>
          <IconButton
            aria-label="Toggle dark mode"
            icon={colorMode === 'dark' ? <FiSun /> : <FiMoon />}
            onClick={toggleColorMode}
          />
        </Flex>
      </Flex>

      <InputGroup mb={6}>
        <InputLeftElement pointerEvents="none">
          <FiSearch color="gray.300" />
        </InputLeftElement>
        <Input
          placeholder="Search memories..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </InputGroup>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
        {filteredMemories.map((memory) => (
          <Card key={memory.id} cursor="pointer" _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }} transition="all 0.2s">
            <CardHeader pb={3}>
              <Flex justify="space-between" align="start">
                <Heading size="sm">{memory.title}</Heading>
                <IconButton
                  aria-label="Bookmark"
                  icon={<FiBookmark />}
                  size="sm"
                  variant="ghost"
                />
              </Flex>
            </CardHeader>
            <CardBody pt={0}>
              <Text fontSize="sm" color="gray.600" mb={3}>
                {memory.content}
              </Text>
              <Flex wrap="wrap" gap={2} mb={3}>
                {memory.tags.map((tag) => (
                  <Badge key={tag} colorScheme="blue" variant="subtle">
                    {tag}
                  </Badge>
                ))}
              </Flex>
              <Flex justify="space-between" align="center">
                <Flex align="center" gap={1} fontSize="xs" color="gray.500">
                  <FiClock />
                  <Text>{memory.timestamp}</Text>
                </Flex>
                <Badge
                  colorScheme={
                    memory.importance === 'high' ? 'red' :
                    memory.importance === 'medium' ? 'yellow' : 'green'
                  }
                >
                  {memory.importance}
                </Badge>
              </Flex>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>

      {filteredMemories.length === 0 && (
        <Box textAlign="center" py={10}>
          <Text color="gray.500">No memories found matching your search.</Text>
        </Box>
      )}
    </Container>
  );
};

export default MemoriesSimple;