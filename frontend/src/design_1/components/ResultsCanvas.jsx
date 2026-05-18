import React, { useState } from 'react';
import '../styles/Results.css';

const ResultsCanvas = ({ results = [], patientName, selectedCount }) => {
  const [activeResultTab, setActiveResultTab] = useState('All');
  
  if (!results) return <div className="results-canvas">No results data available.</div>;

  const pillars = [...new Set(results.map(r => r.ui_category || r.major))].filter(Boolean);

  return (
    <div className="results-layout fade-in">
      <aside className="results-sidebar">
        <h3>Genomic Pillars</h3>
        <div 
          className={`result-nav-item ${activeResultTab === 'All' ? 'active' : ''}`}
          onClick={() => setActiveResultTab('All')}
        >
          📊 All Findings <span>{results.length}</span>
        </div>
        
        {pillars.map(cat => (
          <div 
            key={cat}
            className={`result-nav-item ${activeResultTab === cat ? 'active' : ''}`}
            onClick={() => setActiveResultTab(cat)}
          >
            {cat} <span>{results.filter(r => (r.ui_category || r.major) === cat).length}</span>
          </div>
        ))}
      </aside>

      <main className="results-canvas">
        <div style={{maxWidth: '900px', margin: '0 auto'}}>
          <header className="results-header">
            <div className="patient-meta">
              <h1>Clinical Report: {patientName || 'Patient'}</h1>
              <p>Sequence analyzed against {selectedCount} clinical markers.</p>
            </div>
            <button className="print-btn" onClick={() => window.print()}>📥 Export PDF</button>
          </header>

          <div className="results-list">
            {results
              .filter(r => activeResultTab === 'All' || (r.ui_category || r.major) === activeResultTab)
              .map((r, i) => {
                const catLower = (r.ui_category || r.major || '').toLowerCase();
                const traitLower = (r.trait || '').toLowerCase();
                
                const isPharma = catLower.includes('pharma') || traitLower.includes('drug') || traitLower.includes('medication');
                const isNutri = catLower.includes('nutri') || catLower.includes('nutrient') || traitLower.includes('vitamin') || traitLower.includes('mineral');
                const isFitness = catLower.includes('fitness') || traitLower.includes('muscle') || traitLower.includes('power');

                return (
                  <div key={i} className={`result-card fade-in ${isPharma ? 'pharma' : isNutri ? 'nutri' : isFitness ? 'fitness' : ''}`}>
                    {/* LEFT PANE: CLINICAL NARRATIVE */}
                    <div className="result-main">
                      {/* 1. CLINICAL CONTEXT (HEADER) */}
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px'}}>
                        <div className="clinical-path" style={{fontSize: '0.65rem', color: 'var(--active-teal)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                          {r.major || 'Genetics'} ➔ {r.master || 'Clinical'} ➔ {r.sub || 'Analysis'}
                        </div>
                      </div>

                      {/* 2. PHENOTYPE PILL */}
                      <div style={{marginBottom: '15px'}}>
                        <span className={`status-pill ${
                          r.risk_tier === 'High' ? 'status-alert' : 
                          r.risk_tier === 'Moderate' ? 'status-info' : 'status-success'
                        }`}>
                          {isPharma ? (r.phenotype || (r.risk_tier === 'High' ? 'Poor Metabolizer' : 'Normal Metabolizer')) :
                           isNutri ? (r.efficiency || (r.risk_tier === 'High' ? 'Impaired Absorption' : 'Optimized')) : 
                           isFitness ? (r.profile || 'Standard Profile') : (r.risk_tier || 'Optimized')}
                        </span>
                      </div>
                      
                      {/* 3. CLINICAL FINDING (CORE) */}
                      <h4 style={{margin: '0 0 10px 0', fontSize: '1.4rem', letterSpacing: '-0.5px'}}>{r.trait}</h4>
                      <p className="result-summary" style={{fontSize: '1rem', lineHeight: '1.6', color: '#475569', margin: '0 0 20px 0'}}>
                        {r.summary || r.impact || "No clinical summary available."}
                      </p>

                      {r.advice && !isPharma && !isNutri && (
                        <div className="advice-box" style={{marginBottom: '20px'}}>
                          <strong>📋 Clinical Note:</strong> {r.advice}
                        </div>
                      )}

                      {/* NEW: SCIENTIFIC TRANSPARENCY SECTION */}
                      {r.clinical_plan && (
                        <div className="transparency-box" style={{background: '#f8fafc', padding: '15px', borderRadius: '12px', border: '1px solid #e2e8f0', marginBottom: '15px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: 'var(--active-teal)', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px'}}>
                            🔬 Investigative Plan
                          </div>
                          <div style={{fontSize: '0.9rem', lineHeight: '1.5', color: '#1e293b'}}>
                            {r.clinical_plan}
                          </div>
                        </div>
                      )}

                      {r.genetic_mechanism && (
                        <div className="transparency-box" style={{background: '#f0f9ff', padding: '15px', borderRadius: '12px', border: '1px solid #bae6fd', marginBottom: '15px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: '#0369a1', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px'}}>
                            🧬 Genetic Mechanism
                          </div>
                          <div style={{fontSize: '0.9rem', lineHeight: '1.5', color: '#0c4a6e'}}>
                            {r.genetic_mechanism}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* RIGHT PANE: LABORATORY METRICS */}
                    <div className="result-side" style={{display: 'flex', flexDirection: 'column', gap: '15px', paddingLeft: '20px', borderLeft: '1px solid #f1f5f9'}}>
                      
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                        <div className="genotype-display" style={{flex: 1, padding: '10px', borderRadius: '12px', background: '#f8fafc', border: '1px solid #e2e8f0'}}>
                          <div className="dna-label" style={{fontSize: '0.6rem', textTransform: 'uppercase', marginBottom: '2px'}}>Genotype</div>
                          <div className="dna-sequence" style={{fontSize: '1.2rem', letterSpacing: '0.5px'}}>
                            <span style={{color: 'var(--active-teal)', marginRight: '8px', fontSize: '0.9rem', fontWeight: 600}}>{r.gene || ""}</span>
                            {r.genotype || r.user_genotype || "N/A"}
                          </div>
                        </div>
                        {isPharma && (
                          <div className="activity-box" style={{flex: 1, marginLeft: '10px', padding: '10px', borderRadius: '12px', background: r.risk_tier === 'High' ? '#fee2e2' : '#f1f5f9', border: '1px solid #e2e8f0', textAlign: 'center'}}>
                            <div className="dna-label" style={{fontSize: '0.6rem', textTransform: 'uppercase', marginBottom: '2px'}}>Activity Score</div>
                            <div style={{fontSize: '1.1rem', fontWeight: 800, color: r.risk_tier === 'High' ? '#b91c1c' : 'var(--sidebar-navy)'}}>
                              {r.activity_score || (r.risk_tier === 'High' ? '0.0 / 2.0' : '2.0 / 2.0')}
                            </div>
                          </div>
                        )}
                      </div>

                      {isPharma && (
                        <div className="guideline-badge" style={{fontSize: '0.65rem', fontWeight: 800, background: '#fef2f2', color: '#dc2626', padding: '5px 10px', borderRadius: '6px', border: '1px solid #fecaca', textAlign: 'center'}}>
                          ⚖️ CPIC LEVEL {r.evidence_level || '1A'} EVIDENCE
                        </div>
                      )}

                      {/* SCIENTIFIC COMPLIANCE LEDGER */}
                      <div className="compliance-ledger" style={{background: '#f8fafc', padding: '12px', borderRadius: '10px', border: '1px solid #e2e8f0', marginTop: '10px'}}>
                        <div style={{fontSize: '0.6rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase', marginBottom: '8px', borderBottom: '1px solid #e2e8f0', paddingBottom: '4px'}}>
                          🏛️ Clinical Standards
                        </div>
                        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px'}}>
                          <div style={{fontSize: '0.7rem'}}>
                            <strong style={{color: '#64748b'}}>ACMG:</strong> 
                            <span style={{marginLeft: '4px', fontWeight: 600, color: r.acmg_class === 'Pathogenic' ? '#dc2626' : '#1e293b'}}>
                              {r.acmg_class || 'VUS'}
                            </span>
                          </div>
                          <div style={{fontSize: '0.7rem'}}>
                            <strong style={{color: '#64748b'}}>HGVS:</strong> 
                            <span style={{marginLeft: '4px', fontFamily: 'monospace', color: '#0369a1'}}>
                              {r.hgvs_id || 'N/A'}
                            </span>
                          </div>
                          <div style={{fontSize: '0.7rem'}}>
                            <strong style={{color: '#64748b'}}>HPO:</strong> 
                            <span style={{marginLeft: '4px', color: '#15803d'}}>
                              {r.hpo_term || 'N/A'}
                            </span>
                          </div>
                          <div style={{fontSize: '0.7rem'}}>
                            <strong style={{color: '#64748b'}}>Evidence:</strong> 
                            <span style={{marginLeft: '4px', fontWeight: 600}}>
                              Lvl {r.evidence_level || '3'}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* 4. ACTIONABLE DATA / PERFORMANCE PROFILE */}
                      {isPharma ? (
                        <div className="actionable-context-box" style={{background: '#f8fafc', padding: '12px', borderRadius: '10px', border: '1px solid #e2e8f0'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '5px'}}>
                            📏 Precision Dosing
                          </div>
                          <div style={{fontSize: '0.8rem', marginBottom: '4px'}}><strong>Action:</strong> {r.dosing_recommendation || (r.risk_tier === 'High' ? '100% Dose Reduction (Switch Recommended).' : 'Standard Dosing.')}</div>
                          <div style={{fontSize: '0.8rem'}}><strong>Capacity:</strong> {r.metabolic_capacity || (r.risk_tier === 'High' ? '0% Clearance.' : '100% Normal.')}</div>
                        </div>
                      ) : isNutri ? (
                        <div className="target-box" style={{background: '#f0fdf4', padding: '12px', borderRadius: '10px', border: '1px solid #bbf7d0', marginBottom: '15px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: '#0f766e', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '5px'}}>
                            🎯 Daily Target
                          </div>
                          <div style={{fontSize: '0.8rem', marginBottom: '4px'}}><strong>Action:</strong> {r.target || (r.risk_tier === 'High' ? 'Increase intake + Supplementation' : 'Standard DRI')}</div>
                          <div style={{fontSize: '0.8rem'}}><strong>Bioavailability:</strong> {r.bioavailability || (r.risk_tier === 'High' ? 'Clinically Reduced' : 'Optimal')}</div>
                        </div>
                      ) : isFitness ? (
                        <div className="performance-box" style={{background: '#fef2f2', padding: '12px', borderRadius: '10px', border: '1px solid #fecaca', marginBottom: '15px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: '#b91c1c', textTransform: 'uppercase', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '5px'}}>
                            ⚡ Training Protocol
                          </div>
                          <div style={{fontSize: '0.8rem', marginBottom: '4px'}}><strong>Focus:</strong> {r.training_protocol || 'Balanced conditioning.'}</div>
                          <div style={{fontSize: '0.8rem'}}><strong>Drills:</strong> {r.recommended_drills || 'Compound movements.'}</div>
                        </div>
                      ) : null}

                      {/* 5. CLINICAL LOGIC / METABOLIC PATH / RECOVERY */}
                      {isPharma ? (
                        <div className="logic-context-box" style={{background: '#fff', padding: '12px', borderRadius: '10px', border: '1px dashed #cbd5e1'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase', marginBottom: '6px'}}>🧪 Clinical Logic</div>
                          <div style={{fontSize: '0.8rem', marginBottom: '4px'}}><strong>Risk:</strong> {r.interaction_risk || (r.risk_tier === 'High' ? 'High risk of therapeutic failure.' : 'Low interaction risk.')}</div>
                          <div style={{fontSize: '0.8rem'}}><strong>Implication:</strong> {r.phenotype_implication || 'Therapeutic range affected by metabolic status.'}</div>
                        </div>
                      ) : isNutri ? (
                        <div className="logic-context-box" style={{background: '#fff', padding: '12px', borderRadius: '10px', border: '1px dashed #cbd5e1', marginBottom: '15px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: '#0f766e', textTransform: 'uppercase', marginBottom: '6px'}}>🧬 Metabolic Path</div>
                          <div style={{fontSize: '0.8rem', marginBottom: '4px'}}><strong>Reason:</strong> {r.pathway_logic || 'Standard metabolic conversion pathway.'}</div>
                          <div style={{fontSize: '0.8rem'}}><strong>Implication:</strong> {r.implication || 'Verify with blood biomarkers.'}</div>
                        </div>
                      ) : isFitness ? (
                        <div className="logic-context-box" style={{background: '#fff', padding: '12px', borderRadius: '10px', border: '1px dashed #cbd5e1', marginBottom: '15px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, color: '#b91c1c', textTransform: 'uppercase', marginBottom: '6px'}}>🛡️ Athletic Recovery</div>
                          <div style={{fontSize: '0.8rem', marginBottom: '4px'}}><strong>Need:</strong> {r.recovery_need || '48-hour fiber repair.'}</div>
                          <div style={{fontSize: '0.8rem'}}><strong>Risk:</strong> {r.injury_risk || 'Standard musculoskeletal risk.'}</div>
                        </div>
                      ) : null}

                      {/* 6. SOLUTIONS / METERS */}
                      {isPharma && (r.alternatives || r.alternative) ? (
                        <div className="solution-box" style={{background: 'var(--sidebar-navy)', color: 'white', padding: '12px', borderRadius: '10px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, opacity: 0.8, textTransform: 'uppercase', marginBottom: '4px'}}>💡 Suggested Alternatives</div>
                          <div style={{fontSize: '0.8rem', fontWeight: 600}}>{r.alternatives || r.alternative}</div>
                        </div>
                      ) : isNutri && r.recommended_sources ? (
                        <div className="solution-box" style={{background: '#0f766e', color: 'white', padding: '12px', borderRadius: '10px'}}>
                          <div style={{fontSize: '0.65rem', fontWeight: 800, opacity: 0.8, textTransform: 'uppercase', marginBottom: '4px'}}>🍎 Bioavailable Sources</div>
                          <div style={{fontSize: '0.8rem', fontWeight: 600}}>{r.recommended_sources}</div>
                        </div>
                      ) : isFitness ? (
                        <div className="meter-container" style={{padding: '10px', background: '#f8fafc', borderRadius: '10px'}}>
                          <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.6rem', fontWeight: 800, color: '#64748b', textTransform: 'uppercase', marginBottom: '5px'}}>
                            <span>Endurance</span>
                            <span>Power</span>
                          </div>
                          <div className="performance-meter-track" style={{height: '6px', background: '#e2e8f0', borderRadius: '3px', position: 'relative'}}>
                            <div className="performance-meter-fill" style={{
                              position: 'absolute', height: '100%', 
                              left: '50%',
                              width: `${Math.abs((r.power_score || 50) - 50)}%`,
                              marginLeft: (r.power_score || 50) < 50 ? `-${Math.abs((r.power_score || 50) - 50)}%` : '0',
                              background: 'var(--active-teal)', borderRadius: '3px'
                            }}></div>
                          </div>
                        </div>
                      ) : null}

                      {(() => {
                        const evidenceUrl = (r.mitigation_link && r.mitigation_link !== "N/A" && r.mitigation_link !== "#") 
                          ? r.mitigation_link 
                          : (r.citations && r.citations.length > 0 ? r.citations[0].url : null);
                        
                        if (!evidenceUrl) return null;
                        
                        return (
                          <div className="evidence-link" style={{marginTop: 'auto', borderTop: '1px solid #f1f5f9', paddingTop: '10px'}}>
                            <button 
                              style={{width: '100%'}}
                              onClick={() => window.open(evidenceUrl, "_blank", "noopener,noreferrer")}
                            >
                              View Level {r.evidence_level || '1A'} Evidence ↗
                            </button>
                          </div>
                        );
                      })()}
                    </div>
                  </div>
                );
              })}
          </div>
          
          {results.length === 0 && (
            <div className="empty-results">
              <p>No results found for the selected genomic markers.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default ResultsCanvas;
