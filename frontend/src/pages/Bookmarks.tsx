import React, { useState, useEffect } from 'react';
import { listBookmarks, deleteBookmark } from '../api/bookmarks';
import {
  Box,
  Container,
  Heading,
  VStack,
  Text,
  Button,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Link,
  IconButton,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  HStack,
  Input,
  InputGroup,
  InputLeftElement
} from '@chakra-ui/react';
import { ExternalLinkIcon, DeleteIcon, SearchIcon } from '@chakra-ui/icons';

interface Bookmark {
  id: string;
  title: string;
  url: string;
  description?: string;
  tags: string[];
  created_at: string;
  user_id: string;
}

/**
 * Bookmarks page component
 * 
 * Displays user's saved bookmarks with search and filtering
 */
const Bookmarks: React.FC = () => {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const toast = useToast();



// Fetch bookmarks from API
  useEffect(() => {
    const loadBookmarks = async () => {
      try {
        const response = await listBookmarks();
        if (response.success) {
          setBookmarks(response.data);
        } else {
          throw new Error('Failed to fetch bookmarks');
        }
      } catch (err) {
        setError('Failed to load bookmarks');
      } finally {
        setLoading(false);
      }
    };

    loadBookmarks();
  }, []);

  const handleDeleteBookmark = async (bookmarkId: string) => {
    try {
      const response = await deleteBookmark(bookmarkId);
      if (response.success && response.data.success) {
        setBookmarks((prev: Bookmark[]) => prev.filter((bookmark) => bookmark.id !== bookmarkId));
      } else {
        throw new Error('Failed to delete');
      }
      toast({
        title: 'Bookmark deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Failed to delete bookmark',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const filteredBookmarks = bookmarks.filter(bookmark =>
    bookmark.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bookmark.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bookmark.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading bookmarks...</Text>
        </VStack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="6xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between" align="center">
          <Heading size="lg">My Bookmarks</Heading>
          <Button colorScheme="blue" size="sm">
            Add Bookmark
          </Button>
        </HStack>

        <InputGroup maxW="md">
          <InputLeftElement pointerEvents="none">
            <SearchIcon color="gray.300" />
          </InputLeftElement>
          <Input
            placeholder="Search bookmarks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>

        {filteredBookmarks.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text fontSize="lg" color="gray.500">
              {searchTerm ? 'No bookmarks match your search.' : 'No bookmarks saved yet.'}
            </Text>
            {!searchTerm && (
              <Button colorScheme="blue" mt={4}>
                Add Your First Bookmark
              </Button>
            )}
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {filteredBookmarks.map((bookmark) => (
              <Card key={bookmark.id} variant="outline">
                <CardHeader pb={2}>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex={1}>
                      <Heading size="sm" noOfLines={2}>
                        {bookmark.title}
                      </Heading>
                      <Link
                        href={bookmark.url}
                        isExternal
                        color="blue.500"
                        fontSize="sm"
                        noOfLines={1}
                      >
                        {bookmark.url} <ExternalLinkIcon mx="2px" />
                      </Link>
                    </VStack>
                    <IconButton
                      aria-label="Delete bookmark"
                      icon={<DeleteIcon />}
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      onClick={() => handleDeleteBookmark(bookmark.id)}
                    />
                  </HStack>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack align="start" spacing={3}>
                    {bookmark.description && (
                      <Text fontSize="sm" color="gray.600" noOfLines={3}>
                        {bookmark.description}
                      </Text>
                    )}
                    
                    <HStack wrap="wrap" spacing={2}>
                      {bookmark.tags.map((tag) => (
                        <Badge key={tag} colorScheme="blue" variant="subtle" fontSize="xs">
                          {tag}
                        </Badge>
                      ))}
                    </HStack>
                    
                    <Text fontSize="xs" color="gray.500">
                      Saved {new Date(bookmark.created_at).toLocaleDateString()}
                    </Text>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Container>
  );
};

export default Bookmarks;
