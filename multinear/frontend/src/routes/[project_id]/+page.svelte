<script lang="ts">
    import { page } from '$app/stores';
    import * as Card from "$lib/components/ui/card";
    import * as Table from "$lib/components/ui/table";
    import * as Alert from "$lib/components/ui/alert";
    import { Badge } from "$lib/components/ui/badge";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import * as Select from "$lib/components/ui/select";
    import {
        AlertCircle,
        CheckCircle2,
        XCircle,
        Bookmark,
        FileEdit,
        Play,
    } from "lucide-svelte";
    import LineChart from "$lib/components/LineChart.svelte";
    // import BarChart from './BarChart.svelte';
    import { Loader2 } from "lucide-svelte";
    import { startExperiment, getJobStatus } from '$lib/api';
    import type { JobResponse } from '$lib/api';
    import * as Tooltip from "$lib/components/ui/tooltip";

    import { projects, projectsLoading, projectsError } from '$lib/stores/projects';

    const projectId = $page.params.project_id;
    
    $: currentProject = $projects.find(p => p.id === projectId);

    let searchTerm = "";

    const summaryStats = {
        totalRuns: 1250,
        avgEvalScore: 0.85,
        regressions: 15,
        securityIssues: 3,
    };

    const recentRuns = [
        {
            id: "RUN-001",
            date: "2024-03-15 14:30",
            revision: "a1b2c3d",
            model: "gpt4o",
            score: 0.92,
            totalTests: 500,
            pass: 460,
            fail: 35,
            regression: 5,
            bookmarked: true,
        },
        {
            id: "RUN-002",
            date: "2024-03-15 12:15",
            revision: "e4f5g6h",
            model: "gpt4o",
            score: 0.88,
            totalTests: 480,
            pass: 422,
            fail: 50,
            regression: 8,
            noted: true,
        },
        {
            id: "RUN-003",
            date: "2024-03-14 18:45",
            revision: "i7j8k9l",
            model: "sonnet-3.5",
            score: 0.79,
            totalTests: 520,
            pass: 411,
            fail: 95,
            regression: 14,
        },
        {
            id: "RUN-004",
            date: "2024-03-14 10:30",
            revision: "m1n2o3p",
            model: "gpt4o-mini",
            score: 0.95,
            totalTests: 490,
            pass: 465,
            fail: 20,
            regression: 5,
        },
        {
            id: "RUN-005",
            date: "2024-03-13 16:20",
            revision: "q4r5s6t",
            model: "haiku-3.5",
            score: 0.87,
            totalTests: 510,
            pass: 444,
            fail: 60,
            regression: 0,
        },
    ];

    const alerts = [
        {
            type: "regression",
            message: "Regression detected in security tests for RUN-003",
        },
        {
            type: "security",
            message: "Potential security vulnerability found in RUN-002",
        },
        {
            type: "improvement",
            message: "Significant improvement in evaluation score for RUN-004",
        },
    ];

    const trendData = [
        {
            date: "2024-03-10",
            score: 0.82,
            totalTests: 450,
            pass: 369,
            fail: 72,
            regression: 9,
        },
        {
            date: "2024-03-11",
            score: 0.85,
            totalTests: 460,
            pass: 391,
            fail: 60,
            regression: 9,
        },
        {
            date: "2024-03-12",
            score: 0.81,
            totalTests: 470,
            pass: 380,
            fail: 80,
            regression: 10,
        },
        {
            date: "2024-03-13",
            score: 0.87,
            totalTests: 480,
            pass: 417,
            fail: 55,
            regression: 8,
        },
        {
            date: "2024-03-14",
            score: 0.9,
            totalTests: 490,
            pass: 441,
            fail: 44,
            regression: 5,
        },
        {
            date: "2024-03-15",
            score: 0.88,
            totalTests: 500,
            pass: 440,
            fail: 50,
            regression: 10,
        },
    ];

    const lineChartData = {
        labels: trendData.map((d) => d.date),
        datasets: [
            {
                label: "Score",
                data: trendData.map((d) => d.score),
                borderColor: "#8884d8",
                fill: false,
            },
        ],
    };

    /*    const barChartData = {
        labels: trendData.map(d => d.date),
        datasets: [
            {
                label: 'Pass',
                data: trendData.map(d => d.pass),
                backgroundColor: '#82ca9d',
            },
            {
                label: 'Fail',
                data: trendData.map(d => d.fail),
                backgroundColor: '#ffc658',
            },
            {
                label: 'Regression',
                data: trendData.map(d => d.regression),
                backgroundColor: '#ff8042',
            }
        ]
    };*/

    const options = {
        responsive: true,
        maintainAspectRatio: false,
    };

    // Add these filter value arrays after recentRuns definition
    const modelVersions = [...new Set(recentRuns.map(run => run.model))];
    const codeRevisions = [...new Set(recentRuns.map(run => run.revision))];
    const dateRanges = ["Today", "This Week", "This Month", "Custom Range"];
    const testGroups = ["All Tests", "Security Tests", "Performance Tests", "Functionality Tests"];

    let currentJob: string | null = null;
    let jobStatus: string | null = null;
    let jobDetails: JobResponse | null = null;
    let taskStatusCounts: Record<string, number> = {};

    async function handleStartExperiment() {
        try {
            const data = await startExperiment(projectId);
            currentJob = data.job_id;
            jobStatus = 'started';

            // Start polling
            while (jobStatus !== 'completed' && jobStatus !== 'not_found') {
                await new Promise(r => setTimeout(r, 1000));
                const statusData = await getJobStatus(projectId, currentJob);
                jobStatus = statusData.status;
                jobDetails = statusData;
                
                // Calculate status counts
                if (statusData.task_status_map) {
                    taskStatusCounts = Object.values(statusData.task_status_map).reduce((acc, status) => {
                        acc[status] = (acc[status] || 0) + 1;
                        return acc;
                    }, {} as Record<string, number>);
                }
            }
        } catch (error) {
            console.error('Error:', error);
            jobStatus = 'error';
        }
    }
