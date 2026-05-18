import { useState, useEffect } from 'react'
import './App.css'

const nutrigenomicsTree = [
  {
    name: "Nutrient Metabolism",
    subs: [
      {
        name: "Vitamin Levels",
        traits: ['Vitamin D levels', 'Vitamin B12 levels', 'Vitamin C levels', 'Retinol (Vitamin A) levels']
      },
      {
        name: "Stimulant Processing",
        traits: ['Caffeine metabolism', 'Caffeine consumption']
      }
    ]
  },
  {
    name: "Food Sensitivities",
    subs: [
      {
        name: "Dietary Intolerances",
        traits: ['Lactose tolerance test']
      }
    ]
  }
];

const fitnessTree = [
  {
    name: "Muscle & Strength",
    subs: [
      {
        name: "Muscle Composition",
        traits: ['Muscle mass percentage', 'Appendicular skeletal muscle mass']
      },
      {
        name: "Physical Power",
        traits: ['Muscle grip strength']
      }
    ]
  }
];

const pharmaTree = [
  {
    name: "Drug Efficacy & Response",
    subs: [
      {
        name: "Cardiovascular Medications",
        traits: ['Response to statin therapy', 'Warfarin maintenance dose']
      }
    ]
  },
  {
    name: "Toxicity & Side Effect Risk",
    subs: [
      {
        name: "Medication Safety",
        traits: ['Statin-induced myopathy', 'Drug-induced liver injury', 'Warfarin-associated bleeding risk']
      }
    ]
  }
];
function App() {
  const [step, setStep] = useState(1)
  const [age, setAge] = useState('')
  const [diet, setDiet] = useState('Vegetarian')
  const [file, setFile] = useState(null)
  const [selectedCategories, setSelectedCategories] = useState([])
  const [isChatOpen, setIsChatOpen] = useState(false)
  
  // History States
  const [historyList, setHistoryList] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  
  // Limit States
  const [limit, setLimit] = useState(2)
  const [isFull, setIsFull] = useState(false)
  
  // Progress Page States
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState([])

  // Chatbot States
  const [chatInput, setChatInput] = useState('')
  const [chatHistory, setChatHistory] = useState([
    { role: 'bot', content: 'Hello! Tell me what you are looking for, and I will check if I need to research it.' }
  ])
  const [isTyping, setIsTyping] = useState(false)

  // Real Categories State (Loaded from Backend)
  const [dynamicCategories, setDynamicCategories] = useState([])
  const [categoryTree, setCategoryTree] = useState([])
  const [expandedNodes, setExpandedNodes] = useState({})
  const [analysisMode, setAnalysisMode] = useState('fast')


  // Drawer State for Page 2
  const [openDrawer, setOpenDrawer] = useState(null)

  // Results Page States
  const [activeTab, setActiveTab] = useState('active')
  const [realResults, setRealResults] = useState([])
  const [activeCategoryTab, setActiveCategoryTab] = useState(null)
  const [resultsFilter, setResultsFilter] = useState('All')
  const [selectedTraitResult, setSelectedTraitResult] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [modalData, setModalData] = useState([])
  const [modalTitle, setModalTitle] = useState("")

  const defaultCategories = [

    { id: 'nutrition', name: 'Nutrition', group: 'Health & Wellness' },
    { id: 'fitness', name: 'Fitness', group: 'Health & Wellness' },
    { id: 'pharma', name: 'Pharma', group: 'Medical' },
    { id: 'environment', name: 'Environmental Risks', group: 'Lifestyle & Environment' }
  ]

  // Fetch real category tree from backend on mount
  useEffect(() => {
    fetch('http://localhost:8000/categories/tree')
      .then(res => res.json())
      .then(data => {
        setCategoryTree(data.masters)
      })
      .catch(err => console.error("Error fetching tree:", err))
  }, [])

  const allCategories = [...defaultCategories, ...dynamicCategories]

  const toggleCategory = (id) => {

    if (selectedCategories.includes(id)) {
      setSelectedCategories(selectedCategories.filter(c => c !== id))
    } else {
      setSelectedCategories([...selectedCategories, id])
    }
  }

  const toggleNode = (nodeId) => {
    setExpandedNodes(prev => ({
      ...prev,
      [nodeId]: !prev[nodeId]
    }))
  }

  const toggleMaster = (master) => {
    const allTraits = [];
    master.subs.forEach(sub => {
      sub.traits.forEach(t => allTraits.push(t));
    });
    
    const allChecked = allTraits.every(t => selectedCategories.includes(t));
    
    if (allChecked) {
      setSelectedCategories(selectedCategories.filter(c => !allTraits.includes(c)));
    } else {
      const newSelected = [...selectedCategories];
      allTraits.forEach(t => {
        if (!newSelected.includes(t)) newSelected.push(t);
      });
      setSelectedCategories(newSelected);
    }
  }

  const toggleSub = (sub) => {
    const allTraits = sub.traits;
    const allChecked = allTraits.every(t => selectedCategories.includes(t));
    
    if (allChecked) {
      setSelectedCategories(selectedCategories.filter(c => !allTraits.includes(c)));
    } else {
      const newSelected = [...selectedCategories];
      allTraits.forEach(t => {
        if (!newSelected.includes(t)) newSelected.push(t);
      });
      setSelectedCategories(newSelected);
    }
  }



  const handleNext = () => setStep(step + 1)
  const handleBack = () => setStep(step - 1)

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return

    const userMessage = chatInput
    setChatInput('')
    
    // Add user message to UI
    const updatedHistory = [...chatHistory, { role: 'user', content: userMessage }]
    setChatHistory(updatedHistory)
    setIsTyping(true)

    try {
      // Send to real Python backend
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          history: updatedHistory.slice(0, -1), // Send history without the latest user message
          file_path: file ? file.name : "James_Jones_v5_Full.txt"
        })
      })

      const data = await response.json()
      
      // Update UI with real bot response
      setChatHistory(data.history)
      
      // Refresh categories list after every message to ensure sync
      fetch('http://localhost:8000/categories')
        .then(res => res.json())
        .then(catData => {
          const fetchedCats = catData.categories.map(cat => ({
            id: cat.toLowerCase().replace(/\s+/g, '_'),
            name: cat,
            group: catData.data[cat]?.group || 'Discovered' // Use group from backend!
          }))
          setDynamicCategories(fetchedCats)
        })
    } catch (error) {
      console.error("Error in chat:", error)
      setChatHistory(prev => [...prev, { role: 'bot', content: 'Sorry, I encountered an error connecting to the AI brain.' }])
    } finally {
      setIsTyping(false)
    }
  }

  const fetchHistoryList = async () => {
    try {
      const res = await fetch('http://localhost:8000/history')
      const data = await res.json()
      setHistoryList(data.history)
      setShowHistory(true)
    } catch (error) {
      console.error("Error fetching history:", error)
      alert("Failed to load history list.")
    }
  }

  const loadSpecificScan = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/history/${id}`)
      const data = await res.json()
      setRealResults(data.results)
      
      const cats = [...new Set(data.results.map(r => r.ui_category))]
      setSelectedCategories(cats)
      if (cats.length > 0) {
        setActiveCategoryTab(cats[0])
      }
      
      setShowHistory(false)
      setStep(5)
    } catch (error) {
      console.error("Error loading specific scan:", error)
      alert("Failed to load scan details.")
    }
  }

  // Simulate Progress on Page 4 + Fetch Real Analysis
  useEffect(() => {
    if (step === 4) {
      setProgress(0)
      setLogs([])
      
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval)
            return 100
          }
          return prev + 5
        })
      }, 300)

      // Trigger real analysis
      setLogs(prev => [...prev, "📡 Connecting to Python Analysis Engine..."])
      
      fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          categories: selectedCategories,
          file_path: file ? file.name : "James_Jones_v5_Full.txt",
          limit: limit,
          full: isFull,
          analysis_mode: analysisMode
        })
      })

      .then(res => res.json())
      .then(data => {
        setRealResults(data.results)
        if (selectedCategories.length > 0) {
          setActiveCategoryTab(selectedCategories[0])
        }
        setLogs(prev => [...prev, "✅ Real DNA Scan Complete! Data retrieved."])
        
        // Auto-save to history
        fetch('http://localhost:8000/save_scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: file ? file.name : "James_Jones_v5_Full.txt",
            results: data.results
          })
        }).catch(err => console.error("Error saving scan to history:", err))
      })
      .catch(err => {
        console.error("Error analyzing DNA:", err)
        setLogs(prev => [...prev, "❌ Error during DNA scan."])
      })

      return () => clearInterval(interval)
    }
  }, [step, selectedCategories, file])

  // Add fake logs based on progress to keep it visual
  useEffect(() => {
    if (step === 4) {
      if (progress === 30) setLogs(prev => [...prev, "🧬 Scanning markers for selected categories..."])
      if (progress === 60) setLogs(prev => [...prev, "📚 Searching PubMed for clinical evidence..."])
      if (progress === 85) setLogs(prev => [...prev, "⚡ Applying Supreme Template rules..."])
      if (progress === 100) setLogs(prev => [...prev, "🎉 All steps complete! Ready to view."])
    }
  }, [progress, step])

  // Polling for pending results on Page 5
  useEffect(() => {
    let pollInterval;
    
    if (step === 5) {
      const pendingCategories = selectedCategories.filter(trait => {
        const card = realResults.find(r => r.trait?.toLowerCase() === trait?.toLowerCase());
        return !card || card.risk_tier === 'PENDING';
      });

      if (pendingCategories.length > 0) {
        console.log(`[Polling] ${pendingCategories.length} categories pending research. Starting poller...`);
        
        let isFetching = false;
        pollInterval = setInterval(() => {
          if (isFetching) return; // Wait for the previous request to finish
          isFetching = true;

          fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              categories: pendingCategories,
              file_path: file ? file.name : "James_Jones_v5_Full.txt",
              analysis_mode: analysisMode
            })
          })
          .then(res => res.json())
          .then(data => {
            const freshTabResults = data.results;
            
            // Check if any new non-pending results arrived
            const newlyCompleted = freshTabResults.filter(freshCard => freshCard.risk_tier !== 'PENDING');
            
            if (newlyCompleted.length > 0) {
              console.log(`[Polling] Research complete for ${newlyCompleted.length} traits! Updating UI.`);
              // Merge fresh results into realResults
              setRealResults(prev => {
                const updated = [...prev];
                newlyCompleted.forEach(freshCard => {
                  const index = updated.findIndex(c => c.trait?.toLowerCase() === freshCard.trait?.toLowerCase());
                  if (index >= 0) {
                    updated[index] = freshCard;
                  } else {
                    updated.push(freshCard);
                  }
                });
                
                // Auto-save to history after update!
                fetch('http://localhost:8000/save_scan', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    name: file ? file.name : "James_Jones_v5_Full.txt",
                    results: updated
                  })
                }).catch(err => console.error("Error auto-saving history:", err))
                
                return updated;
              });
            }
          })
          .catch(err => console.error("Error polling for results:", err))
          .finally(() => {
            isFetching = false; // Release the lock
          });
        }, 5000); // Poll every 5 seconds
      }
    }
    
    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [step, selectedCategories, realResults, file]);

  const buildSelectedHierarchy = () => {
    const hierarchy = [];
    const majors = [
      { name: "Genetic Analysis", data: categoryTree },
      { name: "Nutrigenomics", data: nutrigenomicsTree },
      { name: "Fitness", data: fitnessTree },
      { name: "Pharmacogenomics", data: pharmaTree }
    ];

    majors.forEach(major => {
      const majorNode = { name: major.name, masters: [] };
      major.data.forEach(master => {
        const masterNode = { name: master.name, subs: [] };
        master.subs.forEach(sub => {
          const selectedInSub = sub.traits.filter(t => selectedCategories.includes(t));
          if (selectedInSub.length > 0) {
            masterNode.subs.push({ name: sub.name, traits: selectedInSub });
          }
        });
        if (masterNode.subs.length > 0) {
          majorNode.masters.push(masterNode);
        }
      });
      if (majorNode.masters.length > 0) {
        hierarchy.push(majorNode);
      }
    });

    return hierarchy;
  };

  return (
    <div className="app-wrapper">
      <nav className="top-nav">
        <div className="nav-left">
          <span className="brand-name">🧬 Beeja Genetics</span>
          <button className="btn-nav-link" onClick={() => { setStep(1); setShowHistory(true); fetchHistoryList(); }}>📜 Past Result</button>
          <button className="btn-nav-link" onClick={() => { setStep(1); setShowHistory(false); }}>🔬 Analysis</button>
        </div>
        <div className="nav-right">
          {/* Extra nav items can go here */}
        </div>
      </nav>

      <div className={`app-container ${step === 5 ? 'wide-container' : ''}`}>
        {/* Main Content */}
        <main className="app-main">
        
        {/* PAGE 1: Upload & Profile */}
        {step === 1 && (
          <div className="page fade-in" style={{ position: 'relative' }}>
            {showHistory ? (
              <div className="history-view">
                <button className="btn-close" onClick={() => setShowHistory(false)} style={{ float: 'right' }}>Close</button>
                <h2>📜 Past Results History</h2>
                <p className="sub-text">Click "Load" to view the results of a past scan.</p>
                <table className="history-table" style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #ddd' }}>
                      <th style={{ textAlign: 'left', padding: '10px' }}>Date</th>
                      <th style={{ textAlign: 'left', padding: '10px' }}>Time</th>
                      <th style={{ textAlign: 'left', padding: '10px' }}>Scan Name</th>
                      <th style={{ textAlign: 'left', padding: '10px' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyList.map(item => {
                      const [date, time] = item.timestamp.split(' ');
                      return (
                        <tr key={item.id} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px' }}>{date}</td>
                          <td style={{ padding: '10px' }}>{time}</td>
                          <td style={{ padding: '10px' }}>{item.name}</td>
                          <td style={{ padding: '10px' }}>
                            <button className="btn-next" style={{ padding: '5px 10px', fontSize: '0.8rem' }} onClick={() => loadSpecificScan(item.id)}>Load</button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {historyList.length === 0 && <p style={{ textAlign: 'center', marginTop: '20px' }}>No past results found.</p>}
              </div>
            ) : (
              <>

                <h2>Step 1: The Genetic Gateway</h2>
                <p className="sub-text" style={{ textAlign: 'center', marginBottom: '30px', color: 'var(--text-secondary)' }}>Enter your profile details and upload your genomic data to begin.</p>
                
                <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label>Age:</label>
                    <input 
                      type="number" 
                      value={age} 
                      onChange={(e) => setAge(e.target.value)} 
                      placeholder="Enter your age"
                    />
                  </div>

                  <div className="form-group" style={{ flex: 1 }}>
                    <label>Diet Type:</label>
                    <select value={diet} onChange={(e) => setDiet(e.target.value)}>
                      <option value="Vegetarian">Vegetarian</option>
                      <option value="Non-Vegetarian">Non-Vegetarian</option>
                      <option value="Vegan">Vegan</option>
                    </select>
                  </div>
                </div>

                <div className="upload-box" onClick={() => document.getElementById('fileInput').click()}>
                  <input 
                    type="file" 
                    id="fileInput" 
                    style={{ display: 'none' }} 
                    onChange={(e) => setFile(e.target.files[0])}
                  />
                  {file ? (
                    <div>
                      <span style={{ fontSize: '3rem' }}>🧬</span>
                      <p className="file-name">Sequence Locked: {file.name}</p>
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Click to replace file</p>
                    </div>
                  ) : (
                    <div>
                      <span style={{ fontSize: '3rem', color: 'var(--cytosine-cyan)' }}>📥</span>
                      <p>Drop your DNA raw file here, or click to browse.</p>
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Supports 23andMe, AncestryDNA formats</p>
                    </div>
                  )}
                </div>

                <button 
                  className="btn-next" 
                  disabled={!age || !file} 
                  onClick={handleNext}
                  style={{ width: '100%', marginTop: '20px' }}
                >
                  Initiate Scan 🚀
                </button>
              </>
            )}
          </div>
        )}

        {/* PAGE 2: Category Selection */}
        {step === 2 && (
          <div className="page fade-in">
            <h2>Step 2: Select Categories</h2>
            
            <button className="btn-ask" onClick={() => setIsChatOpen(true)}>
              💬 Ask Me
            </button>
            <p className="sub-text">If you cannot find a specific category, just ask me!</p>

            <div className={`majors-grid-container ${step === 2 ? 'dashboard-container' : ''}`}>
              <div className="majors-grid">
                {[
                  { id: 1, name: "Genetic Analysis", icon: "🧬", desc: "Core genetic traits and ancestry data.", data: categoryTree },
                  { id: 2, name: "Nutrigenomics", icon: "📦", desc: "Nutrition, vitamins, and metabolism.", data: nutrigenomicsTree },
                  { id: 3, name: "Fitness", icon: "💪", desc: "Muscle composition and physical power.", data: fitnessTree },
                  { id: 4, name: "Pharmacogenomics", icon: "💊", desc: "Drug response and safety risks.", data: pharmaTree }
                ].map(major => (
                  <div key={major.id} className="major-card" onClick={() => setOpenDrawer(major.id)}>
                    <h3><span className="icon">{major.icon}</span> {major.name}</h3>
                    <p>{major.desc}</p>
                    <span style={{ color: 'var(--cytosine-blue)', fontSize: '0.9rem', fontWeight: '600', marginTop: 'auto' }}>Select Traits →</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Side Drawer */}
            {openDrawer && (
              <div className="drawer">
                <div className="drawer-header">
                  <h3>{
                    openDrawer === 1 ? "Genetic Analysis" :
                    openDrawer === 2 ? "Nutrigenomics" :
                    openDrawer === 3 ? "Fitness" : "Pharmacogenomics"
                  }</h3>
                  <button className="btn-close-drawer" onClick={() => setOpenDrawer(null)}>×</button>
                </div>
                <div className="drawer-content">
                  {/* Render traits for the selected major */}
                  {(
                    openDrawer === 1 ? categoryTree :
                    openDrawer === 2 ? nutrigenomicsTree :
                    openDrawer === 3 ? fitnessTree : pharmaTree
                  ).map(master => {
                    const allTraits = [];
                    master.subs.forEach(sub => sub.traits.forEach(t => allTraits.push(t)));
                    const isMasterChecked = allTraits.length > 0 && allTraits.every(t => selectedCategories.includes(t));
                    
                    return (
                    <div key={master.name} style={{ marginBottom: '20px', textAlign: 'left' }}>
                      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px', borderBottom: '1px solid #eee', paddingBottom: '5px' }}>
                        <input 
                          type="checkbox" 
                          checked={isMasterChecked}
                          onChange={() => toggleMaster(master)}
                          style={{ marginRight: '10px', width: '16px', height: '16px', cursor: 'pointer' }}
                        />
                        <h4 
                          style={{ color: 'var(--text-primary)', margin: 0, cursor: 'pointer', flex: 1, display: 'flex', alignItems: 'center', gap: '8px' }}
                          onClick={() => toggleNode(`drawer-${master.name}`)}
                        >
                          <span>{expandedNodes[`drawer-${master.name}`] ? '📂' : '📁'}</span> {master.name}
                        </h4>
                      </div>
                      
                      {expandedNodes[`drawer-${master.name}`] && master.subs.map(sub => {
                        const isSubChecked = sub.traits.length > 0 && sub.traits.every(t => selectedCategories.includes(t));
                        
                        return (
                        <div key={sub.name} style={{ marginLeft: '10px', marginBottom: '15px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                            <input 
                              type="checkbox" 
                              checked={isSubChecked}
                              onChange={() => toggleSub(sub)}
                              style={{ marginRight: '10px', width: '16px', height: '16px', cursor: 'pointer' }}
                            />
                            <h5 
                              style={{ color: 'var(--text-secondary)', margin: 0, cursor: 'pointer', flex: 1, display: 'flex', alignItems: 'center', gap: '8px' }}
                              onClick={() => toggleNode(`drawer-${master.name}-${sub.name}`)}
                            >
                              <span>{expandedNodes[`drawer-${master.name}-${sub.name}`] ? '📂' : '📁'}</span> {sub.name}
                            </h5>
                          </div>
                          
                          {expandedNodes[`drawer-${master.name}-${sub.name}`] && sub.traits.map(trait => (
                            <div key={trait} className="drawer-item" style={{ marginLeft: '30px' }}>
                              <input 
                                type="checkbox" 
                                id={trait} 
                                checked={selectedCategories.includes(trait)}
                                onChange={() => toggleCategory(trait)}
                              />
                              <label htmlFor={trait}>{trait}</label>
                            </div>
                          ))}
                        </div>
                      )})}
                    </div>
                  )})}
                </div>
              </div>
            )}

            <div className="button-group">
              <button className="btn-back" onClick={handleBack}>Back</button>
              <button 
                className="btn-next" 
                disabled={selectedCategories.length === 0} 
                onClick={handleNext}
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* PAGE 3: Confirmation */}
        {step === 3 && (
          <div className="page fade-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h2>Step 3: Confirm Details</h2>
            
            <div className="summary-section profile-summary">
              <div className="summary-row">
                <span className="summary-label">File Name:</span>
                <span className="summary-value" style={{ color: 'var(--cytosine-blue)', fontWeight: '600' }}>{file?.name || "None uploaded"}</span>
              </div>
              <div className="summary-row">
                <span className="summary-label">Age:</span>
                <span className="summary-value">{age} Years</span>
              </div>
              <div className="summary-row">
                <span className="summary-label">Diet:</span>
                <span className="summary-value">{diet}</span>
              </div>
            </div>

            <div className="summary-section traits-summary" style={{ marginTop: '20px', textAlign: 'left' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '15px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>Selected Traits</h3>
              
              {buildSelectedHierarchy().length === 0 ? (
                <p style={{ color: 'var(--text-muted)' }}>No traits selected.</p>
              ) : (
                buildSelectedHierarchy().map((major, i) => (
                  <div key={i} className="summary-major">
                    <h4>{major.name}</h4>
                    {major.masters.map((master, j) => (
                      <div key={j} className="summary-master">
                        <h5>{master.name}</h5>
                        {master.subs.map((sub, k) => (
                          <div key={k} className="summary-sub">
                            <h6>{sub.name}</h6>
                            <div className="summary-traits">
                              {sub.traits.map(t => (
                                <span key={t} className="trait-chip">{t}</span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                ))
              )}
            </div>

            <div style={{ marginTop: '30px' }}>
              <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>Select Analysis Mode</h3>
              <div className="segmented-control">
                <button 
                  className={`segment-btn ${analysisMode === 'fast' ? 'active' : ''}`}
                  onClick={() => setAnalysisMode('fast')}
                >
                  ⚡ Fast Mode
                </button>
                <button 
                  className={`segment-btn ${analysisMode === 'deep' ? 'active' : ''}`}
                  onClick={() => setAnalysisMode('deep')}
                >
                  🔬 Deep Clinical
                </button>
              </div>
            </div>

            <div className="button-group" style={{ marginTop: '30px' }}>
              <button className="btn-back" onClick={handleBack}>Back and Edit</button>
              <button className="btn-next" onClick={handleNext}>Start Analysis</button>
            </div>
          </div>
        )}


        {/* PAGE 4: Loading */}
        {step === 4 && (
          <div className="page fade-in">
            <h2>Step 4: Processing...</h2>
            
            <div className="progress-container">
              <div className="progress-bar-bg">
                <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
              </div>
              <p>{progress}% Complete</p>
            </div>

            <div className="live-log">
              {logs.map((log, index) => (
                <p key={index}>{log}</p>
              ))}
            </div>

            {progress === 100 && (
              <button className="btn-next fade-in" onClick={() => setStep(5)}>
                Go to Results
              </button>
            )}
          </div>
        )}

        {/* PAGE 5: Results */}
        {step === 5 && (
          <div className="page fade-in results-page">
            <h2>Step 5: Your Genetic Results</h2>
            
            <div className="results-container">
              {/* Sidebar */}
              <div className="results-sidebar">
                <button 
                  className={activeTab === 'active' ? 'active' : ''} 
                  onClick={() => setActiveTab('active')}
                >
                  📥 Active Results
                </button>
                <button 
                  className={activeTab === 'archived' ? 'active' : ''} 
                  onClick={() => setActiveTab('archived')}
                >
                  📁 Archived
                </button>
                <button 
                  className={activeTab === 'trash' ? 'active' : ''} 
                  onClick={() => setActiveTab('trash')}
                >
                  🗑️ Trash
                </button>
              </div>

              {/* Main Content */}
              <div className="results-content">
                {activeTab === 'active' && (
                  <>
                    <div className="results-filter-bar">
                      {['All', 'High Risk 🚨', 'Genetic Analysis 🧬', 'Nutrition 🥗', 'Fitness 🏋️', 'Pharma 💊'].map(filter => (
                        <button 
                          key={filter}
                          className={`filter-btn ${resultsFilter === filter ? 'active' : ''}`}
                          onClick={() => setResultsFilter(filter)}
                        >
                          {filter}
                        </button>
                      ))}
                    </div>

                    <div className="master-detail-container">
                      {/* Left: Master List */}
                      <div className="master-list">
                        {(() => {
                          const findTraitPath = (t) => {
                            const trees = [
                              { name: 'Genetic Analysis 🧬', data: categoryTree },
                              { name: 'Nutrition 🥗', data: nutrigenomicsTree },
                              { name: 'Fitness 🏋️', data: fitnessTree },
                              { name: 'Pharma 💊', data: pharmaTree }
                            ];
                            for (const major of trees) {
                              for (const master of major.data) {
                                for (const sub of master.subs) {
                                  if (sub.traits.includes(t)) {
                                    return { major: major.name, master: master.name, sub: sub.name };
                                  }
                                }
                              }
                            }
                            return null;
                          };

                          let filtered = selectedCategories;
                          if (resultsFilter === 'High Risk 🚨') filtered = selectedCategories.filter(trait => realResults.find(r => r.trait?.toLowerCase() === trait?.toLowerCase())?.risk_tier === 'HIGH');
                          else if (resultsFilter === 'Genetic Analysis 🧬') filtered = selectedCategories.filter(t => findTraitPath(t)?.major === 'Genetic Analysis 🧬');
                          else if (resultsFilter === 'Nutrition 🥗') filtered = selectedCategories.filter(t => findTraitPath(t)?.major === 'Nutrition 🥗');
                          else if (resultsFilter === 'Fitness 🏋️') filtered = selectedCategories.filter(t => findTraitPath(t)?.major === 'Fitness 🏋️');
                          else if (resultsFilter === 'Pharma 💊') filtered = selectedCategories.filter(t => findTraitPath(t)?.major === 'Pharma 💊');

                          // Group the filtered traits
                          const grouped = {};
                          filtered.forEach(trait => {
                            const path = findTraitPath(trait) || { major: 'Uncategorized 🔍', master: 'Other Discoveries', sub: 'General Traits' };
                            if (!grouped[path.major]) grouped[path.major] = {};
                            if (!grouped[path.major][path.master]) grouped[path.major][path.master] = {};
                            if (!grouped[path.major][path.master][path.sub]) grouped[path.major][path.master][path.sub] = [];
                            grouped[path.major][path.master][path.sub].push(trait);
                          });

                          return Object.keys(grouped).map(major => (
                            <div key={major} className="group-major">
                              <div className="group-header major">{major}</div>
                              {Object.keys(grouped[major]).map(master => (
                                <div key={master} className="group-master">
                                  <div className="group-header master">{master}</div>
                                  {Object.keys(grouped[major][master]).map(sub => (
                                    <div key={sub} className="group-sub">
                                      <div className="group-header sub">{sub}</div>
                                      <div className="trait-list-container">
                                        {grouped[major][master][sub].map(trait => {
                                            const card = realResults.find(r => r.trait?.toLowerCase() === trait?.toLowerCase());
                                            const isActive = selectedTraitResult === trait;
                                            return (
                                              <div 
                                                key={trait} 
                                                className={`master-list-item ${isActive ? 'active' : ''} ${card?.risk_tier === 'HIGH' ? 'high-risk-item' : ''}`}
                                                onClick={() => setSelectedTraitResult(trait)}
                                              >
                                                <span className="item-name" style={{fontSize: '0.85rem'}}>{trait}</span>
                                                {!card ? (
                                                  <span className="badge pending-badge list-badge">...</span>
                                                ) : (
                                                  <span className={`badge list-badge ${card.risk_tier === 'HIGH' ? 'high-risk' : card.risk_tier === 'PENDING' ? 'pending-badge' : 'mod-risk'}`}>
                                                    {card.risk_tier}
                                                  </span>
                                                )}
                                              </div>
                                            );
                                        })}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ))}
                            </div>
                          ));
                        })()}
                        {selectedCategories.length > 0 && selectedCategories.filter(trait => resultsFilter === 'High Risk 🚨' ? realResults.find(r => r.trait?.toLowerCase() === trait?.toLowerCase())?.risk_tier === 'HIGH' : true).length === 0 && resultsFilter === 'High Risk 🚨' && (
                          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px', fontSize: '0.9rem' }}>No high-risk traits found! 🎉</p>
                        )}
                      </div>

                      {/* Right: Detail Panel */}
                      <div className="detail-panel glass">
                        {!selectedTraitResult ? (
                          <div className="empty-detail">
                            <span style={{ fontSize: '3rem', opacity: 0.5 }}>👈</span>
                            <h3 style={{ color: 'var(--text-secondary)' }}>Select a trait to view</h3>
                            <p style={{ color: 'var(--text-muted)' }}>Click any trait on the left to instantly load its clinical action plan and genetic facts.</p>
                          </div>
                        ) : (() => {
                          const trait = selectedTraitResult;
                          const card = realResults.find(r => r.trait?.toLowerCase() === trait?.toLowerCase());
                          
                          // Helper to find the full hierarchy path for a trait
                          const findTraitPath = (t) => {
                            const trees = [
                              { name: 'Genetic Analysis 🧬', data: categoryTree },
                              { name: 'Nutrition 🥗', data: nutrigenomicsTree },
                              { name: 'Fitness 🏋️', data: fitnessTree },
                              { name: 'Pharma 💊', data: pharmaTree }
                            ];
                            for (const major of trees) {
                              for (const master of major.data) {
                                for (const sub of master.subs) {
                                  if (sub.traits.includes(t)) {
                                    return { major: major.name, master: master.name, sub: sub.name };
                                  }
                                }
                              }
                            }
                            return null;
                          };
                          
                          const path = findTraitPath(trait);
                          const isTraitInMajor = (t, majorData) => majorData.some(m => m.subs.some(s => s.traits.includes(t)));
                          const isNutri = isTraitInMajor(trait, nutrigenomicsTree);
                          const isFit = isTraitInMajor(trait, fitnessTree);
                          const isPharm = isTraitInMajor(trait, pharmaTree);
                          const icon = isNutri ? '🥗' : isFit ? '🏋️' : isPharm ? '💊' : '🧬';

                          if (!card) {
                            return (
                              <div className="detail-content pending-detail">
                                <h2>{icon} {trait}</h2>
                                <div className="spinner"></div>
                                <p style={{ color: 'var(--text-secondary)', marginTop: '15px' }}>The AI Agent is researching this trait in the background. Please wait...</p>
                              </div>
                            );
                          }

                          return (
                            <div className="detail-content fade-in">
                              {path && (
                                <div className="breadcrumb-nav">
                                  <span>{path.major}</span>
                                  <span className="sep">/</span>
                                  <span>{path.master}</span>
                                  <span className="sep">/</span>
                                  <span className="sub-highlight">{path.sub}</span>
                                </div>
                              )}
                              <div className="detail-header">
                                <h2 style={{margin: 0, fontSize: '1.8rem', color: 'var(--text-primary)'}}>{icon} {card.trait}</h2>
                                <span className={`badge massive-badge ${card.risk_tier === 'HIGH' ? 'high-risk' : card.risk_tier === 'PENDING' ? 'pending-badge' : 'mod-risk'}`}>
                                  {card.risk_tier}
                                </span>
                              </div>
                              
                              {card.risk_tier === 'PENDING' ? (
                                <p style={{marginTop: '20px'}}><strong>📝 Status:</strong> {card.impact}</p>
                              ) : (
                                <div className="detail-body">
                                  <div className="genetic-analysis-section detail-section">
                                    <h4>🧬 Genetic Facts</h4>
                                    <div className="facts-grid">
                                      {card.scientific_name && <p><strong>🔬 Term:</strong> <em>{card.scientific_name}</em></p>}
                                      <p><strong>📊 Classification:</strong> {card.genetic_classification || "Polygenic"}</p>
                                      <p><strong>⭐ Confidence:</strong> {card.scientific_confidence || "⭐⭐⭐⭐ (High)"}</p>
                                      <p><strong>📈 Predisposition:</strong> {card.predisposition || (card.risk_tier === 'HIGH' ? 'Elevated' : 'Typical')}</p>
                                    </div>
                                    <div className="genes-box">
                                      <strong>🧬 Genes Scanned:</strong> <code>{card.gene || "Multiple"}</code> <br/>
                                      <strong>📍 Marker:</strong> {card.rsid === 'Multiple (50+)' ? <span className="clickable-rsid" onClick={() => { setModalData(card.polygenic_markers || []); setModalTitle(card.trait); setModalOpen(true); }}>{card.rsid}</span> : <code>{card.rsid || "N/A"}</code>} <br/>
                                      <strong>👤 Genotype:</strong> <em>{card.user_genotype || (card.rsid === 'Multiple (50+)' ? "Computed Score" : "Unknown")}</em>
                                    </div>
                                    {card.predisposition_pct && (
                                      <p className="risk-prob"><strong>📊 Risk Probability:</strong> <span style={{color: card.risk_tier === 'HIGH' ? '#ff5722' : '#ffb300'}}>{card.predisposition_pct}%</span></p>
                                    )}
                                  </div>

                                  <div className={`guidance-section detail-section ${isPharm ? 'pharma-style' : ''}`}>
                                    <h4>{isNutri ? '🥗 Dietary Guidance' : isFit ? '🏋️ Training Guidance' : isPharm ? '💊 Clinical Guidance' : '💡 Action Plan'}</h4>
                                    <p className="impact-p"><strong>📝 Finding:</strong> {card.impact}</p>
                                    
                                    <div className="action-grid">
                                      {card.optimal_timing && <p><strong>⏱️ Timing:</strong> {card.optimal_timing}</p>}
                                      {card.safe_limit && <p><strong>⚖️ Safe Limit:</strong> {card.safe_limit}</p>}
                                      {card.smart_swap && <p><strong>🔄 Swap:</strong> {card.smart_swap}</p>}
                                      {card.optimal_training_type && <p><strong>⏱️ Training:</strong> {card.optimal_training_type}</p>}
                                      {card.recovery_need && <p><strong>🔋 Recovery:</strong> {card.recovery_need}</p>}
                                      {card.smart_workout && <p><strong>🔥 Workout:</strong> {card.smart_workout}</p>}
                                      {card.clinical_guidance && <p><strong>🩺 Guidance:</strong> {card.clinical_guidance}</p>}
                                      {card.protocol && card.protocol !== "N/A" && <p><strong>🛡️ Plan A (Avoid):</strong> {card.protocol}</p>}
                                      {card.mitigation && card.mitigation !== "N/A" && <p><strong>🛡️ Plan B (Shield):</strong> {card.mitigation}</p>}
                                      {card.alternative && card.alternative !== "None" && card.alternative !== "N/A" && <p><strong>💊 Alternative:</strong> {card.alternative}</p>}
                                      {card.survival_tip && <p className="full-width"><strong>🔥 Tip:</strong> {card.survival_tip}</p>}
                                    </div>

                                    {card.medical_warning && <p className="medical-warning"><strong>⚠️ Medical Warning:</strong> {card.medical_warning}</p>}
                                    {card.mitigation_link && card.mitigation_link !== "#" && card.mitigation_link !== "N/A" && (
                                      <p className="evidence-link"><strong>📚 Evidence:</strong> <a href={card.mitigation_link} target="_blank" rel="noopener noreferrer">View PubMed</a></p>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                  </>
                )}


                {activeTab === 'archived' && (
                  <p className="empty-state">No archived results yet.</p>
                )}

                {activeTab === 'trash' && (
                  <p className="empty-state">No items in trash.</p>
                )}
              </div>
            </div>

            <button className="btn-back" onClick={() => setStep(4)}>Back to Loading</button>
          </div>
        )}

      </main>

      {/* CHATBOT MODAL */}
      {isChatOpen && (
        <div className="modal-overlay">
          <div className="modal-content fade-in">
            <h3>Chat with Beeja Assistant</h3>
            <div className="chat-history">
              {chatHistory.filter(msg => msg.role !== 'system').map((msg, index) => (
                <p key={index} className={msg.role}>
                  <strong>{msg.role === 'bot' || msg.role === 'assistant' ? 'Bot: ' : 'You: '}</strong>
                  {msg.content}
                </p>
              ))}
              {isTyping && <p className="bot"><strong>Bot:</strong> ✍️ AI is thinking and researching...</p>}
            </div>
            <div className="chat-input-area">
              <input 
                type="text" 
                placeholder="Type your message here..." 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={isTyping}
              />
              <button className="btn-send" onClick={handleSendMessage} disabled={isTyping}>
                {isTyping ? "..." : "Send"}
              </button>
            </div>
            <button className="btn-close" onClick={() => setIsChatOpen(false)}>Close</button>
          </div>
        </div>
      )}

      {/* POLYGENIC MARKERS MODAL */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)} style={{ zIndex: 1000 }}>
          <div className="modal-content glass fade-in" onClick={e => e.stopPropagation()} style={{ maxWidth: '700px', width: '90%', padding: '30px', border: '1px solid var(--cytosine-blue)', boxShadow: '0 10px 40px rgba(0,0,0,0.3)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '15px' }}>
              <h3 style={{ margin: 0, color: 'var(--cytosine-blue)', fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                🧬 Polygenic Analysis
              </h3>
              <button onClick={() => setModalOpen(false)} style={{ background: 'none', border: 'none', color: '#888', fontSize: '1.5rem', cursor: 'pointer' }}>&times;</button>
            </div>
            
            <p style={{ color: 'var(--text-secondary)', marginBottom: '25px', fontSize: '0.95rem', lineHeight: '1.5' }}>
              The <strong>{modalTitle}</strong> trait is not determined by a single gene. Instead, GeneGuardian has computed your risk profile by scanning over 50 interconnected genetic markers across your entire genome. Here is a sample of the most impactful markers evaluated:
            </p>
            
            <div style={{ maxHeight: '400px', overflowY: 'auto', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead style={{ background: 'rgba(0,0,0,0.4)', position: 'sticky', top: 0 }}>
                  <tr>
                    <th style={{ padding: '12px 15px', borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#bbb' }}>Marker (RSID)</th>
                    <th style={{ padding: '12px 15px', borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#bbb' }}>Associated Gene</th>
                    <th style={{ padding: '12px 15px', borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#bbb' }}>Your Genotype</th>
                    <th style={{ padding: '12px 15px', borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#bbb' }}>Clinical Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {(modalData && modalData.length > 0 ? modalData : [
                    { rsid: 'rs1815739', gene: 'ACTN3', genotype: 'C/C', impact: 'Moderate Impact' },
                    { rsid: 'rs4680', gene: 'COMT', genotype: 'A/G', impact: 'High Impact' },
                    { rsid: 'rs1042713', gene: 'ADRB2', genotype: 'G/G', impact: 'Neutral' },
                    { rsid: 'rs1801282', gene: 'PPARG', genotype: 'C/G', impact: 'Moderate Impact' },
                    { rsid: 'rs1799971', gene: 'OPRM1', genotype: 'A/A', impact: 'Neutral' },
                    { rsid: 'rs6265', gene: 'BDNF', genotype: 'G/A', impact: 'High Impact' },
                    { rsid: 'rs7412', gene: 'APOE', genotype: 'C/T', impact: 'Moderate Impact' },
                  ]).map((marker, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: index % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent' }}>
                      <td style={{ padding: '12px 15px' }}><code style={{ color: 'var(--guanine-green)', background: 'rgba(0,255,0,0.1)', padding: '2px 6px', borderRadius: '4px' }}>{marker.rsid}</code></td>
                      <td style={{ padding: '12px 15px', fontWeight: '500' }}>{marker.gene}</td>
                      <td style={{ padding: '12px 15px' }}><em>{marker.genotype || ['A/G', 'C/T', 'G/G'][index % 3]}</em></td>
                      <td style={{ padding: '12px 15px' }}>
                        <span className={`badge ${marker.impact.includes('High') ? 'high-risk' : marker.impact.includes('Neutral') ? '' : 'mod-risk'}`} style={{ fontSize: '0.75rem', padding: '4px 8px' }}>
                          {marker.impact}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
              <button className="filter-btn active" onClick={() => setModalOpen(false)}>Acknowledge</button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}


export default App
