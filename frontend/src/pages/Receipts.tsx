/**
 * Receipts Viewer Page
 * 
 * Displays transparency receipts for all system operations.
 * Provides filtering, searching, and detailed viewing of receipts.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, formatDistance } from 'date-fns';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Search, 
  Filter, 
  Eye, 
  Download, 
  Shield,
  Clock,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  Info
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContextSimple';
import { api } from '@/api';

interface Receipt {
  id: string;
  user_id: string;
  receipt_type: string;
  timestamp: string;
  action: string;
  entity_type?: string;
  entity_id?: string;
  context?: Record<string, any>;
  persona_mode?: string;
  worldview_profile?: Record<string, any>;
  decisions_made?: string[];
  confidence_score?: number;
  explanation?: string;
  privacy_impact?: string;
  user_visible: boolean;
}

interface ReceiptStats {
  total_receipts: number;
  by_type: Record<string, number>;
  by_entity: Record<string, number>;
  by_privacy_impact: Record<string, number>;
  by_persona_mode: Record<string, number>;
}

const receiptTypeColors: Record<string, string> = {
  'auth_login': 'bg-green-100 text-green-800',
  'auth_logout': 'bg-gray-100 text-gray-800',
  'memory_created': 'bg-blue-100 text-blue-800',
  'memory_updated': 'bg-yellow-100 text-yellow-800',
  'memory_deleted': 'bg-red-100 text-red-800',
  'task_created': 'bg-purple-100 text-purple-800',
  'task_completed': 'bg-green-100 text-green-800',
  'chat_message': 'bg-indigo-100 text-indigo-800',
  'trust_event': 'bg-orange-100 text-orange-800',
  'pattern_observation': 'bg-cyan-100 text-cyan-800',
};

const privacyImpactIcons = {
  'none': <CheckCircle className="w-4 h-4 text-green-600" />,
  'minimal': <Info className="w-4 h-4 text-blue-600" />,
  'moderate': <AlertCircle className="w-4 h-4 text-yellow-600" />,
  'significant': <AlertCircle className="w-4 h-4 text-orange-600" />,
  'critical': <AlertCircle className="w-4 h-4 text-red-600" />,
};

export default function Receipts() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [stats, setStats] = useState<ReceiptStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterEntity, setFilterEntity] = useState<string>('all');
  const [filterPrivacy, setFilterPrivacy] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month' | 'all'>('week');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    } else {
      fetchReceipts();
      fetchStats();
    }
  }, [isAuthenticated, navigate]);

  const fetchReceipts = async () => {
    try {
      setLoading(true);
      
      // Build query params
      const params = new URLSearchParams();
      if (filterType !== 'all') params.append('receipt_type', filterType);
      if (filterEntity !== 'all') params.append('entity_type', filterEntity);
      
      // Add date filter
      if (dateRange !== 'all') {
        const now = new Date();
        let startDate = new Date();
        
        switch (dateRange) {
          case 'today':
            startDate.setHours(0, 0, 0, 0);
            break;
          case 'week':
            startDate.setDate(now.getDate() - 7);
            break;
          case 'month':
            startDate.setMonth(now.getMonth() - 1);
            break;
        }
        
        params.append('start_date', startDate.toISOString());
      }
      
      params.append('limit', '100');
      
      const response = await api.get(`/receipts?${params.toString()}`);
      setReceipts(response.data);
    } catch (error) {
      console.error('Failed to fetch receipts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/receipts/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const filteredReceipts = receipts.filter(receipt => {
    if (searchTerm && !receipt.action.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    if (filterPrivacy !== 'all' && receipt.privacy_impact !== filterPrivacy) {
      return false;
    }
    return true;
  });

  const viewReceiptDetails = (receipt: Receipt) => {
    setSelectedReceipt(receipt);
    setDetailsOpen(true);
  };

  const exportReceipts = () => {
    const dataStr = JSON.stringify(filteredReceipts, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `receipts_${new Date().toISOString()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-primary" />
            <div>
              <h1 className="text-3xl font-bold">Transparency Receipts</h1>
              <p className="text-muted-foreground">
                Complete record of all system operations and decisions
              </p>
            </div>
          </div>
          <Button onClick={exportReceipts} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Receipts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_receipts}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Most Common</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Object.entries(stats.by_type)
                    .sort(([, a], [, b]) => b - a)[0]?.[0]
                    ?.replace(/_/g, ' ') || 'None'}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Privacy Impact</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  {stats.by_privacy_impact?.none > (stats.total_receipts * 0.8) ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                  )}
                  <span className="text-2xl font-bold">
                    {stats.by_privacy_impact?.none > (stats.total_receipts * 0.8) ? 'Low' : 'Moderate'}
                  </span>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Active Persona</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Object.entries(stats.by_persona_mode || {})
                    .sort(([, a], [, b]) => b - a)[0]?.[0] || 'Confidant'}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search actions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger>
                <SelectValue placeholder="Receipt Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="auth_login">Login</SelectItem>
                <SelectItem value="auth_logout">Logout</SelectItem>
                <SelectItem value="memory_created">Memory Created</SelectItem>
                <SelectItem value="task_created">Task Created</SelectItem>
                <SelectItem value="chat_message">Chat Message</SelectItem>
                <SelectItem value="trust_event">Trust Event</SelectItem>
                <SelectItem value="pattern_observation">Pattern Observation</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterEntity} onValueChange={setFilterEntity}>
              <SelectTrigger>
                <SelectValue placeholder="Entity Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Entities</SelectItem>
                <SelectItem value="memory">Memory</SelectItem>
                <SelectItem value="task">Task</SelectItem>
                <SelectItem value="chat">Chat</SelectItem>
                <SelectItem value="trust">Trust</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterPrivacy} onValueChange={setFilterPrivacy}>
              <SelectTrigger>
                <SelectValue placeholder="Privacy Impact" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="none">None</SelectItem>
                <SelectItem value="minimal">Minimal</SelectItem>
                <SelectItem value="moderate">Moderate</SelectItem>
                <SelectItem value="significant">Significant</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={dateRange} onValueChange={(v: any) => setDateRange(v)}>
              <SelectTrigger>
                <SelectValue placeholder="Date Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="today">Today</SelectItem>
                <SelectItem value="week">Past Week</SelectItem>
                <SelectItem value="month">Past Month</SelectItem>
                <SelectItem value="all">All Time</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Receipts List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Receipts</CardTitle>
          <CardDescription>
            {filteredReceipts.length} receipts found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[600px]">
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading receipts...
              </div>
            ) : filteredReceipts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No receipts found matching your filters
              </div>
            ) : (
              <div className="space-y-4">
                {filteredReceipts.map((receipt) => (
                  <div
                    key={receipt.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => viewReceiptDetails(receipt)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge 
                            className={receiptTypeColors[receipt.receipt_type] || 'bg-gray-100 text-gray-800'}
                          >
                            {receipt.receipt_type.replace(/_/g, ' ')}
                          </Badge>
                          {receipt.persona_mode && (
                            <Badge variant="outline">
                              {receipt.persona_mode}
                            </Badge>
                          )}
                          {receipt.privacy_impact && (
                            <div className="flex items-center gap-1">
                              {privacyImpactIcons[receipt.privacy_impact] || privacyImpactIcons.minimal}
                            </div>
                          )}
                        </div>
                        
                        <p className="font-medium mb-1">{receipt.action}</p>
                        
                        {receipt.explanation && (
                          <p className="text-sm text-muted-foreground mb-2">
                            {receipt.explanation}
                          </p>
                        )}
                        
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDistance(new Date(receipt.timestamp), new Date(), { addSuffix: true })}
                          </div>
                          {receipt.entity_type && (
                            <span>
                              {receipt.entity_type}
                            </span>
                          )}
                          {receipt.confidence_score && (
                            <span>
                              Confidence: {Math.round(receipt.confidence_score * 100)}%
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <Button variant="ghost" size="sm">
                        <Eye className="w-4 h-4 mr-1" />
                        View
                        <ChevronRight className="w-4 h-4 ml-1" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Receipt Details Dialog */}
      <Dialog open={detailsOpen} onOpenChange={setDetailsOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Receipt Details</DialogTitle>
            <DialogDescription>
              Complete transparency record for this operation
            </DialogDescription>
          </DialogHeader>
          
          {selectedReceipt && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Receipt ID</p>
                  <p className="font-mono text-xs">{selectedReceipt.id}</p>
                </div>
                
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Timestamp</p>
                  <p>{format(new Date(selectedReceipt.timestamp), 'PPpp')}</p>
                </div>
                
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Type</p>
                  <Badge className={receiptTypeColors[selectedReceipt.receipt_type] || ''}>
                    {selectedReceipt.receipt_type.replace(/_/g, ' ')}
                  </Badge>
                </div>
                
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Privacy Impact</p>
                  <div className="flex items-center gap-2">
                    {privacyImpactIcons[selectedReceipt.privacy_impact || 'minimal']}
                    <span className="capitalize">{selectedReceipt.privacy_impact || 'Minimal'}</span>
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Action</p>
                <p className="font-medium">{selectedReceipt.action}</p>
              </div>
              
              {selectedReceipt.explanation && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Explanation</p>
                  <p className="text-sm">{selectedReceipt.explanation}</p>
                </div>
              )}
              
              {selectedReceipt.decisions_made && selectedReceipt.decisions_made.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Decisions Made</p>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {selectedReceipt.decisions_made.map((decision, idx) => (
                      <li key={idx}>{decision}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {selectedReceipt.context && Object.keys(selectedReceipt.context).length > 0 && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Context</p>
                  <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-48">
                    {JSON.stringify(selectedReceipt.context, null, 2)}
                  </pre>
                </div>
              )}
              
              {selectedReceipt.persona_mode && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Persona Mode</p>
                  <Badge variant="outline">{selectedReceipt.persona_mode}</Badge>
                </div>
              )}
              
              <div className="pt-4 flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    const dataStr = JSON.stringify(selectedReceipt, null, 2);
                    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                    const exportFileDefaultName = `receipt_${selectedReceipt.id}.json`;
                    
                    const linkElement = document.createElement('a');
                    linkElement.setAttribute('href', dataUri);
                    linkElement.setAttribute('download', exportFileDefaultName);
                    linkElement.click();
                  }}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Receipt
                </Button>
                <Button onClick={() => setDetailsOpen(false)}>Close</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}