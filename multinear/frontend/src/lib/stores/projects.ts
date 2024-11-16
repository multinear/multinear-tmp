import { writable } from 'svelte/store';
import type { Project } from '$lib/api';

export const projects = writable<Project[]>([]);
export const projectsLoading = writable(true);
export const projectsError = writable<string | null>(null);
