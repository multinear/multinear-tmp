import { writable } from 'svelte/store';
import type { Project } from '$lib/api';

export const projects = writable<Project[]>([]);
export const projectsLoading = writable(true);
export const projectsError = writable<string | null>(null);
export const selectedProjectId = writable<string>('');

export function handleProjectHashChange() {
    const hash = window.location.hash;
    const projectId = hash ? hash.slice(1).split('/')[0] : ''; // Remove # and get first path segment
    selectedProjectId.set(projectId);
    return projectId;
}

export function setupHashChangeHandler() {
    const projectId = handleProjectHashChange(); // Initial hash check
    window.addEventListener('hashchange', handleProjectHashChange);
    return {
        projectId,
        cleanup: () => window.removeEventListener('hashchange', handleProjectHashChange)
    };
}
