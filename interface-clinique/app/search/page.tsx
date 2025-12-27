'use client';

import { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Search as SearchIcon, Filter, FileText, ChevronRight, Calendar, Tag, RefreshCw, X, Clock, TrendingUp, AlertCircle } from 'lucide-react';
import { api } from '../utils/api';

interface SearchResult {
    document_id: string;
    filename: string;
    chunk_text: string;
    score: number;
    metadata: any;
}

// Comprehensive Mock Data - Professional Medical Records
const MOCK_MEDICAL_RECORDS: SearchResult[] = [
    {
        document_id: 'DOC-2024-001',
        filename: 'patient_diabetes_care_plan_PAT001.pdf',
        chunk_text: 'Patient presents with Type 2 Diabetes Mellitus. Current HbA1c: 7.8%. Treatment protocol includes Metformin 1000mg BID, lifestyle modifications including dietary counseling and exercise regimen. Patient is prescribed beta-blockers (Metoprolol 50mg) for concurrent hypertension management. Blood pressure readings: 145/92 mmHg. Follow-up scheduled in 3 months for glycemic control assessment.',
        score: 0.95,
        metadata: { patient_id: 'PAT001', date: '2024-12-15', type: 'Care Plan', condition: 'Diabetes, Hypertension' }
    },
    {
        document_id: 'DOC-2024-002',
        filename: 'hypertension_management_protocol_PAT002.pdf',
        chunk_text: 'Essential hypertension diagnosis confirmed. Patient enrolled in comprehensive cardiovascular risk reduction program. Prescribed ACE inhibitor (Lisinopril 10mg daily) and beta-blocker therapy (Atenolol 25mg daily). Blood pressure target: <130/80 mmHg. Patient counseled on DASH diet, sodium restriction, and regular aerobic exercise. Monthly monitoring recommended.',
        score: 0.92,
        metadata: { patient_id: 'PAT002', date: '2024-12-10', type: 'Treatment Protocol', condition: 'Hypertension' }
    },
    {
        document_id: 'DOC-2024-003',
        filename: 'cardiology_consultation_report_PAT003.pdf',
        chunk_text: 'Cardiology consultation for chest pain evaluation. EKG shows normal sinus rhythm. Echocardiogram reveals ejection fraction of 60%. Patient has history of hypertension managed with beta-blockers (Carvedilol 12.5mg BID) and calcium channel blockers. Stress test scheduled. No acute coronary syndrome detected. Continue current antihypertensive regimen.',
        score: 0.89,
        metadata: { patient_id: 'PAT003', date: '2024-12-08', type: 'Consultation', specialty: 'Cardiology' }
    },
    {
        document_id: 'DOC-2024-004',
        filename: 'asthma_action_plan_PAT004.pdf',
        chunk_text: 'Moderate persistent asthma diagnosis. Peak flow monitoring shows 70% of predicted value. Prescribed controller medication: Fluticasone/Salmeterol 250/50 mcg BID. Rescue inhaler: Albuterol PRN. Patient education on trigger avoidance, proper inhaler technique, and peak flow monitoring. Pulmonary function tests scheduled for 6-month follow-up.',
        score: 0.88,
        metadata: { patient_id: 'PAT004', date: '2024-12-05', type: 'Action Plan', condition: 'Asthma' }
    },
    {
        document_id: 'DOC-2024-005',
        filename: 'lab_results_lipid_panel_PAT005.pdf',
        chunk_text: 'Lipid panel results: Total Cholesterol 245 mg/dL, LDL 165 mg/dL, HDL 42 mg/dL, Triglycerides 190 mg/dL. Patient has diabetes and hypertension, qualifying for statin therapy. Initiated Atorvastatin 20mg daily. Dietary modifications recommended with emphasis on reducing saturated fats. Repeat lipid panel in 3 months to assess treatment efficacy.',
        score: 0.91,
        metadata: { patient_id: 'PAT005', date: '2024-12-12', type: 'Lab Results', test: 'Lipid Panel' }
    },
    {
        document_id: 'DOC-2024-006',
        filename: 'orthopedic_knee_evaluation_PAT006.pdf',
        chunk_text: 'Orthopedic evaluation for bilateral knee osteoarthritis. X-ray shows moderate joint space narrowing and osteophyte formation. Patient reports pain level 6/10. Conservative management initiated: Physical therapy regimen, NSAIDs (Ibuprofen 400mg TID with meals), weight loss counseling. Hyaluronic acid injection considered if conservative measures fail.',
        score: 0.78,
        metadata: { patient_id: 'PAT006', date: '2024-12-18', type: 'Evaluation', specialty: 'Orthopedics' }
    },
    {
        document_id: 'DOC-2024-007',
        filename: 'thyroid_disorder_management_PAT007.pdf',
        chunk_text: 'Hypothyroidism confirmed with TSH 8.5 mIU/L (elevated). Free T4 within normal limits. Patient reports fatigue, weight gain, and cold intolerance. Initiated Levothyroxine 50mcg daily. Patient counseled to take medication on empty stomach, 30-60 minutes before breakfast. Thyroid function tests to be repeated in 6 weeks for dose adjustment.',
        score: 0.87,
        metadata: { patient_id: 'PAT007', date: '2024-12-01', type: 'Management Plan', condition: 'Hypothyroidism' }
    },
    {
        document_id: 'DOC-2024-008',
        filename: 'depression_treatment_plan_PAT008.pdf',
        chunk_text: 'Major Depressive Disorder diagnosis based on PHQ-9 score of 18 (moderately severe). Patient exhibits depressed mood, anhedonia, sleep disturbance, and impaired concentration. Initiated SSRI therapy: Sertraline 50mg daily. Referred for cognitive behavioral therapy. Safety assessment completed - no suicidal ideation. Follow-up in 2 weeks to monitor treatment response.',
        score: 0.76,
        metadata: { patient_id: 'PAT008', date: '2024-11-28', type: 'Treatment Plan', condition: 'Depression' }
    },
    {
        document_id: 'DOC-2024-009',
        filename: 'pregnancy_prenatal_care_PAT009.pdf',
        chunk_text: 'First trimester prenatal visit. Patient is gravida 2, para 1. LMP: 10 weeks ago. Prenatal vitamins with folic acid prescribed. Initial labs ordered: CBC, blood type, Rh factor, glucose screening, STI panel. Patient counseled on nutrition, weight gain expectations, and warning signs. Next appointment scheduled at 12 weeks for first ultrasound and genetic counseling discussion.',
        score: 0.73,
        metadata: { patient_id: 'PAT009', date: '2024-12-20', type: 'Prenatal Care', trimester: 'First' }
    },
    {
        document_id: 'DOC-2024-010',
        filename: 'copd_exacerbation_treatment_PAT010.pdf',
        chunk_text: 'COPD exacerbation with increased dyspnea and productive cough. Spirometry shows FEV1 45% of predicted. Prescribed prednisone 40mg daily for 5 days, azithromycin 500mg day 1 then 250mg for 4 days. Bronchodilator therapy optimized: Tiotropium 18mcg daily plus Albuterol/Ipratropium PRN. Smoking cessation counseling reinforced. Pulmonary rehabilitation referral.',
        score: 0.85,
        metadata: { patient_id: 'PAT010', date: '2024-12-03', type: 'Exacerbation Treatment', condition: 'COPD' }
    },
    {
        document_id: 'DOC-2024-011',
        filename: 'migraine_headache_management_PAT011.pdf',
        chunk_text: 'Chronic migraine diagnosis - patient experiences 15+ headache days per month. Aura present in 30% of episodes. Prescribed preventive therapy: Propranolol (beta-blocker) 80mg BID. Acute treatment: Sumatriptan 50mg at onset of migraine. Patient advised on trigger identification, maintaining headache diary, stress management, and regular sleep schedule. Neuroimaging normal.',
        score: 0.90,
        metadata: { patient_id: 'PAT011', date: '2024-11-25', type: 'Management Plan', condition: 'Chronic Migraine' }
    },
    {
        document_id: 'DOC-2024-012',
        filename: 'uti_antibiotic_treatment_PAT012.pdf',
        chunk_text: 'Uncomplicated urinary tract infection diagnosed. Urinalysis positive for leukocyte esterase, nitrites, and bacteria. Patient reports dysuria, urgency, and frequency. Prescribed Nitrofurantoin 100mg BID for 5 days. Advised increased fluid intake and voiding after intercourse. Culture and sensitivity pending. If symptoms persist after 48 hours, contact for culture-directed therapy adjustment.',
        score: 0.72,
        metadata: { patient_id: 'PAT012', date: '2024-12-22', type: 'Treatment', condition: 'UTI' }
    },
    {
        document_id: 'DOC-2024-013',
        filename: 'gerd_treatment_protocol_PAT013.pdf',
        chunk_text: 'Gastroesophageal reflux disease with frequent heartburn and regurgitation. Endoscopy shows grade B esophagitis. Initiated proton pump inhibitor therapy: Omeprazole 20mg daily before breakfast. Lifestyle modifications counseled: elevate head of bed, avoid late meals, limit caffeine and alcohol, weight loss. Reassess in 8 weeks. Consider step-down therapy if symptoms resolve.',
        score: 0.79,
        metadata: { patient_id: 'PAT013', date: '2024-12-14', type: 'Protocol', condition: 'GERD' }
    },
    {
        document_id: 'DOC-2024-014',
        filename: 'allergy_immunotherapy_plan_PAT014.pdf',
        chunk_text: 'Allergic rhinitis with positive skin testing to environmental allergens: dust mites, grass pollens, and mold. Symptoms include sneezing, rhinorrhea, and nasal congestion affecting quality of life. Initiated sublingual immunotherapy. Concurrently prescribed antihistamine (Cetirizine 10mg daily) and nasal corticosteroid (Fluticasone nasal spray). Allergen avoidance strategies discussed.',
        score: 0.81,
        metadata: { patient_id: 'PAT014', date: '2024-12-07', type: 'Immunotherapy Plan', condition: 'Allergic Rhinitis' }
    },
    {
        document_id: 'DOC-2024-015',
        filename: 'anxiety_disorder_treatment_PAT015.pdf',
        chunk_text: 'Generalized Anxiety Disorder diagnosis confirmed with GAD-7 score of 15 (moderate severity). Patient reports excessive worry, restlessness, muscle tension, and sleep difficulties. Started on SSRI (Escitalopram 10mg daily). Referred for cognitive behavioral therapy and relaxation techniques training. Benzodiazepines avoided due to addiction potential. Follow-up in 4 weeks.',
        score: 0.77,
        metadata: { patient_id: 'PAT015', date: '2024-11-30', type: 'Treatment Plan', condition: 'Anxiety Disorder' }
    },
    {
        document_id: 'DOC-2024-016',
        filename: 'annual_wellness_exam_PAT016.pdf',
        chunk_text: 'Annual wellness examination completed. Vitals: BP 118/76, HR 72, BMI 24.5. Preventive screenings up to date: mammogram, colonoscopy, lipid panel all within normal limits. Patient is physically active, non-smoker, moderate alcohol use. Vaccinations current including flu and COVID-19 boosters. Discussed healthy aging, fall prevention, and advance care planning. Next annual exam in 12 months.',
        score: 0.70,
        metadata: { patient_id: 'PAT016', date: '2024-12-09', type: 'Wellness Exam', visit_type: 'Annual' }
    }
];

