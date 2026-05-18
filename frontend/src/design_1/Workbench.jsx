import { useState, useEffect, useRef } from 'react'
import IntakePanel from './components/IntakePanel'
import GenomicModal from './components/GenomicModal'
import ResultsCanvas from './components/ResultsCanvas'
import HelixView from './components/HelixView'
import './Workbench.css'

// DATA MAPPING
const nutrigenomicsTree = [
  { name: "Nutrient Metabolism", subs: [
    { name: "Vitamin Levels", traits: ['Vitamin D levels', 'Vitamin B12 levels', 'Vitamin C levels', 'Retinol (Vitamin A) levels'] },
    { name: "Stimulant Processing", traits: ['Caffeine metabolism', 'Caffeine consumption'] }
  ]},
  { name: "Food Sensitivities", subs: [
    { name: "Dietary Intolerances", traits: ['Lactose tolerance test'] }
  ]}
];

const fitnessTree = [
  { name: "Muscle & Strength", subs: [
    { name: "Muscle Composition", traits: ['Muscle mass percentage', 'Appendicular skeletal muscle mass'] },
    { name: "Physical Power", traits: ['Muscle grip strength'] }
  ]}
];

const pharmaTree = [
  { name: "Drug Efficacy & Response", subs: [
    { name: "Cardiovascular Medications", traits: ['Response to statin therapy', 'Warfarin maintenance dose'] }
  ]},
  { name: "Toxicity & Side Effect Risk", subs: [
    { name: "Medication Safety", traits: ['Statin-induced myopathy', 'Drug-induced liver injury', 'Warfarin-associated bleeding risk'] }
  ]}
];

function Workbench() {
  // GLOBAL STATE
  const [step, setStep] = useState(1) 
  const [patientName, setPatientName] = useState('')
  const [age, setAge] = useState(25)
  const [diet, setDiet] = useState('Veg')
  const [analysisMode, setAnalysisMode] = useState('fast')
  const [file, setFile] = useState(null)
  const [selectedTraits, setSelectedTraits] = useState([])
  const [results, setResults] = useState([])
  
  // UI STATE
  const [showFocusModal, setShowFocusModal] = useState(false)
  const [categoryTree, setCategoryTree] = useState([])
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState([])
  
  const fileInputRef = useRef(null)
  const dietOptions = ['Veg', 'Non-Veg', 'Vegan']

  useEffect(() => {
    fetch('http://localhost:8000/categories/tree')
      .then(res => res.json())
      .then(data => setCategoryTree(data.masters))
      .catch(err => console.error("Error fetching tree:", err))
  }, [])

  const cycleDiet = () => {
    const currentIndex = dietOptions.indexOf(diet)
    const nextIndex = (currentIndex + 1) % dietOptions.length
    setDiet(dietOptions[nextIndex])
  }

  const handleStartAnalysis = () => {
    if (!file) return
    setStep(3)
    startGenomeScan()
  }

  const startGenomeScan = async () => {
    setProgress(0)
    setResults([]) // Reset for new scan
    setLogs(["📡 Initializing Specialist Swarm..."])
    
    if (selectedTraits.length === 0) {
      setLogs(prev => [...prev, "⚠️ No traits selected. Analyzing core BioGenomics markers..."])
    }

    const allResults = [];
    const totalTraits = selectedTraits.length || 1;
    
    // Step through each selected trait one by one
    for (let i = 0; i < totalTraits; i++) {
      const traitEntry = selectedTraits[i] || "General Wellness";
      const traitName = typeof traitEntry === 'string' ? traitEntry : (traitEntry.name || "Unknown Trait");
      
      // Update the LAST log entry to show current activity
      setLogs(prev => {
        const base = prev.filter(l => !l.startsWith("📡 Now analyzing:"));
        return [...base, `📡 Now analyzing: ${traitName.substring(0, 45)}${traitName.length > 45 ? '...' : ''}`];
      });

      try {
        const response = await fetch('http://localhost:8000/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            categories: [traitEntry],
            file_path: file ? file.name : "James_Jones_v5_Full.txt",
            analysis_mode: analysisMode,
            patient_context: { age, diet, gender: "Male" }
          })
        });

        const data = await response.json();
        if (data.results && data.results.length > 0) {
          const result = data.results[0];
          allResults.push(result);
          setResults(prev => [...prev, result]);
          setLogs(prev => {
            const base = prev.filter(l => !l.startsWith("📡 Now analyzing:"));
            return [...base, `✅ Completed: ${traitName.substring(0, 30)}...` ];
          });
        }
      } catch (err) {
        setLogs(prev => [...prev, `❌ Skip: ${traitName.substring(0, 20)}...`]);
      }

      setProgress(Math.round(((i + 1) / totalTraits) * 100));
    }

    setLogs(prev => [...prev, "💎 Finalizing Clinical Evidence Portfolio..."]);
    
    // AUTO-SAVE COMPLETE PORTFOLIO
    if (allResults.length > 0) {
      fetch('http://localhost:8000/save_scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: patientName || "Genomic Scan", results: allResults })
      }).catch(err => console.error("Auto-save failed:", err));
    }

    setTimeout(() => setStep(4), 1200);
  }

  const [activeView, setActiveView] = useState('workbench'); // New state for view switching

  const majors = categoryTree;

  return (
    <div className="workbench-container">
      <nav className="workbench-nav">
        <div className="brand">Beeja Genetics</div>
        <div className="nav-links">
          <button 
            className={`nav-link ${activeView === 'workbench' ? 'active' : ''}`}
            onClick={() => setActiveView('workbench')}
          >
            Clinical Workbench
          </button>
          <button 
            className={`nav-link ${activeView === 'helix' ? 'active' : ''}`}
            onClick={() => setActiveView('helix')}
          >
            Beeja Helix <span>NEW</span>
          </button>
        </div>
        <div className="nav-right">
           {patientName && <span className="patient-label">Patient: <strong>{patientName}</strong></span>}
        </div>
      </nav>

      <main className="main-content">
        {activeView === 'workbench' ? (
          <>
            {step === 1 && (
              <IntakePanel 
                patientName={patientName} setPatientName={setPatientName}
                age={age} setAge={setAge}
                diet={diet} cycleDiet={cycleDiet}
                analysisMode={analysisMode} setAnalysisMode={setAnalysisMode}
                file={file} setFile={setFile}
                fileInputRef={fileInputRef}
                onStartAnalysis={handleStartAnalysis}
                onOpenFocusModal={() => setShowFocusModal(true)}
                selectedCount={selectedTraits.length}
              />
            )}

            {step === 3 && (
              <div className="loading-view fade-in">
                <div className="clinical-pulse"></div>
                <h3>Analyzing Genetic Sequence...</h3>
                <div className="progress-bar-container">
                  <div className="progress-fill" style={{width: `${progress}%`}}></div>
                </div>
                <div className="log-container">
                  {logs.map((log, i) => <div key={i} className="log-entry">{log}</div>)}
                </div>
              </div>
            )}

            {step === 4 && (
              <ResultsCanvas 
                results={results} 
                patientName={patientName} 
                selectedCount={selectedTraits.length} 
              />
            )}
          </>
        ) : (
          <HelixView />
        )}
      </main>

      <GenomicModal 
        isOpen={showFocusModal}
        onClose={() => setShowFocusModal(false)}
        majors={majors}
        selectedTraits={selectedTraits}
        setSelectedTraits={setSelectedTraits}
      />
    </div>
  );
}

export default Workbench;
