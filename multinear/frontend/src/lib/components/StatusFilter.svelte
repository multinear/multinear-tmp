<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { Label } from "$lib/components/ui/label";

    export let statusFilter: string = "";
    export let statusCounts: Record<string, number> = {};
    export let totalCount: number;

    $: availableStatuses = Object.entries(statusCounts)
        .filter(([_, count]) => count > 0)
        .map(([status]) => status);
</script>

{#if availableStatuses.length > 1}
    <div class="flex flex-col space-y-1.5">
        <Label>Filter</Label>
        <div class="flex gap-2">
            <Button
                variant="outline"
                size="sm"
                class={statusFilter === "" ? 'bg-gray-100 border-gray-200' : ''}
                on:click={() => statusFilter = ""}
            >
                All tasks ({totalCount})
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