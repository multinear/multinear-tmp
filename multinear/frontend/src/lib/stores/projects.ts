import { writable } from 'svelte/store';
import type { Project } from '$lib/api';

export const projects = writable<Project[]>([]);
export const projectsLoading = writable(true);
export const projectsError = writable<string | null>(null);
export const selectedProjectId = writable<string>('');
export const selectedRunId = writable<string>('');

export function handlePageHashChange() {
    const hash = window.location.hash;
    const parts = hash ? hash.slice(1).split('/') : [];
    
    const projectId = parts[0] || '';
    selectedProjectId.set(projectId);
    
    const runId = parts[1]?.startsWith('r:') ? parts[1].slice(2) : '';
    selectedRunId.set(runId);
    
    return { projectId, runId };
}

export function setupHashChangeHandler() {
    const hashData = handlePageHashChange(); // Initial hash check
    window.addEventListener('hashchange', handlePageHashChange);
    return {
        ...hashData,
        cleanup: () => window.removeEventListener('hashchange', handlePageHashChange)
    };
}
