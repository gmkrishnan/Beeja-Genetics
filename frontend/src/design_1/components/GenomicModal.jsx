import React, { useState } from 'react';
import '../styles/Modal.css';

const GenomicModal = ({ 
  isOpen, 
  onClose, 
  majors, 
  selectedTraits, 
  setSelectedTraits 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [cartSearchQuery, setCartSearchQuery] = useState('');
  const [expandedNodes, setExpandedNodes] = useState([]);
  const [previewCategory, setPreviewCategory] = useState(null);

  if (!isOpen) return null;

  return (
    <div className="focus-modal-overlay" onClick={onClose}>
      <div className="focus-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-main">
          <div className="modal-header">
            <h2>Categories</h2>
            <div className="search-container">
              <span className="search-icon">🔍</span>
              <input 
                type="text" 
                className="search-input"
                placeholder="Search Major, Master, or Traits..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          <div className="modal-body">
            {majors && majors
              .filter(major => 
                (major.name?.toLowerCase() || "").includes(searchQuery.toLowerCase()) || 
                major.data?.some(m => 
                  (m.name?.toLowerCase() || "").includes(searchQuery.toLowerCase()) || 
                  m.subs?.some(s => 
                    (s.name?.toLowerCase() || "").includes(searchQuery.toLowerCase()) || 
                    s.traits?.some(t => (t?.toLowerCase() || "").includes(searchQuery.toLowerCase()))
                  )
                )
              )
              .map(major => (
              <div key={major.id} className="tree-node">
                <div className="node-header major" onClick={() => {
                  if (expandedNodes.includes(major.id)) setExpandedNodes(expandedNodes.filter(n => n !== major.id))
                  else setExpandedNodes([...expandedNodes, major.id])
                }}>
                  <span>{expandedNodes.includes(major.id) ? '▾' : '▸'}</span> {major.name}
                </div>

                {expandedNodes.includes(major.id) && major.data.map((master, mIdx) => (
                  <div key={master.name || `m-${mIdx}`} className="tree-node" style={{marginLeft: master.name ? '15px' : '0'}}>
                    {master.name && (
                      <div className="node-header master" onClick={() => {
                        if (expandedNodes.includes(master.name)) setExpandedNodes(expandedNodes.filter(n => n !== master.name))
                        else {
                          setExpandedNodes([...expandedNodes, master.name])
                          setPreviewCategory({ name: master.name, traits: master.subs.flatMap(s => s.traits) })
                        }
                      }}>
                        <span>{expandedNodes.includes(master.name) ? '▾' : '▸'}</span> {master.name}
                      </div>
                    )}

                    {(expandedNodes.includes(master.name) || !master.name) && master.subs.map(sub => (
                      <div key={sub.name} className="tree-node" style={{marginLeft: master.name ? '15px' : '0'}}>
                        <div className="node-header sub" onClick={() => setPreviewCategory({ name: sub.name, traits: sub.traits })}>
                          <span>{sub.name}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="modal-cart">
          <div className="cart-header">
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
              <h2 style={{margin:0, fontSize: '1.1rem'}}>
                {previewCategory ? `Browsing: ${previewCategory.name}` : "Genomic Selection"} 
                <span style={{color: 'var(--active-teal)', marginLeft: '10px'}}>({selectedTraits.length})</span>
              </h2>
              {previewCategory && (
                <button 
                  className="add-all-btn"
                  onClick={() => {
                    const newTraits = previewCategory.traits.map(trait => {
                      let path = { major: 'BioGenomics', master: previewCategory.name, sub: previewCategory.name };
                      majors.forEach(m => {
                        m.data.forEach(mast => {
                          if (mast.name === previewCategory.name) {
                            path.major = m.name.replace(/[^a-zA-Z]/g, '').trim();
                            path.master = mast.name;
                          }
                          mast.subs.forEach(s => {
                            if (s.name === previewCategory.name) {
                              path.major = m.name.replace(/[^a-zA-Z]/g, '').trim();
                              path.master = mast.name;
                              path.sub = s.name;
                            }
                          });
                        });
                      });
                      return { name: trait, ...path };
                    });
                    const merged = [...selectedTraits];
                    newTraits.forEach(nt => {
                      if (!merged.some(m => m.name === nt.name)) merged.push(nt);
                    });
                    setSelectedTraits(merged);
                  }}
                >
                  ➕ Add All
                </button>
              )}
            </div>
            <div className="cart-search-container">
              <span className="cart-search-icon">🔍</span>
              <input 
                type="text" 
                className="cart-search-input" 
                placeholder="Filter traits in this category..."
                value={cartSearchQuery}
                onChange={(e) => setCartSearchQuery(e.target.value)}
              />
            </div>
          </div>
          <div className="cart-items">
            {!previewCategory ? (
              <div style={{textAlign: 'center', marginTop: '60px', color: 'var(--text-secondary)'}}>
                Click a category on the left to browse traits.
              </div>
            ) : (
              <div className="preview-group">
                <div className="preview-traits-grid">
                  {previewCategory.traits
                    .filter(t => t.toLowerCase().includes(cartSearchQuery.toLowerCase()))
                    .map(trait => {
                      const isSelected = selectedTraits.some(st => st.name === trait);
                      // Find the hierarchy for this trait
                      let path = { major: 'Genetic Analysis', master: previewCategory.name, sub: previewCategory.name };
                      majors.forEach(m => {
                        m.data.forEach(mast => {
                          if (mast.name === previewCategory.name) {
                            path.major = m.name.replace(/[^a-zA-Z]/g, '').trim();
                            path.master = mast.name;
                          }
                          mast.subs.forEach(s => {
                            if (s.name === previewCategory.name) {
                              path.major = m.name.replace(/[^a-zA-Z]/g, '').trim();
                              path.master = mast.name;
                              path.sub = s.name;
                            }
                          });
                        });
                      });

                      return (
                        <div key={trait} className="cart-item" style={{background: isSelected ? 'var(--active-teal-soft)' : 'white'}}>
                          <span style={{flex: 1, fontWeight: isSelected ? 700 : 400}}>{trait}</span>
                          {isSelected ? (
                            <button 
                              onClick={() => setSelectedTraits(selectedTraits.filter(t => t.name !== trait))}
                              className="trait-remove-btn"
                            >
                              &times;
                            </button>
                          ) : (
                            <button 
                              className="trait-add-btn"
                              onClick={() => setSelectedTraits([...selectedTraits, { 
                                name: trait, 
                                major: path.major, 
                                master: path.master, 
                                sub: path.sub 
                              }])}
                            >
                              +
                            </button>
                          )}
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button className="confirm-btn" onClick={onClose}>
              Confirm {selectedTraits.length} Markers
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GenomicModal;
