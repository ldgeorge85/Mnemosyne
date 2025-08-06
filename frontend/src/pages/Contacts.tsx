import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Button,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  Avatar,
  Badge,
  IconButton,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Input,
  InputGroup,
  InputLeftElement,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Link
} from '@chakra-ui/react';
import { AddIcon, SearchIcon, PhoneIcon, EmailIcon, EditIcon, DeleteIcon, SettingsIcon } from '@chakra-ui/icons';
import { listContacts, deleteContact, type Contact } from '../api/contacts';



/**
 * Contacts page component
 * 
 * Displays user's contacts with search and management features
 */
const Contacts: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const toast = useToast();

  // Fetch from API
  useEffect(() => {
    const loadContacts = async () => {
      try {
        const response = await listContacts();
        if (response.success) {
          setContacts(response.data);
          return;
        }
        throw new Error('Failed to fetch contacts');
        /* legacy mock
        const mockContacts: Contact[] = [
          {
            id: '1',
            name: 'Alice Johnson',
            email: 'alice.johnson@example.com',
            phone: '+1 (555) 123-4567',
            company: 'Tech Corp',
            role: 'Senior Developer',
            tags: ['colleague', 'frontend', 'react'],
            notes: 'Great React developer, worked on the dashboard project together.',
            last_contact: '2025-06-15T10:30:00Z',
            created_at: '2025-06-01T09:00:00Z'
          },
          {
            id: '2',
            name: 'Bob Smith',
            email: 'bob.smith@startup.io',
            phone: '+1 (555) 987-6543',
            company: 'Startup Inc',
            role: 'Product Manager',
            tags: ['client', 'product', 'agile'],
            notes: 'Product manager for the mobile app project. Very detail-oriented.',
            last_contact: '2025-06-14T14:15:00Z',
            created_at: '2025-05-20T11:30:00Z'
          },
          {
            id: '3',
            name: 'Carol Davis',
            email: 'carol.davis@design.co',
            company: 'Design Co',
            role: 'UX Designer',
            tags: ['designer', 'ux', 'freelancer'],
            notes: 'Talented UX designer, available for freelance projects.',
            last_contact: '2025-06-10T16:45:00Z',
            created_at: '2025-05-15T13:20:00Z'
          },
          {
            id: '4',
            name: 'David Wilson',
            email: 'david.wilson@enterprise.com',
            phone: '+1 (555) 456-7890',
            company: 'Enterprise Solutions',
            role: 'DevOps Engineer',
            tags: ['devops', 'aws', 'kubernetes'],
            notes: 'DevOps expert, helped with infrastructure setup.',
            last_contact: '2025-06-12T09:20:00Z',
            created_at: '2025-05-10T10:15:00Z'
          }
        ];
        
        */
      } catch (err) {
        setError('Failed to load contacts');
      } finally {
        setLoading(false);
      }
    };

    loadContacts();
  }, []);

  const handleDeleteContact = async (contactId: string) => {
    try {
      const response = await deleteContact(contactId);
      if (response.success && response.data.success) {
        setContacts(prev => prev.filter((contact) => contact.id !== contactId));
      } else {
        throw new Error('Failed to delete');
      }
      toast({
        title: 'Contact deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Failed to delete contact',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.role?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  const getTagColor = (tag: string) => {
    const colors = ['blue', 'green', 'purple', 'orange', 'teal', 'pink'];
    const index = tag.length % colors.length;
    return colors[index];
  };

  if (loading) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading contacts...</Text>
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
          <Heading size="lg">Contacts</Heading>
          <Button leftIcon={<AddIcon />} colorScheme="blue" size="sm">
            Add Contact
          </Button>
        </HStack>

        <InputGroup maxW="md">
          <InputLeftElement pointerEvents="none">
            <SearchIcon color="gray.300" />
          </InputLeftElement>
          <Input
            placeholder="Search contacts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>

        {filteredContacts.length === 0 ? (
          <Box textAlign="center" py={10}>
            <Text fontSize="lg" color="gray.500" mb={4}>
              {searchTerm ? 'No contacts match your search.' : 'No contacts added yet.'}
            </Text>
            {!searchTerm && (
              <Button leftIcon={<AddIcon />} colorScheme="blue">
                Add Your First Contact
              </Button>
            )}
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {filteredContacts.map((contact) => (
              <Card key={contact.id} variant="outline">
                <CardBody>
                  <VStack spacing={4}>
                    <HStack justify="space-between" w="100%" align="start">
                      <HStack spacing={3}>
                        <Avatar
                          size="md"
                          name={contact.name}
                          src={contact.avatar}
                        />
                        <VStack align="start" spacing={0}>
                          <Text fontWeight="bold" fontSize="lg">
                            {contact.name}
                          </Text>
                          {contact.role && (
                            <Text fontSize="sm" color="gray.600">
                              {contact.role}
                            </Text>
                          )}
                          {contact.company && (
                            <Text fontSize="sm" color="gray.500">
                              {contact.company}
                            </Text>
                          )}
                        </VStack>
                      </HStack>
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          aria-label="Contact options"
                          icon={<SettingsIcon />}
                          variant="ghost"
                          size="sm"
                        />
                        <MenuList>
                          <MenuItem icon={<EditIcon />}>Edit Contact</MenuItem>
                          <MenuItem 
                            icon={<DeleteIcon />} 
                            color="red.500"
                            onClick={() => handleDeleteContact(contact.id)}
                          >
                            Delete Contact
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </HStack>

                    <VStack align="stretch" spacing={2} w="100%">
                      {contact.email && (
                        <HStack>
                          <EmailIcon color="gray.500" />
                          <Link href={`mailto:${contact.email}`} fontSize="sm" color="blue.500">
                            {contact.email}
                          </Link>
                        </HStack>
                      )}
                      {contact.phone && (
                        <HStack>
                          <PhoneIcon color="gray.500" />
                          <Link href={`tel:${contact.phone}`} fontSize="sm" color="blue.500">
                            {contact.phone}
                          </Link>
                        </HStack>
                      )}
                    </VStack>

                    {contact.tags.length > 0 && (
                      <HStack wrap="wrap" spacing={2} justify="center">
                        {contact.tags.map((tag) => (
                          <Badge 
                            key={tag} 
                            colorScheme={getTagColor(tag)} 
                            variant="subtle" 
                            fontSize="xs"
                          >
                            {tag}
                          </Badge>
                        ))}
                      </HStack>
                    )}

                    {contact.notes && (
                      <Text fontSize="sm" color="gray.600" noOfLines={3} textAlign="center">
                        {contact.notes}
                      </Text>
                    )}

                    <Text fontSize="xs" color="gray.500" textAlign="center">
                      Last contact: {new Date(contact.last_contact).toLocaleDateString()}
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

export default Contacts;
