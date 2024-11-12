<script>
    import { onMount } from 'svelte';
    import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@shadcn/svelte/card";
    import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@shadcn/svelte/table";
    import { Alert, AlertDescription, AlertTitle } from "@shadcn/svelte/alert";
    import { Badge } from "@shadcn/svelte/badge";
    import { Button } from "@shadcn/svelte/button";
    import { Input } from "@shadcn/svelte/input";
    import { Label } from "@shadcn/svelte/label";
    import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@shadcn/svelte/select";
    import { AlertCircle, CheckCircle2, XCircle, Bookmark, FileEdit } from "@shadcn/svelte-icons";
    import { Bar, BarChart, Line, LineChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, Cell } from 'recharts';
    import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@shadcn/svelte/chart";
  
    let searchTerm = '';
  
    const summaryStats = {
      totalRuns: 1250,
      avgEvalScore: 0.85,
      regressions: 15,
      securityIssues: 3
    };
  
    const recentRuns = [
      { id: 'RUN-001', date: '2024-03-15 14:30', revision: 'a1b2c3d', model: 'v1.2.3', score: 0.92, totalTests: 500, pass: 460, fail: 35, regression: 5, bookmarked: true },
      { id: 'RUN-002', date: '2024-03-15 12:15', revision: 'e4f5g6h', model: 'v1.2.3', score: 0.88, totalTests: 480, pass: 422, fail: 50, regression: 8, noted: true },
      { id: 'RUN-003', date: '2024-03-14 18:45', revision: 'i7j8k9l', model: 'v1.2.2', score: 0.79, totalTests: 520, pass: 411, fail: 95, regression: 14 },
      { id: 'RUN-004', date: '2024-03-14 10:30', revision: 'm1n2o3p', model: 'v1.2.2', score: 0.95, totalTests: 490, pass: 465, fail: 20, regression: 5 },
      { id: 'RUN-005', date: '2024-03-13 16:20', revision: 'q4r5s6t', model: 'v1.2.1', score: 0.87, totalTests: 510, pass: 444, fail: 60, regression: 6 },
    ];
  
    const alerts = [
      { type: 'regression', message: 'Regression detected in security tests for RUN-003' },
      { type: 'security', message: 'Potential security vulnerability found in RUN-002' },
      { type: 'improvement', message: 'Significant improvement in evaluation score for RUN-004' },
    ];
  
    const trendData = [
      { date: '2024-03-10', score: 0.82, totalTests: 450, pass: 369, fail: 72, regression: 9 },
      { date: '2024-03-11', score: 0.85, totalTests: 460, pass: 391, fail: 60, regression: 9 },
      { date: '2024-03-12', score: 0.81, totalTests: 470, pass: 380, fail: 80, regression: 10 },
      { date: '2024-03-13', score: 0.87, totalTests: 480, pass: 417, fail: 55, regression: 8 },
      { date: '2024-03-14', score: 0.90, totalTests: 490, pass: 441, fail: 44, regression: 5 },
      { date: '2024-03-15', score: 0.88, totalTests: 500, pass: 440, fail: 50, regression: 10 },
    ];
  </script>
  
  <div class="container mx-auto p-4 space-y-6">
    <h1 class="text-3xl font-bold">Dashboard Overview</h1>
  
    <!-- Summary Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total Runs</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{summaryStats.totalRuns}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Regressions</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-yellow-600">{summaryStats.regressions}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Security Issues</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-red-600">{summaryStats.securityIssues}</div>
        </CardContent>
      </Card>
    </div>
  
    <!-- Filters and Controls -->
    <Card>
      <CardHeader>
        <CardTitle>Filters and Controls</CardTitle>
      </CardHeader>
      <CardContent class="flex flex-wrap gap-4">
        <div class="flex flex-col space-y-1.5">
          <Label for="date-range">Date Range</Label>
          <Select>
            <SelectTrigger id="date-range">
              <SelectValue placeholder="Select date range" />
            </SelectTrigger>
            <SelectContent position="popper">
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
              <SelectItem value="custom">Custom Range</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex flex-col space-y-1.5">
          <Label for="model-version">Model Version</Label>
          <Select>
            <SelectTrigger id="model-version">
              <SelectValue placeholder="Select model version" />
            </SelectTrigger>
            <SelectContent position="popper">
              <SelectItem value="v1.2.3">v1.2.3</SelectItem>
              <SelectItem value="v1.2.2">v1.2.2</SelectItem>
              <SelectItem value="v1.2.1">v1.2.1</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex flex-col space-y-1.5">
          <Label for="code-revision">Code Revision</Label>
          <Select>
            <SelectTrigger id="code-revision">
              <SelectValue placeholder="Select code revision" />
            </SelectTrigger>
            <SelectContent position="popper">
              <SelectItem value="main">main</SelectItem>
              <SelectItem value="develop">develop</SelectItem>
              <SelectItem value="feature-x">feature-x</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex flex-col space-y-1.5">
          <Label for="test-group">Test Group</Label>
          <Select>
            <SelectTrigger id="test-group">
              <SelectValue placeholder="Select test group" />
            </SelectTrigger>
            <SelectContent position="popper">
              <SelectItem value="all">All Tests</SelectItem>
              <SelectItem value="security">Security Tests</SelectItem>
              <SelectItem value="performance">Performance Tests</SelectItem>
              <SelectItem value="functionality">Functionality Tests</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex flex-col space-y-1.5 flex-grow">
          <Label for="search">Search</Label>
          <Input
            id="search"
            placeholder="Search by Run ID, name, or metadata"
            bind:value={searchTerm}
          />
        </div>
      </CardContent>
    </Card>
  
    <!-- Recent Runs -->
    <Card>
      <CardHeader>
        <CardTitle>Recent Runs</CardTitle>
        <CardDescription>Latest experiment runs and their key metadata</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Run ID</TableHead>
              <TableHead>Date & Time</TableHead>
              <TableHead>Code Revision</TableHead>
              <TableHead>Model Version</TableHead>
              <TableHead>Evaluation Score</TableHead>
              <TableHead>Total Tests</TableHead>
              <TableHead>Test Results</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {#each recentRuns as run}
              <TableRow class="group">
                <TableCell class="font-medium">{run.id}</TableCell>
                <TableCell>{run.date}</TableCell>
                <TableCell>{run.revision}</TableCell>
                <TableCell>{run.model}</TableCell>
                <TableCell>
                  <Badge variant={run.score >= 0.9 ? "success" : run.score >= 0.8 ? "warning" : "destructive"}>
                    {run.score.toFixed(2)}
                  </Badge>
                </TableCell>
                <TableCell>{run.totalTests}</TableCell>
                <TableCell>
                  <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                    <div class="bg-green-600 h-2.5 rounded-full" style="width: {(run.pass / run.totalTests) * 100}%"></div>
                    <div class="bg-yellow-400 h-2.5 rounded-full" style="width: {(run.fail / run.totalTests) * 100}%; margin-top: -0.625rem"></div>
                    <div class="bg-red-600 h-2.5 rounded-full" style="width: {(run.regression / run.totalTests) * 100}%; margin-top: -0.625rem"></div>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    {#if run.bookmarked}
                      <Bookmark class="h-4 w-4 text-blue-500" />
                    {:else if run.noted}
                      <FileEdit class="h-4 w-4 text-green-500" />
                    {:else}
                      <Button variant="ghost" size="icon" class="h-8 w-8 p-0">
                        <Bookmark class="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" class="h-8 w-8 p-0">
                        <FileEdit class="h-4 w-4" />
                      </Button>
                    {/if}
                  </div>
                </TableCell>
              </TableRow>
            {/each}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  
    <!-- Key Alerts and Notifications -->
    <Card>
      <CardHeader>
        <CardTitle>Key Alerts and Notifications</CardTitle>
      </CardHeader>
      <CardContent class="space-y-4">
        {#each alerts as alert, index}
          <Alert key={index} variant={alert.type === 'improvement' ? 'default' : 'destructive'}>
            {#if alert.type === 'regression'}
              <AlertCircle class="h-4 w-4" />
            {:else if alert.type === 'security'}
              <XCircle class="h-4 w-4" />
            {:else if alert.type === 'improvement'}
              <CheckCircle2 class="h-4 w-4" />
            {/if}
            <AlertTitle>{alert.type.charAt(0).toUpperCase() + alert.type.slice(1)}</AlertTitle>
            <AlertDescription>{alert.message}</AlertDescription>
          </Alert>
        {/each}
      </CardContent>
    </Card>
  
    <!-- Visualizations -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Trend Graphs -->
      <Card>
        <CardHeader>
          <CardTitle>Evaluation Score Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              score: {
                label: "Evaluation Score",
                color: "hsl(var(--chart-1))",
              },
            }}
            class="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <XAxis dataKey="date" />
                <YAxis domain={[0.7, 1]} />
                <Tooltip content={<ChartTooltipContent />} />
                <Legend />
                <Line type="monotone" dataKey="score" stroke="var(--color-score)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
  
      <!-- Tests per Run and Distribution Trend -->
      <Card>
        <CardHeader>
          <CardTitle>Tests per Run and Distribution Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              pass: {
                label: "Pass",
                color: "hsl(var(--chart-1))",
              },
              fail: {
                label: "Fail",
                color: "hsl(var(--chart-2))",
              },
              regression: {
                label: "Regression",
                color: "hsl(var(--chart-3))",
              },
            }}
            class="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip content={<ChartTooltipContent />} />
                <Legend />
                <Bar dataKey="pass" stackId="a" fill="var(--color-pass)" />
                <Bar dataKey="fail" stackId="a" fill="var(--color-fail)" />
                <Bar dataKey="regression" stackId="a" fill="var(--color-regression)" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  </div>
  