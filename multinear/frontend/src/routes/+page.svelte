<script lang="ts">
    import { onMount } from 'svelte';
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { getProjects, type Project } from '$lib/api';
    import { goto } from '$app/navigation';

    let projects: Project[] = [];
    let loading = true;
    let error: string | null = null;

    onMount(async () => {
        try {
            const data = await getProjects();
            projects = data.projects;
        } catch (e) {
            error = "Failed to load projects";
            console.error(e);
        } finally {
            loading = false;
        }
    });

    function handleProjectSelect(projectId: string) {
        goto(`/${projectId}`);
    }
</script>

<div class="container mx-auto flex-1 flex items-center justify-center p-4">
    <div class="w-96 max-w-2xl space-y-8">
        <h1 class="text-4xl font-bold text-center mb-8">Projects</h1>

        {#if loading}
            <div class="text-center text-gray-500">Loading projects...</div>
        {:else if error}
            <div class="text-center text-red-500">{error}</div>
        {:else if projects.length === 0}
            <div class="text-center text-gray-500">No projects found</div>
        {:else}
            <div class="grid gap-4">
                {#each projects as project (project.id)}
                    <Card.Root class="hover:bg-gray-50 transition-colors">
                        <button
                            class="w-full text-left"
                            on:click={() => handleProjectSelect(project.id)}
                        >
                            <Card.Header>
                                <Card.Title>{project.name}</Card.Title>
                                <Card.Description>{project.description}</Card.Description>
                            </Card.Header>
                        </button>
                    </Card.Root>
                {/each}
            </div>
        {/if}
    </div>
</div>
