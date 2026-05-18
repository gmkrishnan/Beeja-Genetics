import { useState, useEffect } from 'react'
import './Workbench.css'

function Workbench() {
  const [step, setStep] = useState(1) // 1: Intake, 2: Categories, 3: Progress, 4: Results
  const [patientName, setPatientName] = useState('')
  const [age, setAge] = useState(25)
  const [diet, setDiet] = useState('Omnivore')
  const [analysisMode, setAnalysisMode] = useState('fast')
  const [file, setFile] = useState(null)
  
  const [selectedTraits, setSelectedTraits] = useState([])
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState([])
  const [results, setResults] = useState([])

  // State for the category tree (fetched from backend)
  const [categoryTree, setCategoryTree] = useState([])

  useEffect(() => {
    fetch('http://localhost:8000/categories/tree')
      .then(res => res.json())
      .then(data => setCategoryTree(data.masters))
      .catch(err => console.error("Error fetching tree:", err))
  }, [])

  const handleStartAnalysis = () => {
    if (!file && !patientName) return
    setStep(3)
    startGenomeScan()
  }

  const startGenomeScan = () => {
    setProgress(0)
    setLogs(["📡 Initializing Clinical Engine..."])
    
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 5
      })
    }, 400)

    fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        categories: selectedTraits,
        file_path: file ? file.name : "James_Jones_v5_Full.txt",
        analysis_mode: analysisMode
      })
    })
    .then(res => res.json())
    .then(data => {
      setResults(data.results)
      setLogs(prev => [...prev, "✅ Analysis Complete. Data synchronized."])
      setTimeout(() => setStep(4), 1000)
    })
    .catch(err => {
      setLogs(prev => [...prev, "❌ Connection Error. Retrying..."])
    })
  }

  return (
    <div className="workbench-container">
      <nav className="workbench-nav">
        <div className="brand">🧬 Beeja Clinical Workbench</div>
      </nav>

      <main className="main-content">
        
        {/* STEP 1: GEMINI-STYLE INTAKE */}
        {step === 1 && (
          <div className="intake-card">
            <h1>Patient Intake</h1>
            <p className="subtitle">Initialize your genomic analysis with clinical bio-data.</p>
            
            <div className="form-group">
              <label>Patient Name</label>
              <input 
                type="text" 
                placeholder="Enter full name..." 
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Genomic Data Source</label>
              <div 
                className={`file-upload-zone ${file ? 'has-file' : ''}`}
                onClick={() => document.getElementById('dna-upload').click()}
              >
                {file ? `📄 ${file.name}` : "Click to upload DNA file (.txt, .vcf)"}
                <input 
                  id="dna-upload" 
                  type="file" 
                  hidden 
                  onChange={(e) => setFile(e.target.files[0])} 
                />
              </div>
            </div>

            <div className="form-group">
              <label>Analysis Engine</label>
              <select value={analysisMode} onChange={(e) => setAnalysisMode(e.target.value)}>
                <option value="fast">⚡ Fast Mode (AI Inferred)</option>
                <option value="deep">🔬 Deep Clinical (PubMed Research)</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '20px' }}>
              <div className="form-group" style={{ flex: 1 }}>
                <label>Biological Age ({age})</label>
                <input 
                  type="range" 
                  min="0" 
                  max="120" 
                  value={age} 
                  onChange={(e) => setAge(parseInt(e.target.value))} 
                />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label>Dietary Baseline</label>
                <select value={diet} onChange={(e) => setDiet(e.target.value)}>
                  <option>Omnivore</option>
                  <option>Vegetarian</option>
                  <option>Vegan</option>
                  <option>Keto</option>
                  <option>Paleo</option>
                </select>
              </div>
            </div>

            <button 
              className="btn-primary" 
              onClick={() => setStep(2)}
              disabled={!patientName}
            >
              Continue to Category Selection →
            </button>
          </div>
        )}

        {/* STEP 2: CATEGORY SELECTION */}
        {step === 2 && (
          <div className="intake-card" style={{ maxWidth: '800px' }}>
            <h1>Select Focus Areas</h1>
            <p className="subtitle">Choose the genetic markers you wish to evaluate for {patientName}.</p>
            
            <div style={{ maxHeight: '400px', overflowY: 'auto', marginBottom: '30px' }}>
              {categoryTree.map(master => (
                <div key={master.name} style={{ marginBottom: '20px' }}>
                  <h3 style={{ fontSize: '0.9rem', color: 'var(--accent-blue)', textTransform: 'uppercase' }}>{master.name}</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '10px' }}>
                    {master.subs.flatMap(s => s.traits).map(trait => (
                      <label key={trait} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem', cursor: 'pointer' }}>
                        <input 
                          type="checkbox" 
                          checked={selectedTraits.includes(trait)}
                          onChange={(e) => {
                            if (e.target.checked) setSelectedTraits([...selectedTraits, trait])
                            else setSelectedTraits(selectedTraits.filter(t => t !== trait))
                          }}
                        />
                        {trait}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '15px' }}>
               <button className="btn-primary" style={{ background: '#334155' }} onClick={() => setStep(1)}>Back</button>
               <button className="btn-primary" onClick={handleStartAnalysis}>Initialize Genome Scan</button>
            </div>
          </div>
        )}

        {/* STEP 3: LOADING */}
        {step === 3 && (
          <div className="loading-state">
            <div className="spinner-ring"></div>
            <h2>Scanning {patientName}'s Genome...</h2>
            <div style={{ width: '300px', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', margin: '20px 0', overflow: 'hidden' }}>
               <div style={{ width: `${progress}%`, height: '100%', background: 'var(--accent-blue)', transition: 'width 0.3s ease' }}></div>
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {logs[logs.length - 1]}
            </div>
          </div>
        )}

        {/* STEP 4: RESULTS CANVAS */}
        {step === 4 && (
          <div className="workbench-results">
             <div className="sidebar-panel">
                <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)' }}>
                  <h4 style={{ margin: 0 }}>{patientName}</h4>
                  <p style={{ fontSize: '0.8rem', color: var(--text-muted), margin: '5px 0 0' }}>{age}y | {diet}</p>
                </div>
                {/* List of traits result badges would go here */}
                <div style={{ padding: '20px' }}>
                  {results.map(r => (
                    <div key={r.trait} style={{ marginBottom: '10px', padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', fontSize: '0.85rem' }}>
                      {r.trait}
                    </div>
                  ))}
                </div>
             </div>
             <div className="canvas-panel">
                <h1 style={{ marginBottom: '10px' }}>Clinical Report</h1>
                <p style={{ color: 'var(--text-muted)' }}>Select a trait from the left to view detailed action plans.</p>
                {/* Detailed card logic would go here */}
             </div>
          </div>
        )}

      </main>
    </div>
  )
}

export default Workbench
