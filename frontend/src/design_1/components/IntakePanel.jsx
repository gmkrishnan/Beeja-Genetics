import React from 'react';
import '../styles/Intake.css';

const IntakePanel = ({ 
  patientName, 
  setPatientName, 
  age, 
  setAge, 
  diet, 
  cycleDiet, 
  analysisMode, 
  setAnalysisMode, 
  file, 
  setFile, 
  fileInputRef, 
  onStartAnalysis,
  onOpenFocusModal,
  selectedCount
}) => {
  const [showAgeSlider, setShowAgeSlider] = React.useState(false);

  return (
    <div className="intake-panel fade-in">
      <div className="hero-text">
        <h1>Hello, {patientName || 'Clinical Specialist'}.</h1>
        <h2>How can I help you analyze your genome today?</h2>
      </div>

      <div className="smart-bar-container">
        <div className="mode-selector">
          <span 
            className={`mode-option ${analysisMode === 'fast' ? 'active' : ''}`} 
            onClick={() => setAnalysisMode('fast')}
          >
            Fast Analysis
          </span>
          <span 
            className={`mode-option ${analysisMode === 'deep' ? 'active' : ''}`} 
            onClick={() => setAnalysisMode('deep')}
          >
            Deep Clinical
          </span>
        </div>

        <div className="smart-bar">
          <button className="file-btn" onClick={() => fileInputRef.current.click()}>
            {file ? '📄' : '➕'}
          </button>
          <input 
            type="text" 
            placeholder={file ? `File: ${file.name}` : "Upload DNA..."} 
            value={patientName}
            onChange={(e) => setPatientName(e.target.value)}
          />
          <input 
            type="file" 
            ref={fileInputRef} 
            hidden 
            onChange={(e) => setFile(e.target.files[0])} 
          />
          <button 
            className="analyze-btn" 
            onClick={onStartAnalysis} 
            disabled={!file}
          >
            Analyze Genome
          </button>
        </div>

        <div className="chip-row">
          <div className="chip-wrapper" style={{position: 'relative'}}>
            <div className={`chip ${showAgeSlider ? 'active' : ''}`} onClick={() => setShowAgeSlider(!showAgeSlider)}>
              🧬 Age: {age}
            </div>
            {showAgeSlider && (
              <div className="chip-overlay">
                <input 
                  type="range" 
                  min="0" 
                  max="120" 
                  value={age} 
                  onChange={(e) => setAge(parseInt(e.target.value))} 
                />
                <span style={{fontWeight: 700, minWidth: '40px'}}>{age}y</span>
              </div>
            )}
          </div>

          <div className="chip" onClick={cycleDiet}>🥗 Diet: {diet}</div>
          
          <div className="chip" onClick={onOpenFocusModal}>
            ✨ {selectedCount > 0 ? `${selectedCount} Areas Selected` : 'Select Focus Areas'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntakePanel;
