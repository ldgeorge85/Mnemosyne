/**
 * Recurring Task Instances Component
 * 
 * Displays and manages recurring task instances for a master task,
 * including the ability to view, edit, and delete individual instances.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  useToast,
  Text,
  VStack,
  HStack,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure
} from '@chakra-ui/react';
import { DeleteIcon, EditIcon, ViewIcon } from '@chakra-ui/icons';
import { getRecurringInstances, deleteRecurringSeries, RecurringTaskInstance } from '../api/recurringTasks';

interface RecurringTaskInstancesProps {
  masterTaskId: string;
  onInstanceUpdate?: () => void;
}

/**
 * Component to display and manage recurring task instances
 */
const RecurringTaskInstances: React.FC<RecurringTaskInstancesProps> = ({
  masterTaskId,
  onInstanceUpdate
}) => {
  const [instances, setInstances] = useState<RecurringTaskInstance[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingSeriesId, setDeletingSeriesId] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  /**
   * Fetch recurring task instances
   */
  const fetchInstances = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const fetchedInstances = await getRecurringInstances(masterTaskId);
      setInstances(fetchedInstances);
    } catch (err) {
      setError('Failed to fetch recurring task instances');
      console.error('Error fetching instances:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle deleting the entire recurring series
   */
  const handleDeleteSeries = async () => {
    setDeletingSeriesId(masterTaskId);
    
    try {
      await deleteRecurringSeries(masterTaskId);
      
      toast({
        title: 'Success',
        description: 'Recurring task series deleted successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
      
      setInstances([]);
      if (onInstanceUpdate) {
        onInstanceUpdate();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete recurring task series',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setDeletingSeriesId(null);
      onClose();
    }
  };

  /**
   * Get status color for badge
   */
  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'green';
      case 'in_progress':
        return 'blue';
      case 'pending':
        return 'yellow';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  /**
   * Load instances on component mount
   */
  useEffect(() => {
    if (masterTaskId) {
      fetchInstances();
    }
  }, [masterTaskId]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={8}>
        <Spinner size="lg" />
        <Text ml={3}>Loading recurring task instances...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (instances.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Text color="gray.500">No recurring task instances found.</Text>
        <Text fontSize="sm" color="gray.400" mt={2}>
          This task may not have a recurring series set up yet.
        </Text>
      </Box>
    );
  }

  return (
    <VStack spacing={4} align="stretch">
      <HStack justifyContent="space-between">
        <Text fontSize="lg" fontWeight="semibold">
          Recurring Task Instances ({instances.length})
        </Text>
        <Button
          size="sm"
          colorScheme="red"
          variant="outline"
          onClick={onOpen}
          leftIcon={<DeleteIcon />}
        >
          Delete Series
        </Button>
      </HStack>

      <Box overflowX="auto">
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Instance Date</Th>
              <Th>Title</Th>
              <Th>Status</Th>
              <Th>Created</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {instances.map((instance) => (
              <Tr key={instance.id}>
                <Td>
                  <Text fontWeight="medium">
                    {formatDate(instance.instance_date)}
                  </Text>
                </Td>
                <Td>
                  <Text>{instance.title}</Text>
                  {instance.description && (
                    <Text fontSize="sm" color="gray.500" noOfLines={1}>
                      {instance.description}
                    </Text>
                  )}
                </Td>
                <Td>
                  <Badge colorScheme={getStatusColor(instance.status)}>
                    {instance.status.replace('_', ' ')}
                  </Badge>
                </Td>
                <Td>
                  <Text fontSize="sm" color="gray.500">
                    {formatDate(instance.created_at)}
                  </Text>
                </Td>
                <Td>
                  <HStack spacing={1}>
                    <IconButton
                      aria-label="View instance"
                      icon={<ViewIcon />}
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        // TODO: Implement view instance details
                        toast({
                          title: 'View Instance',
                          description: 'Instance details view coming soon',
                          status: 'info',
                          duration: 2000,
                          isClosable: true
                        });
                      }}
                    />
                    <IconButton
                      aria-label="Edit instance"
                      icon={<EditIcon />}
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        // TODO: Implement edit instance
                        toast({
                          title: 'Edit Instance',
                          description: 'Instance editing coming soon',
                          status: 'info',
                          duration: 2000,
                          isClosable: true
                        });
                      }}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {/* Delete Series Confirmation Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Delete Recurring Series</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text>
              Are you sure you want to delete this entire recurring task series? 
              This will remove all {instances.length} instances and cannot be undone.
            </Text>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="red"
              onClick={handleDeleteSeries}
              isLoading={deletingSeriesId === masterTaskId}
              loadingText="Deleting..."
            >
              Delete Series
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default RecurringTaskInstances;
