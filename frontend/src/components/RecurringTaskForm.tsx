/**
 * Recurring Task Form Component
 * 
 * Provides UI for creating and managing recurring tasks with pattern validation
 * and preview functionality.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  VStack,
  HStack,
  Text,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Badge,
  Divider,
  useToast,
  Spinner
} from '@chakra-ui/react';
import { validatePattern, createRecurringInstances, COMMON_PATTERNS, RecurringTaskPattern } from '../api/recurringTasks';

interface RecurringTaskFormProps {
  taskId?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

/**
 * Form component for creating recurring tasks
 */
const RecurringTaskForm: React.FC<RecurringTaskFormProps> = ({
  taskId,
  onSuccess,
  onCancel
}) => {
  const [pattern, setPattern] = useState<string>('');
  const [customPattern, setCustomPattern] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [patternValidation, setPatternValidation] = useState<RecurringTaskPattern | null>(null);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const toast = useToast();

  /**
   * Validate the current pattern and show preview
   */
  const validateCurrentPattern = async (patternToValidate: string) => {
    if (!patternToValidate.trim()) {
      setPatternValidation(null);
      return;
    }

    setIsValidating(true);
    try {
      const validation = await validatePattern(patternToValidate, 5);
      setPatternValidation(validation);
    } catch (error) {
      setPatternValidation({
        pattern: patternToValidate,
        is_valid: false,
        error_message: 'Failed to validate pattern'
      });
    } finally {
      setIsValidating(false);
    }
  };

  /**
   * Handle pattern selection change
   */
  const handlePatternChange = (selectedPattern: string) => {
    setPattern(selectedPattern);
    if (selectedPattern === 'custom') {
      validateCurrentPattern(customPattern);
    } else {
      validateCurrentPattern(selectedPattern);
    }
  };

  /**
   * Handle custom pattern input change
   */
  const handleCustomPatternChange = (value: string) => {
    setCustomPattern(value);
    if (pattern === 'custom') {
      validateCurrentPattern(value);
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!taskId) {
      toast({
        title: 'Error',
        description: 'Task ID is required to create recurring instances',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    const finalPattern = pattern === 'custom' ? customPattern : pattern;
    
    if (!finalPattern || !patternValidation?.is_valid) {
      toast({
        title: 'Invalid Pattern',
        description: 'Please select or enter a valid recurrence pattern',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    if (!startDate) {
      toast({
        title: 'Start Date Required',
        description: 'Please select a start date for the recurring series',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
      return;
    }

    setIsCreating(true);
    try {
      await createRecurringInstances(taskId, finalPattern, startDate, endDate || undefined);
      
      toast({
        title: 'Success',
        description: 'Recurring task series created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create recurring task series',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsCreating(false);
    }
  };

  /**
   * Set default start date to today
   */
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    setStartDate(today);
  }, []);

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <VStack spacing={4} align="stretch">
        <FormControl isRequired>
          <FormLabel>Recurrence Pattern</FormLabel>
          <Select
            placeholder="Select a recurrence pattern"
            value={pattern}
            onChange={(e) => handlePatternChange(e.target.value)}
          >
            {COMMON_PATTERNS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
            <option value="custom">Custom Pattern</option>
          </Select>
        </FormControl>

        {pattern === 'custom' && (
          <FormControl isRequired>
            <FormLabel>Custom Pattern</FormLabel>
            <Input
              placeholder="e.g., every 2 weeks, every monday,friday"
              value={customPattern}
              onChange={(e) => handleCustomPatternChange(e.target.value)}
            />
            <Text fontSize="sm" color="gray.500" mt={1}>
              Examples: "daily", "weekly", "every 2 days", "every monday,wednesday,friday"
            </Text>
          </FormControl>
        )}

        {/* Pattern Validation and Preview */}
        {isValidating && (
          <Box display="flex" alignItems="center" gap={2}>
            <Spinner size="sm" />
            <Text fontSize="sm">Validating pattern...</Text>
          </Box>
        )}

        {patternValidation && !isValidating && (
          <Alert status={patternValidation.is_valid ? 'success' : 'error'}>
            <AlertIcon />
            <Box>
              <AlertTitle>
                {patternValidation.is_valid ? 'Valid Pattern' : 'Invalid Pattern'}
              </AlertTitle>
              {patternValidation.error_message && (
                <AlertDescription>{patternValidation.error_message}</AlertDescription>
              )}
              {patternValidation.is_valid && patternValidation.preview_dates && (
                <Box mt={2}>
                  <Text fontSize="sm" fontWeight="semibold">Preview (next 5 occurrences):</Text>
                  <HStack spacing={2} flexWrap="wrap" mt={1}>
                    {patternValidation.preview_dates.map((date, index) => (
                      <Badge key={index} colorScheme="blue" fontSize="xs">
                        {new Date(date).toLocaleDateString()}
                      </Badge>
                    ))}
                  </HStack>
                </Box>
              )}
            </Box>
          </Alert>
        )}

        <Divider />

        <HStack spacing={4}>
          <FormControl isRequired>
            <FormLabel>Start Date</FormLabel>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </FormControl>

          <FormControl>
            <FormLabel>End Date (Optional)</FormLabel>
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={startDate}
            />
          </FormControl>
        </HStack>

        <HStack spacing={3} justifyContent="flex-end">
          {onCancel && (
            <Button variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            colorScheme="blue"
            isLoading={isCreating}
            loadingText="Creating..."
            isDisabled={!patternValidation?.is_valid || !startDate}
          >
            Create Recurring Series
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default RecurringTaskForm;
