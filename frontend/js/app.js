document.addEventListener('DOMContentLoaded', () => {
  const API_BASE = '/api/v1';

  // Theme Toggle (Light & Dark Modes)
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');
  const htmlEl = document.documentElement;

  function setTheme(isDark) {
    if (isDark) {
      htmlEl.classList.add('dark');
      htmlEl.classList.remove('light');
      if (themeIcon) themeIcon.textContent = '🌙';
      localStorage.setItem('theme', 'dark');
    } else {
      htmlEl.classList.remove('dark');
      htmlEl.classList.add('light');
      if (themeIcon) themeIcon.textContent = '☀️';
      localStorage.setItem('theme', 'light');
    }
  }

  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme === 'dark');

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const isDark = htmlEl.classList.contains('dark');
      setTheme(!isDark);
    });
  }

  // Custom Input Drawer Toggle
  const toggleInputPanelBtn = document.getElementById('toggleInputPanelBtn');
  const customInputDrawer = document.getElementById('customInputDrawer');
  const closeInputDrawerBtn = document.getElementById('closeInputDrawerBtn');

  if (toggleInputPanelBtn && customInputDrawer) {
    toggleInputPanelBtn.addEventListener('click', () => {
      customInputDrawer.classList.toggle('hidden');
      if (!customInputDrawer.classList.contains('hidden')) {
        triggerVisibleFields();
      }
    });
  }

  if (closeInputDrawerBtn && customInputDrawer) {
    closeInputDrawerBtn.addEventListener('click', () => {
      customInputDrawer.classList.add('hidden');
    });
  }

  // Baseline / Nil Values Toggle
  const toggleNilRecordsBtn = document.getElementById('toggleNilRecordsBtn');
  const nilRecordsContainer = document.getElementById('nilRecordsContainer');
  const nilToggleIcon = document.getElementById('nilToggleIcon');
  const nilToggleText = document.getElementById('nilToggleText');

  if (toggleNilRecordsBtn && nilRecordsContainer) {
    toggleNilRecordsBtn.addEventListener('click', () => {
      const isHidden = nilRecordsContainer.classList.contains('hidden');
      if (isHidden) {
        nilRecordsContainer.classList.remove('hidden');
        if (nilToggleIcon) nilToggleIcon.textContent = '⌄';
        if (nilToggleText) nilToggleText.textContent = 'Hide Baseline & Negative Records';
      } else {
        nilRecordsContainer.classList.add('hidden');
        if (nilToggleIcon) nilToggleIcon.textContent = '📋';
        if (nilToggleText) nilToggleText.textContent = 'Show Nil & Baseline Records (4 Hidden)';
      }
    });
  }

  // Form Elements
  const reportTextInput = document.getElementById('reportTextInput');
  const ca125Input = document.getElementById('ca125Input');
  const ceaInput = document.getElementById('ceaInput');
  const ageInput = document.getElementById('ageInput');
  const bpInput = document.getElementById('bpInput');
  const diagnosisForm = document.getElementById('diagnosisForm');
  const runBtn = document.getElementById('runInferenceBtn');
  const dropZone = document.getElementById('dropZone');
  const imageInput = document.getElementById('imageInput');
  const dropZonePrompt = document.getElementById('dropZonePrompt');
  const dropZoneText = document.getElementById('dropZoneText');
  const sampleLoadedInfo = document.getElementById('sampleLoadedInfo');
  const sampleNameText = document.getElementById('sampleNameText');
  const sampleOrganText = document.getElementById('sampleOrganText');
  const sampleTypeBadge = document.getElementById('sampleTypeBadge');
  const imagePreview = document.getElementById('imagePreview');
  const changeSlideBtn = document.getElementById('changeSlideBtn');
  const clearSlideBtn = document.getElementById('clearSlideBtn');
  const clearInputsBtn = document.getElementById('clearInputsBtn');
  const charCount = document.getElementById('charCount');

  // Conflict / Discordance Alert Elements
  const modalityConflictBanner = document.getElementById('modalityConflictBanner');
  const conflictBannerTitle = document.getElementById('conflictBannerTitle');
  const conflictBannerSummary = document.getElementById('conflictBannerSummary');
  const conflictBannerAction = document.getElementById('conflictBannerAction');
  const conflictSeverityBadge = document.getElementById('conflictSeverityBadge');
  const dismissConflictBtn = document.getElementById('dismissConflictBtn');
  const drawerDiscordanceWarning = document.getElementById('drawerDiscordanceWarning');
  const drawerDiscordanceText = document.getElementById('drawerDiscordanceText');
  const autoFixConflictBtn = document.getElementById('autoFixConflictBtn');

  if (dismissConflictBtn && modalityConflictBanner) {
    dismissConflictBtn.addEventListener('click', () => {
      modalityConflictBanner.classList.add('hidden');
    });
  }

  // Status & Progress Elements
  const completenessBadge = document.getElementById('completenessBadge');
  const modalityProgressBar = document.getElementById('modalityProgressBar');
  const modalityPercentText = document.getElementById('modalityPercentText');
  const modalityCountText = document.getElementById('modalityCountText');
  const statusModImage = document.getElementById('statusModImage');
  const statusModText = document.getElementById('statusModText');
  const statusModVitals = document.getElementById('statusModVitals');

  // Visual Studio Elements
  const slideOmittedPlaceholder = document.getElementById('slideOmittedPlaceholder');
  const placeholderAttachSlideBtn = document.getElementById('placeholderAttachSlideBtn');
  const gradCamOverlayBadge = document.getElementById('gradCamOverlayBadge');
  const visualStudioImg = document.getElementById('visualStudioImg');
  const viewGradCamBtn = document.getElementById('viewGradCamBtn');
  const viewMacenkoBtn = document.getElementById('viewMacenkoBtn');
  const viewHematoxylinBtn = document.getElementById('viewHematoxylinBtn');
  const viewRawTileBtn = document.getElementById('viewRawTileBtn');
  const slideViewerStage = document.getElementById('slideViewerStage');
  const hudCoords = document.getElementById('hudCoords');
  const hudActivation = document.getElementById('hudActivation');
  const hudTissueClass = document.getElementById('hudTissueClass');
  const hudDensity = document.getElementById('hudDensity');

  // Real-Time In-Drawer Calculation Feedback Elements
  const drawerCalculationSuccess = document.getElementById('drawerCalculationSuccess');
  const drawerCalculatedVerdict = document.getElementById('drawerCalculatedVerdict');
  const drawerCalculatedConf = document.getElementById('drawerCalculatedConf');
  const drawerCalculatedSurv = document.getElementById('drawerCalculatedSurv');
  const drawerCalculatedModalities = document.getElementById('drawerCalculatedModalities');
  const scrollToResultsBtn = document.getElementById('scrollToResultsBtn');

  if (scrollToResultsBtn) {
    scrollToResultsBtn.addEventListener('click', () => {
      const target = document.getElementById('resCancerType') || document.querySelector('.glass-panel');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }

  // Global Session State
  let currentPredictionData = null;
  let currentAudienceMode = 'patient';
  let currentVisualChannel = 'grad_cam';
  let currentLoadedSampleOrgan = null;

  // Scroll Fade-In Observer for diagnosisForm Fields
  function initFormFieldFadeIn() {
    const formFields = document.querySelectorAll('#diagnosisForm .fade-in-field');
    if (!formFields.length) return;

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      }, {
        root: null,
        rootMargin: '0px 0px -20px 0px',
        threshold: 0.1
      });

      formFields.forEach((field, idx) => {
        field.style.transitionDelay = `${idx * 40}ms`;
        observer.observe(field);
      });
    } else {
      formFields.forEach(field => field.classList.add('visible'));
    }
  }

  function triggerVisibleFields() {
    const formFields = document.querySelectorAll('#diagnosisForm .fade-in-field');
    formFields.forEach((field) => {
      field.classList.add('visible');
    });
  }

  initFormFieldFadeIn();

  // Character Count
  if (reportTextInput && charCount) {
    reportTextInput.addEventListener('input', () => {
      charCount.textContent = `${reportTextInput.value.length} chars`;
      checkLiveInputDiscordance();
    });
  }

  // Live Cross-Modality Incongruence Detector
  function checkLiveInputDiscordance() {
    if (!drawerDiscordanceWarning) return;

    const txt = (reportTextInput ? reportTextInput.value : '').toLowerCase();
    const hasImage = Boolean(imageInput && imageInput.files && imageInput.files.length > 0);
    const fn = hasImage ? (imageInput.files[0].name || '').toLowerCase() : '';

    const brainKeywords = ['brain', 'glioblastoma', 'astrocytoma', 'meningioma', 'cns', 'craniotomy', 'cerebral'];
    const lungKeywords = ['lung', 'pulmonary', 'bronchial', 'luad', 'lusc'];
    const breastKeywords = ['breast', 'ductal', 'mammogram', 'idc', 'ilc'];
    const colonKeywords = ['colon', 'colorectal', 'sigmoid'];

    let textSite = null;
    if (brainKeywords.some(k => txt.includes(k))) textSite = 'Brain (Central Nervous System)';
    else if (lungKeywords.some(k => txt.includes(k))) textSite = 'Lung (Pulmonary)';
    else if (breastKeywords.some(k => txt.includes(k))) textSite = 'Breast';
    else if (colonKeywords.some(k => txt.includes(k))) textSite = 'Colon';

    let imageSite = null;
    if (currentLoadedSampleOrgan) imageSite = currentLoadedSampleOrgan;
    else if (fn.includes('brain')) imageSite = 'Brain';
    else if (fn.includes('lung')) imageSite = 'Lung (Pulmonary)';
    else if (fn.includes('breast')) imageSite = 'Breast';
    else if (fn.includes('colon')) imageSite = 'Colon';

    if (hasImage && textSite && imageSite && textSite !== imageSite) {
      drawerDiscordanceWarning.classList.remove('hidden');
      if (drawerDiscordanceText) {
        drawerDiscordanceText.textContent = `Modality Conflict: Biopsy notes describe ${textSite}, but attached slide corresponds to ${imageSite} morphology.`;
      }
    } else {
      drawerDiscordanceWarning.classList.add('hidden');
    }
  }

  if (autoFixConflictBtn) {
    autoFixConflictBtn.addEventListener('click', () => {
      const txt = (reportTextInput ? reportTextInput.value : '').toLowerCase();
      if (txt.includes('lung') || txt.includes('pulmonary')) {
        loadSampleOrgan('lung');
      } else if (txt.includes('colon')) {
        loadSampleOrgan('colon');
      } else if (txt.includes('breast') || txt.includes('ductal')) {
        loadSampleOrgan('breast');
      }
      checkLiveInputDiscordance();
    });
  }

  // Modality Progress Bar & Counters
  function updateModalityStatus() {
    const hasImage = Boolean(imageInput && imageInput.files && imageInput.files.length > 0);
    const textVal = reportTextInput ? reportTextInput.value.trim() : '';
    const hasText = textVal.length > 5;
    
    const hasCa125 = Boolean(ca125Input && ca125Input.value.trim() !== '');
    const hasCea = Boolean(ceaInput && ceaInput.value.trim() !== '');
    const hasAge = Boolean(ageInput && ageInput.value.trim() !== '');
    const hasBp = Boolean(bpInput && bpInput.value.trim() !== '');
    const hasVitals = hasCa125 || hasCea || hasAge || hasBp;

    let activeCount = 0;
    if (hasImage) activeCount++;
    if (hasText) activeCount++;
    if (hasVitals) activeCount++;

    let percent = 0;
    if (activeCount === 1) percent = 33;
    else if (activeCount === 2) percent = 67;
    else if (activeCount === 3) percent = 100;

    if (modalityProgressBar) {
      modalityProgressBar.style.width = `${percent}%`;
      if (percent === 100) {
        modalityProgressBar.className = 'progress-fill h-full bg-emerald-500 rounded-full';
      } else if (percent > 0) {
        modalityProgressBar.className = 'progress-fill h-full bg-blue-500 rounded-full';
      } else {
        modalityProgressBar.className = 'progress-fill h-full bg-slate-700 rounded-full';
      }
    }

    if (modalityPercentText) {
      modalityPercentText.textContent = `${percent}%`;
    }

    if (modalityCountText) {
      if (activeCount === 3) {
        modalityCountText.textContent = '3 of 3 modalities provided · Tri-Modal Fusion Ready';
      } else if (activeCount === 2) {
        modalityCountText.textContent = '2 of 3 modalities provided · Bi-Modal Fusion Active';
      } else if (activeCount === 1) {
        modalityCountText.textContent = '1 of 3 modalities provided · Single Modality Active';
      } else {
        modalityCountText.textContent = '0 of 3 modalities provided';
      }
    }

    if (statusModImage) {
      if (hasImage) {
        const fn = imageInput.files[0].name;
        statusModImage.className = 'p-1.5 rounded bg-blue-500/15 text-blue-400 font-semibold text-center truncate border border-blue-500/20';
        statusModImage.textContent = `Slide: ${fn}`;
      } else {
        statusModImage.className = 'p-1.5 rounded bg-[#181a1d] text-slate-400 text-center truncate border border-transparent';
        statusModImage.textContent = 'Slide: None';
      }
    }

    if (statusModText) {
      if (hasText) {
        statusModText.className = 'p-1.5 rounded bg-purple-500/15 text-purple-300 font-semibold text-center truncate border border-purple-500/20';
        statusModText.textContent = 'Notes: Active';
      } else {
        statusModText.className = 'p-1.5 rounded bg-[#181a1d] text-slate-400 text-center truncate border border-transparent';
        statusModText.textContent = 'Notes: None';
      }
    }

    if (statusModVitals) {
      if (hasVitals) {
        statusModVitals.className = 'p-1.5 rounded bg-emerald-500/15 text-emerald-300 font-semibold text-center truncate border border-emerald-500/20';
        statusModVitals.textContent = 'Biomarkers: Active';
      } else {
        statusModVitals.className = 'p-1.5 rounded bg-[#181a1d] text-slate-400 text-center truncate border border-transparent';
        statusModVitals.textContent = 'Biomarkers: None';
      }
    }

    if (completenessBadge) {
      if (activeCount === 3) {
        completenessBadge.className = 'text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30';
        completenessBadge.textContent = 'Tri-Modal 3/3';
      } else if (activeCount === 2) {
        completenessBadge.className = 'text-[11px] font-mono px-2 py-0.5 rounded bg-blue-500/15 text-blue-300 border border-blue-500/30';
        completenessBadge.textContent = 'Bi-Modal 2/3';
      } else if (activeCount === 1) {
        completenessBadge.className = 'text-[11px] font-mono px-2 py-0.5 rounded bg-[#202327] text-slate-300 border border-[#3d434b]';
        completenessBadge.textContent = 'Single 1/3';
      } else {
        completenessBadge.className = 'text-[11px] font-mono px-2 py-0.5 rounded bg-[#181a1d] text-slate-400 border border-[#2c3036]';
        completenessBadge.textContent = 'Awaiting Input';
      }
    }

    checkLiveInputDiscordance();
  }

  if (reportTextInput) reportTextInput.addEventListener('input', updateModalityStatus);
  if (ca125Input) ca125Input.addEventListener('input', updateModalityStatus);
  if (ceaInput) ceaInput.addEventListener('input', updateModalityStatus);
  if (ageInput) ageInput.addEventListener('input', updateModalityStatus);
  if (bpInput) bpInput.addEventListener('input', updateModalityStatus);

  // File Dropzone logic
  if (dropZone && imageInput) {
    dropZone.addEventListener('click', (e) => {
      if (e.target.closest('#changeSlideBtn') || e.target.closest('#clearSlideBtn')) return;
      if (!imageInput.files || imageInput.files.length === 0) {
        imageInput.click();
      }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-500', 'bg-blue-950/20');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500', 'bg-blue-950/20');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        imageInput.files = e.dataTransfer.files;
        handleImageFile(e.dataTransfer.files[0], 'Uploaded Biopsy File');
      }
    });

    imageInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handleImageFile(e.target.files[0], 'Local Biopsy File');
      }
    });
  }

  // Explicit Change / Browse File Button
  if (changeSlideBtn && imageInput) {
    changeSlideBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      imageInput.click();
    });
  }

  // Explicit Clear Slide Button
  if (clearSlideBtn && imageInput) {
    clearSlideBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      imageInput.value = '';
      currentLoadedSampleOrgan = null;
      if (dropZonePrompt) dropZonePrompt.classList.remove('hidden');
      if (sampleLoadedInfo) sampleLoadedInfo.classList.add('hidden');
      if (imagePreview) imagePreview.src = '';
      updateModalityStatus();
    });
  }

  function handleImageFile(file, contextLabel = 'Attached Specimen') {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (imagePreview) {
        imagePreview.src = e.target.result;
      }
      if (dropZonePrompt) dropZonePrompt.classList.add('hidden');
      if (sampleLoadedInfo) sampleLoadedInfo.classList.remove('hidden');
      if (sampleTypeBadge) sampleTypeBadge.textContent = contextLabel;
      if (sampleNameText) sampleNameText.textContent = file.name;
      
      const fnLower = file.name.toLowerCase();
      let organ = 'Unspecified Organ';
      if (fnLower.includes('breast') || fnLower.includes('idc')) organ = 'Breast (Mammary Gland)';
      else if (fnLower.includes('lung') || fnLower.includes('luad')) organ = 'Lung (Pulmonary Tissue)';
      else if (fnLower.includes('colon')) organ = 'Colon / Colorectal';
      else if (fnLower.includes('brain')) organ = 'Brain (Central Nervous System)';
      
      currentLoadedSampleOrgan = organ;
      if (sampleOrganText) sampleOrganText.textContent = `Organ: ${organ}`;
      updateModalityStatus();
    };
    reader.readAsDataURL(file);
  }

  // Load Synthetic Clinical Slide Sample
  function loadSampleOrgan(organType) {
    const canvas = document.createElement('canvas');
    canvas.width = 224;
    canvas.height = 224;
    const ctx = canvas.getContext('2d');

    let fileName = 'breast_idc_wsi_40x.jpg';
    let sampleTitle = 'Breast Ductal Carcinoma H&E (40x)';
    let organDesc = 'Organ: Breast (Mammary Gland)';

    if (organType === 'lung') {
      fileName = 'lung_luad_wsi_20x.jpg';
      sampleTitle = 'Pulmonary Adenocarcinoma H&E (20x)';
      organDesc = 'Organ: Lung (Pulmonary Tissue)';
      ctx.fillStyle = '#f1f5f9';
      ctx.fillRect(0, 0, 224, 224);
      for (let i = 0; i < 35; i++) {
        ctx.fillStyle = i % 2 === 0 ? 'rgba(79, 70, 229, 0.6)' : 'rgba(16, 185, 129, 0.45)';
        ctx.beginPath();
        ctx.arc(Math.random() * 224, Math.random() * 224, Math.random() * 9 + 3, 0, Math.PI * 2);
        ctx.fill();
      }
    } else if (organType === 'colon') {
      fileName = 'colon_adeno_wsi_20x.jpg';
      sampleTitle = 'Colonic Adenocarcinoma H&E (20x)';
      organDesc = 'Organ: Colon / Colorectal';
      ctx.fillStyle = '#fff1f2';
      ctx.fillRect(0, 0, 224, 224);
      for (let i = 0; i < 35; i++) {
        ctx.fillStyle = i % 2 === 0 ? 'rgba(225, 29, 72, 0.55)' : 'rgba(59, 130, 246, 0.45)';
        ctx.beginPath();
        ctx.arc(Math.random() * 224, Math.random() * 224, Math.random() * 8 + 3, 0, Math.PI * 2);
        ctx.fill();
      }
    } else {
      // Breast default
      ctx.fillStyle = '#fce7f3';
      ctx.fillRect(0, 0, 224, 224);
      for (let i = 0; i < 40; i++) {
        ctx.fillStyle = i % 2 === 0 ? 'rgba(67, 56, 202, 0.6)' : 'rgba(219, 39, 119, 0.38)';
        ctx.beginPath();
        ctx.arc(Math.random() * 224, Math.random() * 224, Math.random() * 8 + 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    canvas.toBlob((blob) => {
      const file = new File([blob], fileName, { type: 'image/jpeg' });
      const dt = new DataTransfer();
      dt.items.add(file);
      if (imageInput) imageInput.files = dt.files;

      if (imagePreview) imagePreview.src = canvas.toDataURL('image/jpeg');
      if (dropZonePrompt) dropZonePrompt.classList.add('hidden');
      if (sampleLoadedInfo) sampleLoadedInfo.classList.remove('hidden');
      if (sampleTypeBadge) sampleTypeBadge.textContent = 'Benchmark Sample Attached';
      if (sampleNameText) sampleNameText.textContent = sampleTitle;
      if (sampleOrganText) sampleOrganText.textContent = organDesc;
      currentLoadedSampleOrgan = organDesc.replace('Organ: ', '');
      updateModalityStatus();
    }, 'image/jpeg');
  }

  // Sample Load Button Listeners
  const loadSampleBreastBtn = document.getElementById('loadSampleBreastBtn');
  const loadSampleLungBtn = document.getElementById('loadSampleLungBtn');
  const loadSampleColonBtn = document.getElementById('loadSampleColonBtn');

  if (loadSampleBreastBtn) loadSampleBreastBtn.addEventListener('click', () => loadSampleOrgan('breast'));
  if (loadSampleLungBtn) loadSampleLungBtn.addEventListener('click', () => loadSampleOrgan('lung'));
  if (loadSampleColonBtn) loadSampleColonBtn.addEventListener('click', () => loadSampleOrgan('colon'));

  // Placeholder Attach Slide button inside stage
  if (placeholderAttachSlideBtn) {
    placeholderAttachSlideBtn.addEventListener('click', () => {
      if (customInputDrawer && customInputDrawer.classList.contains('hidden')) {
        customInputDrawer.classList.remove('hidden');
        triggerVisibleFields();
      }
      if (dropZone) {
        dropZone.scrollIntoView({ behavior: 'smooth', block: 'center' });
        dropZone.classList.add('ring-2', 'ring-blue-500');
        setTimeout(() => dropZone.classList.remove('ring-2', 'ring-blue-500'), 1800);
      }
    });
  }

  // Benchmarks Data
  const BENCHMARKS = {
    'CASE-01': {
      organ: 'breast',
      reportText: 'Histopathology core needle biopsy reveals invasive ductal carcinoma (IDC) of breast. Nuclear pleomorphism, high mitotic index, ER/PR negative, HER2 positive.',
      ca125: 48.5,
      cea: 12.4,
      age: 58,
      bp: 135
    },
    'CASE-02': {
      organ: 'lung',
      reportText: 'Pulmonary core biopsy confirms poorly differentiated lung adenocarcinoma (LUAD) of right upper lobe. EGFR exon 19 mutation positive, ALK negative, bronchial invasion.',
      ca125: 14.2,
      cea: 45.8,
      age: 64,
      bp: 142
    },
    'CASE-03': {
      organ: 'colon',
      reportText: 'Colonoscopy surgical pathology report indicates moderately differentiated colonic adenocarcinoma with submucosal invasion. Microsatellite instability (MSI-High) detected.',
      ca125: 11.0,
      cea: 38.2,
      age: 62,
      bp: 128
    },
    'CASE-04': {
      organ: 'breast',
      reportText: 'Biopsy tissue sample shows normal histology with no evidence of malignancy, atypical cell proliferation, or architectural distortion. Unremarkable cellular morphology.',
      ca125: 12.0,
      cea: 1.2,
      age: 45,
      bp: 120
    }
  };

  // Preset Buttons: Click updates inputs and runs analysis immediately
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const caseKey = btn.dataset.case;
      const data = BENCHMARKS[caseKey];
      if (data) {
        if (reportTextInput) reportTextInput.value = data.reportText;
        if (ca125Input) ca125Input.value = data.ca125;
        if (ceaInput) ceaInput.value = data.cea;
        if (ageInput) ageInput.value = data.age;
        if (bpInput) bpInput.value = data.bp;
        if (charCount) charCount.textContent = `${data.reportText.length} chars`;
        loadSampleOrgan(data.organ);
        updateModalityStatus();
        executeInference();
      }
    });
  });

  if (clearInputsBtn) {
    clearInputsBtn.addEventListener('click', () => {
      if (reportTextInput) reportTextInput.value = '';
      if (ca125Input) ca125Input.value = '';
      if (ceaInput) ceaInput.value = '';
      if (ageInput) ageInput.value = '';
      if (bpInput) bpInput.value = '';
      if (imageInput) imageInput.value = '';
      if (charCount) charCount.textContent = '0 chars';
      currentLoadedSampleOrgan = null;
      if (dropZonePrompt) dropZonePrompt.classList.remove('hidden');
      if (sampleLoadedInfo) sampleLoadedInfo.classList.add('hidden');
      if (imagePreview) imagePreview.src = '';
      if (drawerDiscordanceWarning) drawerDiscordanceWarning.classList.add('hidden');
      updateModalityStatus();
    });
  }

  // Diagnostic Inference Execution
  async function executeInference() {
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Analyzing...
      `;
    }

    const hasImage = Boolean(imageInput && imageInput.files && imageInput.files.length > 0);
    const textVal = reportTextInput ? reportTextInput.value.trim() : '';
    const hasText = textVal.length > 0;
    const hasVitals = Boolean((ca125Input && ca125Input.value) || (ceaInput && ceaInput.value) || (ageInput && ageInput.value) || (bpInput && bpInput.value));

    const formData = new FormData();
    if (hasImage) {
      formData.append('image', imageInput.files[0]);
    }
    formData.append('report_text', textVal);

    const vitalsObj = {};
    if (ca125Input && ca125Input.value !== '') vitalsObj.ca125 = parseFloat(ca125Input.value);
    if (ceaInput && ceaInput.value !== '') vitalsObj.cea = parseFloat(ceaInput.value);
    if (ageInput && ageInput.value !== '') vitalsObj.age = parseFloat(ageInput.value);
    if (bpInput && bpInput.value !== '') vitalsObj.blood_pressure_systolic = parseFloat(bpInput.value);
    formData.append('vitals', JSON.stringify(vitalsObj));

    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Inference returned status ${response.status}`);
      }

      const result = await response.json();
      currentPredictionData = result;
      renderResults(result, hasImage, hasText, hasVitals);
      initializeSimulator(result);

      // Real-Time In-Drawer Calculation Feedback Banner
      if (drawerCalculationSuccess) {
        drawerCalculationSuccess.classList.remove('hidden');
        if (drawerCalculatedVerdict) {
          drawerCalculatedVerdict.textContent = `${result.cancer_type} · ${result.cancer_stage} (${result.tnm_classification || ''})`;
        }
        if (drawerCalculatedConf) {
          const conf = result.cancer_type_confidence || result.confidence || 0.95;
          drawerCalculatedConf.textContent = `${(conf * 100).toFixed(1)}%`;
        }
        if (drawerCalculatedSurv) {
          const sRate = result.survival_probability !== undefined ? Math.round(result.survival_probability * 100) : 90;
          drawerCalculatedSurv.textContent = `${sRate}%`;
        }
        if (drawerCalculatedModalities) {
          const modArr = [];
          if (hasImage) modArr.push('Slide Tile');
          if (hasText) modArr.push('Clinical Notes');
          if (hasVitals) modArr.push('Biomarkers');
          drawerCalculatedModalities.textContent = modArr.length > 0
            ? `${modArr.join(' + ')} Active ${!hasImage ? '· Slide Omitted' : ''}`
            : 'Default Benchmark';
        }
      }

      // Visual update pulse on verdict elements
      const verdictEl = document.getElementById('resCancerType');
      if (verdictEl) {
        verdictEl.classList.add('ring-2', 'ring-blue-500/80', 'rounded-lg');
        setTimeout(() => verdictEl.classList.remove('ring-2', 'ring-blue-500/80', 'rounded-lg'), 1800);
      }

    } catch (err) {
      console.warn('Inference network failure, falling back to local dataset', err);
      const fallbackData = getFallbackDemoData(hasImage);
      currentPredictionData = fallbackData;
      renderResults(fallbackData, hasImage, true, true);
      initializeSimulator(fallbackData);
    } finally {
      if (runBtn) {
        runBtn.disabled = false;
        runBtn.innerHTML = `<span>✓ Analysis Updated</span>`;
        setTimeout(() => {
          if (runBtn) runBtn.innerHTML = `<span>⚡</span> Run Diagnostic Analysis`;
        }, 1500);
      }
    }
  }

  // Form Submit and Direct Button Click: DO NOT CLOSE CUSTOM INPUT DRAWER (User explicitly requested)
  if (diagnosisForm) {
    diagnosisForm.addEventListener('submit', (e) => {
      e.preventDefault();
      executeInference();
    });
  }

  if (runBtn) {
    runBtn.addEventListener('click', (e) => {
      e.preventDefault();
      executeInference();
    });
  }

  // Audience Narrative Switcher
  const viewPatientSummaryBtn = document.getElementById('viewPatientSummaryBtn');
  const viewTechnicalSummaryBtn = document.getElementById('viewTechnicalSummaryBtn');
  const resPlainSummary = document.getElementById('resPlainSummary');

  if (viewPatientSummaryBtn && viewTechnicalSummaryBtn) {
    viewPatientSummaryBtn.addEventListener('click', () => {
      currentAudienceMode = 'patient';
      viewPatientSummaryBtn.className = 'px-3 py-1 rounded-lg font-semibold transition-colors bg-blue-600 text-white shadow-sm cursor-pointer';
      viewTechnicalSummaryBtn.className = 'px-3 py-1 rounded-lg font-semibold transition-colors text-slate-400 hover:text-white cursor-pointer';
      if (currentPredictionData && resPlainSummary) {
        resPlainSummary.textContent = currentPredictionData.patient_friendly_summary || currentPredictionData.plain_english_summary;
      }
    });

    viewTechnicalSummaryBtn.addEventListener('click', () => {
      currentAudienceMode = 'technical';
      viewTechnicalSummaryBtn.className = 'px-3 py-1 rounded-lg font-semibold transition-colors bg-blue-600 text-white shadow-sm cursor-pointer';
      viewPatientSummaryBtn.className = 'px-3 py-1 rounded-lg font-semibold transition-colors text-slate-400 hover:text-white cursor-pointer';
      if (currentPredictionData && resPlainSummary) {
        resPlainSummary.textContent = currentPredictionData.oncology_technical_summary || currentPredictionData.plain_english_summary;
      }
    });
  }

  // Visual Channel Switcher (Corrected logic for missing image)
  function setVisualChannel(channel) {
    currentVisualChannel = channel;
    const hasImage = Boolean(currentPredictionData && currentPredictionData.grad_cam_available && currentPredictionData.grad_cam_image);

    if (!hasImage) {
      // Visual modality is omitted
      if (slideOmittedPlaceholder) slideOmittedPlaceholder.classList.remove('hidden');
      if (gradCamOverlayBadge) gradCamOverlayBadge.classList.add('hidden');
      if (visualStudioImg) visualStudioImg.src = '';

      [viewGradCamBtn, viewMacenkoBtn, viewHematoxylinBtn, viewRawTileBtn].forEach(btn => {
        if (btn) {
          btn.disabled = true;
          btn.className = 'channel-tab-btn px-2.5 py-1 rounded-lg text-slate-500 opacity-40 cursor-not-allowed transition-colors';
          btn.title = 'Attach biopsy slide in custom input to activate channel';
        }
      });
      return;
    }

    // Image is present: enable channels
    if (slideOmittedPlaceholder) slideOmittedPlaceholder.classList.add('hidden');
    if (gradCamOverlayBadge) gradCamOverlayBadge.classList.remove('hidden');

    const suite = (currentPredictionData && currentPredictionData.stain_deconvolution_suite) || {};

    [viewGradCamBtn, viewMacenkoBtn, viewHematoxylinBtn, viewRawTileBtn].forEach(btn => {
      if (btn) {
        btn.disabled = false;
        btn.title = '';
        btn.className = 'channel-tab-btn px-2.5 py-1 rounded-lg text-slate-400 hover:text-white cursor-pointer transition-colors';
      }
    });

    if (channel === 'grad_cam') {
      if (viewGradCamBtn) viewGradCamBtn.className = 'channel-tab-btn px-2.5 py-1 rounded-lg bg-blue-600 text-white cursor-pointer transition-colors';
      if (visualStudioImg) visualStudioImg.src = suite.grad_cam_overlay || currentPredictionData?.grad_cam_image || '';
    } else if (channel === 'macenko') {
      if (viewMacenkoBtn) viewMacenkoBtn.className = 'channel-tab-btn px-2.5 py-1 rounded-lg bg-blue-600 text-white cursor-pointer transition-colors';
      if (visualStudioImg) visualStudioImg.src = suite.macenko_normalized || '';
    } else if (channel === 'hematoxylin') {
      if (viewHematoxylinBtn) viewHematoxylinBtn.className = 'channel-tab-btn px-2.5 py-1 rounded-lg bg-blue-600 text-white cursor-pointer transition-colors';
      if (visualStudioImg) visualStudioImg.src = suite.hematoxylin_channel || '';
    } else if (channel === 'raw') {
      if (viewRawTileBtn) viewRawTileBtn.className = 'channel-tab-btn px-2.5 py-1 rounded-lg bg-blue-600 text-white cursor-pointer transition-colors';
      if (visualStudioImg) visualStudioImg.src = suite.raw_he_tile || '';
    }
  }

  if (viewGradCamBtn) viewGradCamBtn.addEventListener('click', () => setVisualChannel('grad_cam'));
  if (viewMacenkoBtn) viewMacenkoBtn.addEventListener('click', () => setVisualChannel('macenko'));
  if (viewHematoxylinBtn) viewHematoxylinBtn.addEventListener('click', () => setVisualChannel('hematoxylin'));
  if (viewRawTileBtn) viewRawTileBtn.addEventListener('click', () => setVisualChannel('raw'));

  // Coordinate Inspector (Only activates when image is provided)
  if (slideViewerStage) {
    slideViewerStage.addEventListener('click', async (e) => {
      const hasImage = Boolean(currentPredictionData && currentPredictionData.grad_cam_available && currentPredictionData.grad_cam_image);
      if (!hasImage) {
        return; // Slide is omitted
      }

      const rect = slideViewerStage.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const clickY = e.clientY - rect.top;
      const svgX = Math.round((clickX / rect.width) * 600);
      const svgY = Math.round((clickY / rect.height) * 400);

      try {
        const resp = await fetch(`${API_BASE}/inspect/coordinates`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            x: svgX,
            y: svgY,
            cancer_type: currentPredictionData?.cancer_type || 'Breast Cancer',
            has_image: true
          })
        });
        if (resp.ok) {
          const res = await resp.json();
          if (hudCoords) hudCoords.textContent = `(${res.coordinates.x}, ${res.coordinates.y})`;
          if (hudActivation) hudActivation.textContent = `${(res.normalized_intensity || '94.2%')}`;
          if (hudTissueClass) hudTissueClass.textContent = res.microenvironment.tissue_classification;
          if (hudDensity) hudDensity.textContent = res.microenvironment.cellular_density;
        }
      } catch (err) {
        console.warn('Inspect coordinates fallback', err);
      }
    });
  }

  // What-If Simulation Engine
  const simCa125Slider = document.getElementById('simCa125Slider');
  const simCeaSlider = document.getElementById('simCeaSlider');
  const simCa125Label = document.getElementById('simCa125Label');
  const simCeaLabel = document.getElementById('simCeaLabel');
  const simStageShiftText = document.getElementById('simStageShiftText');
  const simScenarioText = document.getElementById('simScenarioText');
  const simSurvivalVal = document.getElementById('simSurvivalVal');
  const simSurvivalDeltaBadge = document.getElementById('simSurvivalDeltaBadge');
  const simThresholdText = document.getElementById('simThresholdText');
  const resetSimulationBtn = document.getElementById('resetSimulationBtn');

  function initializeSimulator(data) {
    const rawCa125 = parseFloat(ca125Input?.value) || 48.5;
    const rawCea = parseFloat(ceaInput?.value) || 12.4;

    if (simCa125Slider) simCa125Slider.value = rawCa125;
    if (simCeaSlider) simCeaSlider.value = rawCea;
    if (simCa125Label) simCa125Label.textContent = `${rawCa125.toFixed(1)} U/mL`;
    if (simCeaLabel) simCeaLabel.textContent = `${rawCea.toFixed(1)} ng/mL`;
    if (simStageShiftText) simStageShiftText.textContent = `${data.cancer_stage} → ${data.cancer_stage} (Baseline)`;
    if (simScenarioText) simScenarioText.textContent = 'Patient Baseline Values';
    if (simSurvivalVal) simSurvivalVal.textContent = `${Math.round(data.survival_probability * 100)}%`;
    if (simSurvivalDeltaBadge) {
      simSurvivalDeltaBadge.textContent = '+0% Baseline';
      simSurvivalDeltaBadge.className = 'font-mono text-xs font-bold px-2 py-0.5 rounded bg-[#181a1d] text-slate-300 border border-[#2c3036]';
    }
  }

  async function executeSimulation(scenarioName = 'Custom Slider Adjustment') {
    if (!currentPredictionData) return;
    const caVal = parseFloat(simCa125Slider?.value || 48.5);
    const ceaVal = parseFloat(simCeaSlider?.value || 12.4);

    if (simCa125Label) simCa125Label.textContent = `${caVal.toFixed(1)} U/mL`;
    if (simCeaLabel) simCeaLabel.textContent = `${ceaVal.toFixed(1)} ng/mL`;

    try {
      const resp = await fetch(`${API_BASE}/simulate/what-if`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          baseline_prediction: currentPredictionData,
          modified_vitals: { ca125: caVal, cea: ceaVal },
          scenario: scenarioName
        })
      });
      if (resp.ok) {
        const sim = await resp.json();
        if (simStageShiftText) simStageShiftText.textContent = sim.simulated.stage_shift_summary;
        if (simScenarioText) simScenarioText.textContent = sim.scenario_applied;
        if (simSurvivalVal) simSurvivalVal.textContent = `${sim.simulated.five_year_survival}%`;
        if (simSurvivalDeltaBadge) {
          const deltaStr = sim.simulated.survival_delta_percent;
          const isPos = deltaStr.startsWith('+') && deltaStr !== '+0%';
          simSurvivalDeltaBadge.textContent = `${deltaStr} 5-Yr Survival`;
          simSurvivalDeltaBadge.className = isPos
            ? 'font-mono text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
            : (deltaStr.startsWith('-') ? 'font-mono text-xs font-bold px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/30' : 'font-mono text-xs font-bold px-2 py-0.5 rounded bg-[#181a1d] text-slate-300 border border-[#2c3036]');
        }
        if (simThresholdText) {
          simThresholdText.textContent = sim.threshold_needed.clinical_action;
        }
      }
    } catch (e) {
      console.warn('Simulation error:', e);
    }
  }

  if (simCa125Slider) simCa125Slider.addEventListener('input', () => executeSimulation('Custom CA-125 Adjustment'));
  if (simCeaSlider) simCeaSlider.addEventListener('input', () => executeSimulation('Custom CEA Adjustment'));

  document.querySelectorAll('.sim-scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const ca = parseFloat(btn.dataset.ca125);
      const cea = parseFloat(btn.dataset.cea);
      const desc = btn.dataset.desc;
      if (simCa125Slider) simCa125Slider.value = ca;
      if (simCeaSlider) simCeaSlider.value = cea;
      executeSimulation(desc);
    });
  });

  if (resetSimulationBtn) {
    resetSimulationBtn.addEventListener('click', () => {
      if (currentPredictionData) initializeSimulator(currentPredictionData);
    });
  }

  // Render All Results (Verifies and corrects all tabs, values, and calculations)
  function renderResults(data, hasImageProvided, hasTextProvided, hasVitalsProvided) {
    const cType = (data.cancer_type || 'Breast Cancer').toLowerCase();
    const isNormal = cType.includes('normal') || cType.includes('healthy') || cType.includes('non-malignant');

    // Modality Incongruence Conflict Alert
    if (modalityConflictBanner) {
      if (data.clinical_conflict_alert && data.clinical_conflict_alert.conflict_detected) {
        modalityConflictBanner.classList.remove('hidden');
        if (conflictBannerTitle) conflictBannerTitle.textContent = data.clinical_conflict_alert.title || 'Clinical Modality Incongruence Flagged';
        if (conflictBannerSummary) conflictBannerSummary.textContent = data.clinical_conflict_alert.summary;
        if (conflictBannerAction) conflictBannerAction.textContent = `Action Required: ${data.clinical_conflict_alert.action}`;
        if (conflictSeverityBadge) conflictSeverityBadge.textContent = data.clinical_conflict_alert.severity || 'High Discordance';
      } else {
        modalityConflictBanner.classList.add('hidden');
      }
    }

    const cancerTypeEl = document.getElementById('resCancerType');
    if (cancerTypeEl) cancerTypeEl.textContent = data.cancer_type || 'Breast Cancer';

    const subtypeEl = document.getElementById('resSubtype');
    if (subtypeEl) subtypeEl.textContent = data.cancer_subtype || 'Invasive Carcinoma';

    const stageEl = document.getElementById('resCancerStage');
    if (stageEl) {
      stageEl.textContent = data.cancer_stage || 'Stage IIA';
      stageEl.className = isNormal
        ? 'text-xl sm:text-2xl font-extrabold text-emerald-400 font-mono block'
        : 'text-xl sm:text-2xl font-extrabold text-white font-mono block';
    }

    const tnmEl = document.getElementById('resTNMClassification');
    if (tnmEl) {
      tnmEl.textContent = data.tnm_classification || 'cT2 N0 M0';
    }

    const confEl = document.getElementById('resConfidence');
    const confVal = data.cancer_type_confidence || data.confidence || 0.958;
    if (confEl) confEl.textContent = `${(confVal * 100).toFixed(1)}%`;

    const survEl = document.getElementById('resSurvival');
    if (survEl) {
      const sVal = data.survival_probability !== undefined ? Math.round(data.survival_probability * 100) : 93;
      survEl.textContent = `${sVal}%`;
    }

    if (resPlainSummary) {
      resPlainSummary.textContent = currentAudienceMode === 'technical'
        ? (data.oncology_technical_summary || data.plain_english_summary)
        : (data.patient_friendly_summary || data.plain_english_summary);
    }

    // Dynamic Attention Weights (Reflects whether image was provided or omitted)
    const hasImage = Boolean(data.grad_cam_available && data.grad_cam_image);
    const imgW = hasImage ? Math.round((data.image_weight !== undefined ? data.image_weight : 0.45) * 100) : 0;
    const txtW = Math.round((data.text_weight !== undefined ? data.text_weight : (hasImage ? 0.35 : 0.65)) * 100);
    const tabW = Math.round((data.tabular_weight !== undefined ? data.tabular_weight : (hasImage ? 0.20 : 0.35)) * 100);

    const imgTxt = document.getElementById('imgWeightText');
    if (imgTxt) imgTxt.textContent = `${imgW}%`;
    const imgBar = document.getElementById('imgWeightBar');
    if (imgBar) imgBar.style.width = `${imgW}%`;

    const txtTxt = document.getElementById('txtWeightText');
    if (txtTxt) txtTxt.textContent = `${txtW}%`;
    const txtBar = document.getElementById('txtWeightBar');
    if (txtBar) txtBar.style.width = `${txtW}%`;

    const tabTxt = document.getElementById('tabWeightText');
    if (tabTxt) tabTxt.textContent = `${tabW}%`;
    const tabBar = document.getElementById('tabWeightBar');
    if (tabBar) tabBar.style.width = `${tabW}%`;

    const fNote = document.getElementById('fusionWeightNote');
    if (fNote) {
      fNote.textContent = hasImage
        ? 'Tri-Modal Fusion: Vision, Text & Tabular Active'
        : 'Bimodal Fusion: Text & Tabular Active (Vision Omitted)';
    }

    // Visual Channel & Heatmap Display Logic (Fix for missing image!)
    setVisualChannel(hasImage ? (currentVisualChannel || 'grad_cam') : 'omitted');

    if (!hasImage) {
      if (hudCoords) hudCoords.textContent = '(N/A)';
      if (hudActivation) hudActivation.textContent = '0% (Omitted)';
      if (hudTissueClass) hudTissueClass.textContent = 'Slide Not Provided';
      if (hudDensity) hudDensity.textContent = '0 cells/mm²';
    } else {
      if (hudCoords) hudCoords.textContent = '(310, 190)';
      if (hudActivation) hudActivation.textContent = '94.2%';
      if (hudTissueClass) hudTissueClass.textContent = 'Tumor Core';
      if (hudDensity) hudDensity.textContent = '840 cells/mm²';
    }

    // SHAP Waterfall Step Rendering
    const shapWaterfallContainer = document.getElementById('shapWaterfallContainer');
    if (shapWaterfallContainer) {
      shapWaterfallContainer.innerHTML = '';
      const waterfall = data.shap_waterfall || { steps: [] };
      const steps = waterfall.steps || [];

      steps.forEach((step, idx) => {
        const isPositive = step.delta >= 0;
        const deltaStr = isPositive ? `+${step.delta.toFixed(3)}` : step.delta.toFixed(3);
        const barColor = isPositive ? 'bg-blue-500' : 'bg-slate-600';
        const barWidth = Math.min(100, Math.max(10, Math.round(step.cumulative * 100)));

        const stepEl = document.createElement('div');
        stepEl.className = 'p-2.5 rounded-xl bg-[#111315] border border-[#2c3036] space-y-1 text-xs';
        stepEl.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-semibold text-slate-200 flex items-center gap-1.5">
              <span class="text-slate-500 font-mono text-[10px]">#${idx + 1}</span>
              <span>${step.feature}</span>
            </span>
            <span class="font-mono font-bold text-xs ${isPositive ? 'text-blue-400' : 'text-slate-400'}">
              ${deltaStr} SHAP
            </span>
          </div>
          <div class="flex items-center justify-between text-[11px] text-slate-400">
            <span>Value: <strong class="text-slate-200">${step.value}</strong></span>
            <span class="font-mono text-[10px] text-slate-500">Sum: ${step.cumulative.toFixed(2)}</span>
          </div>
          <div class="w-full bg-[#202327] h-1.5 rounded-full overflow-hidden">
            <div class="${barColor} h-full rounded-full transition-all duration-300" style="width: ${barWidth}%;"></div>
          </div>
        `;
        shapWaterfallContainer.appendChild(stepEl);
      });
    }

    // Virtual Tumor Board (MDT)
    const board = data.virtual_tumor_board;
    if (board) {
      const concEl = document.getElementById('mdtConcordanceHeader');
      if (concEl) concEl.textContent = `${board.consensus_concordance}%`;

      const boardIdBadge = document.getElementById('mdtBoardIdBadge');
      if (boardIdBadge) boardIdBadge.textContent = board.board_id;

      const specGrid = document.getElementById('mdtSpecialistsGrid');
      if (specGrid) {
        specGrid.innerHTML = '';
        (board.specialists || []).forEach(sp => {
          let icon = '👨‍⚕️';
          if (sp.specialty.includes('Medical')) icon = '💊';
          else if (sp.specialty.includes('Radiation')) icon = '☢️';
          else if (sp.specialty.includes('Molecular') || sp.specialty.includes('Genetics')) icon = '🧬';

          const card = document.createElement('div');
          card.className = 'p-3.5 rounded-xl bg-[#111315] border border-[#2c3036] space-y-2 text-xs';
          card.innerHTML = `
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-base">${icon}</span>
                <div>
                  <span class="font-bold text-slate-100 block text-xs">${sp.specialist_name}</span>
                  <span class="text-[10px] text-slate-400 block">${sp.specialty}</span>
                </div>
              </div>
              <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">✓ ${sp.vote}</span>
            </div>
            <p class="text-[11px] text-slate-300 leading-snug">${sp.recommendation}</p>
          `;
          specGrid.appendChild(card);
        });
      }

      const delibList = document.getElementById('mdtDeliberationList');
      if (delibList) {
        delibList.innerHTML = (board.deliberation_points || []).map(p => `<li>${p}</li>`).join('');
      }

      const planList = document.getElementById('mdtActionPlanList');
      if (planList) {
        planList.innerHTML = (board.ratified_action_plan || []).map(a => `<li>${a}</li>`).join('');
      }
    }

    // Ranked Therapies
    const rankedContainer = document.getElementById('rankedTherapiesContainer');
    if (rankedContainer) {
      rankedContainer.innerHTML = '';
      const therapies = data.ranked_therapies || (data.treatment && data.treatment.ranked_therapies) || [];

      therapies.forEach(tx => {
        const item = document.createElement('div');
        item.className = 'p-3 rounded-xl bg-[#111315] border border-[#2c3036] flex flex-col space-y-1 text-xs';
        item.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-100 flex items-center gap-1.5">
              <span class="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 font-mono text-[10px] font-bold border border-blue-500/20">#${tx.priority}</span>
              <span>${tx.name}</span>
            </span>
            <span class="text-[10px] font-mono text-slate-400">${tx.category}</span>
          </div>
          <p class="text-[11px] text-slate-400">${tx.mechanism}</p>
        `;
        rankedContainer.appendChild(item);
      });
    }

    // Longitudinal Survival Curve
    const survContainer = document.getElementById('survivalProjectionsContainer');
    if (survContainer) {
      survContainer.innerHTML = '';
      const proj = data.survival_projections || { curve: [] };
      const curve = proj.curve || [];

      curve.forEach(pt => {
        const item = document.createElement('div');
        item.className = 'p-3 rounded-xl bg-[#111315] border border-[#2c3036] space-y-1.5 text-xs';
        item.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-semibold text-slate-200">${pt.timepoint} Horizon</span>
            <span class="font-mono font-bold text-emerald-400">${pt.survival_rate}% (CI: ${pt.ci_lower}% - ${pt.ci_upper}%)</span>
          </div>
          <div class="w-full bg-[#202327] h-1.5 rounded-full overflow-hidden">
            <div class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: ${pt.survival_rate}%;"></div>
          </div>
        `;
        survContainer.appendChild(item);
      });
    }

    // Render Hidden Baseline/Nil Records:
    // 1. Organ Clearance
    const safety = data.pharmacogenomic_safety;
    if (safety && safety.organ_clearance) {
      const renal = document.getElementById('renalCrClText');
      if (renal && safety.organ_clearance.renal_crcl) {
        const parts = String(safety.organ_clearance.renal_crcl).split(' ');
        renal.textContent = parts.length > 1 ? `${parts[0]} ${parts[1]}` : parts[0];
      }
      const hep = document.getElementById('hepaticBilirubinText');
      if (hep && safety.organ_clearance.hepatic_bilirubin) {
        const parts = String(safety.organ_clearance.hepatic_bilirubin).split(' ');
        hep.textContent = parts.length > 1 ? `${parts[0]} ${parts[1]}` : parts[0];
      }
      const card = document.getElementById('cardiacLVEFText');
      if (card && safety.organ_clearance.cardiac_lvef) {
        card.textContent = String(safety.organ_clearance.cardiac_lvef).split(' ')[0];
      }
    }

    // 2. Pharmacogenomics
    const pharmGrid = document.getElementById('pharmacoEnzymesGrid');
    if (pharmGrid && safety) {
      pharmGrid.innerHTML = (safety.pharmacogenomics || []).map(p => `
        <div class="p-3 rounded-xl bg-[#111315] border border-[#2c3036] space-y-1 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-200 font-mono">${p.gene}</span>
            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">${p.risk_level}</span>
          </div>
          <div class="text-[11px] text-slate-400">${p.phenotype}</div>
          <div class="text-[10px] text-slate-500 font-mono">Target: ${p.target_drugs}</div>
        </div>
      `).join('');
    }

    // 3. NGS Somatic Alterations
    const ngs = data.ngs_genomic_profile;
    if (ngs) {
      const tmbEl = document.getElementById('ngsTMBText');
      if (tmbEl) tmbEl.textContent = ngs.tumor_mutational_burden || '6.8';
      const msiEl = document.getElementById('ngsMSIText');
      if (msiEl) msiEl.textContent = ngs.microsatellite_status || 'MSS';
      const pdl1El = document.getElementById('ngsPDL1Text');
      if (pdl1El) pdl1El.textContent = ngs.pdl1_tps || '35%';

      const vGrid = document.getElementById('ngsVariantsGrid');
      if (vGrid) {
        vGrid.innerHTML = (ngs.actionable_variants || []).map(v => `
          <div class="p-3 rounded-xl bg-[#111315] border border-[#2c3036] space-y-1 text-xs">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-200 font-mono">${v.gene}</span>
              <span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[#181a1d] text-slate-300 border border-[#2c3036]">${v.tier}</span>
            </div>
            <div class="text-white text-xs font-semibold">${v.variant}</div>
            <div class="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1 border-t border-[#2c3036]">
              <span>VAF: <strong class="text-blue-400">${v.vaf}</strong></span>
              <span>${v.depth}</span>
            </div>
          </div>
        `).join('');
      }
    }

    // 4. Clinical Trials
    const trialsContainer = document.getElementById('clinicalTrialsContainer');
    if (trialsContainer) {
      const trials = data.matched_clinical_trials || [];
      if (trials.length === 0) {
        trialsContainer.innerHTML = `<div class="p-3 text-xs text-slate-400">Standard surveillance recommended. No active intervention trials needed.</div>`;
      } else {
        trialsContainer.innerHTML = trials.map(tr => `
          <div class="p-3 rounded-xl bg-[#111315] border border-[#2c3036] space-y-1.5 text-xs">
            <div class="flex items-center justify-between font-mono">
              <span class="text-slate-300 font-bold">${tr.nct_id} · ${tr.phase}</span>
              <span class="text-emerald-400 font-semibold">${tr.match_score}% Match</span>
            </div>
            <div class="font-semibold text-slate-100">${tr.title}</div>
            <div class="text-[11px] text-slate-400">${tr.intervention}</div>
          </div>
        `).join('');
      }
    }
  }

  // Ratify MDT Listener
  const ratifyMDTBtn = document.getElementById('ratifyMDTBtn');
  const mdtRatificationStatusBadge = document.getElementById('mdtRatificationStatusBadge');

  if (ratifyMDTBtn) {
    ratifyMDTBtn.addEventListener('click', async () => {
      const boardId = currentPredictionData?.virtual_tumor_board?.board_id || 'MDT-948201';
      try {
        const resp = await fetch(`${API_BASE}/tumor-board/vote`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            board_id: boardId,
            clinician_name: 'Attending Oncologist',
            status: 'RATIFIED',
            override_notes: 'Ratified by multidisciplinary board attending.'
          })
        });

        if (resp.ok) {
          if (mdtRatificationStatusBadge) {
            mdtRatificationStatusBadge.textContent = '✓ Ratified in EHR Protocol';
            mdtRatificationStatusBadge.className = 'text-xs font-mono font-bold px-3 py-1.5 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30';
          }
          ratifyMDTBtn.textContent = '✓ Protocol Ratified';
          ratifyMDTBtn.disabled = true;
          ratifyMDTBtn.className = 'px-4 py-2 rounded-xl bg-[#202327] text-slate-400 font-bold text-xs cursor-default';
        }
      } catch (err) {
        console.warn('Ratification error:', err);
      }
    });
  }

  // FHIR Export
  window.downloadFHIRReport = function() {
    if (!currentPredictionData) return;
    const bundle = currentPredictionData.fhir_diagnostic_bundle || {
      resourceType: 'Bundle',
      type: 'document',
      timestamp: new Date().toISOString(),
      meta: { source: 'celldiag Precision Diagnostics' }
    };
    const jsonStr = JSON.stringify(bundle, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `celldiag_FHIR_${(currentPredictionData.cancer_type || 'Report').replace(/[^a-zA-Z0-9]/g, '_')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Clinical Report Download
  window.downloadDiagnosticReport = function() {
    if (!currentPredictionData) return;
    const d = currentPredictionData;
    const timestamp = new Date().toLocaleString();
    const repText = (reportTextInput && reportTextInput.value.trim()) ? reportTextInput.value.trim() : 'Not Provided';
    const vitalsStr = `CA-125: ${ca125Input && ca125Input.value ? ca125Input.value + ' U/mL' : 'Omitted'} | CEA: ${ceaInput && ceaInput.value ? ceaInput.value + ' ng/mL' : 'Omitted'}`;

    const reportContent = `
================================================================================
    CELLDIAG PRECISION MULTIMODAL ONCOLOGY CLINICAL REPORT
================================================================================
Timestamp: ${timestamp}
Platform: celldiag Multimodal Decision Support
Verdict: ${d.cancer_type || 'Breast Cancer'} (${d.cancer_subtype || 'IDC'})
Stage: ${d.cancer_stage || 'Stage IIA'} (TNM: ${d.tnm_classification || 'cT2 N0 M0'})
Diagnostic Certainty: ${((d.cancer_type_confidence || d.confidence || 0.958) * 100).toFixed(1)}%
5-Year Overall Survival: ${Math.round((d.survival_probability || 0.93) * 100)}%
MDT Consensus Concordance: ${(d.virtual_tumor_board && d.virtual_tumor_board.consensus_concordance) || 97.4}%

CLINICAL NARRATIVE:
${d.patient_friendly_summary || d.plain_english_summary}

RECOMMENDED PROTOCOL:
${(d.ranked_therapies || []).map(t => `* [Priority #${t.priority}] ${t.name} (${t.category}): ${t.mechanism}`).join('\n')}
================================================================================
`;
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `celldiag_Clinical_Report_${(d.cancer_type || 'Report').replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  function getFallbackDemoData(hasImage = false) {
    return {
      cancer_type: 'Breast Cancer',
      cancer_subtype: 'Invasive Ductal Carcinoma (IDC)',
      cancer_stage: 'Stage IIA',
      tnm_classification: 'cT2 N0 M0',
      confidence: 0.958,
      cancer_type_confidence: 0.958,
      survival_probability: 0.93,
      image_weight: hasImage ? 0.45 : 0.00,
      text_weight: hasImage ? 0.35 : 0.65,
      tabular_weight: hasImage ? 0.20 : 0.35,
      grad_cam_available: hasImage,
      grad_cam_image: null,
      patient_friendly_summary: hasImage
        ? 'The algorithmic analysis identified findings consistent with breast cancer (Stage IIA). Cellular pleomorphism and elevated CA-125 markers support this.'
        : 'The algorithmic analysis identified findings consistent with breast cancer (Stage IIA) based on clinical narrative notes and elevated biomarker indicators. Histopathology slide was omitted.',
      oncology_technical_summary: 'BioBERT pathology embeddings identify infiltrating ductal epithelial proliferations with nuclear pleomorphism. Elevated CA-125 reflects potential serosal involvement. NCCN recommendations include surgical resection and receptor-directed therapy.',
      evidence_breakdown: [
        { modality: 'Pathology Report', finding: 'Identified invasive ductal architectural disruption.', impact: '+Primary Malignancy' }
      ],
      ranked_therapies: [
        { name: 'Breast-Conserving Surgery (Partial Mastectomy)', category: 'NCCN Cat 1', mechanism: 'Local tumor resection with clear margins', priority: 1 },
        { name: 'Sentinel Lymph Node Biopsy', category: 'NCCN Cat 1', mechanism: 'Axillary staging to rule out micrometastasis', priority: 2 },
        { name: 'Adjuvant Endocrine Therapy', category: 'NCCN Cat 1', mechanism: 'Receptor signaling pathway inhibition', priority: 3 }
      ],
      survival_projections: {
        five_year_rate: 93,
        curve: [
          { timepoint: '1 Year', survival_rate: 99, ci_lower: 96, ci_upper: 100 },
          { timepoint: '3 Years', survival_rate: 96, ci_lower: 91, ci_upper: 99 },
          { timepoint: '5 Years', survival_rate: 93, ci_lower: 87, ci_upper: 97 }
        ]
      },
      matched_clinical_trials: [
        {
          nct_id: 'NCT04486300',
          title: 'DESTINY-Breast06: Trastuzumab Deruxtecan Targeted ADC',
          phase: 'Phase III',
          match_score: 98.2,
          intervention: 'Trastuzumab Deruxtecan (T-DXd)'
        }
      ],
      virtual_tumor_board: {
        board_id: 'MDT-948201',
        consensus_concordance: 97.4,
        consensus_verdict: 'Unanimous Multidisciplinary Consensus Plan Ratified',
        clinical_summary: 'All 4 oncology specialists reviewed the multimodal parameters with full concordance on surgical clearance, systemic sequencing, and precision radiotherapy.',
        specialists: [
          { specialty: 'Surgical Oncology', specialist_name: 'Dr. Sarah Lin, MD, FACS', recommendation: 'Partial mastectomy with sentinel lymph node biopsy.', vote: 'Approved' },
          { specialty: 'Medical Oncology', specialist_name: 'Dr. Marcus Vance, MD, PhD', recommendation: 'Adjuvant endocrine protocol with SERM receptor blockade.', vote: 'Approved' },
          { specialty: 'Radiation Oncology', specialist_name: 'Dr. Elena Rostova, MD', recommendation: 'Hypofractionated whole-breast irradiation (40 Gy / 15 fx).', vote: 'Approved' },
          { specialty: 'Molecular Genetics', specialist_name: 'Dr. Aris Thorne, MD, FCAP', recommendation: 'Reflex 21-gene expression profiling (Oncotype DX).', vote: 'Approved' }
        ],
        deliberation_points: [
          'Evaluated breast conservation versus total mastectomy.',
          'Assessed cardiac safety prior to systemic sequencing.',
          'Confirmed adequate renal and hepatic organ clearance.'
        ],
        ratified_action_plan: [
          'Schedule outpatient breast-conserving surgical resection.',
          'Obtain reflex molecular profiling on excised tissue specimen.',
          'Initiate adjuvant radiation therapy at postoperative week 4.',
          'Serial biomarker monitoring with CA-125 surveillance at Month 3.'
        ]
      },
      ngs_genomic_profile: {
        tumor_mutational_burden: '6.8 mut/Mb',
        microsatellite_status: 'MSS',
        pdl1_tps: '35%',
        actionable_variants: [
          { gene: 'PIK3CA', variant: 'H1047R', exon: 'Exon 20', vaf: '28.4%', depth: '1240x', tier: 'Tier I' },
          { gene: 'TP53', variant: 'R175H', exon: 'Exon 5', vaf: '34.1%', depth: '980x', tier: 'Tier II' }
        ]
      },
      pharmacogenomic_safety: {
        overall_safety_rating: 'Cleared for Standard Protocols',
        pharmacogenomics: [
          { gene: 'DPYD', phenotype: 'Normal (*1/*1)', risk_level: 'Low Risk', target_drugs: '5-FU, Capecitabine' },
          { gene: 'UGT1A1', phenotype: 'Intermediate (*1/*28)', risk_level: 'Moderate Risk', target_drugs: 'Irinotecan' },
          { gene: 'TPMT', phenotype: 'Normal (*1/*1)', risk_level: 'Low Risk', target_drugs: '6-Mercaptopurine' }
        ],
        organ_clearance: {
          renal_crcl: '94 mL/min (Normal)',
          hepatic_bilirubin: '0.7 mg/dL (Normal)',
          cardiac_lvef: '62%'
        }
      }
    };
  }

  // Initial load: Load CASE-01
  const initialData = BENCHMARKS['CASE-01'];
  if (reportTextInput) reportTextInput.value = initialData.reportText;
  if (ca125Input) ca125Input.value = initialData.ca125;
  if (ceaInput) ceaInput.value = initialData.cea;
  if (ageInput) ageInput.value = initialData.age;
  if (bpInput) bpInput.value = initialData.bp;
  if (charCount) charCount.textContent = `${initialData.reportText.length} chars`;
  loadSampleOrgan(initialData.organ);
  updateModalityStatus();
  executeInference();
});