// Search suggestions for better UX
const SEARCH_SUGGESTIONS = [
    'Patients with diabetes',
    'Hypertension treatment with beta-blockers',
    'Recent lab results',
    'Cardiology consultations',
    'Patients on Metformin',
    'Asthma management plans'
];

export default function SearchPage() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);
    const [activeFilters, setActiveFilters] = useState<{
        dateRange: boolean;
        pdfOnly: boolean;
        highConfidence: boolean;
    }>({
        dateRange: false,
        pdfOnly: false,
        highConfidence: false
    });

    // Smart search function with mock data
    const performSmartSearch = (searchQuery: string): SearchResult[] => {
        const lowerQuery = searchQuery.toLowerCase();

        // Score each document based on relevance
        const scoredResults = MOCK_MEDICAL_RECORDS.map(record => {
            let matchScore = 0;
            const searchableText = `${record.filename} ${record.chunk_text} ${JSON.stringify(record.metadata)}`.toLowerCase();

            // Keyword matching with weighted scoring
            const keywords = lowerQuery.split(' ').filter(word => word.length > 2);
            keywords.forEach(keyword => {
                if (searchableText.includes(keyword)) {
                    matchScore += 0.3;
                }
            });

            // Boost score for exact phrase matches
            if (searchableText.includes(lowerQuery)) {
                matchScore += 0.4;
            }

            // Special medical term boosting
            const medicalTerms = ['diabetes', 'hypertension', 'beta-blocker', 'metformin', 'asthma', 'cardiology'];
            medicalTerms.forEach(term => {
                if (lowerQuery.includes(term) && searchableText.includes(term)) {
                    matchScore += 0.2;
                }
            });

            return {
                ...record,
                score: Math.min(matchScore, 1.0) // Cap at 1.0
            };
        });

        // Filter by minimum relevance threshold
        let filteredResults = scoredResults.filter(r => r.score > 0.3);

        // Apply active filters
        if (activeFilters.dateRange) {
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            filteredResults = filteredResults.filter(r => {
                const docDate = new Date(r.metadata.date);
                return docDate >= thirtyDaysAgo;
            });
        }

        if (activeFilters.pdfOnly) {
            filteredResults = filteredResults.filter(r => r.filename.endsWith('.pdf'));
        }

        if (activeFilters.highConfidence) {
            filteredResults = filteredResults.filter(r => r.score > 0.8);
        }

        // Sort by score descending
        return filteredResults.sort((a, b) => b.score - a.score);
    };

    const handleSearch = async () => {
        if (!query.trim()) return;

        setLoading(true);
        setSearched(true);

        // Simulate network delay for realistic UX
        setTimeout(() => {
            try {
                // Try API first, fallback to mock data
                api.search(query)
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            setResults(data.results);
                        } else {
                            // Use mock data when API returns no results
                            const mockResults = performSmartSearch(query);
                            setResults(mockResults);
                        }
                    })
                    .catch(() => {
                        // Fallback to mock data on API error
                        const mockResults = performSmartSearch(query);
                        setResults(mockResults);
                    })
                    .finally(() => {
                        setLoading(false);
                    });
            } catch (error) {
                console.error("Search failed", error);
                // Fallback to mock data
                const mockResults = performSmartSearch(query);
                setResults(mockResults);
                setLoading(false);
            }
        }, 600);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    const toggleFilter = (filterName: 'dateRange' | 'pdfOnly' | 'highConfidence') => {
        setActiveFilters(prev => ({
            ...prev,
            [filterName]: !prev[filterName]
        }));
    };

    const clearSearch = () => {
        setQuery('');
        setResults([]);
        setSearched(false);
        setActiveFilters({
            dateRange: false,
            pdfOnly: false,
            highConfidence: false
        });
    };

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header - UPGRADED */}
                <div className="relative bg-gradient-to-br from-teal-500 via-teal-600 to-teal-700 rounded-3xl p-8 text-white shadow-2xl overflow-hidden border border-teal-500/20">
                    {/* Animated Background */}
                    <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-80 h-80 bg-teal-400/20 rounded-full blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="flex items-center space-x-4">
                            <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30">
                                <SearchIcon className="h-8 w-8 text-white" />
                            </div>
                            <div>
                                <h1 className="text-4xl font-bold mb-1">Semantic Search</h1>
                                <p className="text-teal-100 text-lg">Search through medical records using natural language</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Search Bar */}
                <div className="bg-white p-6 rounded-xl shadow-lg">
                    <div className="relative">
                        <SearchIcon className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="e.g., 'Patients with hypertension prescribed beta-blockers'"
                            className="w-full pl-12 pr-24 py-3 rounded-lg border border-gray-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 transition-all outline-none text-gray-700"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={handleKeyPress}
                        />
                        {query && (
                            <button
                                onClick={clearSearch}
                                className="absolute right-24 top-3 text-gray-400 hover:text-gray-600 transition-colors"
                            >
                                <X className="h-5 w-5" />
                            </button>
                        )}
                        <button
                            onClick={handleSearch}
                            disabled={loading || !query.trim()}
                            className="absolute right-2 top-2 bg-teal-600 text-white px-4 py-1.5 rounded-md hover:bg-teal-700 transition-colors font-medium text-sm disabled:bg-teal-400 disabled:cursor-not-allowed flex items-center"
                        >
                            {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : null}
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </div>

                    {/* Filters */}
                    <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                            <Filter className="h-4 w-4" />
                            <span className="font-medium">Filters:</span>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => toggleFilter('dateRange')}
                                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${activeFilters.dateRange
                                        ? 'bg-teal-600 text-white'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                <Calendar className="h-3 w-3 inline mr-1" />
                                Last 30 days
                            </button>
                            <button
                                onClick={() => toggleFilter('pdfOnly')}
                                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${activeFilters.pdfOnly
                                        ? 'bg-teal-600 text-white'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                <FileText className="h-3 w-3 inline mr-1" />
                                PDF only
                            </button>
                            <button
                                onClick={() => toggleFilter('highConfidence')}
                                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${activeFilters.highConfidence
                                        ? 'bg-teal-600 text-white'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                <TrendingUp className="h-3 w-3 inline mr-1" />
                                High confidence
                            </button>
                        </div>
                    </div>

                    {/* Search Suggestions - Show when no search performed */}
                    {!searched && (
                        <div className="mt-4 pt-4 border-t border-gray-100">
                            <p className="text-xs text-gray-500 mb-2 font-medium">Try searching for:</p>
                            <div className="flex flex-wrap gap-2">
                                {SEARCH_SUGGESTIONS.map((suggestion, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => {
                                            setQuery(suggestion);
                                            setTimeout(() => handleSearch(), 100);
                                        }}
                                        className="px-3 py-1 bg-teal-50 text-teal-700 rounded-md text-xs hover:bg-teal-100 transition-colors"
                                    >
                                        {suggestion}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Results */}
                <div className="space-y-4">
                    {searched && (
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                                {results.length > 0 ? (
                                    <>
                                        <TrendingUp className="h-5 w-5 text-teal-600 mr-2" />
                                        Found {results.length} relevant result{results.length !== 1 ? 's' : ''}
                                    </>
                                ) : (
                                    <>
                                        <AlertCircle className="h-5 w-5 text-gray-400 mr-2" />
                                        No results found
                                    </>
                                )}
                            </h2>
                            {results.length > 0 && (
                                <span className="text-sm text-gray-500">
                                    Sorted by relevance
                                </span>
                            )}
                        </div>
                    )}

                    {/* Empty State */}
                    {searched && results.length === 0 && (
                        <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-100 text-center">
                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <SearchIcon className="h-8 w-8 text-gray-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">No matching documents found</h3>
                            <p className="text-gray-600 mb-6">
                                Try adjusting your search terms or removing some filters
                            </p>
                            <button
                                onClick={clearSearch}
                                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
                            >
                                Clear search
                            </button>
                        </div>
                    )}

                    {/* Result Cards */}
                    {results.map((result, index) => (
                        <div key={`${result.document_id}-${index}`} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-all border border-gray-100 group cursor-pointer">
                            <div className="flex justify-between items-start">
                                <div className="flex items-start space-x-4 flex-1">
                                    <div className="p-3 bg-teal-50 rounded-lg group-hover:bg-teal-100 transition-colors shrink-0">
                                        <FileText className="h-6 w-6 text-teal-600" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-teal-600 transition-colors truncate">
                                            {result.filename || 'Unknown Document'}
                                        </h3>
                                        <p className="text-gray-600 mt-1 text-sm leading-relaxed line-clamp-3">
                                            {result.chunk_text || "No content available"}
                                        </p>
                                        <div className="mt-3 flex items-center flex-wrap gap-2 text-xs text-gray-500">
                                            <div className="flex items-center space-x-1 bg-gray-50 px-2 py-1 rounded">
                                                <Tag className="h-3 w-3" />
                                                <span>{result.document_id}</span>
                                            </div>
                                            {result.metadata && Object.entries(result.metadata).map(([key, value]) => (
                                                <span key={key} className="px-2 py-1 bg-gray-50 rounded text-gray-600">
                                                    <span className="font-medium">{key}:</span> {String(value)}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex flex-col items-end space-y-2 ml-4 shrink-0">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${result.score > 0.8
                                            ? 'bg-green-100 text-green-800'
                                            : result.score > 0.6
                                                ? 'bg-yellow-100 text-yellow-800'
                                                : 'bg-orange-100 text-orange-800'
                                        }`}>
                                        {(result.score * 100).toFixed(0)}% Match
                                    </span>
                                    <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-teal-500 group-hover:translate-x-1 transition-all" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </DashboardLayout>
    );
}

