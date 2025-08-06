/**
 * Chakra UI Theme Configuration
 * 
 * This file contains the theme configuration for the application,
 * including colors, fonts, and component styles.
 */
import { extendTheme, ThemeConfig } from '@chakra-ui/react';

// Color mode config
const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false,
  disableTransitionOnChange: false,
};

// Colors
const colors = {
  brand: {
    50: '#e6f1ff',
    100: '#cce3ff',
    200: '#99c8ff',
    300: '#66acff',
    400: '#3391ff',
    500: '#1f4287', // Primary brand color
    600: '#153163',
    700: '#0c213f',
    800: '#04101f',
    900: '#000509',
  },
  accent: {
    50: '#fff4e6',
    100: '#ffe8cc',
    200: '#ffd199',
    300: '#ffba66',
    400: '#ffa333',
    500: '#ff8c00', // Accent color
    600: '#cc7000',
    700: '#995400',
    800: '#663800',
    900: '#331c00',
  },
};

// Font configuration
const fonts = {
  heading: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  body: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  mono: 'SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
};

// Component specific styles
const components = {
  Button: {
    baseStyle: {
      fontWeight: 'semibold',
      borderRadius: 'md',
    },
    variants: {
      solid: (props: { colorScheme: string }) => ({
        bg: props.colorScheme === 'brand' ? 'brand.500' : `${props.colorScheme}.500`,
        color: 'white',
        _hover: {
          bg: props.colorScheme === 'brand' ? 'brand.600' : `${props.colorScheme}.600`,
        },
      }),
      outline: (props: { colorScheme: string }) => ({
        borderColor: props.colorScheme === 'brand' ? 'brand.500' : `${props.colorScheme}.500`,
        color: props.colorScheme === 'brand' ? 'brand.500' : `${props.colorScheme}.500`,
      }),
    },
    defaultProps: {
      colorScheme: 'brand',
    },
  },
  Heading: {
    baseStyle: {
      fontWeight: 'bold',
      color: 'gray.800',
      _dark: {
        color: 'gray.100',
      },
    },
  },
  Card: {
    baseStyle: {
      p: '6',
      bg: 'white',
      boxShadow: 'md',
      rounded: 'lg',
      _dark: {
        bg: 'gray.700',
      },
    },
  },
  // Add custom Textarea component configuration to prevent autosize-textarea conflict
  Textarea: {
    baseStyle: {
      fontFamily: 'body',
      borderRadius: 'md',
    },
    defaultProps: {
      focusBorderColor: 'brand.500',
      errorBorderColor: 'red.500',
      resize: 'vertical',
    },
  },
};

// Global styles
const styles = {
  global: (props: { colorMode: string }) => ({
    body: {
      bg: props.colorMode === 'dark' ? 'gray.800' : 'gray.50',
      color: props.colorMode === 'dark' ? 'white' : 'gray.800',
    },
  }),
};

// Create the extended theme
const theme = extendTheme({
  config,
  colors,
  fonts,
  components,
  styles,
});

export default theme;
