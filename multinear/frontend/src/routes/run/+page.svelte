<script lang="ts">
    import { onMount } from 'svelte';
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { page } from '$app/stores';
    import { getRunDetails } from '$lib/api';


    let runId: string | null = null;
    let runDetails: any = null;
    let loading = true;
    let error: string | null = null;

    $: {
        // Extract run ID from hash
        const hash = $page.url.hash;
        runId = hash.startsWith('#') ? hash.slice(1) : hash;
        if (runId) loadRunDetails(runId);
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
</script>

<div class="container mx-auto p-4">
    <h1 class="text-4xl font-bold mb-8">Run Details</h1>

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
        <Card.Root>
            <Card.Header>
                <Card.Title>Run {runDetails.id}</Card.Title>
                <Card.Description>
                    <!-- Add run details here based on your API response structure -->
                    <pre class="mt-4 bg-gray-50 p-4 rounded">
                        {JSON.stringify(runDetails, null, 2)}
                    </pre>
                </Card.Description>
            </Card.Header>
        </Card.Root>
    {:else}
        <div class="text-center text-gray-500">No run found</div>
    {/if}
</div>
