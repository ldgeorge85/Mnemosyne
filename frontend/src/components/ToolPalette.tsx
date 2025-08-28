/**
 * Tool Palette Component
 * 
 * Allows manual selection of tools to use in conversation.
 * Displays available tools with metadata and selection state.
 */

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Wrench,
  Calculator,
  Calendar,
  FileJson,
  Type,
  Hash,
  Users,
  Brain,
  ChevronDown,
  ChevronUp,
  Sparkles
} from 'lucide-react';

export interface Tool {
  name: string;
  display_name: string;
  description: string;
  category: 'simple' | 'agent' | 'external' | 'composite';
  capabilities: string[];
  selected?: boolean;
}

interface ToolPaletteProps {
  onToolsChange?: (selectedTools: string[]) => void;
  className?: string;
}

// Icon mapping for tools
const TOOL_ICONS: Record<string, React.FC<any>> = {
  calculator: Calculator,
  datetime: Calendar,
  json_formatter: FileJson,
  text_formatter: Type,
  word_counter: Hash,
  shadow_council: Brain,
  forum_of_echoes: Users,
};

// Category colors
const CATEGORY_COLORS: Record<string, string> = {
  simple: 'bg-blue-100 text-blue-800',
  agent: 'bg-purple-100 text-purple-800',
  external: 'bg-green-100 text-green-800',
  composite: 'bg-orange-100 text-orange-800',
};

const ToolPalette: React.FC<ToolPaletteProps> = ({ onToolsChange, className }) => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [selectedTools, setSelectedTools] = useState<Set<string>>(new Set());
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState(true);

  // Mock tool data - in production, fetch from API
  useEffect(() => {
    // Simulate fetching tools from backend
    const mockTools: Tool[] = [
      {
        name: 'calculator',
        display_name: 'Calculator',
        description: 'Perform mathematical calculations',
        category: 'simple',
        capabilities: ['arithmetic', 'algebra', 'expressions'],
      },
      {
        name: 'datetime',
        display_name: 'Date & Time',
        description: 'Date and time operations',
        category: 'simple',
        capabilities: ['current time', 'date math', 'timezones'],
      },
      {
        name: 'json_formatter',
        display_name: 'JSON Formatter',
        description: 'Format and validate JSON data',
        category: 'simple',
        capabilities: ['format', 'validate', 'minify'],
      },
      {
        name: 'text_formatter',
        display_name: 'Text Formatter',
        description: 'Format and transform text',
        category: 'simple',
        capabilities: ['case conversion', 'formatting', 'cleanup'],
      },
      {
        name: 'word_counter',
        display_name: 'Word Counter',
        description: 'Count words and analyze text',
        category: 'simple',
        capabilities: ['word count', 'character count', 'statistics'],
      },
      {
        name: 'shadow_council',
        display_name: 'Shadow Council',
        description: 'Consult technical and strategic experts',
        category: 'agent',
        capabilities: ['technical analysis', 'strategic planning', 'critical evaluation'],
      },
      {
        name: 'forum_of_echoes',
        display_name: 'Forum of Echoes',
        description: 'Engage philosophical perspectives',
        category: 'agent',
        capabilities: ['philosophical inquiry', 'ethical analysis', 'multiple perspectives'],
      },
    ];
    
    setTools(mockTools);
    setLoading(false);
  }, []);

  const toggleTool = (toolName: string) => {
    const newSelected = new Set(selectedTools);
    if (newSelected.has(toolName)) {
      newSelected.delete(toolName);
    } else {
      newSelected.add(toolName);
    }
    setSelectedTools(newSelected);
    onToolsChange?.(Array.from(newSelected));
  };

  const toggleAll = (category?: string) => {
    const categoryTools = category 
      ? tools.filter(t => t.category === category)
      : tools;
    
    const allSelected = categoryTools.every(t => selectedTools.has(t.name));
    
    const newSelected = new Set(selectedTools);
    categoryTools.forEach(tool => {
      if (allSelected) {
        newSelected.delete(tool.name);
      } else {
        newSelected.add(tool.name);
      }
    });
    
    setSelectedTools(newSelected);
    onToolsChange?.(Array.from(newSelected));
  };

  // Group tools by category
  const toolsByCategory = tools.reduce((acc, tool) => {
    if (!acc[tool.category]) acc[tool.category] = [];
    acc[tool.category].push(tool);
    return acc;
  }, {} as Record<string, Tool[]>);

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-4">
          <div className="flex items-center justify-center text-muted-foreground">
            Loading tools...
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wrench className="h-5 w-5" />
            <CardTitle className="text-lg">Tool Palette</CardTitle>
            {selectedTools.size > 0 && (
              <Badge variant="secondary">{selectedTools.size} selected</Badge>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </CardHeader>
      
      {isExpanded && (
        <CardContent className="pt-0">
          <div className="space-y-4">
            {/* Simple Tools */}
            {toolsByCategory.simple && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-muted-foreground">Simple Tools</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleAll('simple')}
                    className="text-xs"
                  >
                    Toggle All
                  </Button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {toolsByCategory.simple.map(tool => {
                    const Icon = TOOL_ICONS[tool.name] || Wrench;
                    const isSelected = selectedTools.has(tool.name);
                    
                    return (
                      <div
                        key={tool.name}
                        className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-colors ${
                          isSelected ? 'bg-primary/10 border-primary' : 'hover:bg-muted'
                        }`}
                        onClick={() => toggleTool(tool.name)}
                      >
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={() => toggleTool(tool.name)}
                          onClick={(e) => e.stopPropagation()}
                        />
                        <Icon className="h-4 w-4 text-muted-foreground" />
                        <div className="flex-1">
                          <div className="text-sm font-medium">{tool.display_name}</div>
                          <div className="text-xs text-muted-foreground truncate">
                            {tool.description}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Agent Tools */}
            {toolsByCategory.agent && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium text-muted-foreground">Agent Tools</h3>
                    <Sparkles className="h-3 w-3 text-purple-600" />
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleAll('agent')}
                    className="text-xs"
                  >
                    Toggle All
                  </Button>
                </div>
                <div className="space-y-2">
                  {toolsByCategory.agent.map(tool => {
                    const Icon = TOOL_ICONS[tool.name] || Brain;
                    const isSelected = selectedTools.has(tool.name);
                    
                    return (
                      <div
                        key={tool.name}
                        className={`flex items-start gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${
                          isSelected ? 'bg-primary/10 border-primary' : 'hover:bg-muted'
                        }`}
                        onClick={() => toggleTool(tool.name)}
                      >
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={() => toggleTool(tool.name)}
                          onClick={(e) => e.stopPropagation()}
                          className="mt-0.5"
                        />
                        <Icon className="h-5 w-5 text-purple-600 mt-0.5" />
                        <div className="flex-1">
                          <div className="font-medium">{tool.display_name}</div>
                          <div className="text-sm text-muted-foreground">
                            {tool.description}
                          </div>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {tool.capabilities.slice(0, 3).map(cap => (
                              <Badge key={cap} variant="outline" className="text-xs">
                                {cap}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Auto-select recommendation */}
            <div className="pt-2 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  Tools can also be auto-selected based on your query
                </span>
                <Button variant="ghost" size="sm" onClick={() => setSelectedTools(new Set())}>
                  Clear All
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default ToolPalette;