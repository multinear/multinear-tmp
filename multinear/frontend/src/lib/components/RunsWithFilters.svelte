<script lang="ts">
    import { 
        Loader2,
        AlertCircle,
        // Bookmark,
    } from "lucide-svelte";
    import { goto } from '$app/navigation';

    import * as Card from "$lib/components/ui/card";
    import * as Table from "$lib/components/ui/table";
    import * as Alert from "$lib/components/ui/alert";
    import { Badge } from "$lib/components/ui/badge";
    // import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import * as Select from "$lib/components/ui/select";
    import * as Tooltip from "$lib/components/ui/tooltip";
    import type { RecentRun } from "$lib/api";
    import { selectedProjectId } from "$lib/stores/projects";

    // Props passed from the parent component
    export let runsList: RecentRun[];
    export let isLoading: boolean;
    export let loadingError: string | null;
    export let showViewAll: boolean = false;

    $: modelVersions = [...new Set(runsList.map(run => run.model))];
    $: codeRevisions = [...new Set(runsList.map(run => run.revision))];

    const dateRanges = ["Today", "This Week", "This Month", "Custom Range"];
    const testGroups = ["All Tests", "Security Tests", "Performance Tests", "Functionality Tests"];
    let searchTerm: string;

    function handleRunSelect(runId: string) {
        goto(`/run#${$selectedProjectId}/r:${runId}`);
    }

</script>

<!-- Filters and Controls -->
<Card.Root>
    <Card.Header>
        <Card.Title>Filters and Controls</Card.Title>
    </Card.Header>
    <Card.Content class="flex flex-wrap gap-4">
        <!-- Date Range Filter -->
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
        
        <!-- Model Version Filter -->
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
        
        <!-- Code Revision Filter -->
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
        
        <!-- Test Group Filter -->
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
        
        <!-- Search Input -->
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
        <Card.Description>Latest experiment runs and their status</Card.Description>
    </Card.Header>
    <Card.Content>
        {#if isLoading}
            <div class="flex items-center justify-center py-8 text-gray-500">
                <div class="flex items-center gap-2">
                    <Loader2 class="h-6 w-6 animate-spin" />
                    <span>Loading recent runs...</span>
                </div>
            </div>
        {:else if loadingError}
            <Alert.Root variant="destructive">
                <AlertCircle class="h-4 w-4" />
                <Alert.Title>Error loading recent runs</Alert.Title>
                <Alert.Description>{loadingError}</Alert.Description>
            </Alert.Root>
        {:else}
            <Table.Root>
                {#if showViewAll}
                    <Table.Caption>
                        <a href="/experiments#{$selectedProjectId}">View all runs</a>
                    </Table.Caption>
                {/if}
                <Table.Header>
                    <Table.Row>
                        <Table.Head>Run ID</Table.Head>
                        <Table.Head>Date & Time</Table.Head>
                        <Table.Head>Code Revision</Table.Head>
                        <Table.Head>Model Version</Table.Head>
                        <Table.Head>Total Tests</Table.Head>
                        <Table.Head>Evaluation Score</Table.Head>
                        <Table.Head>Test Results</Table.Head>
                        <!-- <Table.Head>Actions</Table.Head> -->
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {#each runsList as run}
                        <Table.Row class="group cursor-pointer" on:click={() => handleRunSelect(run.id)}>
                            <Table.Cell class="font-medium">
                                <Tooltip.Root>
                                    <Tooltip.Trigger>{run.id.slice(-8)}</Tooltip.Trigger>
                                    <Tooltip.Content>
                                        <p>Run ID: {run.id}</p>
                                    </Tooltip.Content>
                                </Tooltip.Root>
                            </Table.Cell>
                            <Table.Cell>
                                {new Date(run.date).toLocaleString(undefined, {
                                    dateStyle: 'medium',
                                    timeStyle: 'short'
                                })}
                            </Table.Cell>
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
                                            class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 overflow-hidden flex"
                                        >
                                            <div
                                                class="bg-green-600 h-4 min-w-[5px]"
                                                style="width: {(run.pass / run.totalTests) * 100}%"
                                            ></div>
                                            {#if run.fail > 0}
                                            <div
                                                class="bg-red-600 h-4 min-w-[5px]"
                                                    style="width: {(run.fail / run.totalTests) * 100}%"
                                                ></div>
                                            {/if}
                                            {#if run.regression > 0}
                                                <div
                                                    class="bg-yellow-400 h-4 min-w-[5px]"
                                                    style="width: {(run.regression / run.totalTests) * 100}%"
                                                ></div>
                                            {/if}
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
                            <!-- 
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
                            -->
                        </Table.Row>
                    {/each}
                </Table.Body>
            </Table.Root>
        {/if}
    </Card.Content>
</Card.Root>
