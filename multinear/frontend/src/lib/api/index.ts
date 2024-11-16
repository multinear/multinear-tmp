const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Project {
    id: string;
    name: string;
    description: string;
}

export interface JobResponse {
    project_id: string;
    job_id: string;
    status: string;
    total_tasks: number;
    current_task?: number;
    task_status_map?: Record<string, string>;
    details?: Record<string, any>;
}

export interface RecentRun {
    id: string;
    date: string;
    revision: string;
    model: string;
    score: number;
    totalTests: number;
    pass: number;
    fail: number;
    regression: number;
    bookmarked?: boolean;
    noted?: boolean;
}

export async function getProjects(): Promise<Project[]> {
    const response = await fetch(`${API_URL}/projects`);
    if (!response.ok) {
        throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    return response.json();
}

export async function startExperiment(projectId: string): Promise<JobResponse> {
    const response = await fetch(`${API_URL}/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_id: projectId }),
    });
    return response.json();
}

export async function getJobStatus(projectId: string, jobId: string): Promise<JobResponse> {
    const response = await fetch(`${API_URL}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_id: projectId, job_id: jobId }),
    });
    return response.json();
}

export async function getRecentRuns(projectId: string): Promise<RecentRun[]> {
    const response = await fetch(`${API_URL}/runs/${projectId}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch recent runs: ${response.statusText}`);
    }
    return response.json();
} 