</script>

<div class="container mx-auto p-4 space-y-6">
    {#if $projectsLoading}
        <div class="flex items-center justify-center h-[50vh] text-gray-500">
            <div class="flex items-center gap-2">
                <Loader2 class="h-6 w-6 animate-spin" />
                <span>Loading project details...</span>
            </div>
        </div>
    {:else if $projectsError}
        <div class="flex items-center justify-center h-[50vh] text-gray-500">
            <Card.Root class="border-red-200 bg-red-50 w-96">
                <Card.Header>
                    <Card.Title class="text-red-800">Error</Card.Title>
                    <Card.Description class="text-red-600">
                        {$projectsError}
                        <p class="pt-1">Check if API is running</p>
                    </Card.Description>
                </Card.Header>
                <Card.Footer class="flex justify-end">
                    <Button 
                        variant="outline" 
                        class="border-red-200 text-red-800 hover:bg-red-100"
                        on:click={() => window.location.reload()}
                    >
                        Try Again
                    </Button>
                </Card.Footer>
            </Card.Root>
        </div>
    {:else if !currentProject}
        <div class="flex items-center justify-center h-[50vh] text-gray-500">
            <Card.Root class="border-yellow-200 bg-yellow-50 w-96 space-y-4">
                <Card.Header>
                    <Card.Title class="text-yellow-800">Project Not Found</Card.Title>
                    <Card.Description class="text-yellow-600 pt-2">
                        The project "{projectId}" could not be found.
                    </Card.Description>
                </Card.Header>
                <Card.Footer class="flex justify-end">
                    <Button 
                        variant="outline" 
                        class="border-yellow-200 text-yellow-800 hover:bg-yellow-100"
                        on:click={() => window.history.back()}
                    >
                        Go Back
                    </Button>
                </Card.Footer>
            </Card.Root>
        </div>
    {:else}
        <div class="flex justify-between items-center">
            <h1 class="text-3xl font-bold">Dashboard: {currentProject.name}</h1>
            {#if currentJob && jobStatus !== 'completed' && jobStatus !== 'error'}
                <div class="flex items-center gap-2">
                    <Loader2 class="h-4 w-4 animate-spin" />
                    <span class="text-gray-500">{jobStatus}</span>
                </div>
            {:else}
                <Button variant="primary" on:click={handleStartExperiment} class="flex items-center gap-2">
                    <Play class="h-4 w-4" />
                    Run Experiment
                </Button>
            {/if}
        </div>

        {#if currentJob}
            <div class="border rounded-lg p-4 bg-gray-50">
                <div class="flex items-center gap-4">
                    <span class="font-medium">Latest Run:</span>
                    <span>{currentJob}</span>
                    <span class="text-gray-500">Status: {jobStatus}</span>
                </div>
                {#if jobDetails}
                    <div class="mt-2">
                        <div class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 relative">
                            <div 
                                class="h-4 rounded-sm transition-all duration-300 bg-blue-600" 
                                style="width: {jobStatus === 'completed' ? '100' : (jobDetails.current_task! / jobDetails.total_tasks * 100)}%"
                            ></div>
                            
                            {#if jobDetails.task_status_map}
                                {#each Object.entries(jobDetails.task_status_map) as [taskId, status]}
                                    {#if status === 'failed'}
                                        <div 
                                            class="absolute top-0 h-4 bg-red-500"
                                            style="width: {100 / jobDetails.total_tasks}%; left: {(parseInt(taskId.split('_')[1]) / jobDetails.total_tasks) * 100}%"
                                        ></div>
                                    {:else if status === 'completed'}
                                        <div 
                                            class="absolute top-0 h-4 bg-green-500"
                                            style="width: {100 / jobDetails.total_tasks}%; left: {(parseInt(taskId.split('_')[1]) / jobDetails.total_tasks) * 100}%"
                                        ></div>
                                    {/if}
                                {/each}
                            {/if}
                        </div>
                        <div class="flex justify-between mt-1 text-sm text-gray-500">
                            <span>{jobDetails?.current_task || 0} / {jobDetails?.total_tasks || 0}</span>
                            <div class="flex gap-8">
                                {#if jobDetails.task_status_map}
                                    <div class="text-sm text-gray-500 flex flex-wrap gap-2">
                                        {#each Object.entries(taskStatusCounts) as [status, count]}
                                            {#if count > 0}
                                                <span class="inline-flex items-center gap-1">
                                                    <div class="w-2 h-2 rounded-full {
                                                        status === 'completed' ? 'bg-green-500' : 
                                                        status === 'running' ? 'bg-blue-500' :
                                                        status === 'failed' ? 'bg-red-500' : 'bg-gray-500'
                                                    }"></div>
                                                    {status}: {count}
                                                </span>
                                            {/if}
                                        {/each}
                                    </div>
                                {/if}
                                <span>{jobStatus === 'completed' ? '100' : Math.round((jobDetails?.current_task || 0) / (jobDetails?.total_tasks || 1) * 100)}%</span>
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        {/if}

        <!-- Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card.Root>
                <Card.Header
                    class="flex flex-row items-center justify-between space-y-0 pb-2"
                >
                    <Card.Title class="text-sm font-medium">Total Runs</Card.Title>
                </Card.Header>
                <Card.Content>
                    <div class="text-2xl font-bold">{summaryStats.totalRuns}</div>
                </Card.Content>
            </Card.Root>
            <Card.Root>
                <Card.Header
                    class="flex flex-row items-center justify-between space-y-0 pb-2"
                >
                    <Card.Title class="text-sm font-medium">Regressions</Card.Title>
                </Card.Header>
                <Card.Content>
                    <div class="text-2xl font-bold text-yellow-600">
                        {summaryStats.regressions}
                    </div>
                </Card.Content>
            </Card.Root>
            <Card.Root>
                <Card.Header
                    class="flex flex-row items-center justify-between space-y-0 pb-2"
                >
                    <Card.Title class="text-sm font-medium"
                        >Security Issues</Card.Title
                    >
                </Card.Header>
                <Card.Content>
                    <div class="text-2xl font-bold text-red-600">
                        {summaryStats.securityIssues}
                    </div>
                </Card.Content>
            </Card.Root>
        </div>

        <!-- Filters and Controls -->
        <Card.Root>
            <Card.Header>
                <Card.Title>Filters and Controls</Card.Title>
            </Card.Header>
            <Card.Content class="flex flex-wrap gap-4">
                <div class="flex flex-col space-y-1.5">
                    <Label for="date-range">Date Range</Label>
                    <Select.Root portal={null}>
                        <Select.Trigger class="w-[180px]" id="date-range">
                            <Select.Value placeholder="Select date range" />
                        </Select.Trigger>
                        <Select.Content>
                            <Select.Group>
                                {#each dateRanges as range}
                                    <Select.Item value={range.toLowerCase()}>{range}</Select.Item>
                                {/each}
                            </Select.Group>
                        </Select.Content>
                        <Select.Input name="dateRange" />
                    </Select.Root>
                </div>
                <div class="flex flex-col space-y-1.5">
                    <Label for="model-version">Model Version</Label>
                    <Select.Root portal={null}>
                        <Select.Trigger class="w-[180px]" id="model-version">
                            <Select.Value placeholder="Select model version" />
                        </Select.Trigger>
                        <Select.Content>
                            <Select.Group>
                                {#each modelVersions as version}
                                    <Select.Item value={version}>{version}</Select.Item>
                                {/each}
                            </Select.Group>
                        </Select.Content>
                        <Select.Input name="modelVersion" />
                    </Select.Root>
                </div>
                <div class="flex flex-col space-y-1.5">
                    <Label for="code-revision">Code Revision</Label>
                    <Select.Root portal={null}>
                        <Select.Trigger class="w-[180px]" id="code-revision">
                            <Select.Value placeholder="Select code revision" />
                        </Select.Trigger>
                        <Select.Content>
                            <Select.Group>
                                {#each codeRevisions as revision}
                                    <Select.Item value={revision}>{revision}</Select.Item>
                                {/each}
                            </Select.Group>
                        </Select.Content>
                        <Select.Input name="codeRevision" />
                    </Select.Root>
                </div>
                <div class="flex flex-col space-y-1.5">
                    <Label for="test-group">Test Group</Label>
                    <Select.Root portal={null}>
                        <Select.Trigger class="w-[180px]" id="test-group">
                            <Select.Value placeholder="Select test group" />
                        </Select.Trigger>
                        <Select.Content>
                            <Select.Group>
                                {#each testGroups as group}
                                    <Select.Item value={group.toLowerCase().replace(' ', '-')}>{group}</Select.Item>
                                {/each}
                            </Select.Group>
                        </Select.Content>
                        <Select.Input name="testGroup" />
                    </Select.Root>
                </div>
                <div class="flex flex-col space-y-1.5 flex-grow">
                    <Label for="search">Search</Label>
                    <Input
                        id="search"
                        placeholder="Search by Run ID, name, or metadata"
                        bind:value={searchTerm}
                    />
                </div>
            </Card.Content>
        </Card.Root>

        <!-- Recent Runs -->
        <Card.Root>
            <Card.Header>
                <Card.Title>Recent Runs</Card.Title>
                <Card.Description
                    >Latest experiment runs and their key metadata</Card.Description
                >
            </Card.Header>
            <Card.Content>
                <Table.Root>
                    <Table.Caption>
                        <!-- Recent experiment runs and their key metadata. -->
                        <a href="/experiments">View all runs</a>
                    </Table.Caption>
                    <Table.Header>
                        <Table.Row>
                            <Table.Head>Run ID</Table.Head>
                            <Table.Head>Date & Time</Table.Head>
                            <Table.Head>Code Revision</Table.Head>
                            <Table.Head>Model Version</Table.Head>
                            <Table.Head>Total Tests</Table.Head>
                            <Table.Head>Evaluation Score</Table.Head>
                            <Table.Head>Test Results</Table.Head>
                            <Table.Head>Actions</Table.Head>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {#each recentRuns as run}
                            <Table.Row class="group">
                                <Table.Cell class="font-medium">{run.id}</Table.Cell
                                >
                                <Table.Cell>{run.date}</Table.Cell>
                                <Table.Cell>{run.revision}</Table.Cell>
                                <Table.Cell>{run.model}</Table.Cell>
                                <Table.Cell>{run.totalTests}</Table.Cell>
                                <Table.Cell>
                                    <Badge
                                        variant={run.score >= 0.9
                                            ? "default"
                                            : run.score >= 0.8
                                              ? "outline"
                                              : "destructive"}
                                    >
                                        {run.score.toFixed(2)}
                                    </Badge>
                                </Table.Cell>
                                <Table.Cell>
                                    <Tooltip.Root>
                                        <Tooltip.Trigger class="w-full">
                                            <div
                                                class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700"
                                            >
                                                <div
                                                    class="bg-green-600 h-4 rounded-sm"
                                                    style="width: {Math.max((run.pass / run.totalTests) * 100, run.pass > 0 ? 5 : 0)}%"
                                                ></div>
                                                <div
                                                    class="bg-red-600 h-4 rounded-sm"
                                                    style="width: {Math.max((run.fail / run.totalTests) * 100, run.fail > 0 ? 5 : 0)}%; margin-top: -1rem"
                                                ></div>
                                                <div
                                                    class="bg-yellow-400 h-4 rounded-sm"
                                                    style="width: {Math.max((run.regression / run.totalTests) * 100, run.regression > 0 ? 5 : 0)}%; margin-top: -1rem"
                                                ></div>
                                            </div>
                                        </Tooltip.Trigger>
                                        <Tooltip.Content>
                                            <div class="space-y-1">
                                                <div class="flex items-center gap-2">
                                                    <div class="w-3 h-3 bg-green-600 rounded-full"></div>
                                                    <span>Pass: {run.pass} <span class="text-gray-400">({((run.pass / run.totalTests) * 100).toFixed(1)}%)</span></span>
                                                </div>
                                                <div class="flex items-center gap-2">
                                                    <div class="w-3 h-3 bg-red-600 rounded-full"></div>
                                                    <span>Fail: {run.fail} <span class="text-gray-400">({((run.fail / run.totalTests) * 100).toFixed(1)}%)</span></span>
                                                </div>
                                                {#if run.regression > 0}
                                                    <div class="flex items-center gap-2">
                                                        <div class="w-3 h-3 bg-yellow-400 rounded-full"></div>
                                                        <span>Regression: {run.regression} <span class="text-gray-400">({((run.regression / run.totalTests) * 100).toFixed(1)}%)</span></span>
                                                    </div>
                                                {/if}
                                                <div class="pt-1 border-t">
                                                    <span>Total: {run.totalTests}</span>
                                                </div>
                                            </div>
                                        </Tooltip.Content>
                                    </Tooltip.Root>
                                </Table.Cell>
                                <Table.Cell>
                                    <div
                                        class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        {#if run.bookmarked}
                                            <Bookmark
                                                class="h-4 w-4 text-blue-500"
                                            />
                                        {:else if run.noted}
                                            <FileEdit
                                                class="h-4 w-4 text-green-500"
                                            />
                                        {:else}
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                class="h-8 w-8 p-0"
                                            >
                                                <Bookmark class="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                class="h-8 w-8 p-0"
                                            >
                                                <FileEdit class="h-4 w-4" />
                                            </Button>
                                        {/if}
                                    </div>
                                </Table.Cell>
                            </Table.Row>
                        {/each}
                    </Table.Body>
                </Table.Root>
            </Card.Content>
        </Card.Root>

        <!-- Key Alerts and Notifications -->
        <Card.Root>
            <Card.Header>
                <Card.Title>Key Alerts and Notifications</Card.Title>
            </Card.Header>
            <Card.Content class="space-y-4">
                {#each alerts as alert, index (index)}
                    <Alert.Root
                        variant={alert.type === "improvement"
                            ? "default"
                            : "destructive"}
                    >
                        {#if alert.type === "regression"}
                            <AlertCircle class="h-4 w-4" />
                        {:else if alert.type === "security"}
                            <XCircle class="h-4 w-4" />
                        {:else if alert.type === "improvement"}
                            <CheckCircle2 class="h-4 w-4" />
                        {/if}
                        <Alert.Title
                            >{alert.type.charAt(0).toUpperCase() +
                                alert.type.slice(1)}</Alert.Title
                        >
                        <Alert.Description>{alert.message}</Alert.Description>
                    </Alert.Root>
                {/each}
            </Card.Content>
        </Card.Root>

        <!-- Visualizations -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Trend Graphs -->
            <Card.Root>
                <Card.Header>
                    <Card.Title>Evaluation Score Trend</Card.Title>
                </Card.Header>
                <Card.Content>
                    <div class="h-[300px]">
                        <LineChart data={lineChartData} {options} />
                    </div>
                </Card.Content>
            </Card.Root>

            <!-- Tests per Run and Distribution Trend -->
            <Card.Root>
                <Card.Header>
                    <Card.Title>Tests per Run and Distribution Trend</Card.Title>
                </Card.Header>
                <Card.Content>
                    <div class="h-[300px]">
                        <!-- <BarChart chartData={barChartData} chartOptions={options} /> -->
                    </div>
                </Card.Content>
            </Card.Root>
        </div>
    {/if}
</div>
