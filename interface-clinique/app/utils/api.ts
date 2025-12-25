import axios from 'axios';

// Backend Service URLs
const SERVICES = {
    DOC_INGESTOR: process.env.NEXT_PUBLIC_DOC_INGESTOR_URL || 'http://localhost:8001',
    DEID: process.env.NEXT_PUBLIC_DEID_URL || 'http://localhost:8002',
    SEARCH: process.env.NEXT_PUBLIC_SEARCH_URL || 'http://localhost:8003',
    QA: process.env.NEXT_PUBLIC_LLM_QA_URL || 'http://localhost:8004',
    SYNTHESIS: process.env.NEXT_PUBLIC_SYNTHESIS_URL || 'http://localhost:8005',
    AUDIT: process.env.NEXT_PUBLIC_AUDIT_URL || 'http://localhost:8006',
};

export const api = {
    // --- Dashboard & Analytics ---
    getStats: async () => {
        // Aggregate stats from multiple services
        try {
            const [docs, search, audit] = await Promise.all([
                axios.get(`${SERVICES.DOC_INGESTOR}/api/v1/documents`),
                axios.get(`${SERVICES.SEARCH}/api/v1/search/stats`),
                axios.get(`${SERVICES.AUDIT}/api/v1/audit/stats`).catch(() => ({ data: { total_events: 0 } }))
            ]);

            return {
                totalDocuments: docs.data.total || 0,
                totalIndexed: search.data.total_documents || 0,
                totalQueries: audit.data.total_events || 0, // Proxy for activity
                processingSuccess: 0 // TODO: Calculate from docs status
            };
        } catch (e) {
            console.error("Error fetching stats", e);
            return { totalDocuments: 0, totalIndexed: 0, totalQueries: 0, processingSuccess: 0 };
        }
    },

    // --- Documents ---
    uploadDocument: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await axios.post(`${SERVICES.DOC_INGESTOR}/api/v1/documents/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },

    getDocuments: async (page = 1, limit = 20) => {
        const response = await axios.get(`${SERVICES.DOC_INGESTOR}/api/v1/documents`, {
            params: { skip: (page - 1) * limit, limit }
        });
        return response.data;
    },

    deleteDocument: async (docId: string) => {
        await axios.delete(`${SERVICES.DOC_INGESTOR}/api/v1/documents/${docId}`);
        // Also delete from index
        try {
            await axios.delete(`${SERVICES.SEARCH}/api/v1/search/document/${docId}`);
        } catch (e) { console.warn("Could not delete from index", e); }
        return true;
    },

    // --- Search ---
    search: async (query: string, filters = {}) => {
        const response = await axios.post(`${SERVICES.SEARCH}/api/v1/search/search`, {
            query,
            top_k: 10,
            ...filters
        });
        return response.data;
    },

    // --- Q&A ---
    askQuestion: async (question: string, sessionId?: string, filters?: any) => {
        const response = await axios.post(`${SERVICES.QA}/api/v1/qa/ask`, {
            question,
            session_id: sessionId,
            include_sources: true,
            filters: filters
        });
        return response.data;
    },

    // --- Patients & Synthesis ---
    generateSummary: async (patientId: string) => {
        const response = await axios.post(`${SERVICES.SYNTHESIS}/api/v1/synthesis/summary`, {
            patient_id: patientId
        });
        return response.data;
    },

    comparePatients: async (patientIds: string[]) => {
        const response = await axios.post(`${SERVICES.SYNTHESIS}/api/v1/synthesis/compare`, {
            patient_ids: patientIds
        });
        return response.data;
    },

    // --- Audit ---
    getAuditLogs: async (limit = 50) => {
        const response = await axios.get(`${SERVICES.AUDIT}/api/v1/audit/logs`, {
            params: { limit }
        });
        return response.data;
    }
};
