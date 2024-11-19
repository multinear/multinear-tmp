<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { getRecentRuns } from '$lib/api';
    import type { RecentRun } from '$lib/api';
    import { setupHashChangeHandler, selectedProjectId } from '$lib/stores/projects';

    let runs: RecentRun[] = [];
    let loading = true;
    let error: string | null = null;

    onMount(() => {
        const { cleanup } = setupHashChangeHandler();
        return cleanup;
    });

    async function loadData() {
        loading = true;
        error = null;
        try {
            runs = await getRecentRuns($selectedProjectId, 100, 0);
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load runs";
            console.error(e);
        } finally {
            loading = false;
        }
    }

    // Reactive statement to load data when selectedProjectId changes
    $: if (selectedProjectId) {
        loadData();
    }

    function handleRunSelect(runId: string) {
        goto(`/run#${runId}`);
    }
</script>

<div class="container mx-auto p-4">
    <h1 class="text-4xl font-bold mb-8">Experiments</h1>

    {#if loading}
        <div class="text-center text-gray-500">Loading experiments...</div>
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
                    on:click={() => window.location.reload()}
                >
                    Try Again
                </Button>
            </Card.Footer>
        </Card.Root>
    {:else if runs.length === 0}
        <div class="text-center text-gray-500">No experiments found</div>
    {:else}
        <div class="grid gap-4">
            {#each runs as run (run.id)}
                <Card.Root class="hover:bg-gray-50 transition-colors">
                    <button
                        class="w-full text-left"
                        on:click={() => handleRunSelect(run.id)}
                    >
                        <Card.Header>
                            <Card.Title class="flex justify-between items-center">
                                <span>{run.model}</span>
                                <span class="text-sm text-gray-500">{new Date(run.date).toLocaleDateString()}</span>
                            </Card.Title>
                            <Card.Description>
                                <div class="flex justify-between items-center">
                                    <div>
                                        Revision: {run.revision}
                                    </div>
                                    <div class="flex gap-4">
                                        <span class="text-green-600">Pass: {run.pass}</span>
                                        <span class="text-red-600">Fail: {run.fail}</span>
                                        <span class="text-orange-600">Regression: {run.regression}</span>
                                    </div>
                                </div>
                            </Card.Description>
                        </Card.Header>
                    </button>
                </Card.Root>
            {/each}
        </div>
    {/if}
</div>
