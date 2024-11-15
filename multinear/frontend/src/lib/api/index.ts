const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface JobResponse {
    job_id: string;
}

export interface StatusResponse {
    status: string;
}

export async function startExperiment(): Promise<JobResponse> {
    const response = await fetch(`${API_URL}/start`, {
        method: 'POST',
    });
    return response.json();
}

export async function getJobStatus(jobId: string): Promise<StatusResponse> {
    const response = await fetch(`${API_URL}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId }),
    });
    return response.json();
} 