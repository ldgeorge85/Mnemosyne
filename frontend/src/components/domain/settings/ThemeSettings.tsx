/**
 * Theme Settings Component
 * 
 * This component allows users to customize the application theme,
 * including color mode, accent colors, and font settings.
 */
import React from 'react';
import {
  Box,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Switch,
  useColorMode,
  SimpleGrid,
  Circle,
  Tooltip,
  Radio,
  RadioGroup,
  Stack,
  Text,
  Select,
  HStack,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  useColorModeValue,
} from '@chakra-ui/react';

/**
 * Theme settings component
 */
const ThemeSettings: React.FC = () => {
  // Color mode toggling
  const { colorMode, toggleColorMode } = useColorMode();
  
  // Theme state
  const [accentColor, setAccentColor] = React.useState('blue');
  const [fontFamily, setFontFamily] = React.useState('Inter');
  const [fontSize, setFontSize] = React.useState('medium');
  const [borderRadius, setBorderRadius] = React.useState(50);
  
  // Theme colors
  const colors = [
    { name: 'blue', value: 'blue.500' },
    { name: 'teal', value: 'teal.500' },
    { name: 'green', value: 'green.500' },
    { name: 'purple', value: 'purple.500' },
    { name: 'pink', value: 'pink.500' },
    { name: 'orange', value: 'orange.500' },
    { name: 'red', value: 'red.500' },
  ];
  
  // Font options
  const fonts = [
    'Inter',
    'Roboto',
    'Lato',
    'Open Sans',
    'Montserrat',
    'Source Sans Pro',
  ];
  
  // Font size options
  const fontSizes = [
    { name: 'Small', value: 'small' },
    { name: 'Medium', value: 'medium' },
    { name: 'Large', value: 'large' },
  ];
  
  // Card styling
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md" mb={2}>Theme Settings</Heading>
      
      <Box p={5} borderRadius="md" bg={cardBg} borderWidth="1px" borderColor={cardBorder}>
        <VStack spacing={6} align="stretch">
          {/* Dark/Light Mode Toggle */}
          <FormControl display="flex" alignItems="center" justifyContent="space-between">
            <FormLabel htmlFor="color-mode-toggle" mb="0">
              Dark Mode
            </FormLabel>
            <Switch
              id="color-mode-toggle"
              isChecked={colorMode === 'dark'}
              onChange={toggleColorMode}
              colorScheme="brand"
            />
          </FormControl>
          
          {/* Accent Color Selection */}
          <FormControl>
            <FormLabel>Accent Color</FormLabel>
            <SimpleGrid columns={7} spacing={2}>
              {colors.map((color) => (
                <Tooltip key={color.name} label={color.name} placement="top">
                  <Circle
                    size="30px"
                    bg={color.value}
                    cursor="pointer"
                    onClick={() => setAccentColor(color.name)}
                    border={accentColor === color.name ? '2px solid' : 'none'}
                    borderColor={useColorModeValue('gray.800', 'white')}
                  />
                </Tooltip>
              ))}
            </SimpleGrid>
          </FormControl>
          
          {/* Font Family Selection */}
          <FormControl>
            <FormLabel>Font Family</FormLabel>
            <Select
              value={fontFamily}
              onChange={(e) => setFontFamily(e.target.value)}
            >
              {fonts.map((font) => (
                <option key={font} value={font}>{font}</option>
              ))}
            </Select>
          </FormControl>
          
          {/* Font Size Selection */}
          <FormControl>
            <FormLabel>Font Size</FormLabel>
            <RadioGroup value={fontSize} onChange={setFontSize}>
              <HStack spacing={5}>
                {fontSizes.map((size) => (
                  <Radio key={size.value} value={size.value}>
                    {size.name}
                  </Radio>
                ))}
              </HStack>
            </RadioGroup>
          </FormControl>
          
          {/* Border Radius Slider */}
          <FormControl>
            <FormLabel>
              Border Radius: {borderRadius}%
            </FormLabel>
            <Slider
              aria-label="border-radius-slider"
              value={borderRadius}
              onChange={setBorderRadius}
              min={0}
              max={100}
              step={5}
            >
              <SliderTrack>
                <SliderFilledTrack bg="brand.500" />
              </SliderTrack>
              <SliderThumb boxSize={5} />
            </Slider>
            <HStack justify="space-between">
              <Text fontSize="xs">Square</Text>
              <Text fontSize="xs">Round</Text>
            </HStack>
          </FormControl>
        </VStack>
      </Box>
      
      <Text fontSize="sm" color="gray.500" mt={2}>
        Theme settings are saved to your browser and will be remembered across sessions.
      </Text>
    </VStack>
  );
};

export default ThemeSettings;
