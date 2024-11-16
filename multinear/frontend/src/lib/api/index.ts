const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Project {
    id: string;
    name: string;
    description: string;
}

export interface ProjectList {
    projects: Project[];
}

export interface JobResponse {
    project_id: string;
    job_id: string;
    status: string;
    details?: Record<string, any>;
}

export async function getProjects(): Promise<ProjectList> {
    const response = await fetch(`${API_URL}/projects`);
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