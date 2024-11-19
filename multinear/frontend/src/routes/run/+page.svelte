<script lang="ts">
    // import { onMount } from 'svelte';
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    // import { page } from '$app/stores';
    import { getRunDetails } from '$lib/api';
    import { selectedRunId } from '$lib/stores/projects';
    import * as Table from "$lib/components/ui/table";
    import { Label } from "$lib/components/ui/label";
    import { Input } from "$lib/components/ui/input";
    import * as Select from "$lib/components/ui/select";

    let runId: string | null = null;
    let runDetails: any = null;
    let loading = true;
    let error: string | null = null;

    $: {
        if ($selectedRunId) loadRunDetails($selectedRunId);
    }

    async function loadRunDetails(id: string) {
        loading = true;
        error = null;
        try {
            runDetails = await getRunDetails(id);
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load run details";
            console.error(e);
        } finally {
            loading = false;
        }
    }

    let statusFilter = "";
    let searchTerm = "";
    
    $: filteredTasks = runDetails?.tasks.filter((task: any) => {
        if (statusFilter && task.status !== statusFilter) return false;
        
        if (searchTerm) {
            const search = searchTerm.toLowerCase();
            return (
                task.id.toLowerCase().includes(search) ||
                task.status.toLowerCase().includes(search) ||
                (task.result && JSON.stringify(task.result).toLowerCase().includes(search)) ||
                (task.error && task.error.toLowerCase().includes(search))
            );
        }
        
        return true;
    });    

    // Calculate status counts
    $: statusCounts = runDetails?.tasks.reduce((acc: Record<string, number>, task: { status: string }) => {
        acc[task.status] = (acc[task.status] || 0) + 1;
        return acc;
    }, {} as Record<string, number>) || {};

    $: availableStatuses = Object.entries(statusCounts)
        .filter(([_, count]: [any, any]) => count > 0)
        .map(([status]) => status);
</script>

<div class="container mx-auto p-4">
    <h1 class="text-4xl font-bold mb-8">Run: {$selectedRunId.slice(-8)}</h1>

    {#if loading}
        <div class="text-center text-gray-500">Loading run details...</div>
    {:else if error}
        <Card.Root class="border-red-200 bg-red-50">
            <Card.Header>
                <Card.Title class="text-red-800">Error</Card.Title>
                <Card.Description class="text-red-600">
                    {error}
                </Card.Description>
            </Card.Header>
            <Card.Footer class="flex justify-end">
                <Button 
                    variant="outline" 
                    class="border-red-200 text-red-800 hover:bg-red-100"
                    on:click={() => loadRunDetails(runId!)}
                >
                    Try Again
                </Button>
            </Card.Footer>
        </Card.Root>
    {:else if runDetails}
        <div class="space-y-8">
            <!-- Summary Card -->
            <Card.Root class="pb-8">
                <Card.Header>
                    <Card.Title class="flex justify-between items-center">
                        <span>Run Summary</span>
                        <span class="text-sm text-gray-500">
                            {new Date(runDetails.date).toLocaleString()}
                        </span>
                    </Card.Title>
                    <Card.Description>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                            <div class="space-y-1">
                                <div class="text-sm text-gray-500">Status</div>
                                <div class="font-semibold">{runDetails.status}</div>
                            </div>
                            <div class="space-y-1">
                                <div class="text-sm text-gray-500">Project</div>
                                <div class="font-semibold">{runDetails.project.name}</div>
                            </div>
                            <div class="space-y-1">
                                <div class="text-sm text-gray-500">Total Tasks</div>
                                <div class="font-semibold">{runDetails.tasks.length}</div>
                            </div>
                            <div class="space-y-1">
                                <div class="text-sm text-gray-500">Model</div>
                                <div class="font-semibold">{runDetails.details.model || 'N/A'}</div>
                            </div>
                        </div>
                        
                        <!-- Filters Row -->
                        <div class="flex gap-8 mt-6 items-end">
                            {#if availableStatuses.length > 1}
                                <div class="flex flex-col space-y-1.5">
                                    <Label>Filter</Label>
                                    <div class="flex gap-2">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            class={`
                                                ${statusFilter === "" ? 'bg-gray-100 border-gray-200' : ''}
                                            `}
                                            on:click={() => statusFilter = ""}
                                        >
                                            All tasks ({runDetails.tasks.length})
                                        </Button>
                                        {#each availableStatuses as status}
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                class={`
                                                    ${status === 'completed' ? 'text-green-700' : 
                                                      status === 'failed' ? 'text-red-700' : 
                                                      'text-gray-700'}
                                                    ${statusFilter === status ? 
                                                      status === 'completed' ? 'bg-green-50 border-green-200' :
                                                      status === 'failed' ? 'bg-red-50 border-red-200' :
                                                      'bg-gray-50 border-gray-200' : ''}
                                                `}
                                                on:click={() => statusFilter = status}
                                            >
                                                {status} ({statusCounts[status]})
                                            </Button>
                                        {/each}
                                    </div>
                                </div>
                            {/if}
                            
                            <div class="flex flex-col space-y-1.5 flex-grow">
                                <Label for="search">Search</Label>
                                <Input
                                    id="search"
                                    placeholder="Search tasks..."
                                    bind:value={searchTerm}
                                />
                            </div>
                        </div>
                    </Card.Description>
                </Card.Header>
            </Card.Root>

            <!-- Tasks Table -->
            <Card.Root>
                <Card.Header>
                    <Card.Title>Tasks</Card.Title>
                </Card.Header>
                <Card.Content>
                    <Table.Root>
                        <Table.Header>
                            <Table.Row>
                                <Table.Head>Task ID</Table.Head>
                                <Table.Head>Status</Table.Head>
                                <Table.Head>Result</Table.Head>
                                <Table.Head>Error</Table.Head>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {#each filteredTasks as task}
                                <Table.Row>
                                    <Table.Cell class="font-medium font-mono">
                                        {task.id.slice(-8)}
                                    </Table.Cell>
                                    <Table.Cell>
                                        <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                            ${task.status === 'completed' ? 'bg-green-100 text-green-800' : 
                                            task.status === 'failed' ? 'bg-red-100 text-red-800' : 
                                            'bg-gray-100 text-gray-800'}`}>
                                            {task.status}
                                        </span>
                                    </Table.Cell>
                                    <Table.Cell>
                                        {#if task.result}
                                            <pre class="text-xs text-gray-600 whitespace-pre-wrap">{JSON.stringify(task.result, null, 2)}</pre>
                                        {/if}
                                    </Table.Cell>
                                    <Table.Cell>
                                        {#if task.error}
                                            <span class="text-red-600 text-sm">{task.error}</span>
                                        {/if}
                                    </Table.Cell>
                                </Table.Row>
                            {/each}
                        </Table.Body>
                    </Table.Root>
                </Card.Content>
            </Card.Root>
        </div>
    {:else}
        <div class="text-center text-gray-500">No run found</div>
    {/if}
</div>
