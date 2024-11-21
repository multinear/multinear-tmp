<script lang="ts">
    import {
        Loader2,
        AlertCircle,
        CheckCircle2,
        XCircle,
    } from 'lucide-svelte';
    import * as Card from '$lib/components/ui/card';
    import * as Alert from '$lib/components/ui/alert';
    import { Button } from '$lib/components/ui/button';
    // import BarChart from './BarChart.svelte';
    import { getRecentRuns } from '$lib/api';
    import type { RecentRun } from '$lib/api';
    import { projects, projectsLoading, projectsError, selectedProjectId } from '$lib/stores/projects';
    import LineChart from '$lib/components/LineChart.svelte';
    import RunsWithFilters from '$lib/components/RunsWithFilters.svelte';
    import JobStatus from '$lib/components/JobStatus.svelte';
    import JobControls from '$lib/components/JobControls.svelte';


    $: currentProject = $projects.find(p => p.id === $selectedProjectId);

    const summaryStats = {
        totalRuns: 1250,
        avgEvalScore: 0.85,
        regressions: 15,
        securityIssues: 3,
    };

    let recentRuns: RecentRun[] = [];
    let recentRunsError: string | null = null;
    let recentRunsLoading = false;

    async function loadRecentRuns() {
        recentRunsLoading = true;
        recentRunsError = null;
        try {
            recentRuns = await getRecentRuns($selectedProjectId);
        } catch (error) {
            console.error('Error loading recent runs:', error);
            recentRunsError = error instanceof Error ? error.message : 'Unknown error';
        } finally {
            recentRunsLoading = false;
        }
    }

    $: if (currentProject) {
        loadRecentRuns();
    }

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
                        The project "{$selectedProjectId}" could not be found.
                    </Card.Description>
                </Card.Header>
                <Card.Footer class="flex justify-end">
                    <Button 
                        variant="outline" 
                        class="border-yellow-200 text-yellow-800 hover:bg-yellow-100"
                        on:click={() => window.location.href = '/'}
                    >
                        Go Back
                    </Button>
                </Card.Footer>
            </Card.Root>
        </div>
    {:else}
        <div class="flex justify-between items-center">
            <h1 class="text-3xl font-bold -mb-2 -mt-2">Dashboard: {currentProject.name}</h1>
            <JobControls reloadRecentRuns={loadRecentRuns} />
        </div>

        <JobStatus />

        <!-- Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card.Root>
                <Card.Content class="flex items-center justify-between py-4">
                    <span class="text-md font-medium">Total Runs</span>
                    <div class="text-2xl font-bold">{summaryStats.totalRuns}</div>
                </Card.Content>
            </Card.Root>
            <Card.Root>
                <Card.Content class="flex items-center justify-between py-4">
                    <span class="text-md font-medium">Regressions</span>
                    <div class="text-2xl font-bold text-yellow-600">
                        {summaryStats.regressions}
                    </div>
                </Card.Content>
            </Card.Root>
            <Card.Root>
                <Card.Content class="flex items-center justify-between py-4">
                    <span class="text-md font-medium">Security Issues</span>
                    <div class="text-2xl font-bold text-red-600">
                        {summaryStats.securityIssues}
                    </div>
                </Card.Content>
            </Card.Root>
        </div>

        <!-- List of Runs Component -->
        <RunsWithFilters
            runsList={recentRuns}
            isLoading={recentRunsLoading}
            loadingError={recentRunsError}
            showViewAll={true}
        />

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
