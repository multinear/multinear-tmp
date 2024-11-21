<script lang="ts">
    import { onMount } from 'svelte';
    import * as Card from "$lib/components/ui/card";
    import * as Table from "$lib/components/ui/table";
    import { Label } from "$lib/components/ui/label";
    import { Input } from "$lib/components/ui/input";
    import { Checkbox } from "$lib/components/ui/checkbox";
    import TimeAgo from '$lib/components/TimeAgo.svelte';
    import StatusFilter from '$lib/components/StatusFilter.svelte';
    import { formatDuration, intervalToDuration } from 'date-fns';

    import { filterTasks, getStatusCounts, getTaskStatus } from '$lib/utils/tasks';
    import { getSameTasks } from '$lib/api';
    // import type { TaskDetails } from '$lib/api';


    let projectId: string | null = null;
    let challengeId: string | null = null;

    let loading = true;
    let error: string | null = null;
    let tasks: any[] = [];
    //TaskDetails[] = [];

    async function loadTasks() {
        loading = true;
        error = null;
        try {
            tasks = await getSameTasks(projectId!, challengeId!);
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load tasks";
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        projectId = 'demo-bank-customer-support';
        challengeId = 'c44f74c212b1163506b411cf5e165e0cf7883eb23bf8b122c857baa32e1c055b';

        loadTasks();
    });


    let statusFilter = "";
    let searchTerm = "";
    let selectedTasks: Set<string> = new Set();

    $: filteredTasks = filterTasks(tasks, statusFilter, searchTerm);
    $: statusCounts = getStatusCounts(tasks);
    
    // Assuming all tasks have the same input since they're from the same challenge
    $: commonInput = tasks?.[0]?.task_input;
</script>

<div class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-4">
        <h1 class="text-3xl font-bold">Compare Tasks</h1>
    </div>

    {#if loading}
        <div class="text-center text-gray-500">Loading tasks...</div>
    {:else if error}
        <Card.Root class="border-red-200 bg-red-50">
            <Card.Header>
                <Card.Title class="text-red-800">Error</Card.Title>
                <Card.Description class="text-red-600">{error}</Card.Description>
            </Card.Header>
        </Card.Root>
    {:else if tasks.length}
        <div class="space-y-6">
            <!-- Common Input Card -->
            <Card.Root>
                <Card.Header>
                    <Card.Title>Common Input</Card.Title>
                    <Card.Description>
                        <div class="bg-white p-2 rounded border overflow-auto" style="white-space: pre-wrap;">
                            {typeof commonInput === 'object' && 'str' in commonInput 
                                ? commonInput.str 
                                : JSON.stringify(commonInput, null, 2)}
                        </div>
                    </Card.Description>
                </Card.Header>
            </Card.Root>

            <!-- Filters Card -->
            <Card.Root>
                <Card.Header>
                    <Card.Description>
                        <div class="grid grid-cols-2 gap-4">
                            <div class="space-y-1.5">
                                <Label for="search">Search</Label>
                                <Input
                                    id="search"
                                    placeholder="Search tasks..."
                                    bind:value={searchTerm}
                                />
                            </div>
                            
                            <StatusFilter 
                                bind:statusFilter
                                statusCounts={statusCounts}
                                totalCount={tasks.length}
                            />
                        </div>
                    </Card.Description>
                </Card.Header>
            </Card.Root>

            <!-- Tasks Table -->
            <Card.Root>
                <Card.Content>
                    <Table.Root>
                        <Table.Header>
                            <Table.Row>
                                <Table.Head class="w-[50px]">
                                    <Checkbox />
                                </Table.Head>
                                <Table.Head class="w-[50%]">Output</Table.Head>
                                <Table.Head>Details</Table.Head>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {#each filteredTasks as task}
                                {@const {isPassed, statusClass} = getTaskStatus(task)}
                                <Table.Row class={statusClass}>
                                    <Table.Cell>
                                        <Checkbox 
                                            checked={selectedTasks.has(task.id)}
                                            onCheckedChange={(checked) => {
                                                if (checked) {
                                                    selectedTasks.add(task.id);
                                                } else {
                                                    selectedTasks.delete(task.id);
                                                }
                                                selectedTasks = selectedTasks;
                                            }}
                                        />
                                    </Table.Cell>
                                    <Table.Cell>
                                        <div class="text-sm bg-white p-2 rounded border overflow-auto">
                                            {typeof task.task_output === 'object' && 'str' in task.task_output 
                                                ? task.task_output.str 
                                                : JSON.stringify(task.task_output, null, 2)}
                                        </div>
                                    </Table.Cell>
                                    <Table.Cell>
                                        <div class="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 items-center">
                                            <!-- Left column -->
                                            <div class="font-medium text-gray-500 text-sm">ID</div>
                                            <div class="font-mono text-sm">{task.id.slice(-8)}</div>

                                            <div class="font-medium text-gray-500 text-sm">Model</div>
                                            <div class="text-sm">{task.task_details.model}</div>

                                            <div class="font-medium text-gray-500 text-sm">Status</div>
                                            <div class="flex items-center gap-2">
                                                <span class={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                                                    ${task.status === 'completed' ? 'bg-green-100 text-green-800' : 
                                                    task.status === 'failed' ? 'bg-red-100 text-red-800' : 
                                                    'bg-gray-100 text-gray-800'}`}>
                                                    {task.status}
                                                </span>
                                                <div class="flex items-center gap-1">
                                                    <div class="w-16 bg-gray-200 rounded-sm h-2 overflow-hidden flex">
                                                        <div
                                                            class="h-2 min-w-[3px] {isPassed ? 'bg-green-600' : 'bg-red-600'}"
                                                            style="width: {(task.eval_score * 100).toFixed(0)}%"
                                                        ></div>
                                                    </div>
                                                    <div class="text-xs text-gray-600">
                                                        {(task.eval_score * 100).toFixed(0)}%
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="font-medium text-gray-500 text-sm">Time</div>
                                            <div class="flex items-center gap-3 text-sm text-gray-600">
                                                <TimeAgo date={task.created_at} />
                                                {#if task.finished_at}
                                                    <span class="text-gray-400">·</span>
                                                    <span>{formatDuration(
                                                        intervalToDuration({
                                                            start: new Date(task.created_at),
                                                            end: new Date(task.finished_at)
                                                        }),
                                                        { format: ['minutes', 'seconds'] }
                                                    )}</span>
                                                {/if}
                                            </div>

                                            {#if task.task_details.temperature || task.task_details.max_tokens}
                                                <div class="font-medium text-gray-500 text-sm">Parameters</div>
                                                <div class="flex gap-3 text-sm text-gray-600">
                                                    {#if task.task_details.temperature}
                                                        <span>temperature: {task.task_details.temperature}</span>
                                                    {/if}
                                                    {#if task.task_details.max_tokens}
                                                        {#if task.task_details.temperature}
                                                            <span class="text-gray-400">·</span>
                                                        {/if}
                                                        <span>max tokens: {task.task_details.max_tokens}</span>
                                                    {/if}
                                                </div>
                                            {/if}
                                        </div>
                                    </Table.Cell>
                                </Table.Row>
                            {/each}
                        </Table.Body>
                    </Table.Root>
                </Card.Content>
            </Card.Root>
        </div>
    {:else}
        <div class="text-center text-gray-500">No tasks found</div>
    {/if}
</div>
