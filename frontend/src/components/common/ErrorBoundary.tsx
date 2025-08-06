/**
 * Global Error Boundary Component
 * 
 * Catches JavaScript errors anywhere in the component tree and displays
 * a fallback UI instead of crashing the entire application.
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Heading,
  Text,
  Button,
  VStack,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Collapse,
  useColorModeValue
} from '@chakra-ui/react';
import { FiRefreshCw, FiAlertTriangle } from 'react-icons/fi';

/**
 * Error boundary props
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

/**
 * Error boundary state
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
}

/**
 * Error fallback component
 */
interface ErrorFallbackProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
  onToggleDetails: () => void;
  onReload: () => void;
  onGoHome: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorInfo,
  showDetails,
  onToggleDetails,
  onReload,
  onGoHome
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box
      minHeight="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      bg="gray.50"
      _dark={{ bg: 'gray.900' }}
      p={8}
    >
      <Box
        maxW="2xl"
        w="full"
        bg={bgColor}
        borderRadius="lg"
        border="1px"
        borderColor={borderColor}
        p={8}
        textAlign="center"
      >
        <VStack spacing={6}>
          {/* Error Icon */}
          <Box
            p={4}
            borderRadius="full"
            bg="red.100"
            _dark={{ bg: 'red.900', color: 'red.300' }}
            color="red.500"
          >
            <FiAlertTriangle size={48} />
          </Box>

          {/* Error Message */}
          <VStack spacing={2}>
            <Heading size="lg" color="red.600" _dark={{ color: 'red.400' }}>
              Something went wrong
            </Heading>
            <Text color="gray.600" _dark={{ color: 'gray.400' }}>
              An unexpected error occurred while rendering this page.
              Please try refreshing or go back to the home page.
            </Text>
          </VStack>

          {/* Error Alert */}
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            <Box>
              <AlertTitle>Error Details</AlertTitle>
              <AlertDescription>
                {error?.message || 'Unknown error occurred'}
              </AlertDescription>
            </Box>
          </Alert>

          {/* Action Buttons */}
          <VStack spacing={3} w="full">
            <Button
              leftIcon={<FiRefreshCw />}
              colorScheme="blue"
              onClick={onReload}
              size="lg"
              w="full"
            >
              Reload Page
            </Button>
            
            <Button
              variant="outline"
              onClick={onGoHome}
              size="lg"
              w="full"
            >
              Go to Home
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleDetails}
            >
              {showDetails ? 'Hide' : 'Show'} Technical Details
            </Button>
          </VStack>

          {/* Technical Details */}
          <Collapse in={showDetails} style={{ width: '100%' }}>
            <Box
              mt={4}
              p={4}
              bg="gray.100"
              _dark={{ bg: 'gray.700' }}
              borderRadius="md"
              textAlign="left"
            >
              <Text fontWeight="semibold" mb={2}>
                Error Stack:
              </Text>
              <Code
                display="block"
                whiteSpace="pre-wrap"
                p={3}
                bg="gray.50"
                _dark={{ bg: 'gray.800' }}
                borderRadius="md"
                fontSize="xs"
                maxH="200px"
                overflowY="auto"
              >
                {error?.stack || 'No stack trace available'}
              </Code>
              
              {errorInfo?.componentStack && (
                <>
                  <Text fontWeight="semibold" mt={4} mb={2}>
                    Component Stack:
                  </Text>
                  <Code
                    display="block"
                    whiteSpace="pre-wrap"
                    p={3}
                    bg="gray.50"
                    _dark={{ bg: 'gray.800' }}
                    borderRadius="md"
                    fontSize="xs"
                    maxH="200px"
                    overflowY="auto"
                  >
                    {errorInfo.componentStack}
                  </Code>
                </>
              )}
            </Box>
          </Collapse>
        </VStack>
      </Box>
    </Box>
  );
};

/**
 * Error Boundary Class Component
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    };
  }

  /**
   * Update state when an error is caught
   */
  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Handle error and log details
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log minimal error information for debugging
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error.message);
    }
    
    this.setState({
      error,
      errorInfo,
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Send error to monitoring service (e.g., Sentry)
    // if (window.Sentry) {
    //   window.Sentry.captureException(error, {
    //     contexts: {
    //       react: {
    //         componentStack: errorInfo.componentStack,
    //       },
    //     },
    //   });
    // }
  }

  /**
   * Toggle technical details visibility
   */
  toggleDetails = (): void => {
    this.setState(prevState => ({
      showDetails: !prevState.showDetails,
    }));
  };

  /**
   * Reload the page
   */
  handleReload = (): void => {
    window.location.reload();
  };

  /**
   * Navigate to home page
   */
  handleGoHome = (): void => {
    window.location.href = '/';
  };

  /**
   * Reset error state
   */
  resetError = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error fallback
      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          showDetails={this.state.showDetails}
          onToggleDetails={this.toggleDetails}
          onReload={this.handleReload}
          onGoHome={this.handleGoHome}
        />
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
