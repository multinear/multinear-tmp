<script>
    // import { onMount } from 'svelte';
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
    } from "lucide-svelte";
    import LineChart from "$lib/components/LineChart.svelte";
    // import BarChart from './BarChart.svelte';

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
            model: "v1.2.3",
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
            model: "v1.2.3",
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
            model: "v1.2.2",
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
            model: "v1.2.2",
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
            model: "v1.2.1",
            score: 0.87,
            totalTests: 510,
            pass: 444,
            fail: 60,
            regression: 6,
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
</script>

<div class="container mx-auto p-4 space-y-6">
    <h1 class="text-3xl font-bold">Dashboard Overview</h1>

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
                            <Select.Item value="today">Today</Select.Item>
                            <Select.Item value="week">This Week</Select.Item>
                            <Select.Item value="month">This Month</Select.Item>
                            <Select.Item value="custom"
                                >Custom Range</Select.Item
                            >
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
                            <Select.Item value="v1.2.3">v1.2.3</Select.Item>
                            <Select.Item value="v1.2.2">v1.2.2</Select.Item>
                            <Select.Item value="v1.2.1">v1.2.1</Select.Item>
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
                            <Select.Item value="main">main</Select.Item>
                            <Select.Item value="develop">develop</Select.Item>
                            <Select.Item value="feature-x"
                                >feature-x</Select.Item
                            >
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
                            <Select.Item value="all">All Tests</Select.Item>
                            <Select.Item value="security"
                                >Security Tests</Select.Item
                            >
                            <Select.Item value="performance"
                                >Performance Tests</Select.Item
                            >
                            <Select.Item value="functionality"
                                >Functionality Tests</Select.Item
                            >
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
                                <div
                                    class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700"
                                >
                                    <div
                                        class="bg-green-600 h-2.5 rounded-full"
                                        style="width: {(run.pass /
                                            run.totalTests) *
                                            100}%"
                                    ></div>
                                    <div
                                        class="bg-yellow-400 h-2.5 rounded-full"
                                        style="width: {(run.fail /
                                            run.totalTests) *
                                            100}%; margin-top: -0.625rem"
                                    ></div>
                                    <div
                                        class="bg-red-600 h-2.5 rounded-full"
                                        style="width: {(run.regression /
                                            run.totalTests) *
                                            100}%; margin-top: -0.625rem"
                                    ></div>
                                </div>
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
</div>
